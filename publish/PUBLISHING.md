# Publishing this project to GitHub

How the public repository is assembled from the project folder on the laptop. The project folder itself is never
changed: `prepare_repo.py` writes a cleaned copy next to it.

```
slm-kiosk\
  slm-kiosk-catalogue\        the project (run every command below from here unless a step says otherwise)
  slm-kiosk-publish\          written by prepare_repo.py
    repo\                     -> pushed to GitHub
    release\                  -> GitHub release assets (setup.bat downloads them)
    drive\                    -> Google Drive (files too large for GitHub)
    publish_report.md         what went where, what was scrubbed, what to look at
```

## 1. Tools (once)

```powershell
winget install Git.Git
winget install GitHub.cli
winget install Rclone.Rclone
```

Open a new terminal afterwards so the three commands are found.

## 2. Build the copy

In the project's own environment, so the package versions that are recorded are the ones the results were measured
with:

```powershell
cd slm-kiosk-catalogue
# activate the project's environment (slm-env) first, as for any other run
python publish\prepare_repo.py build --github <your-github-user>/<repository-name>
```

It prints the user folder name, computer name and Kaggle user name it will look for, then copies, scrubs, makes the
release assets, moves large files into `drive\` archives and writes the report. On a few gigabytes of results this
takes some minutes; hashing the two model files is the slow part.

Useful options:

| Option | What it does |
|---|---|
| `--scrub-kaggle-user <name>` | also replaces your Kaggle user name (by default it is kept and counted) |
| `--user-name <name>`, `--host-name <name>` | another Windows user folder or computer name to scrub (for results made on another machine) |
| `--budget-mb 700`, `--file-limit-mb 50` | size of the repository tree and of its largest file; everything above goes to `drive\` |

## 3. Read the report

Open `..\slm-kiosk-publish\publish_report.md` and check four things:

1. **In short**: the tree is under the budget, both release assets were made, nothing the app needs is missing.
2. **Scrubbed**: which kinds of secret or laptop detail were found and in which files. If a key or token is listed,
   that key was sitting in a log: revoke it at its provider, whatever happens to this repository.
3. **Look at these by hand**: e-mail addresses that will become public, key-like values in code that were left
   alone, your Kaggle user name, and any file containing a word from `publish\review_terms.txt` (your own list of
   words to double-check; the file is not published).
4. **Left out altogether**: anything listed as `COULD NOT BE COPIED` (a path that is too long or a file in use).

To change something, fix it in the project folder (or add an option) and run `build` again. `repo\.git` is kept
between builds.

## 4. Google Drive, with rclone

Skip this step if the report says no Drive archives were needed.

```powershell
rclone config create gdrive drive scope=drive.file
```

A browser window opens: sign in to the Google account that should hold the files and allow access. The
`drive.file` scope lets rclone see only the files it uploads itself, nothing else in your Drive. Use a personal
Google account if your institute account does not allow sharing with people outside it.

```powershell
python publish\prepare_repo.py drive --remote gdrive:slm-kiosk-large-files
```

This uploads every archive in `drive\` to a Drive folder named `slm-kiosk-large-files` (finished files are skipped
if you run it again), makes each one viewable by anyone with its link, and writes the links into
`repo\docs\LARGE_FILES.md` and `repo\docs\large_files.json`.

If you would rather upload in the browser: put the archives in a Drive folder, set each to "Anyone with the link",
and record the links yourself:

```powershell
python publish\prepare_repo.py drive --set large__results_obj3.zip=https://drive.google.com/file/d/<id>/view
```

## 5. Last check

```powershell
python publish\prepare_repo.py check
```

It scans the tree to be pushed once more for keys, tokens, the user folder and computer names, files GitHub would
refuse, files the app needs, and Drive archives without a link. Go on when it prints `READY TO PUSH`.

## 6. Create the repository and the release

```powershell
cd ..\slm-kiosk-publish\repo
git init -b main
git config core.autocrlf false
git config user.name "Anany Dev Choudhary"
git config user.email "<id>+<user>@users.noreply.github.com"
git add -A
git commit -m "Offline kiosk assistant on small language models: code, data, results, write-ups"
gh auth login
gh repo create <repository-name> --private --source . --remote origin --push
```

The commit e-mail is public for ever once pushed. GitHub gives every account a private one of the form above:
GitHub → Settings → Emails → "Keep my email addresses private" shows it.

Then the release that `setup.bat` downloads from:

```powershell
gh release create v1.0 ..\release\retrieval_models_ov.zip ..\release\adapters_gguf.zip --title "Runtime files v1.0" --notes "Retrieval models in OpenVINO form and the Objective 4 adapters. setup.bat downloads these; they are not needed separately."
```

## 7. Test it as a stranger would

While the repository is private its release assets cannot be downloaded without signing in, so point the setup at
the local copies for this test:

```powershell
cd ..\..
git clone https://github.com/<your-github-user>/<repository-name>.git clone-test
cd clone-test
setup.bat --local-assets ..\slm-kiosk-publish\release
```

To avoid downloading the models a second time, copy them in before running setup (present files are skipped):

```powershell
mkdir runtime
robocopy ..\models\qwen3.5-2b runtime\models\qwen3.5-2b Qwen3.5-2B-Q8_0.gguf
robocopy ..\models\qwen3.5-4b runtime\models\qwen3.5-4b Qwen3.5-4B-Q4_K_M.gguf
robocopy ..\llama-cpu runtime\llama-cpu /E
robocopy ..\llama-vulkan runtime\llama-vulkan /E
```

Lab mode should open at http://127.0.0.1:8000. Then close it and try `start_side_by_side.bat`: Tier A on port 8001
and Tier B on port 8002, in two windows. `stop_all.bat` stops everything.

At least once, also run a plain `setup.bat` in a fresh clone after the repository is public, with nothing copied in,
ideally on another Windows computer: that is the path a visitor takes.

## 8. Make it public

```powershell
cd ..\slm-kiosk-publish\repo
gh repo edit --visibility public --accept-visibility-change-consequences
```

Add a description and topics on the repository page (for example: `small-language-models`, `llama-cpp`, `rag`,
`tool-calling`, `on-device-ai`, `retail`).

## Later changes

Change the project folder, run `build` again (and `drive` if the archives changed), then in `repo\`:

```powershell
git add -A
git commit -m "<what changed>"
git push
```

If a release asset changed, upload it again: `gh release upload v1.0 ..\release\<file> --clobber`.

## What the scrub looks for

| Kind | Replaced by |
|---|---|
| Hugging Face, Kaggle, GitHub, Google, AWS, Slack tokens; `sk-…` keys; Kaggle `"key"`; Authorization headers; private key blocks; `api_key = …` style pairs in data and log files | `[REDACTED]` |
| The Windows user folder name in paths (`C:\Users\<name>\…`) | `user` |
| This computer's name, including the `host` field every run's `run_meta.json` records | `kiosk-laptop` |
| Private network addresses (192.168.x.x, 10.x.x.x, 172.16–31.x.x) | `[private-ip]` |

Never copied at all: `kaggle.json`, `.env` files, key files, browser profiles, virtual environments, caches, Kaggle
staging folders, and model weights. The author's name and roll number in the write-ups, `README.md`, `LICENSE` and
`CITATION.cff` are left as written. Binary files (PDF, PowerPoint, images) are copied unchanged.
