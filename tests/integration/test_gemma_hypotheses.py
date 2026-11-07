import httpx
import pytest

from flowguard.dataset import load_evidence, load_ground_truth, load_incident
from flowguard.domain.evidence import EvidenceItem
from flowguard.domain.incidents import Incident
from flowguard.graph.nodes.root_cause import propose_hypotheses
from flowguard.llm.client import MODEL, OLLAMA_URL, OllamaLLM

pytestmark = pytest.mark.llm


def model_is_available() -> bool:
    try:
        tags = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5).json()
    except httpx.HTTPError:
        return False
    return any(model["name"] == MODEL for model in tags.get("models", []))


@pytest.fixture(scope="module")
def llm():
    if not model_is_available():
        pytest.skip(f"Ollama is not running with {MODEL}")
    return OllamaLLM()


def inc_001_evidence() -> list[EvidenceItem]:
    # What an investigation of INC-001 would gather, with every runbook as a
    # distractor. All eight incidents' evidence together is longer than the
    # model's context.
    truth = load_ground_truth("INC-001")
    wanted = {*truth.required_evidence_ids, *truth.relevant_evidence_ids}
    return [
        item
        for item in load_evidence()
        if item.evidence_id in wanted or item.source_type == "runbook"
    ]


def test_gemma_finds_the_inc_001_root_cause(llm):
    incident = Incident.model_validate(load_incident("INC-001"))

    hypotheses, _ = propose_hypotheses(incident, inc_001_evidence(), llm)

    # Code ranks the hypotheses, so the model's order is not checked.
    required = {"LOG-882", "SPEC-INVOICE-V3", "DEPLOY-SOURCE-221"}
    assert any(
        required <= set(hypothesis.supporting_evidence_ids) for hypothesis in hypotheses
    )
