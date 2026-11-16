"""
Fetch a Kaggle job's results into the project (run on the laptop).

    python kaggle\\pull_job.py step9_train            # status now; if finished, download and unpack
    python kaggle\\pull_job.py step9_train --wait     # check every minute until it finishes
(Kaggle's command-line tool gives a job's log only once the job has finished; the last 25 lines are printed then.)

Downloads job_output.zip, job_log.txt and status.json into kaggle/_pulled/<job>/ and unpacks job_output.zip over
the project. The zip holds only the files the job created or changed under its output paths, so nothing else in
results folders is touched. Paths that would land outside the project are refused.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from push_job import cli, STAGING  # noqa: E402


def status(kernel):
    r = cli("kernels", "status", kernel, check=False, capture=True)
    m = re.search(r'status\s+"?([A-Za-z_.]+)', (r.stdout or "") + (r.stderr or ""))
    return (m.group(1).lower().replace("kernelworkerstatus.", "") if m else "unknown"), (r.stdout or r.stderr or "").strip()


def unpack(zpath, root=ROOT):
    root = os.path.abspath(root)
    done = []
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            dest = os.path.abspath(os.path.join(root, info.filename))
            if not dest.startswith(root + os.sep):
                raise SystemExit(f"refusing a path outside the project: {info.filename}")
            if info.is_dir():
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(info) as src, open(dest, "wb") as out:
                out.write(src.read())
            done.append(info.filename)
    return done


def download(kernel, out):
    if os.path.isdir(out):                       # no stale files from an earlier run of the same job
        for fn in os.listdir(out):
            fp = os.path.join(out, fn)
            if os.path.isfile(fp):
                os.remove(fp)
    os.makedirs(out, exist_ok=True)
    r = cli("kernels", "output", kernel, "-p", out, check=False)
    if r.returncode != 0 and not os.path.exists(os.path.join(out, "status.json")):
        raise SystemExit("downloading the job's output failed; run the same command again")


def output_bundle(out):
    """The push the downloaded output belongs to: status.json, else the log's first line ('(bundle X)')."""
    try:
        with open(os.path.join(out, "status.json"), encoding="utf-8") as f:
            b = json.load(f).get("bundle_id")
        if b:
            return b
    except (OSError, ValueError):
        pass
    try:
        with open(os.path.join(out, "job_log.txt"), encoding="utf-8", errors="replace") as f:
            m = re.search(r"\(bundle ([0-9-]+)\)", f.read(4000))
        return m.group(1) if m else None
    except OSError:
        return None


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")      # a log line with "−" must not crash a Windows console
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--any-run", action="store_true",
                    help="take whatever output Kaggle serves now, even from an earlier push (the log says which)")
    ap.add_argument("--from-zip", help="unpack a job_output.zip already downloaded (no Kaggle calls)")
    a = ap.parse_args(argv)
    if a.from_zip:
        files = unpack(a.from_zip)
        print(f"Unpacked {len(files)} files into the project.")
        return 0
    with open(os.path.join(STAGING, f"last_{a.job}.json"), encoding="utf-8") as f:
        kernel = json.load(f)["kernel"]
    t0 = time.time()
    while True:
        st, raw = status(kernel)
        print(f"{kernel}: {st} ({(time.time() - t0) / 60:.0f} min waited)", flush=True)
        if st in ("complete", "error", "cancelacknowledged", "cancelrequested") or not a.wait:
            break
        time.sleep(60)
    if st not in ("complete", "error"):
        print("Not finished yet." + ("" if a.wait else " Run again later, or add --wait."))
        return 0
    with open(os.path.join(STAGING, f"last_{a.job}.json"), encoding="utf-8") as f:
        want = json.load(f).get("bundle_id")
    out = os.path.join(HERE, "_pulled", a.job)
    for attempt in range(21):
        download(kernel, out)
        got = output_bundle(out)
        if not want or got == want or a.any_run:
            if a.any_run and want and got != want:
                print(f"Taking the output Kaggle serves now: bundle {got} (the last push recorded was {want}).")
            break
        if attempt == 0:
            print(f"Kaggle is still serving an earlier run's output (bundle {got}, this push is {want}); "
                  "waiting for the new output (up to 20 minutes) ...", flush=True)
        time.sleep(60)
    else:
        print(f"Kaggle still serves the earlier run's output (bundle {got}); nothing unpacked. Run the same "
              "command again later.")
        return 2
    sp = os.path.join(out, "status.json")
    s = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    logp = os.path.join(out, "job_log.txt")
    if os.path.exists(logp):
        with open(logp, encoding="utf-8", errors="replace") as f:
            tail = f.readlines()[-25:]
        print("--- last lines of job_log.txt ---\n" + "".join(tail))
    zp = os.path.join(out, "job_output.zip")
    files = unpack(zp) if os.path.exists(zp) else []
    print(f"Job {'succeeded' if s.get('ok') else 'FAILED'}"
          + (f" at: {s.get('failed_command')}" if s.get("failed_command") else "")
          + (f" ({s.get('error')})" if s.get("error") else "")
          + f"; {len(files)} files unpacked into the project; full log: {logp}")
    return 0 if s.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
