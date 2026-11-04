from functools import partial

import httpx
import pytest
import json

from flowguard.dataset import DATA_DIR, load_incident
from flowguard.graph.builder import investigate
from flowguard.graph.context import Dependencies
from flowguard.llm.client import MODEL, OLLAMA_URL, OllamaLLM
from flowguard.mcp.evidence_tools import open_evidence_tools
from flowguard.rag.retrieval import retrieve

pytestmark = [pytest.mark.llm, pytest.mark.anyio]


@pytest.fixture
def anyio_backend():
    return "asyncio"


def model_is_available() -> bool:
    try:
        tags = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5).json()
    except httpx.HTTPError:
        return False
    return any(model["name"] == MODEL for model in tags.get("models", []))


async def test_gemma_diagnoses_inc_001_end_to_end(client, embedder):
    if not model_is_available():
        pytest.skip(f"Ollama is not running with {MODEL}")
    retriever = partial(retrieve, embedder=embedder, client=client)

    async with open_evidence_tools() as tools:
        dependencies = Dependencies(retriever=retriever, tools=tools, llm=OllamaLLM())
        state = await investigate(load_incident("INC-001"), dependencies)

    best = state["selected_root_cause"]
    # Documents are cited by chunk, such as SPEC-INVOICE-V3#post-v3-invoices.
    cited = {evidence_id.split("#")[0] for evidence_id in best.supporting_evidence_ids}
    assert {"LOG-882", "SPEC-INVOICE-V3", "DEPLOY-SOURCE-221"} <= cited
    assert best.confidence >= 0.85

    ground_truth = json.loads(
        (DATA_DIR / "ground_truth" / "INC-001.json").read_text(encoding="utf-8")
    )
    assert state["category"] == ground_truth["category"]
