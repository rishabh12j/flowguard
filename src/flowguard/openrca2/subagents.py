"""Subagents: a fresh context that answers one question for the lead (phase 5).

Once the lead has a draft answer, code sends each fault in it to subagents:

- the kind check tries to disprove the kind the lead chose;
- the spread check traces every call link the fault's effect travelled, from a
  list of the routes up from the faulty service that code computes.

The findings go back to the lead, which keeps or changes its answer: the checks
are advice, never a limit on the answer.

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
from flowguard.openrca2.score import KINDS, norm, same_kind
from flowguard.openrca2.survey import _pair

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
        data = consult(
            conversation,
            self.run_tool,
            KIND_ANSWER,
            VERDICT_SCHEMA,
            self.max_calls,
            budget,
            verdict,
            "kind check",
        )
        try:
            if data is not None:
                if data["kind"] not in KINDS:
                    raise ValueError(f"not a kind: {data['kind']!r}")
                verdict.kind = data["kind"]
                verdict.confidence = str(data.get("confidence", ""))
                verdict.scope = str(data.get("scope", ""))
                verdict.ruled_out = list(data.get("ruled_out", []))
                verdict.evidence = list(data.get("evidence", []))
        except (ValueError, KeyError, TypeError) as error:
            verdict.notes.append(f"the kind check gave no usable finding: {error}")
        verdict.seconds = round(time.monotonic() - started, 1)
        return verdict


def consult(
    conversation: Conversation,
    run_tool: Callable[[ToolCall], str],
    answer_prompt: str,
    schema: dict[str, Any],
    max_calls: int,
    budget: Callable[[float], bool] | None,
    into: Any,
    what: str,
) -> dict[str, Any] | None:
    """Let a subagent explore, then ask for its finding; None when there is none.

    What it did (calls, turns, usage, notes, transcript) is written into `into`.
    A failure is noted, never raised: a failed check does not lose the case.
    """
    data = None
    try:
        found = explore(
            conversation,
            run_tool,
            max_calls=max_calls,
            refusal=f"Tool-call budget exhausted: the hard cap of {max_calls} calls is reached. Stop now.",
            budget=budget,
        )
        into.usage.add(found.usage)
        into.calls, into.turns = sum(found.calls.values()), found.turns
        into.notes += found.notes
        final = conversation.conclude(None, answer_prompt, schema)
        into.usage.add(final.usage)
        into.turns += 1
        into.notes += final.notes
        data = json.loads(final.text)
        if not isinstance(data, dict):
            raise ValueError("the finding is not a JSON object")
    except ModelFailed as error:
        into.notes.append(f"the {what} failed: {error}")
        into.usage.usd = max(into.usage.usd, float(getattr(conversation, "spent", 0.0)))
        data = None
    except ValueError as error:
        into.notes.append(f"the {what} gave no usable finding: {error}")
        data = None
    into.transcript = conversation.transcript()
    return data


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


# The spread check ---------------------------------------------------------------

SPREAD_CALLS = 20
SPREAD_FAULTS = 3  # at most this many faults of a draft are traced
MAX_LINKS = 40  # call links listed for the subagent, nearest the fault first

SPREAD_SYSTEM = """You are tracing how the effect of one fault travelled through a microservice system. The lead investigator has found a fault at a service. Find every call link through which its effect reached other services, up to the services users call. You are not asked whether the fault is real or what kind it is.

## The data
{data}
## What a propagation edge is
{rules}
## How to judge a link
A link joins a service and one of its callers. It carried the effect when the caller's calls to that service changed in the incident against the normal period: more errors, longer times, fewer calls, or calls that stopped. Write the edge from the called service to the caller: the direction the failure travelled, opposite to the calls.

- Follow every route, not only the first one you find. The effect often reaches a caller by several routes at once, including a direct call that skips a service on another route. Each link that carried the effect is one edge.
- A fault in a service's network, or in its outgoing requests, can touch every connection the service uses: check the links from the services it calls as well as the links to its callers. If the faulty service itself stopped working, its calls to others simply ceased: nothing travelled to them, so those links are not edges.
- A link whose calls look as they did in the normal period did not carry the effect, even if it lies on a route to the users. Leave it out.
- Load generators are not services: never use them in an edge.

## How to work
Code has listed the call links on every route from the faulty service up to the entry services, and from the services it calls, each with how its calls changed. Use the list as a starting point and check it with your own queries: it is computed from parent and child spans and may miss links. For each edge, find one query that shows the change on that link, abnormal against normal. Aim for about 10 tool calls; the hard cap is {max_calls}. Use think_tool to record what each result shows.
"""

SPREAD_FIRST = """The fault: service `{service}`, kind `{kind}`.

