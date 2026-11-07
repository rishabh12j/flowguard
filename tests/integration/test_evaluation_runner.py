"""Runs the whole evaluation with the oracle model, so every metric should be perfect.

This proves the runner's wiring: if a perfect model can't score perfectly, the
runner or the data is wrong, not the model.
"""

from functools import partial

import pytest

from flowguard.dataset import incident_ids, load_ground_truth
from flowguard.evaluation.investigations import (
    ModelUnavailable,
    evaluate,
    render_markdown,
    write_report,
)
from flowguard.evaluation.oracle import Oracle
from flowguard.llm.client import LLMError
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


class Unreachable:
    """A model that fails if it's used: a resumed run must not need it."""

    def generate(self, system: str, prompt: str, schema: dict) -> str:
        raise AssertionError("the journal should have answered for this incident")


async def test_an_interrupted_run_resumes_from_its_journal(client, embedder, tmp_path):
    journal = tmp_path / "evaluation.journal.jsonl"
    search = partial(retrieve, embedder=embedder, client=client)
    incidents = ["INC-001", "INC-002"]
    first = await evaluate(
        lambda incident_id: Oracle(load_ground_truth(incident_id)),
        search,
        incidents,
        "oracle",
        journal=journal,
    )

    resumed = await evaluate(
        lambda incident_id: Unreachable(), search, incidents, "oracle", journal=journal
    )

    assert len(journal.read_text(encoding="utf-8").splitlines()) == 2
    assert resumed.incidents == first.incidents
    assert resumed.metrics == first.metrics


class Down:
    """A model that can't be reached, as when Ollama fails to load it."""

    def generate(self, system: str, prompt: str, schema: dict) -> str:
        raise LLMError("could not reach Ollama")


async def test_a_model_outage_stops_the_run_instead_of_being_scored(
    client, embedder, tmp_path
):
    journal = tmp_path / "evaluation.journal.jsonl"
    search = partial(retrieve, embedder=embedder, client=client)
    incidents = ["INC-001", "INC-002"]

    def failing_on_the_second(incident_id: str):
        if incident_id == "INC-002":
            return Down()
        return Oracle(load_ground_truth(incident_id))

    with pytest.raises(ModelUnavailable, match="could not reach Ollama"):
        await evaluate(
            failing_on_the_second, search, incidents, "oracle", journal=journal
        )
    # The outage wasn't journaled as an abstention, so a resume retries it.
    assert len(journal.read_text(encoding="utf-8").splitlines()) == 1

    resumed = await evaluate(
        lambda incident_id: Oracle(load_ground_truth(incident_id)),
        search,
        incidents,
        "oracle",
        journal=journal,
    )
    assert [result.status for result in resumed.incidents] == [
        "awaiting_approval",
        "awaiting_approval",
    ]
