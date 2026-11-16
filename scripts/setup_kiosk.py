"""
Set this copy of the repository up to run (setup.bat calls this with whatever Python it found or installed):

  1. a virtual environment in .venv (so nothing is installed into your own Python)
  2. the four packages the kiosk needs (requirements.txt: numpy, openvino, tokenizers, psutil)
  3. scripts/fetch_assets.py: llama.cpp, the two language models, the retrieval models, the adapters

    python scripts\\setup_kiosk.py                 everything
    python scripts\\setup_kiosk.py --only tier-a   pass-through to fetch_assets.py (see its --help)

Safe to run again: each step skips what is already done, and interrupted downloads resume. Standard library only.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VENV = os.path.join(ROOT, ".venv")
MIN, MAX = (3, 10), (3, 13)


def venv_python():
    win = os.path.join(VENV, "Scripts", "python.exe")
    return win if os.name == "nt" else os.path.join(VENV, "bin", "python")


def step(n, text):
    print(f"\n=== Step {n} of 3: {text} ===", flush=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    v = sys.version_info[:2]
    if not MIN <= v <= MAX:
        print(f"This is Python {v[0]}.{v[1]}; the kiosk was built and measured on 3.13 and its packages support "
              f"{MIN[0]}.{MIN[1]} to {MAX[0]}.{MAX[1]}. Install Python 3.13 (python.org) and run setup again.")
        return 1
    step(1, "virtual environment (.venv)")
    py = venv_python()
    if os.path.exists(py):
        print("already there")
    else:
        if subprocess.call([sys.executable, "-m", "venv", VENV]) or not os.path.exists(py):
            print("Could not create .venv. If this is a Python from the Microsoft Store, install Python 3.13 from "
                  "python.org instead and run setup again.")
            return 1
        print(f"created with Python {v[0]}.{v[1]}")
    step(2, "Python packages (requirements.txt)")
    pip = [py, "-m", "pip", "--disable-pip-version-check"]
    subprocess.call(pip + ["install", "--quiet", "--upgrade", "pip"])
    if subprocess.call(pip + ["install", "-r", os.path.join(ROOT, "requirements.txt")]):
        lock = os.path.join(ROOT, "requirements.txt")
        print(f"\nThe pinned versions in {os.path.basename(lock)} could not be installed for this Python; "
              "trying the newest versions of the same packages.")
        names = []
        with open(lock, encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if line:
                    names.append(line.split("==")[0].split(">=")[0].strip())
        if subprocess.call(pip + ["install"] + names):
            print("Could not install the packages. Check the internet connection and run setup again.")
            return 1
    step(3, "llama.cpp, models, retrieval models, adapters")
    return subprocess.call([py, os.path.join(HERE, "fetch_assets.py")] + list(argv), cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