The edges in the lead investigator's draft, for the whole incident: {edges}

Entry services (users' requests arrive here): {entries}

### Call links from the faulty service toward the users, computed by code
Each row is written in the direction a failure travels: from the called service to its caller. Each change is normal → incident; a dash means no such calls were seen in that period.

{links}

Code has also surveyed this case's telemetry; the survey follows. Use it as a starting point and check it: it may miss what matters.

{survey}"""

SPREAD_ANSWER = """Report your finding now, in the required JSON format:
- `reasoning`: which routes the effect took and which listed links it did not touch, in two to four sentences;
- `edges`: every link that carried the effect, from the called service to its caller, each with a query showing the change on that link and what its rows show. Use service names exactly as they appear in the data. Each query must run on the tables as you queried them;
- `reaches_users`: whether the effect reached an entry service."""

_SQL_EVIDENCE: dict[str, Any] = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {"sql": {"type": "string"}, "claim": {"type": "string"}},
        "required": ["sql", "claim"],
        "additionalProperties": False,
    },
}
SPREAD_SCHEMA: dict[str, Any] = {
    "type": "object",
    # In this order, so the reasoning is written before the edges.
    "properties": {
        "reasoning": {"type": "string"},
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "evidence": _SQL_EVIDENCE,
                },
                "required": ["from", "to", "evidence"],
                "additionalProperties": False,
            },
        },
        "reaches_users": {"type": "boolean"},
    },
    "required": ["reasoning", "edges", "reaches_users"],
    "additionalProperties": False,
}

REVIEW_ALL = """Other investigators, each starting fresh with the same tools, checked your draft answer: the kind of each fault, and how each fault's effect travelled. Their findings:

{findings}

They saw less of the case than you did, and they can be wrong. Weigh their evidence against yours: which account explains everything you observed? You may keep your draft or change it, faults and edges alike.

Now write your final answer in the required JSON format, under the same rules as before. If you use their queries as evidence, copy them exactly."""


def propagation_rules(contract: str) -> str:
    """The contract's field rules on propagation and on load generators."""
    fields = contract[contract.index("## Field rules") : contract.index("## SQL rules")]
    kept = [
        item
        for item in fields.split("\n  * ")[1:]
        if "propagation" in item or "Synthetic traffic" in item
    ]
    return "".join(f"- {' '.join(item.split())}\n" for item in kept)


Link = tuple[
    Any, ...
]  # (caller, callee, rate n, a, errors n, a, p95 n, a), as survey.calls


def routes(links: list[Link], service: str, entries: list[str]) -> list[Link]:
    """The call links a fault at `service` could travel, nearest first.

    The links from the services it calls, then up from it through its callers.
    The climb stops at the entry services: their callers are not services users
    call.
    """
    want = norm(service)
    stop = {norm(e) for e in entries}
    out: list[Link] = []
    seen: set[tuple[str, str]] = set()

    def add(link: Link) -> None:
        if (link[0], link[1]) not in seen:
            seen.add((link[0], link[1]))
            out.append(link)

    for link in links:
        if norm(link[0]) == want:
            add(link)  # one of its callees: the fault may sit on that connection
    queue, reached = [want], {want}
    while queue:
        node = queue.pop(0)
        if node in stop and node != want:
            continue
        for link in links:
            if norm(link[1]) != node:
                continue
            add(link)
            caller = norm(link[0])
            if caller not in reached:
                reached.add(caller)
                queue.append(caller)
    return out[:MAX_LINKS]


def link_table(links: list[Link]) -> str:
    if not links:
        return "No calls to or from this service were found in the traces."
    rows = [
        "| From (called) | To (caller) | Calls a minute | Error share | p95 ms |",
        "|---|---|---|---|---|",
    ]
    rows += [
        f"| {callee} | {caller} | {_pair(rn, ra)} | {_pair(en, ea, 2)} | {_pair(pn, pa)} |"
        for caller, callee, rn, ra, en, ea, pn, pa in links
    ]
    return "\n".join(rows)


@dataclass
class Spread:
    """What a spread check found for one fault of the draft."""

    service: str
    kind: str
    edges: list[dict[str, Any]] | None = None  # None when there is no usable finding
    reaches_users: bool | None = None
    reasoning: str = ""
    links_listed: int = 0
    calls: int = 0
    turns: int = 0
    usage: Usage = field(default_factory=Usage)
    seconds: float = 0.0
    notes: list[str] = field(default_factory=list)
    transcript: list[dict[str, Any]] = field(default_factory=list)

    def pairs(self) -> set[tuple[str, str]]:
        return {(norm(str(e["from"])), norm(str(e["to"]))) for e in self.edges or []}

    def record(self) -> dict[str, Any]:
        return {**vars(self), "usage": vars(self.usage)}


@dataclass
class SpreadCheck:
    """Runs a spread subagent on one fault of a draft answer."""

    spawn: Callable[[str, str], Conversation]
    run_tool: Callable[[ToolCall], str]
    data: str
    rules: str
    survey: str
    links: list[Link]  # every call link of the case, as survey.calls gives them
    entries: list[str]
    max_calls: int = SPREAD_CALLS
    max_faults: int = SPREAD_FAULTS

    def __call__(
        self,
        claim: dict[str, Any],
        draft_edges: list[tuple[str, str]],
        budget: Callable[[float], bool] | None = None,
    ) -> Spread:
        started = time.monotonic()
        spread = Spread(str(claim.get("service", "")), str(claim.get("fault_kind", "")))
        listed = routes(self.links, spread.service, self.entries)
        spread.links_listed = len(listed)
        conversation = self.spawn(
            SPREAD_SYSTEM.format(
                data=self.data, rules=self.rules, max_calls=self.max_calls
            ),
            SPREAD_FIRST.format(
                service=spread.service,
                kind=spread.kind,
                edges=", ".join(f"{a} → {b}" for a, b in draft_edges) or "none",
                entries=", ".join(self.entries) or "not found",
                links=link_table(listed),
                survey=self.survey,
            ),
        )
        data = consult(
            conversation,
            self.run_tool,
            SPREAD_ANSWER,
            SPREAD_SCHEMA,
            self.max_calls,
            budget,
            spread,
            "spread check",
        )
        try:
            if data is not None:
                spread.edges = [
                    e
                    for e in data["edges"]
                    if str(e["from"]).strip() and str(e["to"]).strip()
                ]
                spread.reaches_users = bool(data["reaches_users"])
                spread.reasoning = str(data.get("reasoning", ""))
        except (KeyError, TypeError) as error:
            spread.edges = None
            spread.notes.append(f"the spread check gave no usable finding: {error}")
        spread.seconds = round(time.monotonic() - started, 1)
        return spread


def changes_edges(spreads: list[Spread], draft_edges: list[tuple[str, str]]) -> bool:
    """Whether the spread checks found edges other than the draft's."""
    found = [s for s in spreads if s.edges is not None]
    if not found:
        return False
    proposed = set().union(*(s.pairs() for s in found))
    return proposed != {(norm(a), norm(b)) for a, b in draft_edges}


def review_all(
    verdicts: list[Verdict], spreads: list[Spread], draft_edges: list[tuple[str, str]]
) -> str:
    """The message that shows the lead what the kind and spread checks found."""
    parts = []
    if verdicts:
        kinds = review(verdicts)
        parts.append(kinds[kinds.index("###") : kinds.index("\n\nThey saw less")])
    draft = {(norm(a), norm(b)) for a, b in draft_edges}
    for s in spreads:
        head = f"### How the effect of `{s.service}` (`{s.kind}`) travelled"
        if s.edges is None:
            parts.append(f"{head}\nThe check gave no finding.")
            continue
        lines = [head, f"Reasoning: {s.reasoning}"]
        if not s.reaches_users:
            lines.append("They found that its effect did not reach the entry services.")
        lines.append("Edges they found, from the called service to its caller:")
        for e in s.edges:
            pair = (norm(str(e["from"])), norm(str(e["to"])))
            lines.append(
                f"- {e['from']} → {e['to']}"
                + ("" if pair in draft else " (not in your draft)")
            )
            lines += [
                f"  - {ev.get('claim')}\n    `{ev.get('sql')}`" for ev in e["evidence"]
            ]
        ends = {norm(s.service)} | {x for pair in s.pairs() for x in pair}
        left = [
            f"{a} → {b}"
            for a, b in draft_edges
            if (norm(a), norm(b)) not in s.pairs() and {norm(a), norm(b)} & ends
        ]
        if left:
            lines.append(
                "Edges in your draft near this fault that they did not find: "
                + ", ".join(left)
            )
        parts.append("\n".join(lines))
    return REVIEW_ALL.format(findings="\n\n".join(parts))
