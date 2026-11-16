"""
Download everything the kiosk needs that is not stored in the repository (setup.bat runs this):

  1. llama.cpp for Windows, CPU build (Tier A) and Vulkan build (Tier B)      -> runtime/llama-cpu, runtime/llama-vulkan
  2. the two language models, GGUF files from Hugging Face (about 5 GB)       -> runtime/models/qwen3.5-2b, .../qwen3.5-4b
  3. the retrieval models in OpenVINO form (this repository's release assets) -> models/ov
  4. the Objective 4 adapters, GGUF (this repository's release assets)        -> finetune/adapters_gguf

    python scripts\\fetch_assets.py                    everything (skips what is already there)
    python scripts\\fetch_assets.py --check            download nothing; say what is present and what is missing
    python scripts\\fetch_assets.py --only models      only the two language models
    python scripts\\fetch_assets.py --only model-2b,llama-cpu      only what Tier A needs (ids as printed by --check)
    python scripts\\fetch_assets.py --build-retrieval  build the retrieval models here instead of downloading them
                                                      (installs sentence-transformers, optimum-intel and nncf; slow)
    python scripts\\fetch_assets.py --local-assets <folder>     take the two release zips from a folder

What is downloaded, from where and to where is listed in scripts/assets.json. Downloads resume if interrupted, and a
file whose size or SHA-256 is recorded there is checked against it. Standard library only.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = {"User-Agent": "slm-kiosk-setup/1.0"}
GROUPS = {"llama": ("llama-cpu", "llama-vulkan"), "models": ("model-2b", "model-4b"),
          "tier-a": ("llama-cpu", "model-2b", "retrieval"),
          "tier-b": ("llama-vulkan", "model-4b", "retrieval", "adapters")}


def say(msg=""):
    print(msg, flush=True)


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def human(n):
    return f"{n / 1e9:.2f} GB" if n >= 1e9 else f"{n / 1e6:.1f} MB"


def open_url(url, headers=None, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers=dict(UA, **(headers or {}))), timeout=timeout)


def download(url, dest, label, expect_size=None, expect_sha=None, tries=4):
    """Download url to dest through dest.part, resuming a partial file. Returns True when dest is complete."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    for attempt in range(1, tries + 1):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        try:
            r = open_url(url, {"Range": f"bytes={have}-"} if have else None)
            if "text/html" in (r.headers.get("Content-Type") or "") and not url.lower().endswith((".html", ".htm")):
                r.close()
                raise OSError("the server sent a web page instead of the file (not public, or the link is wrong)")
            if have and r.status != 206:           # the server ignored the range: start again
                have = 0
            total = int(r.headers.get("Content-Length") or 0) + have
            mode = "ab" if have else "wb"
            t0, last, got = time.time(), 0.0, have
            with r, open(part, mode) as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
                    got += len(b)
                    now = time.time()
                    if now - last >= 1.0:
                        last = now
                        speed = (got - have) / max(now - t0, 1e-6)
                        pct = f"{100 * got / total:5.1f}%" if total else "      "
                        sys.stdout.write(f"\r    {label}: {pct}  {human(got)} of {human(total) if total else '?'}"
                                         f"  {speed / 1e6:5.1f} MB/s   ")
                        sys.stdout.flush()
            sys.stdout.write("\r" + " " * 100 + "\r")
            if total and got < total:
                raise OSError(f"connection closed after {human(got)} of {human(total)}")
            break
        except urllib.error.HTTPError as e:
            if e.code == 416 and have:              # the partial file is already the whole file
                break
            if e.code in (401, 403, 404):
                say(f"    {label}: the server answered {e.code} for {url}")
                return False
            err = f"HTTP {e.code}"
        except (OSError, urllib.error.URLError) as e:
            err = str(getattr(e, "reason", e))
        sys.stdout.write("\n")
        if attempt == tries:
            say(f"    {label}: download failed ({err}). Run setup again to resume.")
            return False
        say(f"    {label}: {err}; trying again in {5 * attempt} s (try {attempt + 1} of {tries})")
        time.sleep(5 * attempt)
    size = os.path.getsize(part)
    if expect_size and size != expect_size:
        say(f"    {label}: WARNING: size is {size:,} bytes, the recorded size is {expect_size:,}. "
            "The file at the source has changed since the results were measured.")
    if expect_sha:
        say(f"    {label}: checking SHA-256 ...")
        got_sha = sha256(part)
        if got_sha != expect_sha:
            say(f"    {label}: WARNING: SHA-256 {got_sha[:16]}… differs from the recorded {expect_sha[:16]}…. "
                "This is not the exact file the results were measured with.")
    os.replace(part, dest)
    return True


