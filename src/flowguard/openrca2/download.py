"""Check that the OpenRCA 2.0 download is complete, without naming a case.

The file list of the dataset at the pinned commit is fetched from Hugging Face:
every file's path, its size, and a hash (SHA-256 for the large files, which are
stored in LFS; git's SHA-1 for the small ones). Each local file is compared with
it. Only counts are printed. Where files differ, they are counted by file name
(`label.json`, `abnormal_logs.parquet`), never by case folder.

Run: python -m flowguard.openrca2.download --raw data/external/openrca2/raw
     add --sizes-only to skip hashing; add --save FILE to keep the SHA-256 list
"""

import argparse
import hashlib
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from flowguard.openrca2 import ANSWER_FILES, COMMIT, DATASET, TELEMETRY_FILES

CASE_FILES = TELEMETRY_FILES | ANSWER_FILES
CHUNK = 1 << 20


@dataclass(frozen=True)
class Expected:
    path: str
    size: int
    sha256: str | None  # LFS files
    git_sha1: str | None  # the others


def repo_files() -> list[Expected]:
    """Every file of the dataset at the pinned commit, from Hugging Face."""
    from huggingface_hub import HfApi
    from huggingface_hub.hf_api import RepoFile

    tree = HfApi().list_repo_tree(
        DATASET, repo_type="dataset", revision=COMMIT, recursive=True
    )
    files = []
    for entry in tree:
        if not isinstance(entry, RepoFile):
            continue
        if entry.lfs is not None:
            files.append(Expected(entry.path, entry.lfs.size, entry.lfs.sha256, None))
        else:
            files.append(Expected(entry.path, entry.size, None, entry.blob_id))
    return files


def hashes(path: Path) -> tuple[str, str]:
    """A file's SHA-256, and the SHA-1 git gives it as a blob."""
    sha256 = hashlib.sha256()
    git = hashlib.sha1(f"blob {path.stat().st_size}\0".encode())  # noqa: S324
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK):
            sha256.update(chunk)
            git.update(chunk)
    return sha256.hexdigest(), git.hexdigest()


def local_files(raw: Path) -> set[str]:
    """Paths under the download folder, leaving out the downloader's own cache."""
    return {
        path.relative_to(raw).as_posix()
        for path in raw.rglob("*")
        if path.is_file() and ".cache" not in path.relative_to(raw).parts
    }


def check(
    raw: Path, expected: list[Expected], *, hash_files: bool
) -> tuple[bool, dict[str, str]]:
    """Print counts. Returns whether the download is complete, and SHA-256 by path."""
    have = local_files(raw)
    want = {item.path for item in expected}
    missing = Counter(Path(path).name for path in want - have)
    extra = Counter(Path(path).name for path in have - want)

    wrong_size: Counter[str] = Counter()
    wrong_hash: Counter[str] = Counter()
    sha256_of: dict[str, str] = {}
    for item in expected:
        if item.path not in have:
            continue
        path = raw / item.path
        if path.stat().st_size != item.size:
            wrong_size[path.name] += 1
            continue
        if not hash_files:
            continue
        sha256, git = hashes(path)
        sha256_of[item.path] = sha256
        if (item.sha256 or sha256) != sha256 or (item.git_sha1 or git) != git:
            wrong_hash[path.name] += 1

    cases_expected = {Path(p).parts[1] for p in want if p.startswith("cases/")}
    case_dirs = (
        [d for d in (raw / "cases").iterdir() if d.is_dir()]
        if (raw / "cases").is_dir()
        else []
    )
    whole = sum(1 for d in case_dirs if {f.name for f in d.iterdir()} == CASE_FILES)
    odd_names = Counter(
        Path(p).name
        for p in want
        if p.startswith("cases/") and Path(p).name not in CASE_FILES
    )
    unfinished = (
        sum(1 for _ in (raw / ".cache").rglob("*.incomplete"))
        if (raw / ".cache").is_dir()
        else 0
    )

    print(f"dataset {DATASET} at {COMMIT}")
    print(
        f"files in the repo:        {len(want)}, {sum(i.size for i in expected):,} bytes"
    )
    print(f"case folders in the repo: {len(cases_expected)}")
    print(
        f"case folders on disk:     {len(case_dirs)}, of which {whole} hold exactly the 14 files"
    )
    print(f"files on disk:            {len(have)}")
    print(f"missing:                  {sum(missing.values())} {dict(missing) or ''}")
    print(f"not in the repo:          {sum(extra.values())} {dict(extra) or ''}")
    print(
        f"wrong size:               {sum(wrong_size.values())} {dict(wrong_size) or ''}"
    )
    if hash_files:
        print(
            f"wrong hash:               {sum(wrong_hash.values())} {dict(wrong_hash) or ''}"
        )
        print(f"hashes checked:           {len(sha256_of)}")
    print(f"unfinished parts in cache: {unfinished}")
    if odd_names:
        print(f"repo files in a case folder outside the 14 names: {dict(odd_names)}")

    complete = not (missing or wrong_size or wrong_hash) and len(case_dirs) == len(
        cases_expected
    )
    print("COMPLETE" if complete else "NOT COMPLETE")
    return complete, sha256_of


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--sizes-only", action="store_true")
    parser.add_argument("--save", type=Path, help="write 'sha256  path' lines here")
    args = parser.parse_args()

    complete, sha256_of = check(args.raw, repo_files(), hash_files=not args.sizes_only)
    if args.save and complete and sha256_of:
        lines = [f"{digest}  {path}\n" for path, digest in sorted(sha256_of.items())]
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text("".join(lines), encoding="utf-8", newline="\n")
        listing = hashlib.sha256("".join(lines).encode()).hexdigest()
        print(f"saved {len(lines)} hashes; SHA-256 of the list: {listing}")
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
