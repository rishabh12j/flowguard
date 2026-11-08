from fakes import FakeEmbedder

from flowguard.domain.hypotheses import CATEGORY_DEFINITIONS
from flowguard.rag.fit import CategoryFit


class Recording(FakeEmbedder):
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, text: str) -> list[float]:
        self.queries.append(text)
        return super().embed_query(text)


def test_every_category_but_unknown_gets_a_similarity():
    sims = CategoryFit(FakeEmbedder())(["ERROR 429 Too Many Requests"])

    assert set(sims) == set(CATEGORY_DEFINITIONS) - {"unknown"}


def test_the_error_logs_are_embedded_together_as_one_query():
    embedder = Recording()
    fit = CategoryFit(embedder)
    # The fake embeds the definitions through embed_query too.
    embedder.queries.clear()

    fit(["first error", "second error"])

    assert embedder.queries == ["first error\nsecond error"]


def test_no_error_logs_means_no_fit():
    assert CategoryFit(FakeEmbedder())([]) == {}
