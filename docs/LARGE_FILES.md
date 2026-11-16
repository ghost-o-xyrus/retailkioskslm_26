# Files kept on Google Drive

GitHub refuses files over 100 MB and asks repositories to stay under 1 GB, so the largest result and log files are zip archives on Google Drive. Each archive unpacks into the repository's own folders: the paths inside it are the paths the files had in the project.

    python scripts\fetch_large_files.py            download and unpack all of them
    python scripts\fetch_large_files.py --list     what each archive holds

| Archive | Files | Unpacked | Download | SHA-256 | Link |
|---|---:|---:|---:|---|---|
| `large__kaggle.zip` | 6 | 609.2 MB | 608.9 MB | `5d82f7d9bfd274a0…` | [Google Drive](https://drive.google.com/open?id=1tPW5n-3HTXgmtGpaFx_60FghvgBG9od0) |
| `large__weights_other.zip` | 12 | 550.5 MB | 481.6 MB | `6808500034666923…` | [Google Drive](https://drive.google.com/open?id=1KbaM8D-FbWCvsgQ14RQGnKPZEpQS-4a6) |

## What is in each archive

**`large__kaggle.zip`**: `kaggle/_pulled` (609.2 MB)

**`large__weights_other.zip`**: `finetune/adapters` (344.6 MB); `results_retrieval/latency` (114.2 MB); `models/reranker-veyra-minilm` (91.6 MB)

