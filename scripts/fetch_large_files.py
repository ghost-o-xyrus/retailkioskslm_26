"""
Download the result and log files that were too large for GitHub and unpack them into their own folders.

They are zip archives on Google Drive, listed in docs/LARGE_FILES.md (docs/large_files.json is the same list for
this script). The kiosk does not need them; they are the raw per-case outputs and long logs behind the reports.

    python scripts\\fetch_large_files.py                  all archives
    python scripts\\fetch_large_files.py --list           what each archive holds, download nothing
    python scripts\\fetch_large_files.py --only results_obj3      archives whose name contains this text

Each archive's SHA-256 is checked. Paths inside an archive are the paths the files had in the project, so they land
next to the files already here. Standard library only.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fetch_assets as fa  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", default="", help="only archives whose name contains this text")
    ap.add_argument("--keep", action="store_true", help="keep the downloaded zip files (in runtime/_large)")
    a = ap.parse_args(argv)
    path = os.path.join(ROOT, "docs", "large_files.json")
    if not os.path.exists(path):
        print("docs/large_files.json is not in this copy: there are no large files to fetch.")
        return 0
    archives = [x for x in json.load(open(path, encoding="utf-8"))["archives"] if a.only in x["name"]]
    if not archives:
        print("No archive matches." if a.only else "Every file is already in the repository; nothing to fetch.")
        return 0
    if a.list:
        for x in archives:
            print(f"{x['name']}: {len(x['files'])} files, {fa.human(x['unpacked'])} unpacked, "
                  f"{fa.human(x['size'])} to download{'' if x.get('gdrive_id') or x.get('link') else '  (no link yet)'}")
            folders = {}
            for f in x["files"]:
                k = "/".join(f["path"].split("/")[:2])
                folders[k] = folders.get(k, 0) + f["size"]
            for k, v in sorted(folders.items(), key=lambda kv: -kv[1])[:15]:
                print(f"    {k:<60} {fa.human(v)}")
        return 0
    tmp = os.path.join(ROOT, "runtime", "_large")
    failed = 0
    for n, x in enumerate(archives, 1):
        print(f"[{n}/{len(archives)}] {x['name']}")
        if all(os.path.exists(os.path.join(ROOT, f["path"])) for f in x["files"]):
            print("    -> already unpacked")
            continue
        if not x.get("gdrive_id"):
            print(f"    -> no Google Drive id recorded{': open ' + x['link'] if x.get('link') else ''}")
            failed += 1
            continue
        z = os.path.join(tmp, x["name"])
        if not fa.download(fa.gdrive_url(x["gdrive_id"]), z, x["name"], x.get("size"), x.get("sha256")):
            print(f"    -> download failed; open {x.get('link')} in a browser and unzip it into {ROOT}")
            failed += 1
            continue
        fa.unzip(z, ROOT)
        if not a.keep:
            os.remove(z)
        print(f"    -> unpacked {len(x['files'])} files")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
