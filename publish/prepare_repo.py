"""
Assemble the public repository from this project folder (run on the laptop, where the results are).

Nothing in the project folder is changed. Everything is written next to it, in ..\\slm-kiosk-publish\\ :

    repo\\      the tree to push to GitHub (code, data, results, logs, write-ups), cleaned
    release\\   retrieval_models_ov.zip and adapters_gguf.zip  -> GitHub release assets (setup.bat downloads them)
    drive\\     zip archives of the files too large for GitHub -> Google Drive
    publish_report.md   what went where, what was left out, what was scrubbed, what to look at by hand

    python publish\\prepare_repo.py build --github <owner>/<repository>
    python publish\\prepare_repo.py drive --remote gdrive:slm-kiosk-large-files     upload drive\\ with rclone, write the links
    python publish\\prepare_repo.py check                                           last look before pushing

What `build` does, in order:
  1. copies the project, leaving out caches, virtual environments, browser profiles, Kaggle staging folders, key files
     (kaggle.json, .env) and model weights;
  2. scrubs every text file in the copy: API keys and tokens -> [REDACTED]; the Windows user folder name ->
     "user"; this computer's name -> "kiosk-laptop"; private network addresses -> [private-ip]. Names in the
     write-ups and the code are not touched;
  3. zips models/ov and finetune/adapters_gguf as release assets and records their size and SHA-256, those of the two
     GGUF models and the llama.cpp build in scripts/assets.json; pins requirements.txt to the installed versions;
  4. moves every file over --file-limit-mb (50), and then the largest files until the tree is under --budget-mb (700),
     into drive\\ archives (never code, data, write-ups, reports or the files the app reads);
  5. writes docs/RESULTS.md (an index of every results folder), docs/LARGE_FILES.md and docs/ENVIRONMENT.md.

Standard library only.
"""
import argparse
import fnmatch
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MB = 1000 * 1000

# ---------------------------------------------------------------- what is left out of the copy
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "env", "slm-env", ".pytest_cache", ".ipynb_checkpoints",
             "node_modules", "browser_profile", "_staging", "_llama_build", "hf_cache", ".cache", "runtime",
             "_downloads", ".idea", ".vscode", ".mypy_cache", ".ruff_cache"}
SKIP_FILES = ["kaggle.json", ".env", ".env.*", "*.pem", "*.key", "*.pfx", "id_rsa*", "*.pyc", "*.pyo", "Thumbs.db",
              "desktop.ini", ".DS_Store", "*.part", "*.tmp", ".hash_cache.json", "app.pid", "credentials*.json",
              "client_secret*.json", "token.json", "rclone.conf", "review_terms.txt"]
WEIGHT_EXT = {".gguf", ".safetensors", ".bin", ".pt", ".pth", ".onnx", ".ckpt", ".h5"}
RELEASE = [  # (archive, source folder relative to the project, what it is)
    ("retrieval_models_ov.zip", "models/ov", "retrieval models in OpenVINO form"),
    ("adapters_gguf.zip", "finetune/adapters_gguf", "Objective 4 adapters, GGUF"),
]
# never moved to Google Drive: the app reads these, or they are what a reader opens first
KEEP_PATTERNS = ["results_obj3/_speed_step12/*.json", "results_retrieval/integration/*.json",
                 "results_retrieval/fallback_bypass/*.json", "results_retrieval/fallback/*.json", "eval/*",
                 "harness/plans/*", "knowledge/*", "router/*", "app/*", "data/*", "data_v1/*", "data_train/*",
                 "writeups/*", "docs/*", "scripts/*", "publish/*", "tools/*", "kiosk_core/*", "retrieval/*",
                 "harness/*", "finetune/*.py", "finetune/*.md", "finetune/*.sh", "kaggle/*.py", "kaggle/*.md",
                 "kaggle/*.json", "*/report.md", "*/README.md", "*/summary.json", "*/run_meta.json",
                 "*/verdicts.json", "*/policy.json", "*/scorecard*.json", "*/scorecard*.md"]
KEEP_BELOW = 256 * 1024          # small files stay in the repository whatever they are
MUST_HAVE = ["results_obj3/_speed_step12/fallback.json", "results_obj3/_speed_step12/choice.json",
             "results_retrieval/integration/integration.json", "eval/system_prompts.json",
             "harness/plans/obj3_step14.json", "knowledge/corpus.jsonl", "router/prototypes.json",
             "data/kiosk/skus.csv", "app/evidence.json", "scripts/assets.json", "setup.bat", "start_lab.bat",
             "start_tier_a.bat", "start_tier_b.bat", "README.md", "LICENSE"]

TEXT_EXT = {".py", ".md", ".json", ".jsonl", ".txt", ".log", ".csv", ".tsv", ".yaml", ".yml", ".sh", ".bat", ".ps1",
            ".cmd", ".html", ".htm", ".js", ".css", ".tex", ".bib", ".cfg", ".ini", ".toml", ".xml", ".out", ".err",
            ".ipynb", ".cff", ""}
CODE_EXT = {".py", ".js", ".sh", ".bat", ".ps1", ".cmd", ".html", ".css", ".tex"}

