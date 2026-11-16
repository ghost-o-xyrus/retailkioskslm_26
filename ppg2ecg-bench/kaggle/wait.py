"""Wait until one or more Kaggle kernels finish, printing their status every 2 minutes.

    python kaggle/wait.py --user YOUR_KAGGLE_USERNAME k00 k01

Short names (k00, k10, k20, ...) are expanded to the full kernel slugs. Exits with code 1 if any failed.
"""
import argparse
import subprocess
import sys
import time

SLUGS = {
    "k00": "ppg2ecg-k00-prep-data", "k01": "ppg2ecg-k01-models", "k10": "ppg2ecg-k10-smoke",
    "k20a": "ppg2ecg-k20a-cardiogan-clean-long", "k20b": "ppg2ecg-k20b-cardiogan-clean-aurora",
    "k21a": "ppg2ecg-k21a-cardiogan-robust-a", "k21b": "ppg2ecg-k21b-cardiogan-robust-b",
    "k30a": "ppg2ecg-k30a-ppgflowecg-clean-long", "k30b": "ppg2ecg-k30b-ppgflowecg-clean-aurora",
    "k31a": "ppg2ecg-k31a-ppgflowecg-robust-a", "k31b": "ppg2ecg-k31b-ppgflowecg-robust-b",
    "k40a": "ppg2ecg-k40a-baseline-clean", "k40b": "ppg2ecg-k40b-baseline-robust",
    "k50": "ppg2ecg-k50-cpu-profile",
    "k02": "ppg2ecg-k02-prep-bidmc", "k22": "ppg2ecg-k22-cardiogan-bidmc",
    "k32": "ppg2ecg-k32-ppgflowecg-bidmc", "k42": "ppg2ecg-k42-baseline-bidmc",
    "k03": "ppg2ecg-k03-prep-maf", "k04": "ppg2ecg-k04-models-rddm", "k60": "ppg2ecg-k60-info",
    "k70a": "ppg2ecg-k70a-rddm-clean-long", "k70b": "ppg2ecg-k70b-rddm-clean-aurora",
    "k71a": "ppg2ecg-k71a-rddm-robust-a", "k71b": "ppg2ecg-k71b-rddm-robust-b",
    "k23": "ppg2ecg-k23-cardiogan-maf", "k33": "ppg2ecg-k33-ppgflowecg-maf", "k43": "ppg2ecg-k43-baseline-maf",
    "k80": "ppg2ecg-k80-author-eval", "k44a": "ppg2ecg-k44a-zhu-clean", "k44b": "ppg2ecg-k44b-zhu-robust",
    "k51": "ppg2ecg-k51-cpu-profile-new",
    "k89": "ppg2ecg-k89-train-smoke", "k90": "ppg2ecg-k90-train-chiu", "k91": "ppg2ecg-k91-train-clep",
    "k92": "ppg2ecg-k92-train-p2e", "k93": "ppg2ecg-k93-train-yalcin",
    "k95a": "ppg2ecg-k95a-trained-clean-long", "k95b": "ppg2ecg-k95b-trained-clean-aurora",
    "k95c": "ppg2ecg-k95c-trained-robust", "k52": "ppg2ecg-k52-cpu-profile-trained",
    "k96a": "ppg2ecg-k96a-yalcin-clean-long", "k96b": "ppg2ecg-k96b-yalcin-clean-aurora",
    "k96c": "ppg2ecg-k96c-yalcin-robust", "k53": "ppg2ecg-k53-cpu-profile-yalcin",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("kernels", nargs="+")
    ap.add_argument("--every", type=int, default=120, help="seconds between checks")
    a = ap.parse_args()

    pending = {k: f"{a.user}/{SLUGS.get(k, k)}" for k in a.kernels}
    failed = []
    while pending:
        for k, ref in list(pending.items()):
            out = subprocess.run(["kaggle", "kernels", "status", ref], capture_output=True, text=True)
            s = (out.stdout + out.stderr).strip()
            low = s.lower()
            if out.returncode != 0:          # network hiccup / kernel not visible yet: just retry later
                print(f"{time.strftime('%H:%M:%S')}  {k}: (could not get status, retrying) {s[-200:]}", flush=True)
                continue
            print(f"{time.strftime('%H:%M:%S')}  {k}: {s}", flush=True)
            if "complete" in low:
                pending.pop(k)
            elif "error" in low or "cancel" in low or "fail" in low:
                failed.append(k)
                pending.pop(k)
        if pending:
            time.sleep(a.every)
    print("finished." + (f"  FAILED: {failed} - open the kernel page on kaggle.com and read its log" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped watching - the jobs keep running on Kaggle.")
