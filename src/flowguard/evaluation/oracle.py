"""A stand-in model that answers from the ground truth.

It checks the pipeline and the data, never the model: if a perfect answer can't
solve an incident, the incident's data or FlowGuard's wiring is wrong.
"""

import json
from typing import Any

from flowguard.seed_schemas import GroundTruth


def offered(schema: dict[str, Any], model: str, field: str) -> list[str]:
    """The evidence IDs the schema lets the model cite."""
    properties = schema["$defs"][model]["properties"]
    options: list[str] = properties[field]["items"]["enum"]
    return options


class Oracle:
    """Answers as if it knew the ground truth, citing only evidence it was given."""

    def __init__(self, truth: GroundTruth) -> None:
        self.truth = truth
        self.required = set(truth.required_evidence_ids)

    def cited(self, available: list[str]) -> list[str]:
        # Documents are cited by chunk, so SPEC-X#section matches SPEC-X.
        return [item for item in available if item.split("#")[0] in self.required]

    def generate(self, system: str, prompt: str, schema: dict[str, Any]) -> str:
        if "actions" in schema["properties"]:
            cited = self.cited(offered(schema, "ProposedAction", "evidence_ids"))
            steps = [
                {
                    **step.model_dump(),
                    "reason": "From the runbook.",
                    "evidence_ids": cited[:1],
                }
                for step in self.truth.reference_plan
            ]
            return json.dumps({"actions": steps})
        cited = self.cited(
            offered(schema, "ProposedHypothesis", "supporting_evidence_ids")
        )
        hypothesis = {
            "description": self.truth.root_cause,
            "category": self.truth.category,
            "supporting_evidence_ids": cited,
            "contradicting_evidence_ids": [],
            "missing_evidence": [],
        }
        return json.dumps({"hypotheses": [hypothesis]})
