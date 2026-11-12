"""Score an answer to an OpenRCA 2.0 case. DRAFT, waiting for the user's review.

The matching follows the official scoring code (rcabench_platform v3 SDK,
`evaluation/set_match.py` and `graph_match.py` in github.com/OperationsPAI/aegis,
commit 979ae70). That code reads every injected fault from `injection.json` as a
true fault. Dataset version 2.1.0 makes `label.json` the authority and gives each
fault a role; the README defines what each role means, and these rules add that:

- required: part of the answer. It is what recall counts.
- optional: "naming it is neither required nor penalised". A claim left over
  after the required faults are paired, whose service is an optional fault's,
  is set aside: it counts in neither precision's numerator nor its denominator,
  and does not break an exact match. One claim per optional fault.
- not_effective: "naming it counts as a wrong root cause". Such a claim is an
  ordinary wrong claim.

A claim's service matches a fault when, after names are lower-cased and their
hyphens and underscores removed, it is the fault's service, a service in its
`also_accept`, or, for a network fault, either end of the link. The two pairs of
kinds the official code treats as the same answer are treated so here.

The graph scores use the label's `service_edges`, which the README names as the
graph they are computed on, with load generators removed. They are left out
(None) where `process_applicable` is false. Path reachability's targets are the
services of `causal_graph.json`'s alarm nodes.

These numbers follow the published definitions; they are not official.
"""

import json
from collections import deque
from collections.abc import Hashable, Iterable
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from flowguard.openrca2.access import HELD_OUT, NotAllowed

# Observable fault kinds, from the official vocabulary (`fault_kind.py`).
KIND_OF_CHAOS = {
    "PodKill": "pod_failure",
    "ContainerKill": "pod_failure",
    "PodFailure": "pod_unavailable",
    "NetworkDelay": "network_delay",
    "NetworkLoss": "network_loss",
    "NetworkPartition": "network_partition",
    "NetworkCorrupt": "network_corrupt",
    "NetworkDuplicate": "network_duplicate",
    "NetworkBandwidth": "network_bandwidth_throttled",
    "HTTPRequestAbort": "http_aborted",
    "HTTPResponseAbort": "http_aborted",
    "HTTPRequestDelay": "http_slow",
    "HTTPResponseDelay": "http_slow",
    "HTTPResponseReplaceBody": "http_response_body_corrupted",
    "HTTPResponsePatchBody": "http_response_body_corrupted",
    "HTTPRequestReplacePath": "http_response_body_corrupted",
    "HTTPRequestReplaceMethod": "http_response_body_corrupted",
    "HTTPResponseReplaceCode": "http_wrong_status_code",
    "CPUStress": "container_cpu_saturated",
    "JVMCPUStress": "process_cpu_saturated",
    "MemoryStress": "container_memory_saturated",
    "JVMMemoryStress": "jvm_heap_exhausted",
    "JVMGarbageCollector": "jvm_gc_thrashing",
    "JVMException": "application_exception",
    "JVMMySQLException": "database_call_failed",
    "JVMLatency": "application_method_slow",
    "JVMMySQLLatency": "database_call_slow",
    "JVMReturn": "wrong_return_value",
    "JVMRuntimeMutator": "wrong_return_value",
    "DNSError": "dns_lookup_failed",
    "DNSChaos": "dns_lookup_failed",
    "DNSRandom": "dns_returned_wrong_address",
    "TimeSkew": "clock_skew",
    "TimeChaos": "clock_skew",
}
KINDS = frozenset(KIND_OF_CHAOS.values())
SAME_ANSWER = (
    frozenset({"pod_failure", "pod_unavailable"}),
    frozenset({"network_loss", "network_partition"}),
)
LOADGEN = frozenset({"loadgenerator", "locust", "wrk2", "dsbwrk2", "k6"})


def norm(name: str) -> str:
    return name.strip().lower().replace("-", "").replace("_", "")


def same_kind(a: str, b: str) -> bool:
    return a == b or any(a in group and b in group for group in SAME_ANSWER)


@dataclass(frozen=True)
class Fault:
    role: str  # required, optional or not_effective
    kind: str
    service: str
    names: frozenset[str]  # normalised names that count as this fault's service


@dataclass(frozen=True)
class Truth:
    case_id: str
    system: str
    faults: tuple[Fault, ...]
    applicable: bool  # process_applicable
    edges: frozenset[tuple[str, str]]
    alarms: frozenset[str]

    @property
    def required(self) -> tuple[Fault, ...]:
        return tuple(f for f in self.faults if f.role == "required")


def load_truth(answers: Path, case_id: str, *, final_test: bool = False) -> Truth:
    """A case's answer, from `answers/<split>/<case_id>`. `answers` is one split's folder."""
    if answers.resolve().name == HELD_OUT and not final_test:
        raise NotAllowed("held-out answers are read only by the final test")
    folder = answers / case_id
    label = json.loads((folder / "label.json").read_text(encoding="utf-8"))
    graph = json.loads((folder / "causal_graph.json").read_text(encoding="utf-8"))
    injection_file = folder / "injection.json"
    injected = (
        json.loads(injection_file.read_text(encoding="utf-8")).get("engine_config")
        if injection_file.is_file()
        else None
    )
    leaves = injected if isinstance(injected, list) else []
    faults = []
    for item in label["faults"]:
        kind = KIND_OF_CHAOS.get(item["chaos_type"], "unknown")
        names = {item["service"], *item.get("also_accept", [])}
        if kind.startswith("network_"):
            # Both ends of the link. The other end's service is the injection's
            # target_service (entries are in the label's index order); older
            # records lack it, and there the label's containers are the services.
            names |= set(item.get("container", []))
            index = item.get("index")
            if isinstance(index, int) and index < len(leaves):
                target = leaves[index].get("target_service")
                if target:
                    names.add(target)
        faults.append(
            Fault(
                item["role"], kind, item["service"], frozenset(norm(n) for n in names)
            )
        )
    to_service = graph.get("component_to_service", {})
    alarms = {
        norm(to_service.get(a["component"], a["component"]))
        for a in graph.get("alarm_nodes", [])
    }
    return Truth(
        case_id=case_id,
        system=label["system"],
        faults=tuple(faults),
        applicable=bool(label["process_applicable"]),
        edges=_edges(tuple(e) for e in label["service_edges"]),
        alarms=frozenset(alarms - LOADGEN - {""}),
    )


