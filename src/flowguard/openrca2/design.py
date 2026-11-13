"""FlowGuard's own agents for OpenRCA 2.0, built part by part (phase 5).

The design is in docs/openrca2-design.md. Each part is added on top of the last
and kept only if it passes the rule written there.

1. `lead`: one agent with the standard agent's tools, but this project's prompt
   (how answers are judged, as the user agreed the agents may be told, and how to
   work) and an answer held to the official schema by structured output. The
   answer turn keeps the same system prompt, so no history is edited.
2. `lead+survey`: the same, with the code survey of the case (survey.py) in the
   first message.

The prompt draws on the task's official texts (the answer contract and the
dataset's README) and on how each kind of fault works. Nothing in it is fitted to
particular development cases or to one system.
"""

from dataclasses import dataclass
from typing import Any, Callable

from flowguard.openrca2.access import CaseTelemetry
from flowguard.openrca2.survey import survey

LEAD_SYSTEM = """You are investigating an incident in a microservice system, using only its telemetry. Find every fault that caused it, the kind of each fault, and how the effect of each travelled to the services users call.

## The data
Ten tables, queried with DuckDB SQL through the tools. `normal_*` tables cover a period before the incident, `abnormal_*` tables the incident. For each period there are traces, logs, metrics, metrics_sum and metrics_histogram. In the tools, dots in column names are underscores (`attr_status_code`). Duration in traces is in nanoseconds. Metrics include container, pod and JVM metrics, `k8s.container.restarts` and `k8s.pod.uptime`; some cases also have per-connection network metrics (`hubble_*` in metrics_sum, with `attr_source` and `attr_destination` naming pods).

## How the answer is judged
- Each fault is named as a service and a kind, from the list of kinds below.
- Name a fault only if its effect reached beyond its own service: other services, or the requests users make. A fault whose effect stayed inside its own service is not part of the answer. A fault that had no effect at all counts as a wrong answer if named. There may be more than one fault, each named separately.
- Where a fault is counted:
  - an HTTP fault (`http_*`) at the calling service, whose outgoing requests were altered; the called service's own server spans stay normal;
  - a network fault (`network_*`) between two services at either end;
  - any other fault at the service it is in.
- Propagation edges run from the faulty service toward the users: the direction the failure spread, which is usually the opposite of the direction of the calls.

## How to work
1. Compare abnormal with normal for every service at once (error share, latency, request counts, log errors, key metrics) before looking closely at any. Don't stop at the first anomaly.
2. For each service that changed, decide whether its own work went wrong or it inherited the problem from something it calls: compare its own time with its callees' time, and find where errors first appear.
3. A service that went quiet (fewer or no spans or logs) may be the one that failed.
4. For each fault you suspect, decide its kind with evidence that tells similar kinds apart, using the rules below. In particular:
   - A network fault on a connection shows at the network level on that connection (its traffic, retransmissions, drops), seen from both ends. A fault inside a service's own database calls changes that service's database spans and leaves the network traffic as it was.
   - A restart shows as restarts, a new pod, a reset uptime or a gap in spans, not as steady saturation.
   - An HTTP fault changes requests on particular HTTP paths from the caller; other traffic from the same pod is unaffected.
5. Trace how each fault's effect reached the services users call.

Use think_tool to record your reasoning after each round of queries. Aim for about 50 tool calls; the hard cap is 100.

{agent_contract}
"""

LEAD_ANSWER = """Write your answer now, in the required JSON format: every fault you found (service, fault_kind, evidence) and the propagation edges (from, to, evidence). Use service names exactly as they appear in the data. Each evidence query must run on the tables as you queried them, and its claim must be what the rows show."""

SURVEY_NOTE = "\n\nCode has surveyed this case's telemetry; the survey follows. Use it as a starting point and check it: it may miss what matters.\n\n"


@dataclass(frozen=True)
class Agent:
    """How one kind of agent is prompted.

    `answer_system` None keeps the investigation's system prompt for the answer
    turn, so no history is edited; a string replaces it, as the standard agent's
    separate synthesis call does. `answer_schema` holds the answer to a JSON
    schema by structured output.
    """

    name: str
    system: str
    first: Callable[[CaseTelemetry], str]
    answer_system: str | None
    answer_prompt: str
    answer_schema: dict[str, Any] | None


def lead_agents(
    incident: str, contract: str, schema: dict[str, Any]
) -> dict[str, Agent]:
    """The design's agents, from the incident text, the answer contract and the answer schema."""
    system = LEAD_SYSTEM.format(agent_contract=contract)
    return {
        "lead": Agent("lead", system, lambda case: incident, None, LEAD_ANSWER, schema),
        "lead+survey": Agent(
            "lead+survey",
            system,
            lambda case: incident + SURVEY_NOTE + survey(case.connect()),
            None,
            LEAD_ANSWER,
            schema,
        ),
    }
