"""Walks one incident through a running FlowGuard API, start to finish.

python -m flowguard.demo                    # investigate INC-001 and stop for approval
python -m flowguard.demo --approve          # ...and approve the plan
python -m flowguard.demo --reject "Reason"  # ...or decline it
python -m flowguard.demo --incident INC-003 --url http://localhost:8000
"""

import argparse
import json
from collections.abc import Callable

import httpx

from flowguard.dataset import load_incident

Print = Callable[[str], None]


def run(
    client: httpx.Client,
    incident_id: str,
    *,
    decision: str | None = None,
    comment: str = "",
    approver: str = "demo",
    say: Print = print,
) -> str:
    """Runs the demo against the API and returns the investigation's final status."""
    ready = client.get("/health/ready")
    checks = ready.json().get("checks", {})
    say("Readiness: " + ", ".join(f"{name} {state}" for name, state in checks.items()))
    if ready.status_code != 200:
        say("FlowGuard isn't ready. Start Ollama and Qdrant, then try again.")
        return "not ready"

    say(f"\nInvestigating {incident_id}. With Gemma, this takes about a minute...")
    started = client.post("/investigations", json=load_incident(incident_id))
    record = started.json()
    if started.status_code != 201:
        say(f"The request was rejected: {json.dumps(record['detail'])}")
        return "rejected"

    path = f"/investigations/{record['investigation_id']}"
    say(f"Status: {record['status']}. Category: {record['category']}.")
    for action in record["actions"]:
        approval = "needs approval" if action["requires_approval"] else "no approval"
        say(
            f"  {action['step']}. {action['action']} on {action['target']} ({approval})"
        )

    if record["status"] == "awaiting_approval" and decision:
        route = "approve" if decision == "approve" else "reject"
        decided = client.post(
            f"{path}/{route}", json={"approver": approver, "comment": comment}
        )
        record = decided.json()
        say(f"\nDecision recorded: {record['status']}.")
    elif record["status"] == "awaiting_approval":
        say(
            f"\nWaiting for approval. Decide with POST {path}/approve or "
            f"{path}/reject, or rerun with --approve."
        )

    say("\n" + client.get(f"{path}/report").text)
    events = client.get(f"{path}/events").json()
    say("Audit trail: " + ", ".join(f"v{e['version']} {e['status']}" for e in events))
    return str(record["status"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--incident", default="INC-001")
    parser.add_argument("--approver", default="demo")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--approve", action="store_true")
    choice.add_argument("--reject", metavar="REASON")
    arguments = parser.parse_args()

    decision = (
        "approve" if arguments.approve else "reject" if arguments.reject else None
    )
    # A real model takes about a minute, so wait longer than httpx's default.
    with httpx.Client(base_url=arguments.url, timeout=600) as client:
        run(
            client,
            arguments.incident,
            decision=decision,
            comment=arguments.reject or "",
            approver=arguments.approver,
        )


if __name__ == "__main__":
    main()
