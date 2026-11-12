"""Separate the answers of OpenRCA 2.0, rename the cases, and make the split.

Done once, before anything in a case is read. From the download's manifest this
reads two fields of each record and no others: the case's folder name and its
system. It prints counts only: no case name, label or fault kind.

What it does, in this order:

1. Gives every case an anonymous ID, `case-001` to `case-455`, in an order
   shuffled with the seed, so an ID says nothing about the system or the date.
   (The original folder names start with a timestamp.)
2. Draws the development cases at random within each system. The one case whose
   label is printed in the dataset's README is put in development first, since
   its answer has already been seen; the other places are drawn.
3. Moves each case's ten telemetry files to `telemetry/<split>/<id>/` and its
   four answer files to `answers/<split>/<id>/`. The manifest, which names every
   case's root services and fault kinds, moves to `answers/all-cases/`, beside
   the map from IDs to the original folder names.
4. Writes `split.json`: each ID with its system and its split, nothing else.

Run: python -m flowguard.openrca2.prepare --root data/external/openrca2
     add --dry-run to print the counts and move nothing
     add --verify, afterwards, to hash every moved file against the download
"""

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

from flowguard.openrca2 import ANSWER_FILES, COMMIT, DATASET, TELEMETRY_FILES
from flowguard.openrca2.download import hashes

SEED = 20261112

# The systems and their sizes, from the dataset's README. Development is 100 of
# the 455, shared out in proportion (60.4, 32.5, 7.0) and rounded.
SYSTEMS = {"ts": 275, "hs": 148, "otel-demo": 32}
DEV = {"ts": 60, "hs": 33, "otel-demo": 7}

# The README prints this case's label.json as its example.
SEEN_IN_README = "batch-01KQHDBBNP9A2BWM50Z37QJT3A"

HELD_OUT = "held-out"
SPLITS = ("dev", HELD_OUT)


def assign_ids(names: list[str], seed: int) -> dict[str, str]:
    """Original folder name to anonymous ID, in an order shuffled with the seed."""
    order = sorted(names)
    random.Random(f"{seed}:ids").shuffle(order)
    width = max(3, len(str(len(order))))
    return {
        name: f"case-{number:0{width}d}" for number, name in enumerate(order, start=1)
    }


def draw_split(
    system_of: dict[str, str],
    dev: dict[str, int],
    seed: int,
    always_dev: frozenset[str],
) -> dict[str, str]:
    """ID to "dev" or "held-out": `dev[system]` cases of each system, at random.

    IDs in `always_dev` are development and count towards their system's number.
    """
    split = {}
    for system in sorted(dev):
        ids = sorted(
            case for case, its_system in system_of.items() if its_system == system
        )
        fixed = [case for case in ids if case in always_dev]
        rest = [case for case in ids if case not in always_dev]
        drawn = random.Random(f"{seed}:split:{system}").sample(
            rest, dev[system] - len(fixed)
        )
        chosen = set(fixed) | set(drawn)
        split.update({case: "dev" if case in chosen else HELD_OUT for case in ids})
    return split


def split_text(system_of: dict[str, str], split: dict[str, str], seed: int) -> str:
    """The split file's exact text, so that its SHA-256 can be recorded."""
    cases = [
        {"id": case, "system": system_of[case], "split": split[case]}
        for case in sorted(split)
    ]
    body = {"dataset": DATASET, "commit": COMMIT, "seed": seed, "cases": cases}
    return json.dumps(body, indent=1) + "\n"


def read_manifest(path: Path) -> dict[str, str]:
    """Folder name to system. No other field of a record is looked at."""
    system_of = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                record = json.loads(line)
                system_of[record["name"]] = record["system"]
    return system_of


