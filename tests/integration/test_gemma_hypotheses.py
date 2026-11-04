import httpx
import pytest

from flowguard.dataset import load_evidence, load_incident
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


def test_gemma_finds_the_inc_001_root_cause(llm):
    incident = Incident.model_validate(load_incident("INC-001"))

    hypotheses = propose_hypotheses(incident, load_evidence(), llm)

    required = {"LOG-882", "SPEC-INVOICE-V3", "DEPLOY-SOURCE-221"}
    assert required <= set(hypotheses[0].supporting_evidence_ids)
