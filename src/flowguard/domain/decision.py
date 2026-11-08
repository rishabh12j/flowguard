"""The rules that choose a root cause from scored hypotheses, or abstain.

The same functions run inside an investigation and when a finished evaluation
is re-scored, so a rule measured offline is the rule that would run live.

- rubric: the original rule. The best hypothesis's own evidence score ranks it,
  and must reach 0.65.
- evidence: the evidence the hypotheses cite together must reach 0.65, so one
  hypothesis's citation style can't make FlowGuard abstain. Hypotheses are ranked
  by their score, with a bonus for the category whose definition best matches the
  incident's error logs.
- evidence_shared: as evidence, but every hypothesis gets the points for a cited
  change, such as a release, so a release story can't win just by citing it.
- model: as evidence for abstaining, but the model's own first choice is the answer.
- checked: as evidence, but a second model call first rules out hypotheses the
  evidence doesn't support, and ranks what failed above what only came before.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, Literal, Protocol, TypeVar

from flowguard.domain.confidence import (
    CHANGE_SIGNALS,
    clamp,
    deductions,
    points,
)

Rule = Literal["rubric", "evidence", "evidence_shared", "model", "checked"]
RULES: tuple[Rule, ...] = ("rubric", "evidence", "evidence_shared", "model", "checked")

# The brief's line between moderate and insufficient confidence.
MIN_SUPPORT = 0.65
# Added to the hypothesis whose category best matches the error logs. Chosen on
# data/benchmark-2028, so it is confirmed on a fresh set before it is relied on.
FIT_BONUS = 0.20
# Higher is better: what failed, then what only came before, then no verdict.
VERDICT_ORDER = {"mechanism": 2, "trigger_only": 1}


class Scored(Protocol):
    @property
    def category(self) -> str: ...
    @property
    def support(self) -> float | None: ...
    @property
    def contradicting_evidence_ids(self) -> Sequence[str]: ...
    @property
    def proposed_rank(self) -> int | None: ...
    @property
    def signals(self) -> Sequence[str]: ...
    @property
    def fit(self) -> float | None: ...
    @property
    def verdict(self) -> str | None: ...


H = TypeVar("H", bound=Scored)


@dataclass(frozen=True)
class Decision(Generic[H]):
    # Best first. The selected hypothesis, if any, is the first.
    ranked: tuple[H, ...]
    selected: H | None
    abstention: str | None


def best_fit(hypotheses: Sequence[Scored]) -> str | None:
    fits = [(h.fit, h.category) for h in hypotheses if h.fit is not None]
    return max(fits)[1] if fits else None


def shared_support(
    hypothesis: Scored, hypotheses: Sequence[Scored], missing_sources: int
) -> float:
    """Its score if every hypothesis got the points for the changes any of them cite."""
    changes = {s for h in hypotheses for s in h.signals} & CHANGE_SIGNALS
    own = (frozenset(hypothesis.signals) - CHANGE_SIGNALS) | changes
    return clamp(
        points(frozenset(own))
        - deductions(len(hypothesis.contradicting_evidence_ids), missing_sources)
    )


def decide(
    rule: Rule,
    hypotheses: Sequence[H],
    evidence_score: float | None,
    missing_sources: int = 0,
) -> Decision[H]:
    if not hypotheses:
        return Decision((), None, "no hypothesis was proposed")

    fittest = best_fit(hypotheses)

    def bonus(h: Scored) -> float:
        return FIT_BONUS if fittest is not None and h.category == fittest else 0.0

    def evidence_key(h: Scored) -> float:
        return (h.support or 0.0) + bonus(h)

    candidates = list(hypotheses)
    if rule == "rubric":
        ranked = sorted(candidates, key=lambda h: h.support or 0.0, reverse=True)
    elif rule == "evidence":
        ranked = sorted(candidates, key=evidence_key, reverse=True)
    elif rule == "evidence_shared":
        ranked = sorted(
            candidates,
            key=lambda h: shared_support(h, hypotheses, missing_sources) + bonus(h),
            reverse=True,
        )
    elif rule == "model":
        # Hypotheses without a recorded rank go last, in code's order.
        ranked = sorted(
            candidates, key=lambda h: h.proposed_rank or len(candidates) + 1
        )
    else:
        ruled_out = [h for h in candidates if h.verdict == "not_supported"]
        kept = [h for h in candidates if h.verdict != "not_supported"]
        if not kept:
            return Decision(
                tuple(ruled_out),
                None,
                "the check found no hypothesis the evidence supports",
            )
        ranked = (
            sorted(
                kept,
                key=lambda h: (VERDICT_ORDER.get(h.verdict or "", 1), evidence_key(h)),
                reverse=True,
            )
            + ruled_out
        )

    best = ranked[0]
    if rule == "rubric" or evidence_score is None:
        # Records from before the evidence score was kept fall back to the rubric's gate.
        score = best.support or 0.0
        if score < MIN_SUPPORT:
            return Decision(
                tuple(ranked),
                None,
                f"the best hypothesis scored {score:.2f}, below {MIN_SUPPORT:.2f}",
            )
    elif evidence_score < MIN_SUPPORT:
        return Decision(
            tuple(ranked),
            None,
            f"the evidence together scored {evidence_score:.2f}, below {MIN_SUPPORT:.2f}",
        )
    return Decision(tuple(ranked), best, None)