def plan(root: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Read the manifest and decide IDs and split. Returns (id of name, system of id, split)."""
    raw = root / "raw"
    by_name = read_manifest(raw / "manifest.jsonl")
    folders = {entry.name for entry in (raw / "cases").iterdir() if entry.is_dir()}
    if folders != set(by_name):
        raise SystemExit(
            f"the manifest lists {len(by_name)} cases and the download holds {len(folders)} "
            f"folders; {len(folders ^ set(by_name))} names are in one and not the other"
        )
    if dict(Counter(by_name.values())) != SYSTEMS:
        raise SystemExit(
            f"systems are not as the README says: {dict(Counter(by_name.values()))}"
        )
    for folder in folders:
        if {
            entry.name for entry in (raw / "cases" / folder).iterdir()
        } != TELEMETRY_FILES | ANSWER_FILES:
            raise SystemExit(
                "a case folder does not hold exactly the 14 files; run the download check"
            )

    id_of = assign_ids(list(by_name), SEED)
    system_of = {id_of[name]: system for name, system in by_name.items()}
    split = draw_split(system_of, DEV, SEED, frozenset({id_of[SEEN_IN_README]}))
    return id_of, system_of, split


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def move(root: Path, id_of: dict[str, str], split: dict[str, str]) -> None:
    """Move every case's files to their new places, then the manifest."""
    raw = root / "raw"
    for name, case in id_of.items():
        for kind, files in (("telemetry", TELEMETRY_FILES), ("answers", ANSWER_FILES)):
            target = root / kind / split[case] / case
            target.mkdir(parents=True)
            for file in files:
                (raw / "cases" / name / file).rename(target / file)
        (raw / "cases" / name).rmdir()
    (raw / "cases").rmdir()
    (raw / "manifest.jsonl").rename(root / "answers" / "all-cases" / "manifest.jsonl")


def report(system_of: dict[str, str], split: dict[str, str]) -> None:
    counts = Counter((system_of[case], split[case]) for case in split)
    print(f"{'system':<10} {'dev':>5} {'held-out':>9} {'all':>5}")
    for system in SYSTEMS:
        dev, held = counts[system, "dev"], counts[system, HELD_OUT]
        print(f"{system:<10} {dev:>5} {held:>9} {dev + held:>5}")
    dev, held = (sum(1 for s in split.values() if s == name) for name in SPLITS)
    print(f"{'total':<10} {dev:>5} {held:>9} {dev + held:>5}")


def verify(root: Path) -> bool:
    """Hash every moved file against the list saved by the download check. Counts only."""
    all_cases = root / "answers" / "all-cases"
    id_of = json.loads((all_cases / "case-ids.json").read_text(encoding="utf-8"))[
        "id_of_folder"
    ]
    split = {
        c["id"]: c["split"]
        for c in json.loads((root / "split.json").read_text(encoding="utf-8"))["cases"]
    }
    checked = wrong = missing = 0
    for line in (
        (all_cases / "download.sha256").read_text(encoding="utf-8").splitlines()
    ):
        digest, path = line.split("  ", 1)
        parts = Path(path).parts
        if parts[0] != "cases":
            continue
        case, file = id_of[parts[1]], parts[2]
        kind = "telemetry" if file in TELEMETRY_FILES else "answers"
        moved = root / kind / split[case] / case / file
        if not moved.is_file():
            missing += 1
            continue
        checked += 1
        wrong += hashes(moved)[0] != digest

    stray = 0
    for kind, files in (("telemetry", TELEMETRY_FILES), ("answers", ANSWER_FILES)):
        for name in SPLITS:
            for folder in (root / kind / name).iterdir():
                stray += {entry.name for entry in folder.iterdir()} != files
    left = sum(1 for _ in (root / "raw").glob("cases/*"))
    print(f"files checked against the download's hashes: {checked}")
    print(f"missing: {missing}   wrong hash: {wrong}")
    print(f"case folders not holding exactly their files: {stray}")
    print(f"case folders left in raw: {left}")
    return not (missing or wrong or stray or left)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root: Path = args.root
    split_file = root / "split.json"

    if args.verify:
        text = split_file.read_text(encoding="utf-8")
        print(f"SHA-256 of split.json: {hashlib.sha256(text.encode()).hexdigest()}")
        return 0 if verify(root) else 1

    if split_file.exists():
        raise SystemExit(
            "split.json already exists: the split is made once and is not redrawn"
        )
    if not (root / "answers" / "all-cases" / "download.sha256").is_file():
        raise SystemExit(
            "run the download check with --save first, so the moved files can be verified"
        )
    started = [
        str(p)
        for p in (
            root / "telemetry",
            root / "answers" / "dev",
            root / "answers" / HELD_OUT,
        )
        if p.exists()
    ]
    if started:
        raise SystemExit(
            f"already there, from an earlier run that did not finish: {started}"
        )

    id_of, system_of, split = plan(root)
    report(system_of, split)
    text = split_text(system_of, split, SEED)
    print(f"seed {SEED}")
    print(f"SHA-256 of split.json: {hashlib.sha256(text.encode()).hexdigest()}")
    if args.dry_run:
        print("dry run: nothing moved, nothing written")
        return 0

    ids = (
        json.dumps(
            {"seed": SEED, "id_of_folder": dict(sorted(id_of.items()))}, indent=1
        )
        + "\n"
    )
    write(root / "answers" / "all-cases" / "case-ids.json", ids)
    print(f"SHA-256 of case-ids.json: {hashlib.sha256(ids.encode()).hexdigest()}")
    move(root, id_of, split)
    write(split_file, text)
    print(f"moved {len(id_of)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
