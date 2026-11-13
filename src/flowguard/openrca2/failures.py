"""Compare runs on the same development cases, and say what each miss was.

Used to read the baseline (phase 4) and to judge each part of the design against
it (phase 5). Development cases only: it reads `answers/dev`.

For two runs it reports how often they agree case by case, which is the measure of
run-to-run spread, and an exact paired test on the cases where they disagree.
For each run it classes every case without an exact match:

- invalid answer;
- missed a required fault (no claim names its service), and what was named
  instead: the service that fault's service calls or is called by (a neighbour
  in the true graph), an entry service, or another;
- wrong kind on a required fault's service, as "true kind -> claimed kind";
- an extra claim, naming a not-effective fault (which counts as wrong) or a
  service with no fault (an optional fault's service is free, and not listed).

Run: python -m flowguard.openrca2.failures --root data/external/openrca2
     reports/openrca2-baseline-haiku reports/openrca2-baseline-haiku-run2
"""

import argparse
import json
import sys
from collections import Counter
from math import comb
from pathlib import Path
from typing import Any

from flowguard.openrca2.score import Answer, Truth, load_truth, norm, same_kind

ENTRY = frozenset({"tsuidashboard", "tsgatewayservice", "frontend", "frontendproxy"})


def load_run(folder: Path) -> dict[str, dict[str, Any]]:
    return {
        r["case"]: r
        for r in (
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(folder.glob("case-*.json"))
        )
    }


def classify(answer: Answer | None, truth: Truth) -> list[str]:
    """What went wrong in one case; empty when nothing did."""
    if answer is None:
        return ["invalid answer"]
    out = []
    claims = list(answer.root_causes)
    used: set[int] = set()
    neighbours = {s for edge in truth.edges for s in edge}
    for fault in truth.required:
        matches = [
            i
            for i, c in enumerate(claims)
            if i not in used and norm(c.service) in fault.names
        ]
        if not matches:
            out.append("missed a required fault")
            continue
        i = matches[0]
        used.add(i)
        if not same_kind(claims[i].kind, fault.kind):
            out.append(f"wrong kind: {fault.kind} -> {claims[i].kind}")
    optional = [f for f in truth.faults if f.role == "optional"]
    not_effective = [f for f in truth.faults if f.role == "not_effective"]
    for i, claim in enumerate(claims):
        if i in used:
            continue
        name = norm(claim.service)
        if any(name in f.names for f in optional):
            continue  # free under the scoring rules
        if any(name in f.names for f in not_effective):
            out.append("extra claim: a not-effective fault")
        elif name in ENTRY:
            out.append("named instead: an entry service")
        elif name in neighbours:
            out.append("named instead: a service on the true graph")
        else:
            out.append("named instead: another service")
    return out


def paired_p(only_a: int, only_b: int) -> float:
    """Exact two-sided sign test on the cases where two runs disagree."""
    n = only_a + only_b
    if n == 0:
        return 1.0
    k = min(only_a, only_b)
    tail = sum(comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def report(root: Path, folders: list[Path]) -> str:
    runs = {f.name: load_run(f) for f in folders}
    cases = sorted(set.intersection(*(set(r) for r in runs.values())))
    truths = {c: load_truth(root / "answers" / "dev", c) for c in cases}
    lines = [f"# Runs compared on {len(cases)} development cases\n"]
    lines.append(
        "| Run | Exact match | "
        + " | ".join(sorted({t.system for t in truths.values()}))
        + " | Cost | Seconds a case |"
    )
    systems = sorted({t.system for t in truths.values()})
    lines.append("|---|---|" + "---|" * len(systems) + "---|---|")
    for name, run in runs.items():
        acc = {c: run[c]["scores"]["acc"] for c in cases}
        per = [
            f"{sum(acc[c] for c in cases if truths[c].system == s):.0f} of {sum(truths[c].system == s for c in cases)}"
            for s in systems
        ]
        usd = sum(run[c]["usage"]["usd"] for c in cases)
        secs = sum(run[c]["seconds"] for c in cases) / len(cases)
        lines.append(
            f"| {name} | {sum(acc.values()):.0f} | "
            + " | ".join(per)
            + f" | ${usd:.2f} | {secs:.0f} |"
        )

    names = list(runs)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            only_a = sum(
                runs[a][c]["scores"]["acc"] > runs[b][c]["scores"]["acc"] for c in cases
            )
            only_b = sum(
                runs[b][c]["scores"]["acc"] > runs[a][c]["scores"]["acc"] for c in cases
            )
            both = sum(
                runs[a][c]["scores"]["acc"] == runs[b][c]["scores"]["acc"] == 1
                for c in cases
            )
            lines.append(
                f"\n{a} against {b}: both right in {both}, both wrong in {len(cases) - both - only_a - only_b}, "
                f"only {a} right in {only_a}, only {b} right in {only_b}; exact paired test p = {paired_p(only_a, only_b):.3f}."
            )

    for name, run in runs.items():
        classes: Counter[str] = Counter()
        kinds: Counter[str] = Counter()
        misses = 0
        for c in cases:
            if run[c]["scores"]["acc"] == 1:
                continue
            misses += 1
            found = classify(Answer.from_json(run[c]["answer"]), truths[c])
            classes.update(
                {x.split(":")[0] if x.startswith("wrong kind") else x for x in found}
            )
            kinds.update(
                x.removeprefix("wrong kind: ")
                for x in found
                if x.startswith("wrong kind")
            )
        lines.append(f"\n## {name}: {misses} cases without an exact match\n")
        lines.append(
            "A case can show more than one problem.\n\n| Problem | Cases |\n|---|---|"
        )
        lines += [f"| {k} | {v} |" for k, v in classes.most_common()]
        if kinds:
            lines.append("\n| Wrong kind: true -> claimed | Times |\n|---|---|")
            lines += [f"| {k} | {v} |" for k, v in kinds.most_common()]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="also write the report here")
    parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args()
    text = report(args.root, args.runs)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