@dataclass(frozen=True)
class Claim:
    service: str
    kind: str


@dataclass(frozen=True)
class Answer:
    root_causes: tuple[Claim, ...]
    edges: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_json(cls, text: str) -> "Answer | None":
        """The official answer format. None when it isn't valid; such an answer scores 0."""
        try:
            data = json.loads(text)
            claims = tuple(
                Claim(str(rc["service"]), str(rc["fault_kind"]))
                for rc in data["root_causes"]
            )
            edges = tuple(
                (str(e["from"]), str(e["to"])) for e in data.get("propagation", [])
            )
            if any(not rc.get("evidence") for rc in data["root_causes"]):
                return None
        except (ValueError, KeyError, TypeError):
            return None
        return cls(claims, edges)


def _edges(pairs: Iterable[tuple[str, ...]]) -> frozenset[tuple[str, str]]:
    out = set()
    for a, b in pairs:
        a, b = norm(a), norm(b)
        if a and b and a != b and a not in LOADGEN and b not in LOADGEN:
            out.add((a, b))
    return frozenset(out)


def _f1(p: float, r: float) -> float:
    return 2 * p * r / (p + r) if p + r else 0.0


def _set_f1(guess: AbstractSet[Hashable], true: AbstractSet[Hashable]) -> float:
    if not guess and not true:
        return 1.0
    hit = len(guess & true)
    return _f1(hit / len(guess) if guess else 0.0, hit / len(true) if true else 0.0)


def score(answer: Answer | None, truth: Truth) -> dict[str, float | None]:
    """One case's scores. Keys follow the leaderboard's columns."""
    graph_keys = ("node_f1", "edge_f1", "path_acc", "path_acc_service")
    if answer is None:
        zero: dict[str, float | None] = dict.fromkeys(
            ("f1", "precision", "recall", "acc", "any_hit", "all_hit"), 0.0
        )
        zero["type_acc"] = None
        zero.update({k: (0.0 if truth.applicable else None) for k in graph_keys})
        return zero

    required = truth.required
    claims = answer.root_causes

    # Pair claims with required faults: right service and kind first, then right service only.
    status = {}  # required fault index -> (claim index, hit?)
    used: set[int] = set()
    for want_kind in (True, False):
        for j, fault in enumerate(required):
            if j in status:
                continue
            for i, claim in enumerate(claims):
                if i in used or norm(claim.service) not in fault.names:
                    continue
                if want_kind and not same_kind(claim.kind, fault.kind):
                    continue
                status[j] = (i, want_kind)
                used.add(i)
                break

    # Left-over claims naming an optional fault are set aside, one per fault.
    aside = 0
    for fault in (f for f in truth.faults if f.role == "optional"):
        for i, claim in enumerate(claims):
            if i not in used and norm(claim.service) in fault.names:
                used.add(i)
                aside += 1
                break

    hits = sum(1 for _, hit in status.values() if hit)
    counted = len(claims) - aside
    precision = hits / counted if counted else (1.0 if not required else 0.0)
    recall = hits / len(required) if required else (1.0 if counted == 0 else 0.0)
    service_right = len(status)
    result: dict[str, float | None] = {
        "f1": _f1(precision, recall),
        "precision": precision,
        "recall": recall,
        "acc": float(bool(required) and hits == len(required) == counted),
        "any_hit": float(service_right > 0),
        "all_hit": float(bool(required) and service_right == len(required)),
        "type_acc": hits / service_right if service_right else None,
    }
    if not truth.applicable:
        result.update(dict.fromkeys(graph_keys))
        return result

    edges = _edges(answer.edges)
    nodes = {a for e in edges for a in e} | (
        {norm(c.service) for c in claims} - LOADGEN - {""}
    )
    true_nodes = {a for e in truth.edges for a in e}
    result["node_f1"] = _set_f1(nodes, true_nodes)
    result["edge_f1"] = _set_f1(edges, truth.edges)
    hit_claims = [claims[i] for i, hit in status.values() if hit]
    right_claims = [claims[i] for i, _ in status.values()]
    result["path_acc"] = float(_reaches(hit_claims, edges, truth.alarms))
    result["path_acc_service"] = float(_reaches(right_claims, edges, truth.alarms))
    return result


def _reaches(
    starts: list[Claim], edges: frozenset[tuple[str, str]], alarms: frozenset[str]
) -> bool:
    """A start joins an alarmed service through the answer's edges, in either direction."""
    near: dict[str, set[str]] = {}
    for a, b in edges:
        near.setdefault(a, set()).add(b)
        near.setdefault(b, set()).add(a)
    for claim in starts:
        start = norm(claim.service)
        seen, queue = {start}, deque([start])
        while queue:
            node = queue.popleft()
            if node in alarms:
                return True
            for nxt in near.get(node, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return False


def summarise(scores: list[dict[str, float | None]]) -> dict[str, float]:
    """Means over cases. A score that is None for a case leaves that case out of its mean."""
    keys = scores[0].keys() if scores else ()
    out = {}
    for key in keys:
        values = [v for s in scores if (v := s[key]) is not None]
        out[key] = mean(values) if values else float("nan")
    return out
