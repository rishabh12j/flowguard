"""Score a run on RCAEval RE3 incidents by the root-cause service.

RE3 labels each case with the service a code fault was released into, so an
answer is right when FlowGuard diagnoses (doesn't abstain) and names that
service. Every case has a cause, so an abstention is a miss. The category isn't
scored: every case is a release broken in itself.

Two baselines use no model, so a model's score can be read against them:
- the most common faulty service among the cases in the folder, always guessed;
- the service of the first ERROR line at or after the incident's reported start,
  in the same condensed logs the model sees.

Run: python -m flowguard.evaluation.rcaeval --data-dir <converted folder>
     --report-dir <the run's output folder> --split dev
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from flowguard.benchmark.rcaeval import BEFORE
from flowguard.dataset import incident_ids, load_ground_truth, load_incident
from flowguard.evaluation.investigations import IncidentResult, family_interval, wilson


class Counts(BaseModel):
    right: int = 0
    wrong: int = 0
    abstained: int = 0

    @property
    def total(self) -> int:
        return self.right + self.wrong + self.abstained


class ServiceScore(BaseModel):
    model: str | None
    commit: str | None
    split: str
    counts: Counts
    accuracy: float
    interval: tuple[float, float]
    family_interval: tuple[float, float] | None
    precision: float | None
    by_fault: dict[str, Counts]
    by_service: dict[str, Counts]
    abstentions: dict[str, int]
    # Abstentions where the second answer still named the right service.
    right_service_when_abstained: int
    majority_service: str
    majority_baseline: float
    first_error_baseline: float
    incidents: list[dict[str, str | None]]
    # True when the run covered only some of the folder's incidents.
    partial: bool = False


def outcome(result: IncidentResult, expected: str) -> str:
    if result.category == "unknown":
        return "abstained"
    return "right" if result.root_cause_service == expected else "wrong"


def first_error_service(data_dir: Path, incident_id: str) -> str | None:
    incident = load_incident(incident_id, data_dir)
    start = datetime.fromisoformat(incident["start_time"]) + BEFORE
    end = datetime.fromisoformat(incident["end_time"])
    errors = []
    for path in (data_dir / "logs").glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            when = datetime.fromisoformat(record["timestamp"])
            if record["level"] == "ERROR" and start <= when <= end:
                errors.append((when, record["service"]))
    return min(errors)[1] if errors else None


def score(data_dir: Path, report_dir: Path, split: str) -> ServiceScore:
    journal = report_dir / f"evaluation-{split}.journal.jsonl"
    results = [
        IncidentResult.model_validate(json.loads(line)["result"])
        for line in journal.read_text(encoding="utf-8").splitlines()
    ]
    expected = {
        i: load_ground_truth(i, data_dir).root_cause_service
        for i in incident_ids(data_dir)
    }
    # A partial run, such as one with --limit, is scored on the incidents it ran,
    # and the baselines on the same incidents.
    ran = {r.incident_id for r in results}
    partial = len(ran) < len(expected)
    expected = {i: s for i, s in expected.items() if i in ran}
    report_path = report_dir / f"evaluation-{split}.json"
    report = (
        json.loads(report_path.read_text(encoding="utf-8"))
        if report_path.exists()
        else {}
    )

    counts = Counts()
    by_fault: dict[str, Counts] = defaultdict(Counts)
    by_service: dict[str, Counts] = defaultdict(Counts)
    abstentions: Counter[str] = Counter()
    right_when_abstained = 0
    rows = []
    scored = []
    for result in results:
        truth = expected[result.incident_id]
        assert truth is not None, f"{result.incident_id} has no root-cause service"
        verdict = outcome(result, truth)
        for bucket in (
            counts,
            by_fault[(result.family or "_f?").rsplit("_", 1)[1]],
            by_service[truth],
        ):
            setattr(bucket, verdict, getattr(bucket, verdict) + 1)
        if verdict == "abstained":
            abstentions[(result.abstention or "")[:70]] += 1
            right_when_abstained += result.root_cause_service == truth
        scored.append(result.model_copy(update={"correct": verdict == "right"}))
        rows.append(
            {
                "incident_id": result.incident_id,
                "expected": truth,
                "named": result.root_cause_service,
                "outcome": verdict,
            }
        )

    services = Counter(s for s in expected.values() if s)
    majority, majority_count = services.most_common(1)[0]
    first_error_right = sum(
        first_error_service(data_dir, i) == s for i, s in expected.items()
    )
    total = counts.total
    answered = counts.right + counts.wrong
    return ServiceScore(
        model=report.get("model"),
        commit=report.get("commit"),
        split=split,
        counts=counts,
        accuracy=round(counts.right / total, 3),
        interval=wilson(counts.right, total),
        family_interval=family_interval(scored),
        precision=round(counts.right / answered, 3) if answered else None,
        by_fault=dict(sorted(by_fault.items())),
        by_service=dict(sorted(by_service.items())),
        abstentions=dict(abstentions.most_common()),
        right_service_when_abstained=right_when_abstained,
        majority_service=majority,
        majority_baseline=round(majority_count / total, 3),
        first_error_baseline=round(first_error_right / total, 3),
        incidents=rows,
        partial=partial,
    )


def percent(share: float) -> str:
    return f"{share:.0%}"


def markdown(result: ServiceScore) -> str:
    c = result.counts
    lines = [
        f"# RCAEval RE3: root-cause service, {result.split}",
        "",
        f"Model: `{result.model}`. Code from commit `{(result.commit or '?')[:7]}`."
        + (" **Partial run.**" if result.partial else ""),
        "",
        "| | Result |",
        "|---|---|",
        f"| Right service | {c.right} of {c.total}, {percent(result.accuracy)} "
        f"({percent(result.interval[0])} to {percent(result.interval[1])}) |",
    ]
    if result.family_interval:
        low, high = result.family_interval
        lines.append(
            f"| Interval counting families | {percent(low)} to {percent(high)} |"
        )
    lines += [
        f"| Wrong service | {c.wrong} |",
        f"| Abstained | {c.abstained} (named the right service anyway in "
        f"{result.right_service_when_abstained}) |",
        "| Right when it answered | "
        + (f"{percent(result.precision)} |" if result.precision is not None else "- |"),
        f"| Baseline: always {result.majority_service} | "
        f"{percent(result.majority_baseline)} |",
        f"| Baseline: first error's service | {percent(result.first_error_baseline)} |",
        "",
        "| By | Right | Wrong | Abstained |",
        "|---|---|---|---|",
    ]
    for name, group in [*result.by_fault.items(), *result.by_service.items()]:
        lines.append(f"| {name} | {group.right} | {group.wrong} | {group.abstained} |")
    if result.abstentions:
        lines += ["", "Abstentions:", ""]
        lines += [f"- {n}: {reason}" for reason, n in result.abstentions.items()]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--split", default="dev")
    arguments = parser.parse_args()
    result = score(arguments.data_dir, arguments.report_dir, arguments.split)
    text = markdown(result)
    (arguments.report_dir / f"rcaeval-{arguments.split}.md").write_text(
        text, encoding="utf-8"
    )
    (arguments.report_dir / f"rcaeval-{arguments.split}.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8"
    )
    print(text)


if __name__ == "__main__":
    main()
