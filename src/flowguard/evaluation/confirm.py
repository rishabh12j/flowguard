"""Judge the one confirmation of a decision rule on fresh incidents.

    python -m flowguard.evaluation.confirm reports/benchmark-2030-gemma \
        reports/benchmark-2030-claude

The pass mark was fixed on 2026-11-08, before any confirmation run (brief §22),
and is written here before the runs so it can't drift to fit them. In each run,
the chosen rule is compared with the rubric on the same answers. It passes only
if, in every run, it:

- diagnoses at least 5 more incidents than the rubric;
- makes at most 1 more wrong diagnosis;
- abstains on at least 9 of the 10 incidents with no diagnosable cause.

The marks are counts out of the benchmark's 100 diagnosable and 10 no-cause
incidents, so a run of any other size, or one that didn't use the rule live,
isn't judged. Confidence AUROC is printed but not judged: it isn't in the mark.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from flowguard.domain.decision import RULES, Rule
from flowguard.evaluation.investigations import EvaluationReport
from flowguard.evaluation.rules import RuleScore, score_rule

MIN_GAIN = 5
MAX_EXTRA_WRONG = 1
MIN_ABSTAINED = 9
TO_DIAGNOSE = 100
TO_ABSTAIN = 10


@dataclass(frozen=True)
class Verdict:
    name: str
    passed: bool
    # One line per criterion, or the reason the run isn't judged.
    lines: tuple[str, ...]


def judge(name: str, chosen: RuleScore, rubric: RuleScore) -> Verdict:
    if (chosen.to_diagnose, chosen.to_abstain) != (TO_DIAGNOSE, TO_ABSTAIN):
        return Verdict(
            name,
            False,
            (
                f"not judged: the run has {chosen.to_diagnose} incidents to diagnose "
                f"and {chosen.to_abstain} to abstain on, not {TO_DIAGNOSE} and "
                f"{TO_ABSTAIN}",
            ),
        )
    gain = chosen.diagnosed - rubric.diagnosed
    extra_wrong = chosen.wrong - rubric.wrong
    checks = [
        (
            gain >= MIN_GAIN,
            f"diagnosed {chosen.diagnosed} of {chosen.to_diagnose} against the "
            f"rubric's {rubric.diagnosed}, {gain:+d}; needs +{MIN_GAIN} or more",
        ),
        (
            extra_wrong <= MAX_EXTRA_WRONG,
            f"wrong {chosen.wrong} against the rubric's {rubric.wrong}, "
            f"{extra_wrong:+d}; needs +{MAX_EXTRA_WRONG} or fewer",
        ),
        (
            chosen.abstained_rightly >= MIN_ABSTAINED,
            f"abstained on {chosen.abstained_rightly} of {chosen.to_abstain}; "
            f"needs {MIN_ABSTAINED} or more",
        ),
    ]
    return Verdict(
        name,
        all(ok for ok, _ in checks),
        tuple(f"{'pass' if ok else 'FAIL'}: {text}" for ok, text in checks),
    )


def used_live(report: EvaluationReport, rule: Rule) -> bool:
    """Whether the run chose root causes with this rule, from its model line."""
    parts = report.model.split(", ")
    return rule == "rubric" or f"rule {rule}" in parts


def judge_report(name: str, report: EvaluationReport, rule: Rule) -> Verdict:
    if not used_live(report, rule):
        return Verdict(
            name, False, (f"not judged: the run didn't use rule {rule} live",)
        )
    return judge(
        name,
        score_rule(report.incidents, rule),
        score_rule(report.incidents, "rubric"),
    )


def auroc_line(report: EvaluationReport, rule: Rule) -> str:
    def text(score: RuleScore) -> str:
        auroc = score.confidence_auroc
        return "n/a" if auroc is None else f"{auroc:.2f}"

    chosen = score_rule(report.incidents, rule)
    rubric = score_rule(report.incidents, "rubric")
    return (
        f"not judged: confidence AUROC {text(chosen)} under {rule}, "
        f"{text(rubric)} under the rubric"
    )


def render(rule: Rule, verdicts: Sequence[Verdict], notes: Sequence[str]) -> str:
    lines = []
    for verdict, note in zip(verdicts, notes, strict=True):
        lines += [f"### {verdict.name}", ""]
        lines += [f"- {line}" for line in verdict.lines]
        lines += [f"- {note}", ""]
    passed = bool(verdicts) and all(v.passed for v in verdicts)
    lines.append(
        f"**{rule} {'passes' if passed else 'fails'} the confirmation**"
        + ("." if passed else ": it must pass in every run.")
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "runs", nargs="+", type=Path, help="report folders or JSON files"
    )
    parser.add_argument("--rule", choices=RULES, default="evidence")
    parser.add_argument("--split", default="dev")
    arguments = parser.parse_args()
    verdicts, notes = [], []
    for run in arguments.runs:
        path = run / f"evaluation-{arguments.split}.json" if run.is_dir() else run
        report = EvaluationReport.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        name = f"{run} ({report.model})"
        verdicts.append(judge_report(name, report, arguments.rule))
        notes.append(auroc_line(report, arguments.rule))
    print(render(arguments.rule, verdicts, notes))
    sys.exit(0 if all(v.passed for v in verdicts) else 1)


if __name__ == "__main__":
    main()
