"""How closely an incident's error logs match each category's definition.

The rubric counts what kinds of evidence a hypothesis cites, not whether the
evidence points to its category. This adds that: the error logs are embedded
and compared with each category's written definition. Nothing here is written
for a particular incident or template; on data/benchmark-2028 the logs alone
named the right category 65% of the time, so it's a tie-breaker, not a verdict.
"""

from collections.abc import Sequence

from flowguard.domain.hypotheses import CATEGORY_DEFINITIONS
from flowguard.rag.embedding import Embedder


class CategoryFit:
    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._categories = [name for name in CATEGORY_DEFINITIONS if name != "unknown"]
        self._definitions = embedder.embed_documents(
            [
                f"{name.replace('_', ' ')}: {CATEGORY_DEFINITIONS[name]}"
                for name in self._categories
            ]
        )

    def __call__(self, error_logs: Sequence[str]) -> dict[str, float]:
        """Each category's cosine similarity to the error logs, or nothing without logs."""
        if not error_logs:
            return {}
        query = self._embedder.embed_query("\n".join(error_logs))
        # The embeddings are normalised, so the dot product is the cosine.
        return {
            name: round(sum(a * b for a, b in zip(definition, query, strict=True)), 3)
            for name, definition in zip(
                self._categories, self._definitions, strict=True
            )
        }
