"""Subagents: a fresh context that answers one question for the lead (phase 5).

The kind check is the first. Once the lead has a draft answer, code sends each
fault in it to a subagent, whose job is to try to disprove the kind the lead
chose. The findings go back to the lead, which keeps or changes its answer: the
check is advice, never a limit on the answer.

What the subagent is told comes from two sources and no others: the official
definitions and boundary rules (the answer contract, part of the task), and how
each family of fault works, which fixes what it can and cannot touch. Nothing is
written from particular development cases, and nothing depends on a metric that
only some systems record.
"""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from flowguard.openrca2.chat import (
    Conversation,
    ModelFailed,
    ToolCall,
    Usage,
    explore,
)
from flowguard.openrca2.score import KINDS, same_kind

KIND_CALLS = 20
KIND_FAULTS = 3  # at most this many faults of a draft are checked

KIND_SYSTEM = """You are checking one claim from an incident investigation in a microservice system. The lead investigator believes a particular service suffered a particular kind of fault. Test the kind: try to disprove it against the kinds most easily confused with it, using the telemetry, and report which kind the evidence supports. You are not asked whether the service is the right one, and you are not asked to solve the whole incident.

## The data
{data}
## The kinds of fault: official definitions and boundary rules
{rules}
## How to tell kinds apart: find the scope
Each kind of fault acts at one level, and the level decides what it touches and what it leaves alone. Find the smallest set of operations that holds everything affected, then check that everything in that set is affected and that what lies outside it is not.

- **A network fault (`network_*`) acts on a connection between two pods.** Everything carried on that connection is affected, whatever the protocol, route or statement: HTTP and RPC calls, database and cache traffic alike. The services' own processing stays normal: the time is lost between the two ends of a call (a Client span lasts much longer than the Server span it called), or the call never arrives. A delay adds a similar amount to every call on the connection. Loss and corruption cause retransmissions: irregular times with long tails, timeouts, resets, connection errors. A partition leaves calls hanging until a timeout, or unable to connect, while both services stay alive and go on with their other work.
- **An HTTP fault (`http_*`) acts on particular HTTP requests of one service:** certain routes or methods. Other routes between the same two services, and the same pod's database, cache and RPC traffic, stay normal. The connection itself stays healthy.
- **A code-level fault (`application_*`, `database_call_*`, `wrong_return_value`) acts inside one process, on one method or one kind of database statement.** The time or the error arises inside the service. A database-call fault is in the service's own driver: the affected statements are slower by a steady amount, or throw at once with an error from the SQL layer, while other statements on the same database connection, the connection pool and the network to the database stay normal.
- **A pod fault (`pod_*`) stops the whole instance:** restarts, a new pod name, a reset uptime, not ready, and a gap in every signal from that pod at once. Its callers fail fast or time out. A process that has just started uses much CPU and memory for a while; that is start-up, not saturation.
- **A resource fault (`*_saturated`, `jvm_*`) slows everything the process does at once.** It shows in that resource's own metric for a sustained period, beginning before any restart it leads to. If the heap climbs to its limit and the process then dies or restarts, the heap came first.
- **A DNS fault shows in the error text:** a name cannot be resolved, before any connection is tried. Timeouts and connection failures without such text point to the network.

Questions that separate kinds often confused:
- *Slow calls to a database.* Is everything on that connection slower, by irregular amounts, with timeouts, connection errors, waits for a pooled connection, or signs at the network level? That is a network fault on the link. Or are only certain statements slower, by a steady amount, with the connection and its other statements normal? That is `database_call_slow`.
- *Failing calls to a database.* Connection-level errors (link failure, connect or read timed out, no connection available) point to the network. An exception from the SQL layer, at once, on particular statements while others succeed, is `database_call_failed`.
- *Slow outgoing calls.* Is every call on the connection slower, on any route and any protocol, or every connection of the pod? That is `network_delay`. Only particular HTTP routes, with the pod's other traffic to the same peer normal? That is `http_slow`. Did the service's own Server or Internal span time grow, and not the gap between caller and called? That is `application_method_slow`.
- *Failing outgoing calls.* Hanging until a timeout, on everything to one peer, with the peer alive: the network. Cut quickly on particular HTTP routes: `http_aborted`. The peer itself silent in all its signals: a pod fault at the peer.
- *A restart.* Check what the resource metrics did before it. A restart with nothing before it is a pod fault.

## Where to look
- **Traces:** `attr_span_kind` is Client, Server or Internal. `span_name` carries the route or the statement. The two ends of one call are a Client span and the Server span whose `parent_span_id` is its `span_id`. Compare by service, peer, span kind and span name, abnormal against normal.
- **Logs:** exception and error text of the service and its peers.
- **Metrics:** `k8s.container.restarts`, `k8s.container.ready`, `k8s.pod.uptime`, `k8s.pod.network.io`, `k8s.pod.network.errors`, container and pod CPU and memory, and, where a case has them, `jvm.*`, `db.client.connections.*` and the per-connection `hubble_*` metrics. A metric missing from a case proves nothing: say it is missing.

## How to work
Query the telemetry yourself; don't rely on the lead's evidence alone. Aim for about 10 tool calls; the hard cap is {max_calls}. Use think_tool to record what each result rules in or out. Look for evidence against the claimed kind as hard as for it. If the telemetry cannot separate two kinds, say so and give low confidence; a guess presented as a finding does harm. Kinds scored as the same answer (see the equivalence classes) need not be told apart.
"""

