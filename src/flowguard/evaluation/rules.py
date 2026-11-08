"""Score every decision rule on the same finished run.

A run records each hypothesis's evidence signals, the model's own order, the
error-log fit, and the check's verdicts, so each rule in
flowguard.domain.decision can be applied afterwards without calling the model
again. It is the same function that runs inside an investigation.

    python -m flowguard.evaluation.rules reports/benchmark-2028-claude ...

Runs from before 2026-11-08 lack those records, and every rule falls back to the
rubric on them.
"""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from flowguard.domain.confidence import lead
from flowguard.domain.decision import RULES, Rule, decide
from flowguard.evaluation.investigations import (
    HIGH_CONFIDENCE,
    EvaluationReport,
    IncidentResult,
    auroc,
)


class RuleScore(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: Rule
    diagnosed: int
    to_diagnose: int
    wrong: int
    abstained_rightly: int
    to_abstain: int
    confidence_auroc: float | None
    high_confidence_right: int
    high_confidence: int


def outcome(result: IncidentResult, rule: Rule) -> tuple[str, float | None]:
    """The category this rule would have chosen, with its confidence."""
    if not result.hypotheses:
        # Nothing was proposed, so no rule could change the result.
        return result.category or "unknown", None
    decision = decide(
        rule, result.hypotheses, result.evidence_score, result.missing_sources
    )
    if decision.selected is None:
        return "unknown", None
    rivals = [(h.category, h.support or 0.0) for h in result.hypotheses]
    confidence, _ = lead(
        decision.selected.category, decision.selected.support or 0.0, rivals
    )
    return decision.selected.category, confidence


def score_rule(results: Sequence[IncidentResult], rule: Rule) -> RuleScore:
    # Paired by position, not by ID, so nothing is lost if two results share one.
    chosen = [(r, *outcome(r, rule)) for r in results]
    diagnose = [
        (r, c, conf) for r, c, conf in chosen if r.expected_outcome == "diagnose"
    ]
    abstain = [(r, c) for r, c, _ in chosen if r.expected_outcome == "abstain"]
    answered = [
        (confidence, category == r.expected_category)
        for r, category, confidence in diagnose
        if confidence is not None
    ]
    high = [right for confidence, right in answered if confidence >= HIGH_CONFIDENCE]
    return RuleScore(
        rule=rule,
        diagnosed=sum(c == r.expected_category for r, c, _ in diagnose),
        to_diagnose=len(diagnose),
        wrong=sum(c not in ("unknown", r.expected_category) for r, c, _ in diagnose),
        abstained_rightly=sum(c == "unknown" for _, c in abstain),
        to_abstain=len(abstain),
        confidence_auroc=auroc(answered),
        high_confidence_right=sum(high),
        high_confidence=len(high),
    )


def compare(results: Sequence[IncidentResult]) -> list[RuleScore]:
    return [score_rule(results, rule) for rule in RULES]


def render(name: str, scores: Sequence[RuleScore]) -> list[str]:
    lines = [
        f"### {name}",
        "",
        "| Rule | Diagnosed | Wrong | Abstained rightly | AUROC | Right at high confidence |",
        "|---|---|---|---|---|---|",
    ]
    for s in scores:
        auroc_text = (
            "n/a" if s.confidence_auroc is None else f"{s.confidence_auroc:.2f}"
        )
        lines.append(
            f"| {s.rule} | {s.diagnosed} of {s.to_diagnose} | {s.wrong} | "
            f"{s.abstained_rightly} of {s.to_abstain} | {auroc_text} | "
            f"{s.high_confidence_right} of {s.high_confidence} |"
        )
    return lines + [""]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "runs", nargs="+", type=Path, help="report folders or JSON files"
    )
    parser.add_argument("--split", default="dev")
    arguments = parser.parse_args()
    for run in arguments.runs:
        path = run / f"evaluation-{arguments.split}.json" if run.is_dir() else run
        report = EvaluationReport.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        print("\n".join(render(f"{run} ({report.model})", compare(report.incidents))))


if __name__ == "__main__":
    main()