def gdrive_url(file_id):
    """Direct download address of a public Google Drive file. Large files need a token from a confirmation page."""
    base = "https://drive.usercontent.google.com/download"
    url = f"{base}?id={urllib.parse.quote(file_id)}&export=download&confirm=t"
    try:
        r = open_url(url)
        ctype = r.headers.get("Content-Type") or ""
        if "text/html" not in ctype:
            r.close()
            return url
        page = r.read(200000).decode("utf-8", "replace")
        r.close()
    except (OSError, urllib.error.URLError):
        return url
    fields = dict(re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', page))
    action = re.search(r'<form[^>]+action="([^"]+)"', page)
    if fields.get("id"):
        return (action.group(1).replace("&amp;", "&") if action else base) + "?" + urllib.parse.urlencode(fields)
    return url


def unzip(zip_path, dest):
    """Extract, refusing any entry that would land outside dest."""
    dest = os.path.abspath(dest)
    with zipfile.ZipFile(zip_path) as z:
        for m in z.infolist():
            target = os.path.abspath(os.path.join(dest, m.filename))
            if not (target == dest or target.startswith(dest + os.sep)):
                raise ValueError(f"unsafe path in {os.path.basename(zip_path)}: {m.filename}")
        z.extractall(dest)


def github_repo(cfg):
    repo = os.environ.get("SLM_GITHUB_REPO") or cfg.get("github_repo") or ""
    if not repo:
        try:
            out = subprocess.run(["git", "-C", ROOT, "remote", "get-url", "origin"], capture_output=True, text=True,
                                 timeout=10).stdout.strip()
            m = re.search(r"github\.com[:/]+([^/]+/[^/]+?)(?:\.git)?/?$", out)
            repo = m.group(1) if m else ""
        except (OSError, subprocess.SubprocessError):
            repo = ""
    return repo


# ---------------------------------------------------------------- the four kinds of item
def llama_assets(cfg, tag=None):
    """{build id: (url, name, tag)} for the llama.cpp release `tag` (the newest release if that tag is gone)."""
    ll = cfg["llama"]
    tag = tag or ll.get("tag")
    api = ll.get("api", "https://api.github.com/repos/" + ll["repo"])
    out, used = {}, tag
    for attempt, path in enumerate(([f"/releases/tags/{tag}"] if tag else []) + ["/releases/latest"]):
        try:
            with open_url(api + path, {"Accept": "application/vnd.github+json"}, timeout=30) as r:
                rel = json.loads(r.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, ValueError) as e:
            say(f"    llama.cpp release {path.rsplit('/', 1)[-1]}: could not be read ({getattr(e, 'reason', e)})")
            continue
        used = rel.get("tag_name") or tag
        for b in ll["builds"]:
            for a in rel.get("assets", []):
                if re.search(b["asset_regex"], a["name"]):
                    out[b["id"]] = (a["browser_download_url"], a["name"], used)
                    break
        if out:
            if tag and used != tag:
                say(f"    NOTE: llama.cpp {tag} (the build the results were measured with) is no longer offered; "
                    f"using the newest release, {used}. Replies and timings can differ slightly.")
            return out
    if tag:                                          # no API (rate limit, proxy): the usual file names
        base = ll.get("download", f"https://github.com/{ll['repo']}/releases/download")
        for b in ll["builds"]:
            kind = "cpu" if "cpu" in b["id"] else "vulkan"
            name = f"llama-{tag}-bin-win-{kind}-x64.zip"
            out[b["id"]] = (f"{base}/{tag}/{name}", name, tag)
    return out


def get_llama(cfg, b, rt, urls, state):
    dest = os.path.join(rt, b["dest"])
    exe = os.path.join(dest, b["exe"])
    if os.path.exists(exe):
        return "present"
    if b["id"] not in urls:
        return "FAILED: no download found for this build"
    url, name, tag = urls[b["id"]]
    tmp = os.path.join(rt, "_downloads", name)
    if not download(url, tmp, b["label"]):
        return "FAILED: download"
    stage = dest + "._new"
    shutil.rmtree(stage, ignore_errors=True)
    unzip(tmp, stage)
    found = None
    for d, _, files in os.walk(stage):               # some releases put the programs in build/bin/
        if b["exe"] in files:
            found = d
            break
    if not found:
        shutil.rmtree(stage, ignore_errors=True)
        return f"FAILED: {b['exe']} is not in {name}"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.move(found, dest)
    shutil.rmtree(stage, ignore_errors=True)
    os.remove(tmp)
    state.setdefault("llama", {})[b["id"]] = {"tag": tag, "asset": name, "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    return f"downloaded ({tag})"


def get_model(m, rt):
    dest = os.path.join(rt, m["dest"])
    if os.path.exists(dest):
        if m.get("size") and os.path.getsize(dest) != m["size"]:
            return f"present, but its size differs from the recorded {m['size']:,} bytes"
        return "present"
    ok = download(m["url"], dest, m["label"], m.get("size"), m.get("sha256"))
    return "downloaded" if ok else "FAILED: download"


def provided(a):
    return all(os.path.exists(os.path.join(ROOT, p)) for p in a["provides"])


def retrieval_ready():
    """Both retrieval models usable by retrieval/ov_runtime.py (an .xml file and a tokenizer each)."""
    import glob
    for name in ("bge-small", "minilm"):
        d = os.path.join(ROOT, "models", "ov", name)
        if not (glob.glob(os.path.join(d, "**", "*.xml"), recursive=True)
                and glob.glob(os.path.join(d, "**", "tokenizer.json"), recursive=True)):
            return False
    return True


def build_retrieval():
    say("    Building the retrieval models on this computer (about 10 minutes; needs about 3 GB of packages) ...")
    pk = ["sentence-transformers", "optimum[openvino]", "nncf"]
    if subprocess.call([sys.executable, "-m", "pip", "install", "--disable-pip-version-check"] + pk):
        return "FAILED: could not install " + ", ".join(pk)
    for script in ("export_openvino.py", "quantize_reranker.py"):
        if subprocess.call([sys.executable, os.path.join(ROOT, "retrieval", script)], cwd=ROOT):
            return f"FAILED: retrieval/{script}"
    return "built here (not byte-identical to the files the results were measured with)" if retrieval_ready() \
        else "FAILED: the build did not produce models/ov"


def get_project_asset(a, cfg, rt, force_build=False, local=None):
    ready = retrieval_ready() if a["id"] == "retrieval" else provided(a)
    if ready:
        return "present"
    if local and os.path.exists(os.path.join(local, a["file"])):
        unzip(os.path.join(local, a["file"]), os.path.join(ROOT, a.get("unpack_to", ".")))
        ready = retrieval_ready() if a["id"] == "retrieval" else provided(a)
        return f"unpacked from {local}" if ready else "FAILED: the archive did not contain " + ", ".join(a["provides"])
    if force_build and a.get("rebuild") == "retrieval":
        return build_retrieval()
    repo = github_repo(cfg)
    sources = []
    if a.get("url"):
        sources.append(a["url"])
    if repo:
        base = cfg.get("release_base", "https://github.com")
        sources.append(f"{base}/{repo}/releases/download/{cfg.get('release_tag', 'v1.0')}/{a['file']}")
    tmp = os.path.join(rt, "_downloads", a["file"])
    ok = False
    for url in sources:
        ok = download(url, tmp, a["label"].split(" (")[0], a.get("size"), a.get("sha256"))
        if ok:
            break
    if not ok and a.get("gdrive_id"):
        ok = download(gdrive_url(a["gdrive_id"]), tmp, a["label"].split(" (")[0] + " [Google Drive]",
                      a.get("size"), a.get("sha256"))
    if ok:
        unzip(tmp, os.path.join(ROOT, a.get("unpack_to", ".")))
        os.remove(tmp)
        ready = retrieval_ready() if a["id"] == "retrieval" else provided(a)
        return "downloaded" if ready else "FAILED: the archive did not contain " + ", ".join(a["provides"])
    if not sources and not a.get("gdrive_id"):
        say("    This copy does not know which GitHub repository it came from (no 'github_repo' in "
            "scripts/assets.json and no git remote), so the project's own files cannot be downloaded.")
    if a.get("rebuild") == "retrieval":
        return build_retrieval()
    return "MISSING (optional)" if a.get("optional") else "FAILED: download"


# ---------------------------------------------------------------- what can run
def readiness(cfg, rt):
    def has(*parts):
        return os.path.exists(os.path.join(*parts))
    cpu, vk = has(rt, "llama-cpu", "llama-server.exe"), has(rt, "llama-vulkan", "llama-server.exe")
    m2, m4 = (has(rt, m["dest"]) for m in cfg["models"][:2])
    ret = retrieval_ready()
    lora = has(ROOT, "finetune", "adapters_gguf", "lora_4b.gguf")
    a, b = cpu and m2 and ret, vk and m4 and ret
    return {"Tier A (start_tier_a.bat)": (a, "" if a else "needs the CPU build, the 2B model and the retrieval models"),
            "Tier B (start_tier_b.bat)": (b, ("" if lora else "runs without the adapter (lora_4b.gguf is missing)")
                                          if b else "needs the Vulkan build, the 4B model and the retrieval models"),
            "Lab (start_lab.bat)": (a or b, "both tiers selectable" if a and b else
                                    ("only the tier above that is ready" if a or b else "needs at least one tier"))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assets", default=os.path.join(HERE, "assets.json"))
    ap.add_argument("--only", default="", help="comma-separated ids or groups: llama, models, tier-a, tier-b, "
                    "llama-cpu, llama-vulkan, model-2b, model-4b, retrieval, adapters")
    ap.add_argument("--check", action="store_true", help="download nothing; report what is present")
    ap.add_argument("--build-retrieval", action="store_true", help="build models/ov here instead of downloading it")
    ap.add_argument("--llama-tag", default=None, help="llama.cpp release to use instead of the recorded one")
    ap.add_argument("--local-assets", default=None, metavar="FOLDER",
                    help="take retrieval_models_ov.zip and adapters_gguf.zip from this folder instead of the release")
    a = ap.parse_args(argv)
    with open(a.assets, encoding="utf-8") as f:
        cfg = json.load(f)
    rt = os.path.join(ROOT, cfg.get("runtime_dir", "runtime"))
    os.makedirs(rt, exist_ok=True)
    state_path = os.path.join(rt, "setup_state.json")
    state = json.load(open(state_path, encoding="utf-8")) if os.path.exists(state_path) else {}
    want = set()
    for w in filter(None, (x.strip() for x in a.only.split(","))):
        want.update(GROUPS.get(w, (w,)))
    items = [("llama", b) for b in cfg["llama"]["builds"]] + [("model", m) for m in cfg["models"]] + \
            [("asset", x) for x in cfg["project_assets"]]
    known = {x["id"] for _, x in items}
    if want - known:
        say(f"Unknown id(s): {', '.join(sorted(want - known))}. Known: {', '.join(sorted(known | set(GROUPS)))}")
        return 2
    items = [(k, x) for k, x in items if not want or x["id"] in want]

    if a.check:
        say("What is on this computer:")
        for kind, x in items:
            if kind == "llama":
                ok = os.path.exists(os.path.join(rt, x["dest"], x["exe"]))
            elif kind == "model":
                ok = os.path.exists(os.path.join(rt, x["dest"]))
            else:
                ok = retrieval_ready() if x["id"] == "retrieval" else provided(x)
            say(f"  [{'x' if ok else ' '}] {x['id']:<13} {x['label']}")
    else:
        free = shutil.disk_usage(rt).free
        if free < 8e9 and any(k == "model" and not os.path.exists(os.path.join(rt, x["dest"])) for k, x in items):
            say(f"WARNING: only {human(free)} free on this drive; the two models need about 6 GB.")
        urls = None
        results = []
        for n, (kind, x) in enumerate(items, 1):
            say(f"[{n}/{len(items)}] {x['label']}")
            try:
                if kind == "llama":
                    if urls is None and not os.path.exists(os.path.join(rt, x["dest"], x["exe"])):
                        urls = llama_assets(cfg, a.llama_tag)
                    res = get_llama(cfg, x, rt, urls or {}, state)
                elif kind == "model":
                    res = get_model(x, rt)
                else:
                    res = get_project_asset(x, cfg, rt, a.build_retrieval,
                                            os.path.abspath(a.local_assets) if a.local_assets else None)
            except (OSError, ValueError, zipfile.BadZipFile) as e:
                res = f"FAILED: {type(e).__name__}: {e}"
            say(f"    -> {res}")
            results.append((x["id"], res))
        state["last_run"] = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "results": dict(results)}
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=1)
        shutil.rmtree(os.path.join(rt, "_downloads"), ignore_errors=True) if not any(
            r.startswith("FAILED") for _, r in results) else None
    say()
    say("What can run now:")
    ready = readiness(cfg, rt)
    for name, (ok, note) in ready.items():
        say(f"  {'READY    ' if ok else 'NOT READY'}  {name}{'   - ' + note if note else ''}")
    return 0 if ready["Lab (start_lab.bat)"][0] else 1


if __name__ == "__main__":
    sys.exit(main())