KIND_FIRST = """The claim to test: service `{service}` suffered `{kind}`.

The lead investigator's evidence for it:
{evidence}

Code has also surveyed this case's telemetry; the survey follows. Use it as a starting point and check it: it may miss what matters.

{survey}"""

KIND_ANSWER = """Report your finding now, in the required JSON format:
- `scope`: what is affected and what is not, in two or three sentences;
- `ruled_out`: each kind you tested and rejected, and the evidence that rejects it;
- `kind`: the kind the evidence supports (the claimed one, if it stands);
- `confidence`: high, medium or low;
- `evidence`: the queries that show it, each with what its rows show. Each query must run on the tables as you queried them."""

_KIND = {"type": "string", "enum": sorted(KINDS)}
VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    # In this order, so the reasoning is written before the verdict.
    "properties": {
        "scope": {"type": "string"},
        "ruled_out": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"kind": _KIND, "why": {"type": "string"}},
                "required": ["kind", "why"],
                "additionalProperties": False,
            },
        },
        "kind": _KIND,
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "evidence": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {"sql": {"type": "string"}, "claim": {"type": "string"}},
                "required": ["sql", "claim"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["scope", "ruled_out", "kind", "confidence", "evidence"],
    "additionalProperties": False,
}

REVIEW = """A second investigator, starting fresh with the same tools, tested the kind of each fault in your draft answer. Their findings:

{findings}

They saw less of the case than you did, and they can be wrong. Weigh their evidence against yours: which account explains everything you observed, above all what is affected and what is not? You may keep your draft or change it.

Now write your final answer in the required JSON format, under the same rules as before. If you use their queries as evidence, copy them exactly."""


def kind_rules(contract: str) -> str:
    """The contract's definitions, boundary rules and equivalence classes, without the answer format."""
    start = contract.index("`fault_kind` labels a root cause")
    end = contract.index("## Field rules")
    return contract[start:end].strip() + "\n"


@dataclass
class Verdict:
    """What a kind check found for one fault of the draft."""

    service: str
    claimed: str
    kind: str | None = None  # None when the subagent gave no usable finding
    confidence: str = ""
    scope: str = ""
    ruled_out: list[dict[str, str]] = field(default_factory=list)
    evidence: list[dict[str, str]] = field(default_factory=list)
    calls: int = 0
    turns: int = 0
    usage: Usage = field(default_factory=Usage)
    seconds: float = 0.0
    notes: list[str] = field(default_factory=list)
    transcript: list[dict[str, Any]] = field(default_factory=list)

    @property
    def disagrees(self) -> bool:
        return self.kind is not None and not same_kind(self.kind, self.claimed)

    def record(self) -> dict[str, Any]:
        return {**vars(self), "usage": vars(self.usage), "disagrees": self.disagrees}