# ---------------------------------------------------------------- secrets (replaced by [REDACTED] everywhere)
SECRETS = [
    ("Hugging Face token", re.compile(r"(?<![A-Za-z0-9])hf_[A-Za-z0-9]{30,}")),
    ("Kaggle token", re.compile(r"(?<![A-Za-z0-9])KGAT_[A-Za-z0-9]{20,}")),
    ("GitHub token", re.compile(r"(?<![A-Za-z0-9])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("API key (sk-...)", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_\-]{24,}")),
    ("Google API key", re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_\-]{35}")),
    ("Google OAuth token", re.compile(r"(?<![A-Za-z0-9])ya29\.[A-Za-z0-9_\-]{20,}")),
    ("AWS key id", re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![A-Za-z0-9])")),
    ("Slack token", re.compile(r"(?<![A-Za-z0-9])xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("Kaggle key", re.compile(r'("key"\s*:\s*")[0-9a-f]{32}(")')),
]
AUTH = re.compile(r"((?:Authorization\s*[:=]\s*(?:Bearer\s+)?|Bearer\s+))([A-Za-z0-9_\-\.=+/]{24,})", re.I)
KEY_BEGIN = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
KEY_END = re.compile(r"-----END [A-Z ]*PRIVATE KEY-----")
KEY_BLOCK = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|\Z)", re.S)
REVIEW_TERMS_FILE = os.path.join(HERE, "review_terms.txt")     # words to flag for a look by hand; not published
# key = value pairs with a secret-looking name: redacted in data and log files, only reported in code
ASSIGN = re.compile(r"""((?:api[_-]?key|apikey|secret|access[_-]?token|auth[_-]?token|password|passwd|kaggle_key)
                        ["']?\s*[:=]\s*["']?)([A-Za-z0-9_\-\.=+/]{20,})""", re.I | re.X)
EMAIL = re.compile(r"(?<![A-Za-z0-9._%+\-])[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+")
PRIVATE_IP = re.compile(r"(?<![0-9.])(?:192\.168|10\.(?:25[0-5]|2[0-4]\d|1?\d?\d)|172\.(?:1[6-9]|2\d|3[01]))"
                        r"\.(?:25[0-5]|2[0-4]\d|1?\d?\d)\.(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![0-9.])")
USERS_ANY = re.compile(r"((?<=[\\/])Users(?:\\\\|\\|/))([^\\/\s\"'<>|:*?,;)\]]+)")   # a path: \\Users\\<name>
HOST_FIELD = re.compile(r'("host"\s*:\s*")([^"]*)(")')
NO_NAME_SCRUB = ("writeups/", "README.md", "LICENSE", "CITATION.cff")   # the author's name stays as written
NOT_USERS = {"public", "default", "user", "all users", "defaultuser0", "<you>", "<user>", "you", "name", "%username%",
             "$env:username", "username"}


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def human(n):
    return f"{n / 1e9:.2f} GB" if n >= 1e9 else (f"{n / 1e6:.1f} MB" if n >= 1e5 else f"{n / 1e3:.1f} KB")


def rel(path, base):
    return os.path.relpath(path, base).replace("\\", "/")


def matches(relpath, patterns):
    """'folder/*' covers everything below that folder; '*/name' matches the file name at any depth; anything else
    is matched against the whole relative path."""
    name = relpath.rsplit("/", 1)[-1]
    for p in patterns:
        if p.startswith("*/"):
            if fnmatch.fnmatch(name, p[2:]):
                return True
        elif p.endswith("/*") and "*" not in p[:-2]:
            if relpath.startswith(p[:-1]):
                return True
        elif fnmatch.fnmatch(relpath, p):
            return True
    return False


# ---------------------------------------------------------------- scrubbing
class Scrubber:
    def __init__(self, user_names, host_names, kaggle_user=None, scrub_kaggle=False):
        self.users = sorted({u for u in user_names if u and u.lower() not in NOT_USERS}, key=len, reverse=True)
        self.hosts = sorted({h for h in host_names if h and len(h) >= 4 and h.lower() not in ("local", "localhost")},
                            key=len, reverse=True)
        self.user_rx = [re.compile(r"((?<![A-Za-z])Users(?:\\\\|\\|/))" + re.escape(u) + r"(?=$|[\\/\"'\s,;)\]])", re.I)
                        for u in self.users]
        # a computer name is replaced wherever it appears only if it looks like one (LAPTOP-1A2B3C: a digit or a
        # hyphen); a plain word could be a person's name, so it is replaced in "host" fields only
        self.host_rx = [re.compile(r"(?<![A-Za-z0-9_\-])" + re.escape(h) + r"(?![A-Za-z0-9_\-])", re.I)
                        for h in self.hosts if re.search(r"[\d\-]", h)]
        self.kaggle_user = kaggle_user
        self.kaggle_rx = re.compile(r"(?<![A-Za-z0-9_\-])" + re.escape(kaggle_user) + r"(?![A-Za-z0-9_\-])") \
            if kaggle_user else None
        self.scrub_kaggle = scrub_kaggle
        terms = []
        if os.path.exists(REVIEW_TERMS_FILE):
            with open(REVIEW_TERMS_FILE, encoding="utf-8") as f:
                terms = [x.strip() for x in f if x.strip() and not x.startswith("#")]
        self.review_rx = re.compile(r"(?<![A-Za-z])(" + "|".join(re.escape(t) for t in terms) + r")(?![A-Za-z])",
                                    re.I) if terms else None
        self.counts = {}            # kind -> {file: n}
        self.review = {}            # kind -> {detail: n}

    def _hit(self, kind, relpath, n=1):
        self.counts.setdefault(kind, {})
        self.counts[kind][relpath] = self.counts[kind].get(relpath, 0) + n

    def _note(self, kind, detail, n=1):
        self.review.setdefault(kind, {})
        self.review[kind][detail] = self.review[kind].get(detail, 0) + n

    def text(self, s, relpath):
        ext = os.path.splitext(relpath)[1].lower()
        code = ext in CODE_EXT
        for kind, rx in SECRETS:
            def rep(m, kind=kind):
                self._hit(kind, relpath)
                g = m.groups()
                return (g[0] + "[REDACTED]" + (g[1] if len(g) > 1 else "")) if g else "[REDACTED]"
            if rx.search(s):
                s = rx.sub(rep, s)

        def assign(m):
            val = m.group(2)
            if not (re.search(r"\d", val) and re.search(r"[A-Za-z]", val)) or "[REDACTED]" in val:
                return m.group(0)
            if code:
                self._note("key-like value in code (not changed; look at it)", relpath)
                return m.group(0)
            self._hit("key = value with a secret-looking name", relpath)
            return m.group(1) + "[REDACTED]"
        if ASSIGN.search(s):
            s = ASSIGN.sub(assign, s)

        def auth(m):
            if not (re.search(r"\d", m.group(2)) and re.search(r"[A-Za-z]", m.group(2))):
                return m.group(0)
            self._hit("Authorization header", relpath)
            return m.group(1) + "[REDACTED]"
        if AUTH.search(s):
            s = AUTH.sub(auth, s)
        if self.review_rx is not None:
            n = len(self.review_rx.findall(s))
            if n and not relpath.startswith("publish/"):
                self._note("a word from publish/review_terms.txt (kept; check it is meant to be public)", relpath, n)
        if relpath.startswith(NO_NAME_SCRUB):
            return s

        for rx in self.user_rx:
            s, n = rx.subn(lambda m: m.group(1) + "user", s)
            if n:
                self._hit("Windows user folder name", relpath, n)

        def any_user(m):
            name = m.group(2)
            if name.lower() in NOT_USERS or name.startswith(("<", "%", "$", "{")):
                return m.group(0)
            self._hit("Windows user folder name", relpath)
            return m.group(1) + "user"
        if "sers" in s:
            s = USERS_ANY.sub(any_user, s)

        def host_field(m):
            if any(m.group(2).lower() == h.lower() for h in self.hosts):
                self._hit("computer name", relpath)
                return m.group(1) + "kiosk-laptop" + m.group(3)
            return m.group(0)
        if '"host"' in s:
            s = HOST_FIELD.sub(host_field, s)
        for rx in self.host_rx:
            s, n = rx.subn("kiosk-laptop", s)
            if n:
                self._hit("computer name", relpath, n)
        s, n = PRIVATE_IP.subn("[private-ip]", s)
        if n:
            self._hit("private network address", relpath, n)
        if self.kaggle_rx is not None:
            if self.scrub_kaggle:
                s, n = self.kaggle_rx.subn("kaggle-user", s)
                if n:
                    self._hit("Kaggle user name", relpath, n)
            else:
                n = len(self.kaggle_rx.findall(s))
                if n:
                    self._note("Kaggle user name (kept; --scrub-kaggle-user replaces it)", relpath, n)
        top = relpath.split("/")[0]
        if top not in ("data", "data_v1", "data_train", "knowledge", "eval", "finetune") and "@" in s:
            for e in set(EMAIL.findall(s)):
                if not e.lower().endswith((".example", ".png", ".jpg")) and "noreply" not in e.lower():
                    self._note("e-mail address (kept; check it is meant to be public)", e)
        return s

    def copy(self, src, dst, relpath):
        """Copy src to dst, scrubbed if it is text. Binary files are copied unchanged."""
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        ext = os.path.splitext(src)[1].lower()
        if ext not in TEXT_EXT:
            shutil.copy2(src, dst)
            return
        with open(src, "rb") as f:
            head = f.read(8192)
        enc = None
        if head.startswith(b"\xff\xfe") or head.startswith(b"\xfe\xff"):
            enc = "utf-16"
        elif b"\x00" in head:
            shutil.copy2(src, dst)          # binary after all
            return
        if enc:
            with open(src, "r", encoding=enc, errors="replace", newline="") as f:
                raw = f.read()
            if KEY_BEGIN.search(raw):
                raw = KEY_BLOCK.sub("[REDACTED PRIVATE KEY]", raw)
                self._hit("private key", relpath)
            out = self.text(raw, relpath)
            with open(dst, "w", encoding="utf-16", newline="") as f:
                f.write(out)
        else:
            with open(src, "r", encoding="utf-8", errors="surrogateescape", newline="") as fi, \
                    open(dst, "w", encoding="utf-8", errors="surrogateescape", newline="") as fo:
                in_key = False
                for line in fi:             # line by line: result files can be hundreds of MB
                    if in_key:
                        in_key = not KEY_END.search(line)
                        continue
                    if KEY_BEGIN.search(line):
                        self._hit("private key", relpath)
                        in_key = not KEY_END.search(line)
                        fo.write("[REDACTED PRIVATE KEY]\n")
                        continue
                    fo.write(self.text(line, relpath))
        shutil.copystat(src, dst)


# ---------------------------------------------------------------- facts about this computer (for assets.json, docs)
def parse_llama_version(text):
    m = re.search(r"version:[^\n]*\bbuild\s+(\d+)", text or "")
    if m and int(m.group(1)) > 1:
        return "b" + m.group(1)
    m = re.search(r"version:\s*v?(\d+\.\d+\.\d+)", text or "")
    if m:
        return "v" + m.group(1)
    m = re.search(r"version:\s*(\d+)\b", text or "")
    if m and int(m.group(1)) > 0:
        return "b" + m.group(1)
    return None


def llama_tag(base):
    for name in ("llama-cpu", "llama-vulkan"):
        for exe in ("llama-server.exe", "llama-server"):
            p = os.path.join(base, name, exe)
            if os.path.exists(p):
                try:
                    r = subprocess.run([p, "--version"], capture_output=True, text=True, timeout=30)
                    tag = parse_llama_version((r.stdout or "") + (r.stderr or ""))
                    if tag:
                        return tag, name
                except Exception:  # noqa: BLE001
                    pass
    return None, None


def kaggle_user():
    u = os.environ.get("KAGGLE_USERNAME")
    p = os.path.join(os.path.expanduser("~"), ".kaggle", "kaggle.json")
    if not u and os.path.exists(p):
        try:
            u = json.load(open(p, encoding="utf-8")).get("username")
        except Exception:  # noqa: BLE001
            u = None
    return u or None


def pinned_requirements(names):
    import importlib.metadata as md
    out = []
    for n in names:
        try:
            out.append(f"{n}=={md.version(n)}")
        except md.PackageNotFoundError:
            out.append(n)
    return out


def wmic(query):
    """One value from PowerShell's CIM classes (Windows), or None."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, timeout=30)
        v = " / ".join(x.strip() for x in (r.stdout or "").splitlines() if x.strip())
        return v or None
    except Exception:  # noqa: BLE001
        return None


def environment_md(tag, reqs):
    cpu = wmic("(Get-CimInstance Win32_Processor).Name") or platform.processor() or platform.machine()
    ram = wmic("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB)")
    gpu = wmic("(Get-CimInstance Win32_VideoController).Name")
    try:
        freeze = subprocess.run([sys.executable, "-m", "pip", "freeze", "--disable-pip-version-check"],
                                capture_output=True, text=True, timeout=120).stdout.strip()
    except Exception:  # noqa: BLE001
        freeze = ""
    lines = ["# Environment the results were measured in", "",
             "Written by `publish/prepare_repo.py` on the test laptop. Both tiers were measured on this one machine.",
             "", "| | |", "|---|---|",
             f"| Processor | {cpu} |", f"| Memory | {ram + ' GB' if ram else 'not read'} |",
             f"| Graphics | {gpu or 'not read'} |",
             f"| Operating system | {platform.system()} {platform.release()} ({platform.version()}) |",
             f"| Python | {platform.python_version()} |",
             f"| llama.cpp | {tag or 'not read (see scripts/assets.json)'} |", "",
             "## Packages the kiosk uses at run time", "", "```", *reqs, "```", "",
             "## Every package in the project's environment (`pip freeze`)", "",
             "The evaluation, retrieval-building and write-up tools need more than the kiosk does.", "",
             "```", freeze or "(pip freeze gave nothing)", "```", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- build
def walk(src, skipped):
    for d, dirs, files in os.walk(src):
        keep = []
        for x in dirs:
            if x in SKIP_DIRS:
                skipped.append((rel(os.path.join(d, x), src) + "/", "cache, environment, profile or staging folder"))
            else:
                keep.append(x)
        dirs[:] = keep
        for f in files:
            yield os.path.join(d, f)


def zip_files(archive, base, relpaths, level=6):
    os.makedirs(os.path.dirname(archive), exist_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=level, allowZip64=True) as z:
        for r in sorted(relpaths):
            z.write(os.path.join(base, r), r)


def folder_sizes(repo):
    sizes, counts = {}, {}
    for d, dirs, files in os.walk(repo):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in files:
            p = os.path.join(d, f)
            top = rel(p, repo).split("/")[0] if "/" in rel(p, repo) else "(top level)"
            sizes[top] = sizes.get(top, 0) + os.path.getsize(p)
            counts[top] = counts.get(top, 0) + 1
    return sizes, counts


def first_heading(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    return line.lstrip("# ").strip()[:110]
                if line:
                    return line[:110]
    except OSError:
        pass
    return ""


RESULT_ROOTS = [
    ("results", "Objective 1: choosing the model (screening, number format, head-to-head, speed)"),
    ("results_obj2", "Objective 2: the model with retrieval (pilots and the confirming run)"),
    ("results_retrieval", "Objective 2: retrieval benchmarks, fallback calibration, integration settings"),
    ("results_obj3", "Objective 3: the harness (thirteen changes on development data, the test-set run, the ladder)"),
    ("results_obj4", "Objective 4: adapters (development-set comparisons, speed, decision)"),
    ("results_o4", "Objective 4: training trajectories and adapter runs"),
    ("results_obj5", "Objective 5: the app (parity, stages, streaming, images, measurement, walkthroughs)"),
    ("kaggle/_pulled", "Kaggle jobs: the log and returned files of every job"),
    ("logs", "Run-time logs of the app, llama-server and the kiosk launcher"),
    ("finetune", "Objective 4: training data, examples, plans and training outputs"),
]


def results_md(repo, moved):
    moved_by = {}
    for r in moved:
        parts = r.split("/")
        for depth in (1, 2, 3):
            if len(parts) > depth:
                moved_by["/".join(parts[:depth])] = moved_by.get("/".join(parts[:depth]), 0) + 1
    out = ["# Results, logs and job data: where everything is", "",
           "Written by `publish/prepare_repo.py`. Folder names are the ones the code writes to, so every script and "
           "plan in the repository still finds its inputs. A folder's own `report.md`, where there is one, is the "
           "place to start; the reports in `writeups/` cite these folders.", "",
           "\"On Drive\" counts files that were too large for GitHub: see [LARGE_FILES.md](LARGE_FILES.md).", ""]
    known = {r for r, _ in RESULT_ROOTS}
    extra = sorted(x for x in os.listdir(repo) if x.startswith("results") and x not in known
                   and os.path.isdir(os.path.join(repo, x)))
    for root, what in RESULT_ROOTS + [(x, "Results folder") for x in extra]:
        base = os.path.join(repo, root)
        if not os.path.isdir(base) and root not in moved_by:
            continue
        out += [f"## `{root}/`", "", what + ".", "", "| Folder | Files here | Size here | On Drive | Starts with |",
                "|---|---:|---:|---:|---|"]
        subs = sorted(x for x in os.listdir(base)) if os.path.isdir(base) else []
        loose_n = loose_s = 0
        for x in subs:
            p = os.path.join(base, x)
            if os.path.isfile(p):
                loose_n += 1
                loose_s += os.path.getsize(p)
                continue
            n = s = 0
            for d, _, files in os.walk(p):
                for f in files:
                    n += 1
                    s += os.path.getsize(os.path.join(d, f))
            head = first_heading(os.path.join(p, "report.md")) if os.path.exists(os.path.join(p, "report.md")) else ""
            out.append(f"| `{x}/` | {n} | {human(s)} | {moved_by.get(root + '/' + x, 0) or ''} | {head} |")
        if loose_n:
            out.append(f"| (files directly in `{root}/`) | {loose_n} | {human(loose_s)} | | |")
        out.append("")
    return "\n".join(out)


def large_files_md(manifest):
    out = ["# Files kept on Google Drive", "",
           "GitHub refuses files over 100 MB and asks repositories to stay under 1 GB, so the largest result and log "
           "files are zip archives on Google Drive. Each archive unpacks into the repository's own folders: the paths "
           "inside it are the paths the files had in the project.", "",
           "    python scripts\\fetch_large_files.py            download and unpack all of them",
           "    python scripts\\fetch_large_files.py --list     what each archive holds", ""]
    if not manifest["archives"]:
        out += ["Nothing had to be moved: every file is in the repository.", ""]
        return "\n".join(out)
    out += ["| Archive | Files | Unpacked | Download | SHA-256 | Link |", "|---|---:|---:|---:|---|---|"]
    for a in manifest["archives"]:
        link = f"[Google Drive]({a['link']})" if a.get("link") else "_not uploaded yet_"
        out.append(f"| `{a['name']}` | {len(a['files'])} | {human(a['unpacked'])} | {human(a['size'])} | "
                   f"`{a['sha256'][:16]}…` | {link} |")
    out += ["", "## What is in each archive", ""]
    for a in manifest["archives"]:
        folders = {}
        for f in a["files"]:
            k = "/".join(f["path"].split("/")[:2])
            folders[k] = folders.get(k, 0) + f["size"]
        out.append(f"**`{a['name']}`**: " + "; ".join(f"`{k}` ({human(v)})" for k, v in
                                                     sorted(folders.items(), key=lambda kv: -kv[1])[:12])
                   + (" …" if len(folders) > 12 else ""))
        out.append("")
    return "\n".join(out)


def build(a):
    out = os.path.abspath(a.out)
    repo, release, drive = (os.path.join(out, x) for x in ("repo", "release", "drive"))
    if (out + os.sep).lower().startswith((ROOT + os.sep).lower()):
        print("The output folder must be outside the project folder.")
        return 2
    t0 = time.time()
    # start clean, but keep repo/.git so a rebuilt tree can be committed on top of an earlier one
    if os.path.isdir(repo):
        for x in os.listdir(repo):
            if x != ".git":
                p = os.path.join(repo, x)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for d in (release, drive):
        shutil.rmtree(d, ignore_errors=True)
    for d in (repo, release, drive):
        os.makedirs(d, exist_ok=True)

    users = {os.environ.get("USERNAME"), os.environ.get("USER"), os.path.basename(os.path.expanduser("~"))} | set(a.user_name)
    hosts = {platform.node(), os.environ.get("COMPUTERNAME")} | set(a.host_name)
    kuser = a.scrub_kaggle_user or kaggle_user()
    sc = Scrubber(users, hosts, kuser, bool(a.scrub_kaggle_user))

    # 1. copy + scrub
    skipped, weights, n = [], [], 0
    release_dirs = [s for _, s, _ in RELEASE]
    print(f"Scrubbing user folder name(s): {', '.join(sc.users) or '(none known)'}; computer name(s): "
          f"{', '.join(sc.hosts) or '(none known)'}; Kaggle user: {kuser or '(not found)'}"
          f"{' (replaced)' if a.scrub_kaggle_user else ' (kept, counted in the report)' if kuser else ''}")
    print("1/5 copying and scrubbing ...", flush=True)
    for src in walk(ROOT, skipped):
        r = rel(src, ROOT)
        name = os.path.basename(src)
        if any(r.startswith(d + "/") for d in release_dirs):
            continue                                             # goes into a release asset
        if any(fnmatch.fnmatch(name, p) for p in SKIP_FILES):
            skipped.append((r, "key, cache or temporary file"))
            continue
        if "/" not in r and name.lower().endswith((".zip", ".7z", ".rar", ".tar", ".gz")):
            skipped.append((r, "archive in the project's top folder (a delivery bundle, not a result)"))
            continue
        if r.startswith("models/") or os.path.splitext(name)[1].lower() in WEIGHT_EXT:
            weights.append(r)
            continue
        try:
            sc.copy(src, os.path.join(repo, r), r)
        except OSError as e:
            skipped.append((r, f"COULD NOT BE COPIED ({type(e).__name__}: path too long or file in use?)"))
            continue
        n += 1
        if n % 2000 == 0:
            print(f"    {n} files", flush=True)
    print(f"    {n} files copied", flush=True)

    # 2. release assets, model facts, pinned requirements
    print("2/5 release assets and scripts/assets.json ...", flush=True)
    assets_path = os.path.join(repo, "scripts", "assets.json")
    cfg = json.load(open(assets_path, encoding="utf-8")) if os.path.exists(assets_path) else None
    rel_info = []
    for name, srcdir, what in RELEASE:
        base = os.path.join(ROOT, srcdir)
        files = []
        if os.path.isdir(base):
            for d, dirs, fs in os.walk(base):
                dirs[:] = [x for x in dirs if not x.startswith("_")]
                files += [rel(os.path.join(d, f), ROOT) for f in fs if not f.endswith((".part", ".tmp"))]
        if not files:
            rel_info.append((name, None, None, f"MISSING: {srcdir} is empty or not there"))
            continue
        z = os.path.join(release, name)
        zip_files(z, ROOT, files, level=1)
        info = (name, os.path.getsize(z), sha256(z), f"{len(files)} files from {srcdir}")
        rel_info.append(info)
        if cfg:
            for x in cfg["project_assets"]:
                if x["file"] == name:
                    x["size"], x["sha256"] = info[1], info[2]
    base_dir = os.path.abspath(a.base_dir or os.path.join(ROOT, ".."))
    tag, tag_from = llama_tag(base_dir)
    model_notes = []
    if cfg:
        if a.github:
            cfg["github_repo"] = a.github
        if tag:
            cfg["llama"]["tag"] = tag
            cfg["llama"]["tag_source"] = f"read from {tag_from}\\llama-server.exe --version on the test laptop"
        for m in cfg["models"]:
            p = os.path.join(base_dir, m["dest"])
            if os.path.exists(p):
                print(f"    SHA-256 of {os.path.basename(p)} ...", flush=True)
                m["size"], m["sha256"] = os.path.getsize(p), sha256(p)
                model_notes.append(f"{os.path.basename(p)}: {human(m['size'])}, SHA-256 {m['sha256'][:16]}…")
            else:
                model_notes.append(f"{os.path.basename(p)}: NOT FOUND at {p} (size and SHA-256 not recorded)")
        with open(assets_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cfg, f, indent=1)
            f.write("\n")
    readme = os.path.join(repo, "README.md")
    if a.github and os.path.exists(readme):
        t = open(readme, encoding="utf-8").read()
        t = t.replace("https://github.com/<owner>/<repository>.git", f"https://github.com/{a.github}.git") \
             .replace("cd <repository>", "cd " + a.github.split("/")[-1])
        with open(readme, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    reqs = pinned_requirements(["numpy", "openvino", "tokenizers", "psutil"])
    with open(os.path.join(repo, "requirements.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# What the kiosk app needs at run time (setup.bat installs these into .venv),\n"
                "# at the versions the results were measured with.\n" + "\n".join(reqs) + "\n")

    # 3. other weights -> Drive (our own trained files), base models left out
    print("3/5 sorting large files ...", flush=True)
    to_drive, left_out = {}, []
    for r in weights:
        size = os.path.getsize(os.path.join(ROOT, r))
        if size > 1500 * MB:
            left_out.append((r, size, "a base model: download it from its source"))
        else:
            to_drive.setdefault("weights_other", []).append((r, size, ROOT))
    # 4. size rules on the copy
    files = []
    for d, dirs, fs in os.walk(repo):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in fs:
            p = os.path.join(d, f)
            files.append((rel(p, repo), os.path.getsize(p)))
    total = sum(s for _, s in files)
    limit, budget = a.file_limit_mb * MB, a.budget_mb * MB
    movable = sorted(((r, s) for r, s in files if not matches(r, KEEP_PATTERNS) and s >= KEEP_BELOW),
                     key=lambda x: -x[1])
    stuck = [(r, s) for r, s in files if s > limit and (matches(r, KEEP_PATTERNS))]
    moved = []
    for r, s in movable:
        if s > limit or total > budget:
            top = r.split("/")[0]
            to_drive.setdefault(top, []).append((r, s, repo))
            moved.append(r)
            total -= s
    # archives of at most ~1.5 GB of input each
    manifest = {"made": time.strftime("%Y-%m-%d"), "archives": []}
    for group in sorted(to_drive):
        part, acc, parts = [], 0, []
        for item in sorted(to_drive[group]):
            if part and acc + item[1] > 1500 * MB:
                parts.append(part)
                part, acc = [], 0
            part.append(item)
            acc += item[1]
        if part:
            parts.append(part)
        for i, part in enumerate(parts, 1):
            name = f"large__{group}{'' if len(parts) == 1 else f'__part{i}'}.zip"
            z = os.path.join(drive, name)
            print(f"    {name}: {len(part)} files, {human(sum(x[1] for x in part))}", flush=True)
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zf:
                for r, _, base in part:
                    zf.write(os.path.join(base, r), r)
            manifest["archives"].append({"name": name, "size": os.path.getsize(z), "sha256": sha256(z),
                                         "unpacked": sum(x[1] for x in part), "link": None, "gdrive_id": None,
                                         "files": [{"path": r, "size": s} for r, s, _ in part]})
            for r, _, base in part:
                if base == repo:
                    os.remove(os.path.join(repo, r))
    for d, dirs, fs in os.walk(repo, topdown=False):            # folders emptied by the move
        if ".git" not in d.split(os.sep) and not os.listdir(d):
            os.rmdir(d)

    # 5. docs
    print("4/5 docs ...", flush=True)
    docs = os.path.join(repo, "docs")
    os.makedirs(docs, exist_ok=True)
    moved_all = [f["path"] for x in manifest["archives"] for f in x["files"]]
    with open(os.path.join(docs, "large_files.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
    for name, text in (("LARGE_FILES.md", large_files_md(manifest)), ("RESULTS.md", results_md(repo, moved_all)),
                       ("ENVIRONMENT.md", sc.text(environment_md(tag, reqs), "docs/ENVIRONMENT.md"))):
        with open(os.path.join(docs, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")

    # report
    print("5/5 report ...", flush=True)
    sizes, counts = folder_sizes(repo)
    total = sum(sizes.values())
    big = sorted(((os.path.getsize(os.path.join(d, f)), rel(os.path.join(d, f), repo))
                  for d, dirs, fs in os.walk(repo) if ".git" not in d.split(os.sep) for f in fs), reverse=True)[:20]
    missing = [m for m in MUST_HAVE if not os.path.exists(os.path.join(repo, m))]
    L = ["# Publishing report", "", f"Made {time.strftime('%Y-%m-%d %H:%M')} from `{ROOT}` in {time.time() - t0:.0f} s.",
         "", "## In short", "",
         f"- Repository tree: **{human(total)}** in {sum(counts.values()):,} files "
         f"(budget {a.budget_mb} MB, no file over {a.file_limit_mb} MB)"
         + (" - **over the budget**: see the largest files below" if total > budget else ""),
         f"- Release assets: {sum(1 for x in rel_info if x[1])} of {len(RELEASE)} made",
         f"- Google Drive archives: {len(manifest['archives'])} "
         f"({human(sum(x['size'] for x in manifest['archives']))} to upload)",
         f"- Scrubbed: {sum(sum(v.values()) for v in sc.counts.values()):,} replacements in "
         f"{len({f for v in sc.counts.values() for f in v}):,} files",
         f"- Files the app or the README needs that are missing: {', '.join('`' + m + '`' for m in missing) or 'none'}",
         "", "## Repository tree by folder", "", "| Folder | Files | Size |", "|---|---:|---:|"]
    L += [f"| `{k}` | {counts[k]:,} | {human(v)} |" for k, v in sorted(sizes.items(), key=lambda kv: -kv[1])]
    L += ["", "## Release assets (`release/`)", ""]
    for name, size, sha, note in rel_info:
        L.append(f"- `{name}`: " + (f"{human(size)}, {note}, SHA-256 `{sha[:16]}…`" if size else f"**{note}**"))
    L += ["", "Recorded in `scripts/assets.json`:", "", f"- GitHub repository: `{(cfg or {}).get('github_repo') or 'NOT SET (pass --github owner/name)'}`",
          f"- llama.cpp build: `{tag or 'could not be read; left at ' + str((cfg or {}).get('llama', {}).get('tag'))}`"]
    L += [f"- {x}" for x in model_notes]
    L += ["", "## Google Drive archives (`drive/`)", ""]
    L += [f"- `{x['name']}`: {len(x['files'])} files, {human(x['unpacked'])} unpacked, {human(x['size'])} to upload"
          for x in manifest["archives"]] or ["- none needed"]
    if stuck:
        L += ["", "**Over the file limit but not moved (the app or a reader needs them where they are):**", ""]
        L += [f"- `{r}` ({human(s)})" for r, s in stuck]
    L += ["", "## Left out altogether", ""]
    by = {}
    for r, why in skipped:
        by.setdefault(why, []).append(r)
    for why, rs in by.items():
        L.append(f"- {why}: {len(rs)} ({', '.join('`' + x + '`' for x in rs[:8])}{' …' if len(rs) > 8 else ''})")
    L += [f"- `{r}` ({human(s)}): {why}" for r, s, why in left_out]
    L += ["", "## Scrubbed (in the copy only; the project folder is unchanged)", "",
          f"Looked for: API keys and tokens; the Windows user folder name ({', '.join(sc.users) or 'none known'}); "
          f"this computer's name ({', '.join(sc.hosts) or 'none known'}); private network addresses.", ""]
    if not sc.counts:
        L.append("Nothing was found.")
    for kind, fs in sorted(sc.counts.items()):
        topf = sorted(fs.items(), key=lambda kv: -kv[1])[:6]
        L.append(f"- **{kind}**: {sum(fs.values()):,} in {len(fs):,} files, e.g. "
                 + ", ".join(f"`{f}` ({n})" for f, n in topf))
    L += ["", "## Look at these by hand", ""]
    if not sc.review:
        L.append("Nothing to review.")
    for kind, items in sorted(sc.review.items()):
        topi = sorted(items.items(), key=lambda kv: -kv[1])[:15]
        L.append(f"- **{kind}**: " + ", ".join(f"`{d}` ({n})" for d, n in topi) + (" …" if len(items) > 15 else ""))
    L += ["", "## Largest files left in the tree", ""]
    L += [f"- {human(s)}  `{r}`" for s, r in big]
    L += ["", "## Next", "", "See `publish/PUBLISHING.md`, from step 3.", ""]
    with open(os.path.join(out, "publish_report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print()
    print("\n".join(L[4:11]))
    print(f"\nWritten: {out}\n  open publish_report.md, then follow publish\\PUBLISHING.md from step 3")
    return 1 if missing else 0


# ---------------------------------------------------------------- drive: upload with rclone, record the links
def drive(a):
    out = os.path.abspath(a.out)
    repo, dr = os.path.join(out, "repo"), os.path.join(out, "drive")
    mpath = os.path.join(repo, "docs", "large_files.json")
    if not os.path.exists(mpath):
        print("Run `build` first.")
        return 2
    manifest = json.load(open(mpath, encoding="utf-8"))
    manual = dict(x.split("=", 1) for x in a.set)
    if not manifest["archives"]:
        print("No archives: nothing was too large for GitHub.")
    elif not manual:
        if not shutil.which("rclone"):
            print("rclone is not installed (winget install Rclone.Rclone, then open a new terminal). "
                  "See publish\\PUBLISHING.md, step 4.")
            return 2
        remote = a.remote.rstrip("/")
        if not a.links_only:
            print(f"Uploading {dr} -> {remote} ...", flush=True)
            if subprocess.call(["rclone", "copy", dr, remote, "--progress", "--drive-chunk-size", "64M"]):
                print("The upload did not finish; run the same command again (finished files are skipped).")
                return 1
    for x in manifest["archives"]:
        link = manual.get(x["name"])
        if not link and not manual:
            r = subprocess.run(["rclone", "link", f"{a.remote.rstrip('/')}/{x['name']}"], capture_output=True, text=True)
            link = (r.stdout or "").strip().splitlines()[-1] if r.returncode == 0 and (r.stdout or "").strip() else None
            if not link:
                print(f"  {x['name']}: no link ({(r.stderr or '').strip()[:200]})")
        if link:
            x["link"] = link
            m = re.search(r"(?:[?&]id=|/d/|/folders/)([A-Za-z0-9_\-]{10,})", link)
            x["gdrive_id"] = m.group(1) if m else None
            print(f"  {x['name']}: {link}")
    with open(mpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(repo, "docs", "LARGE_FILES.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(large_files_md(manifest) + "\n")
    todo = [x["name"] for x in manifest["archives"] if not x.get("link")]
    print("docs/LARGE_FILES.md and docs/large_files.json updated."
          + (f" Still without a link: {', '.join(todo)}" if todo else ""))
    return 1 if todo else 0


# ---------------------------------------------------------------- check: a last look at the tree to be pushed
def check(a):
    repo = os.path.join(os.path.abspath(a.out), "repo")
    if not os.path.isdir(repo):
        print("Run `build` first.")
        return 2
    users = {os.environ.get("USERNAME"), os.environ.get("USER"), os.path.basename(os.path.expanduser("~"))} | set(a.user_name)
    hosts = {platform.node(), os.environ.get("COMPUTERNAME")} | set(a.host_name)
    sc = Scrubber(users, hosts)
    problems, total, n = [], 0, 0
    for d, dirs, fs in os.walk(repo):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in fs:
            p = os.path.join(d, f)
            r = rel(p, repo)
            s = os.path.getsize(p)
            total += s
            n += 1
            if s > 95 * MB:
                problems.append(f"over 95 MB (GitHub refuses 100 MB): {r} ({human(s)})")
            if any(fnmatch.fnmatch(f, pat) for pat in SKIP_FILES) or os.path.splitext(f)[1].lower() in WEIGHT_EXT:
                problems.append(f"should not be published: {r}")
            if os.path.splitext(f)[1].lower() in TEXT_EXT and not r.startswith("publish/"):
                with open(p, "rb") as fh:
                    if b"\x00" in fh.read(4096):
                        continue
                with open(p, encoding="utf-8", errors="surrogateescape") as fh:
                    for line in fh:
                        sc.text(line, r)
    for kind, fs in sc.counts.items():
        problems.append(f"still present after scrubbing - {kind}: " + ", ".join(sorted(fs)[:5]))
    for m in MUST_HAVE:
        if not os.path.exists(os.path.join(repo, m)):
            problems.append(f"missing: {m}")
    manifest = os.path.join(repo, "docs", "large_files.json")
    if os.path.exists(manifest):
        nolink = [x["name"] for x in json.load(open(manifest, encoding="utf-8"))["archives"] if not x.get("link")]
        if nolink:
            problems.append("Google Drive archives without a link in docs/LARGE_FILES.md: " + ", ".join(nolink))
    cfg = json.load(open(os.path.join(repo, "scripts", "assets.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(repo, "scripts", "assets.json")) else {}
    if not cfg.get("github_repo"):
        problems.append("scripts/assets.json has no github_repo (build with --github owner/name), so a copy downloaded "
                        "as a zip cannot find the release assets")
    if total > 1000 * MB:
        problems.append(f"the tree is {human(total)}; GitHub asks for under 1 GB")
    print(f"{n:,} files, {human(total)}")
    if problems:
        print("\nNOT READY:")
        for p in problems:
            print("  - " + p)
        return 1
    print("READY TO PUSH: no key or token, no computer or user name, nothing over the size limits, "
          "every file the app needs is there.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    default_out = os.path.join(os.path.dirname(ROOT), "slm-kiosk-publish")

    def common(p):
        p.add_argument("--out", default=default_out, help="output folder (default: ..\\slm-kiosk-publish)")
        p.add_argument("--user-name", action="append", default=[], help="another user folder name to scrub")
        p.add_argument("--host-name", action="append", default=[], help="another computer name to scrub")
    b = sub.add_parser("build", help="assemble repo\\, release\\ and drive\\")
    common(b)
    b.add_argument("--github", default="", help="owner/name of the GitHub repository (written to scripts/assets.json)")
    b.add_argument("--base-dir", default=None, help="folder with llama-cpu\\, llama-vulkan\\, models\\ (default: ..)")
    b.add_argument("--budget-mb", type=int, default=700, help="largest size of the repository tree")
    b.add_argument("--file-limit-mb", type=int, default=50, help="largest single file in the repository")
    b.add_argument("--scrub-kaggle-user", default="", metavar="NAME",
                   help="also replace this Kaggle user name (by default it is kept and counted in the report)")
    d = sub.add_parser("drive", help="upload drive\\ with rclone and write the links into docs/LARGE_FILES.md")
    common(d)
    d.add_argument("--remote", default="gdrive:slm-kiosk-large-files", help="rclone remote and folder")
    d.add_argument("--links-only", action="store_true", help="do not upload; only read the links")
    d.add_argument("--set", action="append", default=[], metavar="ARCHIVE=LINK",
                   help="record a link by hand (if you uploaded in the browser)")
    c = sub.add_parser("check", help="scan repo\\ once more before pushing")
    common(c)
    a = ap.parse_args(argv)
    return {"build": build, "drive": drive, "check": check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
