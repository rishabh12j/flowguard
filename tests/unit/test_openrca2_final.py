"""The final test's case choice and scoring, on a made-up root: no real case is read."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from test_openrca2_score import fault, write_case  # noqa: E402

from flowguard.openrca2.baseline import choose_cases, write_summary  # noqa: E402
from flowguard.openrca2.failures import load_run  # noqa: E402
from flowguard.openrca2.final import compare, score_run, unanswered  # noqa: E402

SPLIT = [
    {"id": "case-001", "system": "ts", "split": "dev"},
    {"id": "case-002", "system": "hs", "split": "held-out"},
    {"id": "case-003", "system": "ts", "split": "held-out"},
    {"id": "case-004", "system": "ts", "split": "held-out"},
    {"id": "case-005", "system": "hs", "split": "dev"},
    {"id": "case-006", "system": "otel-demo", "split": "held-out"},
]
EVIDENCE = [{"kind": "trace", "sql": "SELECT 1", "claim": "x"}]
RIGHT = json.dumps(
    {
        "root_causes": [
            {"service": "a", "fault_kind": "pod_failure", "evidence": EVIDENCE}
        ],
        "propagation": [],
    }
)
WRONG = json.dumps(
    {
        "root_causes": [
            {"service": "b", "fault_kind": "pod_failure", "evidence": EVIDENCE}
        ],
        "propagation": [],
    }
)


def test_the_held_out_cases_go_only_as_the_whole_split_and_shards_cover_it() -> None:
    whole = choose_cases(SPLIT, held_out=True)
    assert whole == ["case-002", "case-003", "case-004", "case-006"]
    shards = [choose_cases(SPLIT, held_out=True, shard=f"{k}/3") for k in (1, 2, 3)]
    assert sorted(sum(shards, [])) == whole
    assert shards[0] == ["case-002", "case-006"]
    # A held-out case cannot be picked by name.
    with pytest.raises(SystemExit, match="development cases only"):
        choose_cases(SPLIT, cases="case-001,case-003")
    assert choose_cases(SPLIT, cases="case-001, case-005") == ["case-001", "case-005"]
    with pytest.raises(SystemExit, match="k/n"):
        choose_cases(SPLIT, held_out=True, shard="4/3")


def record(case: str, system: str, answer: str, draft: str | None = None) -> dict:  # type: ignore[type-arg]
    out = {
        "case": case,
        "split": "held-out",
        "system": system,
        "model": "claude:test",
        "agent": "test",
        "tool_calls": {"query_parquet_files": 3},
        "turns": 4,
        "usage": {"prompt": 10, "output": 5, "usd": 0.01},
        "seconds": 1.0,
        "stopped": "the model stopped calling tools",
        "notes": [],
        "scores": None,
        "answer": answer,
    }
    if draft is not None:
        out |= {"draft": draft, "draft_scores": None}
    return out


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "split.json").write_text(json.dumps({"cases": SPLIT}), encoding="utf-8")
    for case in ("case-002", "case-003", "case-004", "case-006"):
        write_case(
            tmp_path / "answers", "held-out", case, [fault("a", "PodKill")], [], []
        )
    return tmp_path


def save(folder: Path, records: list[dict]) -> Path:  # type: ignore[type-arg]
    folder.mkdir(parents=True)
    for r in records:
        (folder / f"{r['case']}.json").write_text(json.dumps(r), encoding="utf-8")
    return folder


def test_a_run_is_scored_once_from_its_saved_answers_and_drafts(root: Path) -> None:
    run = save(
        root / "design",
        [
            record("case-002", "hs", RIGHT, draft=WRONG),
            record("case-003", "ts", WRONG, draft=RIGHT),
        ],
    )
    write_summary(run)
    assert "2 cases are not scored yet" in (run / "summary.md").read_text(
        encoding="utf-8"
    )
    assert unanswered(root, run) == ["case-004", "case-006"]
    assert score_run(root, run) == 2
    done = load_run(run)
    assert (
        done["case-002"]["scores"]["acc"],
        done["case-002"]["draft_scores"]["acc"],
    ) == (1, 0)
    assert (
        done["case-003"]["scores"]["acc"],
        done["case-003"]["draft_scores"]["acc"],
    ) == (0, 1)
    assert "not scored yet" not in (run / "summary.md").read_text(encoding="utf-8")
    # Scoring again changes nothing.
    assert score_run(root, run) == 0


def test_the_public_rule_requires_every_injected_fault(root: Path) -> None:
    # case-007 has one required fault and one optional one; the answer names the first.
    write_case(
        root / "answers",
        "held-out",
        "case-007",
        [fault("a", "PodKill"), fault("c", "PodKill", role="optional")],
        [],
        [],
    )
    run = save(root / "design", [record("case-007", "ts", RIGHT)])
    assert score_run(root, run) == 1
    done = load_run(run)["case-007"]
    assert (done["scores"]["acc"], done["scores_public"]["acc"]) == (1, 0)
    # A record scored before the public rule existed gains it, and keeps its scores.
    path = run / "case-007.json"
    old = json.loads(path.read_text(encoding="utf-8"))
    del old["scores_public"]
    old["scores"]["acc"] = 0.5  # a marker: the saved scores must not be recomputed
    path.write_text(json.dumps(old), encoding="utf-8")
    assert score_run(root, run) == 1
    again = load_run(run)["case-007"]
    assert (again["scores"]["acc"], again["scores_public"]["acc"]) == (0.5, 0)


def test_only_held_out_runs_are_scored_here(root: Path) -> None:
    dev = record("case-002", "hs", RIGHT) | {"split": "dev"}
    with pytest.raises(SystemExit, match="not from a held-out run"):
        score_run(root, save(root / "dev-run", [dev]))


def test_the_comparison_counts_a_missing_case_as_wrong_and_applies_the_bar(
    root: Path,
) -> None:
    systems = {
        "case-002": "hs",
        "case-003": "ts",
        "case-004": "ts",
        "case-006": "otel-demo",
    }
    standard = save(
        root / "standard",
        [record(c, s, WRONG) for c, s in systems.items() if c != "case-006"],
    )
    design = save(root / "design", [record(c, s, RIGHT) for c, s in systems.items()])
    score_run(root, standard)
    score_run(root, design)
    text = compare(systems, load_run(standard), load_run(design))
    assert "Not answered, counted as wrong: standard agent 1, design 0." in text
    assert "| ts | 2 | 0 | 2 |" in text
    assert "| all | 4 | 0 | 4 |" in text
    assert "in 4 cases, and wrong where it is right in 0: p = 0.1250" in text
    assert "## Under the public scorer's rule" in text
    assert "Case by case under this rule: 4 won, 0 lost" in text
    # Four cases cannot reach p < 0.05.
    assert "**not met**" in text