@dataclass
class KindCheck:
    """Runs a kind subagent on one fault of a draft answer."""

    spawn: Callable[[str, str], Conversation]  # (system prompt, first message)
    run_tool: Callable[[ToolCall], str]
    data: str  # the description of the tables
    rules: str
    survey: str
    max_calls: int = KIND_CALLS
    max_faults: int = KIND_FAULTS

    def __call__(
        self, claim: dict[str, Any], budget: Callable[[float], bool] | None = None
    ) -> Verdict:
        started = time.monotonic()
        verdict = Verdict(
            str(claim.get("service", "")), str(claim.get("fault_kind", ""))
        )
        evidence = "\n".join(
            f"- {e.get('claim', '')}\n  `{e.get('sql', '')}`"
            for e in claim.get("evidence", [])
        )
        conversation = self.spawn(
            KIND_SYSTEM.format(
                data=self.data, rules=self.rules, max_calls=self.max_calls
            ),
            KIND_FIRST.format(
                service=verdict.service,
                kind=verdict.claimed,
                evidence=evidence or "- (none given)",
                survey=self.survey,
            ),
        )
        try:
            found = explore(
                conversation,
                self.run_tool,
                max_calls=self.max_calls,
                refusal=f"Tool-call budget exhausted: the hard cap of {self.max_calls} calls is reached. Stop now.",
                budget=budget,
            )
            verdict.usage.add(found.usage)
            verdict.calls, verdict.turns = sum(found.calls.values()), found.turns
            verdict.notes += found.notes
            final = conversation.conclude(None, KIND_ANSWER, VERDICT_SCHEMA)
            verdict.usage.add(final.usage)
            verdict.turns += 1
            verdict.notes += final.notes
            data = json.loads(final.text)
            if data["kind"] not in KINDS:
                raise ValueError(f"not a kind: {data['kind']!r}")
            verdict.kind = data["kind"]
            verdict.confidence = str(data.get("confidence", ""))
            verdict.scope = str(data.get("scope", ""))
            verdict.ruled_out = list(data.get("ruled_out", []))
            verdict.evidence = list(data.get("evidence", []))
        except ModelFailed as error:
            # A failed check does not lose the case: the lead's draft stands.
            verdict.notes.append(f"the kind check failed: {error}")
            verdict.usage.usd = max(
                verdict.usage.usd, float(getattr(conversation, "spent", 0.0))
            )
        except (ValueError, KeyError, TypeError) as error:
            verdict.notes.append(f"the kind check gave no usable finding: {error}")
        verdict.seconds = round(time.monotonic() - started, 1)
        verdict.transcript = conversation.transcript()
        return verdict


def review(verdicts: list[Verdict]) -> str:
    """The message that shows the lead what the kind checks found."""
    parts = []
    for v in verdicts:
        if v.kind is None:
            parts.append(
                f"### `{v.service}`: you said `{v.claimed}`. The check gave no finding."
            )
            continue
        head = (
            f"### `{v.service}`: you said `{v.claimed}`. They conclude `{v.kind}`"
            if v.disagrees
            else f"### `{v.service}`: you said `{v.claimed}`. They agree"
        )
        lines = [f"{head} (confidence: {v.confidence}).", f"Scope: {v.scope}"]
        if v.ruled_out:
            lines.append("Ruled out:")
            lines += [f"- `{r.get('kind')}`: {r.get('why')}" for r in v.ruled_out]
        lines.append("Evidence:")
        lines += [f"- {e.get('claim')}\n  `{e.get('sql')}`" for e in v.evidence]
        parts.append("\n".join(lines))
    return REVIEW.format(findings="\n\n".join(parts))
