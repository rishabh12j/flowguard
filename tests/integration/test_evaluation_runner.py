"""Runs the whole evaluation with the oracle model, so every metric should be perfect.

This proves the runner's wiring: if a perfect model can't score perfectly, the
runner or the data is wrong, not the model.
"""

from functools import partial

import pytest
from oracle import Oracle

from flowguard.dataset import incident_ids, load_ground_truth
from flowguard.evaluation.investigations import evaluate, render_markdown, write_report
from flowguard.rag.retrieval import retrieve

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def report(client, embedder):
    return await evaluate(
        lambda incident_id: Oracle(load_ground_truth(incident_id)),
        partial(retrieve, embedder=embedder, client=client),
        incident_ids(),
        "oracle",
    )


async def test_a_perfect_model_scores_perfectly(report):
    metrics = report.metrics

    assert metrics.diagnosis_accuracy == 1.0
    assert metrics.top_3_recall == 1.0
    assert metrics.evidence_precision == 1.0
    assert metrics.required_evidence_recall == 1.0
    assert metrics.tool_call_success_rate == 1.0
    assert metrics.unsupported_claim_rate == 0.0
    assert metrics.plan_recall == 1.0


async def test_no_plan_is_unsafe_or_skips_approval(report):
    assert report.metrics.unsafe_action_rate == 0.0
    assert report.metrics.approval_bypass_rate == 0.0
    assert {result.status for result in report.incidents} == {"awaiting_approval"}


async def test_without_logs_every_incident_abstains(report):
    assert len(report.abstentions) == len(incident_ids())
    assert report.metrics.abstention_when_logs_are_missing == 1.0


async def test_the_report_is_written_as_json_and_markdown(report, tmp_path):
    write_report(report, tmp_path)

    saved = (tmp_path / "evaluation.json").read_text(encoding="utf-8")
    assert '"diagnosis_accuracy": 1.0' in saved
    summary = render_markdown(report)
    assert "| diagnosis accuracy | 100% | ≥ 80% | met |" in summary
    assert "| approval bypass rate | 0% | 0% | met |" in summary
