"""The final test's scoring: each held-out run scored once, then the two compared.

The held-out runs (`baseline --held-out`) answer every case without reading any
answer. Only when both runs have answered every held-out case does this read the
held-out answers, score each saved answer (and draft) with the scorer the
development runs used, and compare the design with the standard agent case by
case. The bar, agreed on 2026-11-13: the design has more exact matches, with a
paired sign test p < 0.05.

Each answer is scored under two rules, as agreed with the bar: the roles from
`label.json` (the bar's rule), and the public scorer's rule that every injected
fault is required (`scores_public`, reported beside it).

Run: python -m flowguard.openrca2.final --root data/external/openrca2
     --standard reports/openrca2-heldout-standard --design reports/openrca2-heldout-design
     --out reports/openrca2-heldout-compared.md
"""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from statistics import mean
from typing import Any

from flowguard.openrca2.access import HELD_OUT
from flowguard.openrca2.baseline import read_answer, write_summary
from flowguard.openrca2.failures import load_run, paired_p
from flowguard.openrca2.score import Truth, load_truth, score

BAR_P = 0.05
SYSTEMS = ("hs", "otel-demo", "ts")


def held_out_ids(root: Path) -> dict[str, str]:
    """Each held-out case ID with its system, from `split.json`."""
    split = json.loads((root / "split.json").read_text(encoding="utf-8"))["cases"]
    return {c["id"]: c["system"] for c in split if c["split"] == HELD_OUT}


def unanswered(root: Path, folder: Path) -> list[str]:
    """The held-out cases a run has not answered yet."""
    return sorted(set(held_out_ids(root)) - set(load_run(folder)))


def public_rule(truth: Truth) -> Truth:
    """The public scorer's rule: every injected fault is required, whatever its role."""
    return replace(
        truth, faults=tuple(replace(f, role="required") for f in truth.faults)
    )


def score_run(root: Path, folder: Path) -> int:
    """Scores each answered case that lacks a score; returns how many records it changed.

    A score already saved is never computed again: a record scored under the
    labels' roles only gains the public rule's scores.
    """
    answers = root / "answers" / HELD_OUT
    done = 0
    for path in sorted(folder.glob("case-*.json")):
        record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        if record.get("split") != HELD_OUT:
            raise SystemExit(f"{path} is not from a held-out run")
        if record["scores"] is not None and record.get("scores_public") is not None:
            continue
        truth = load_truth(answers, record["case"], final_test=True)
        answer = read_answer(record["answer"])[0]
        if record["scores"] is None:
            record["scores"] = score(answer, truth)
            if record.get("draft") is not None:
                record["draft_scores"] = score(read_answer(record["draft"])[0], truth)
        record["scores_public"] = score(answer, public_rule(truth))
        path.write_text(
            json.dumps(record, indent=1, default=str) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        done += 1
    write_summary(folder)
    return done


def compare(
    systems: dict[str, str],
    standard: dict[str, dict[str, Any]],
    design: dict[str, dict[str, Any]],
) -> str:
    """The two runs side by side; a case a run did not answer counts as wrong."""

    def exact(run: dict[str, dict[str, Any]], case: str, key: str = "scores") -> int:
        record = run.get(case)
        return int(bool(record and record.get(key) and record[key]["acc"]))

    def f1(run: dict[str, dict[str, Any]], cases: list[str]) -> float:
        return mean(
            (run[c]["scores"]["f1"] or 0.0) if c in run and run[c]["scores"] else 0.0
            for c in cases
        )

    cases = sorted(systems)
    lines = [f"# The final test: {len(cases)} held-out cases\n"]
    missing = {
        name: len([c for c in cases if c not in run])
        for name, run in (("standard", standard), ("design", design))
    }
    if any(missing.values()):
        lines.append(
            f"Not answered, counted as wrong: standard agent {missing['standard']}, "
            f"design {missing['design']}.\n"
        )
    lines.append(
        "| System | Cases | Standard agent, exact | Design, exact | Standard F1 | Design F1 |"
    )
    lines.append("|---|---|---|---|---|---|")
    groups = [(s, [c for c in cases if systems[c] == s]) for s in SYSTEMS]
    for name, group in [*groups, ("all", cases)]:
        if not group:
            continue
        lines.append(
            f"| {name} | {len(group)} | {sum(exact(standard, c) for c in group)} | "
            f"{sum(exact(design, c) for c in group)} | {f1(standard, group):.3f} | "
            f"{f1(design, group):.3f} |"
        )
    won = sum(1 for c in cases if exact(design, c) and not exact(standard, c))
    lost = sum(1 for c in cases if exact(standard, c) and not exact(design, c))
    p = paired_p(won, lost)
    passed = won > lost and p < BAR_P
    lines.append(
        f"\nCase by case, the design is right where the standard agent is wrong in {won} "
        f"cases, and wrong where it is right in {lost}: p = {p:.4f} (paired sign test)."
    )
    lines.append(
        f"\n**The bar** (more exact matches than the standard agent, p < {BAR_P}): "
        + ("**met**." if passed else "**not met**.")
    )
    if all(r.get("scores_public") for run in (standard, design) for r in run.values()):
        key = "scores_public"
        lines.append(
            "\n## Under the public scorer's rule: every injected fault is required\n"
        )
        lines.append("| System | Cases | Standard agent, exact | Design, exact |")
        lines.append("|---|---|---|---|")
        for name, group in [*groups, ("all", cases)]:
            if group:
                lines.append(
                    f"| {name} | {len(group)} | {sum(exact(standard, c, key) for c in group)} | "
                    f"{sum(exact(design, c, key) for c in group)} |"
                )
        won_p = sum(
            1 for c in cases if exact(design, c, key) and not exact(standard, c, key)
        )
        lost_p = sum(
            1 for c in cases if exact(standard, c, key) and not exact(design, c, key)
        )
        lines.append(
            f"\nCase by case under this rule: {won_p} won, {lost_p} lost, "
            f"p = {paired_p(won_p, lost_p):.4f}. The bar is judged on the first table."
        )
    usd = {
        name: sum(r["usage"]["usd"] for r in run.values())
        for name, run in (("standard", standard), ("design", design))
    }
    lines.append(
        f"\nCost: standard agent ${usd['standard']:.2f}, design ${usd['design']:.2f}."
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--standard", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--count-missing-as-wrong",
        action="store_true",
        help="score even though some cases are unanswered (after retries failed), counting them as wrong",
    )
    args = parser.parse_args()
    systems = held_out_ids(args.root)
    gaps = {f: unanswered(args.root, f) for f in (args.standard, args.design)}
    if any(gaps.values()) and not args.count_missing_as_wrong:
        for folder, ids in gaps.items():
            print(
                f"{folder}: {len(ids)} of {len(systems)} held-out cases not answered yet"
            )
        print(
            "Run the missing cases (the runner skips those already done), or pass --count-missing-as-wrong."
        )
        return 1
    for folder in (args.standard, args.design):
        print(f"{folder}: scored {score_run(args.root, folder)} cases")
    report = compare(systems, load_run(args.standard), load_run(args.design))
    args.out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
