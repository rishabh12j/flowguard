"""The standard OpenRCA 2.0 agent, rebuilt to measure it (phase 3, brief section 33).

This is the leaderboard's agent as published, not FlowGuard's design: one model
in a loop with four tools, then one call that turns the transcript into the
answer. Sources, all read in phase 1:

- Prompts: the paper's appendix F.4 (arXiv 2606.27154v2), word for word, with the
  reflection prompt the co-author's adaptation adds to the system prompt.
- The answer contract: the official SDK's `get_agent_contract_prompt()`
  (prompts/agent_contract.md).
- The incident text: the SDK's `RCABench` template.
- Tools: the co-author's adaptation (github.com/QishengLu/rca_study_thinkdepthai,
  commit 26b5166, MIT): dots in column names become underscores, a query
  returns 10 rows unless asked for more, and a result over about 5,000 tokens is
  refused with a suggested LIMIT.
- About 50 tool calls advised, 100 the cap, after which the answer is forced.

Known differences from the leaderboard's runs: its harness is not public; the
current Claude Haiku and Sonnet refuse a temperature, so 0.7 is used only on
local models; and all ten tables are queryable in every call, where the
co-author's tool mounts only the tables a call names.

Run: python -m flowguard.openrca2.baseline --root data/external/openrca2
     --provider ollama --model gpt-oss:20b --sample 10 --out reports/openrca2-baseline-gptoss
"""

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import duckdb

from flowguard.openrca2.access import CaseTelemetry
from flowguard.openrca2.chat import Conversation, ModelFailed, ToolCall, ToolSpec, Usage
from flowguard.openrca2.design import Agent, lead_agents
from flowguard.openrca2.score import KINDS, Answer, load_truth, score, summarise

PROMPTS = Path(__file__).parent / "prompts"
MAX_CALLS = 100
ROW_LIMIT = 10
TOKEN_LIMIT = 5000  # per tool result, at 3 characters a token, as the co-author's tools
SAMPLE_SEED = 20261112
NEWLINE = chr(10)

INVESTIGATION = """You are a Root Cause Analysis (RCA) expert investigating a microservices incident.
For context, today's date is {date}.
## Goal
Identify the root cause(s) of the SLO violation from the telemetry. There may be more than one. Let the data tell you how many faults there are and where they sit.
Your job in this phase is INVESTIGATION ONLY. A separate synthesis step will turn your findings into the final structured output. Do not try to emit JSON or final answers here.
## Available data
Parquets in this case directory:
- abnormal_metrics.parquet, abnormal_traces.parquet, abnormal_logs.parquet
- abnormal_metrics_histogram.parquet, abnormal_metrics_sum.parquet
- normal_metrics.parquet, normal_traces.parquet, normal_logs.parquet
Common columns:
- metrics: time, metric, value, service_name, attr.k8s.pod.name, attr.k8s.namespace.name
- metrics_sum: same shape; carries jvm.cpu.*, jvm.memory.*, jvm.thread.count, jvm.gc.*, container.cpu.*, container.memory.*
- metrics_histogram: time, metric, service_name, count, sum, min, max, attr.jvm.gc.action, attr.jvm.gc.name
- traces: time, trace_id, span_id, parent_span_id, span_name, service_name, duration, attr.status_code, attr.http.request.method, attr.http.response.status_code
- logs: time, trace_id, span_id, level, service_name, message
## Tools
1. query_parquet_files: DuckDB SQL on parquets in this case dir.
2. list_tables_in_directory: list parquets.
3. get_schema: column types of a parquet.
4. think_tool: REQUIRED after each query; summarize, plan next step.
## Hard limits
- Tool-call budget: aim for ~50 calls; extend if the evidence genuinely warrants it. Hard cap is 100, at which point the runtime forces a stop.
- Spend the budget efficiently: list_tables_in_directory once, get_schema on the files you actually plan to query, then spend the rest on query_parquet_files.
## Investigation playbook
1. list_tables_in_directory to confirm the parquet files.
2. get_schema on the relevant ones (start with abnormal_traces).
3. Diff abnormal vs normal: error rates, latency, status codes, log levels.
4. Trace the call chain (parent_span_id -> span_id) to find the earliest service whose own work, not its dependency's, went wrong.
5. Decide every root cause and every propagation edge. More than one root cause is possible; note each separately when evidence supports it.
"""

REFLECTION = """<Reflection Methodology — MANDATORY>
**CRITICAL: You MUST call think_tool after every round of data queries. Never skip reflection.**

Failing to reflect leads to misidentifying symptoms as root causes. You MUST follow this discipline:

1. **After discovering available data (list_tables + get_schema)** → call think_tool to plan:
   - Which data sources are most relevant to this incident?
   - What should I query first and why?

2. **After EVERY round of SQL queries** → call think_tool to analyze:
   - What anomalies or patterns did I find?
   - Which services show abnormal behavior?
   - What's the timeline of events?
   - What evidence is still missing to confirm root cause?
   - Am I looking at a symptom or the actual origin?

3. **Before concluding** → call think_tool to verify your hypothesis:
   - Does the evidence clearly point to a single root cause service?
   - Can I trace the full propagation path from root cause to all affected services?
   - The root cause is the UPSTREAM service that INITIATED the failure, not the downstream service with the most errors.

**NEVER output your final CausalGraph without first calling think_tool to verify your conclusion.**
</Reflection Methodology — MANDATORY>
"""

INCIDENT = """A user has filed a support ticket reporting that their experience
with the service has degraded — requests feel slow or are failing
for them. The on-call team needs you to investigate.

Telemetry parquets are stored in: `.`
Available files: abnormal_metrics.parquet, abnormal_traces.parquet,
abnormal_logs.parquet, abnormal_metrics_histogram.parquet,
abnormal_metrics_sum.parquet, normal_metrics.parquet,
normal_traces.parquet, normal_logs.parquet.

Walk the telemetry to identify which endpoints / services are
actually affected, then determine the root cause(s) of the
degradation.
"""

SYNTHESIS = """You are an RCA synthesizer. Today's date is {date}.
Your job: convert the investigation messages above into a single STRICT JSON object matching the RCA schema. Output JSON only, with no markdown, commentary, or prose.
{agent_contract}
## Filtering investigation messages
- Include: query results showing anomalies, errors, or elevated latency.
- Exclude: think_tool outputs (the agent's own reasoning notes).
"""

SYNTHESIS_USER = """## Incident
{incident}
Synthesize the investigation messages above into ONE JSON object as specified in the system prompt. No prefix, no suffix, no markdown fences, no explanation. Begin output now."""

_EVIDENCE = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["metric", "trace", "log"]},
            "sql": {"type": "string"},
            "claim": {"type": "string"},
        },
        "required": ["kind", "sql", "claim"],
        "additionalProperties": False,
    },
}
# The official answer format (AgentRCAOutput) as a JSON schema, for --json-answer.
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "root_causes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "service": {"type": "string"},
                    "fault_kind": {"type": "string", "enum": sorted(KINDS)},
                    "evidence": _EVIDENCE,
                },
                "required": ["service", "fault_kind", "evidence"],
                "additionalProperties": False,
            },
        },
        "propagation": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "evidence": _EVIDENCE,
                },
                "required": ["from", "to", "evidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["root_causes", "propagation"],
    "additionalProperties": False,
}

BUDGET_SPENT = (
    "Tool-call budget exhausted: the hard cap of 100 calls is reached. Stop now."
)

TABLES = {"type": "array", "items": {"type": "string"}}
TOOLS = [
    ToolSpec(
        "list_tables_in_directory",
        "List telemetry tables in the current incident with metadata.\n\n"
        'Args:\n    directory: Use "." to list the current incident\'s telemetry tables\n\n'
        "Returns:\n    JSON string containing table names and metadata",
        {"type": "object", "properties": {"directory": {"type": "string"}}},
    ),
    ToolSpec(
        "get_schema",
        "Get schema information of a table, or a list of tables.\n\n"
        "Args:\n    parquet_files: Table name or list of table names for batch lookup\n\n"
        "Returns:\n    JSON string containing table metadata — single object if one table, list if multiple",
        {
            "type": "object",
            "properties": {"parquet_files": TABLES},
            "required": ["parquet_files"],
        },
    ),
    ToolSpec(
        "query_parquet_files",
        "Query telemetry tables using SQL syntax for data analysis and exploration.\n\n"
        "Args:\n    parquet_files: Table name(s) returned by list_tables_in_directory\n"
        "    query: SQL query to execute; each table is available under its own name\n"
        "    limit: Maximum number of records to return\n\nReturns:\n    JSON string of query results",
        {
            "type": "object",
            "properties": {
                "parquet_files": TABLES,
                "query": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["parquet_files", "query"],
        },
    ),
    ToolSpec(
        "think_tool",
        "Tool for strategic reflection on research progress and decision-making.\n\n"
        "Use this tool after each search to analyze results and plan next steps systematically.\n"
        "This creates a deliberate pause in the research workflow for quality decision-making.",
        {
            "type": "object",
            "properties": {"reflection": {"type": "string"}},
            "required": ["reflection"],
        },
    ),
]


def agent_contract() -> str:
    text = (PROMPTS / "agent_contract.md").read_text(encoding="utf-8")
    return re.sub(r"^<!--.*?-->\n", "", text, flags=re.S)


class Tools:
    """The four tools on one case, through the locked connection."""

    def __init__(self, case: CaseTelemetry) -> None:
        self.con = case.connect(underscore_columns=True)
        self.views = [name.removesuffix(".parquet") for name in case.tables()]
        self._hide = str(case.path(case.tables()[0]).parent)

    def _limit(self, payload: str) -> str:
        tokens = (len(payload) + 2) // 3
        if tokens <= TOKEN_LIMIT:
            return payload
        return json.dumps(
            {
                "error": "Result exceeds token budget",
                "estimated_tokens": tokens,
                "token_limit": TOKEN_LIMIT,
                "suggestions": [
                    "Reduce the LIMIT value",
                    "Filter rows with WHERE clauses to reduce result size",
                    "Use aggregation (COUNT, SUM, AVG) instead of retrieving raw rows",
                ],
            }
        )

    def _names(self, value: Any) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                try:
                    value = json.loads(value)
                except ValueError:
                    value = [value]
            else:
                value = [value]
        return [
            str(v).strip().strip('"').removesuffix(".parquet") for v in (value or [])
        ]

    def _count(self, view: str) -> int:
        row = self.con.execute(f"SELECT count(*) FROM {view}").fetchone()
        return int(row[0]) if row else 0

    def _error(self, error: Exception) -> str:
        return str(error).replace(self._hide, "").replace("\\", "/")

    def run(self, call: ToolCall) -> str:
        args = call.arguments
        try:
            if call.name == "think_tool":
                return f"Reflection recorded: {args.get('reflection', '')}"
            if call.name == "list_tables_in_directory":
                if args.get("directory", ".") not in (".", "", "tables"):
                    return json.dumps(
                        {"error": "Use directory='.' for the current case"}
                    )
                info = []
                for view in self.views:
                    rows = self._count(view)
                    cols = len(
                        self.con.execute(f"SELECT * FROM {view} LIMIT 0").description
                    )
                    info.append(
                        {"table": view, "row_count": rows, "column_count": cols}
                    )
                return self._limit(json.dumps(info, indent=2))
            if call.name == "get_schema":
                out: list[dict[str, Any]] = []
                for name in self._names(args.get("parquet_files")):
                    if name not in self.views:
                        out.append(
                            {
                                "error": "Use a table name returned by list_tables_in_directory"
                            }
                        )
                        continue
                    described = self.con.execute(
                        f"SELECT column_name, column_type FROM (DESCRIBE {name})"
                    ).fetchall()
                    out.append(
                        {
                            "table": name,
                            "row_count": self._count(name),
                            "columns": [{"name": c, "type": t} for c, t in described],
                        }
                    )
                return self._limit(
                    json.dumps(out[0] if len(out) == 1 else out, indent=2)
                )
            if call.name == "query_parquet_files":
                return self._query(
                    str(args.get("query", "")),
                    args.get("limit", ROW_LIMIT),
                    args.get("parquet_files"),
                )
        except duckdb.Error as error:
            return json.dumps({"error": self._error(error)})
        return json.dumps({"error": f"no tool called {call.name!r}"})

    def _query(self, query: str, limit: Any, tables: Any) -> str:
        # `read_parquet('x.parquet')` and `'x.parquet'` name the view x, as in the official judge.
        for view in self.views:
            query = re.sub(
                rf"read_parquet\(\s*'(?:\./)?{view}\.parquet'\s*\)", view, query
            )
            query = re.sub(rf"'(?:\./)?{view}\.parquet'", view, query)
        try:
            n = max(1, int(limit))
        except (TypeError, ValueError):
            n = ROW_LIMIT
        try:
            cursor = self.con.execute(query)
            columns = [d[0] for d in cursor.description or []]
            rows = [
                dict(zip(columns, row, strict=False)) for row in cursor.fetchmany(n)
            ]
        except duckdb.Error as error:
            message = self._error(error)
            kind = (
                "SQL syntax error in query"
                if "syntax" in message.lower() or "parser" in message.lower()
                else "Table reference error"
                if "catalog" in message.lower() or "table" in message.lower()
                else "Query execution failed"
            )
            return json.dumps(
                {
                    "error": f"{kind}: {message}",
                    "query": query,
                    "available_tables": self._names(tables),
                }
            )
        return self._limit(json.dumps(rows, indent=2, default=str))

    def sql_status(self, sql: str) -> str:
        """OK, EMPTY or SQL_ERROR, as the official judge grades an evidence query."""
        result = self._query(sql, 1, [])
        if result.startswith('{"error"'):
            return "SQL_ERROR"
        return "EMPTY" if result.strip() == "[]" else "OK"


@dataclass
class CaseRun:
    answer: Answer | None
    raw: str
    calls: Counter[str]
    turns: int
    usage: Usage
    seconds: float
    notes: list[str]
    stopped: str  # why the investigation ended
    per_turn: list[tuple[int, int]]  # (prompt, output) tokens of each turn


def investigate(
    conversation: Conversation,
    tools: Tools,
    *,
    agent: Agent | None = None,
    max_calls: int = MAX_CALLS,
    budget: Callable[[float], bool] | None = None,
) -> CaseRun:
    """Run the loop until the model stops calling tools or reaches the cap, then ask for the answer."""
    started = time.monotonic()
    total = Usage()
    calls: Counter[str] = Counter()
    notes: list[str] = []
    turns = 0
    per_turn: list[tuple[int, int]] = []
    stopped = "the model stopped calling tools"

    def add(u: Usage) -> None:
        total.prompt += u.prompt
        total.cache_write += u.cache_write
        total.cache_read += u.cache_read
        total.output += u.output
        total.usd += u.usd

    while True:
        turn = conversation.ask()
        turns += 1
        add(turn.usage)
        per_turn.append((turn.usage.prompt, turn.usage.output))
        notes += turn.notes
        if not turn.calls:
            break
        results = []
        for call in turn.calls:
            if sum(calls.values()) >= max_calls:
                results.append((call, BUDGET_SPENT))
                continue
            calls[call.name] += 1
            results.append((call, tools.run(call)))
        conversation.answer_tools(results)
        if sum(calls.values()) >= max_calls:
            stopped = f"the cap of {max_calls} tool calls"
            break
        if budget is not None and not budget(total.usd):
            stopped = "the spending limit"
            break

    agent = agent or agents()["standard"]
    final = conversation.conclude(
        agent.answer_system, agent.answer_prompt, agent.answer_schema
    )
    turns += 1
    add(final.usage)
    per_turn.append((final.usage.prompt, final.usage.output))
    notes += final.notes
    if final.calls and not final.text.strip():
        # The answer turn offers no tools; a model that calls one anyway gives no answer.
        notes.append("the answer turn called a tool instead of answering")
    raw = final.text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", raw, flags=re.S)
    answer = Answer.from_json(fenced.group(1) if fenced else raw)
    return CaseRun(
        answer,
        raw,
        calls,
        turns,
        total,
        time.monotonic() - started,
        notes,
        stopped,
        per_turn,
    )


def agents() -> dict[str, Agent]:
    """Every agent the runner can run: the standard one, and the design's parts."""
    today = date.today().isoformat()
    standard = Agent(
        "standard",
        INVESTIGATION.format(date=today) + "\n" + REFLECTION,
        lambda case: INCIDENT,
        SYNTHESIS.format(date=today, agent_contract=agent_contract()),
        SYNTHESIS_USER.format(incident=INCIDENT),
        None,
    )
    return {
        "standard": standard,
        **lead_agents(INCIDENT, agent_contract(), ANSWER_SCHEMA),
    }


def within(spent: float, limit: float | None) -> Callable[[float], bool] | None:
    """Whether a case's spending so far keeps the run under its limit."""
    if limit is None:
        return None
    return lambda usd: spent + usd < limit


def sample(split: list[dict[str, str]], n: int, seed: int = SAMPLE_SEED) -> list[str]:
    """`n` development cases, shared among the systems in proportion and drawn within each."""
    dev = [c for c in split if c["split"] == "dev"]
    by_system: dict[str, list[str]] = {}
    for c in dev:
        by_system.setdefault(c["system"], []).append(c["id"])
    shares = {s: round(n * len(ids) / len(dev)) for s, ids in sorted(by_system.items())}
    chosen = []
    for system, ids in sorted(by_system.items()):
        chosen += random.Random(f"{seed}:phase3:{system}").sample(
            sorted(ids), max(1, shares[system])
        )
    return sorted(chosen)


def make_conversation(
    provider: str,
    model: str,
    num_ctx: int,
    binding: str | None = None,
    capture: Path | None = None,
    json_answer: bool = False,
) -> Callable[[str, str, str], Conversation]:
    """A factory taking (system prompt, first message, case ID)."""
    if provider == "claude":
        from flowguard.openrca2.chat_claude import ClaudeConversation

        def claude(system: str, first: str, case_id: str) -> Conversation:
            file = capture / f"{case_id}.jsonl" if capture else None
            return ClaudeConversation(
                model, system, first, TOOLS, binding=binding, capture=file
            )

        return claude
    if provider == "ollama":
        from flowguard.openrca2.chat_ollama import OllamaConversation

        schema = ANSWER_SCHEMA if json_answer else None
        return lambda system, first, case_id: OllamaConversation(
            model, system, first, TOOLS, num_ctx=num_ctx, answer_format=schema
        )
    raise SystemExit(f"unknown provider {provider!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--provider", choices=("claude", "ollama"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sample",
        type=int,
        help="this many development cases, drawn with the fixed seed",
    )
    group.add_argument("--cases", help="development case IDs, comma-separated")
    parser.add_argument("--max-calls", type=int, default=MAX_CALLS)
    parser.add_argument(
        "--max-usd",
        type=float,
        default=None,
        help="stop the run once this much is spent",
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=131072,
        help="context length for a local model (gpt-oss:20b fits 128K on the laptop)",
    )
    parser.add_argument(
        "--thinking-check",
        choices=("error", "drop_block"),
        help="Claude: send the thinking-binding controls and record input_transformations",
    )
    parser.add_argument(
        "--capture",
        type=Path,
        help="Claude: write each request body to <dir>/<case>.jsonl, for prefix_diff.py",
    )
    parser.add_argument(
        "--agent",
        choices=("standard", "lead", "lead+survey"),
        default="standard",
        help="the standard agent, or the design's parts (docs/openrca2-design.md)",
    )
    parser.add_argument(
        "--json-answer",
        action="store_true",
        help="local models: hold the answer turn to the official JSON schema, so it cannot call a tool",
    )
    args = parser.parse_args()
    if args.json_answer and args.provider != "ollama":
        raise SystemExit(
            "--json-answer is for local models; Claude's answer turn already forbids tools"
        )

    split = json.loads((args.root / "split.json").read_text(encoding="utf-8"))["cases"]
    dev_ids = {c["id"] for c in split if c["split"] == "dev"}
    cases = (
        sample(split, args.sample)
        if args.sample
        else [c.strip() for c in args.cases.split(",")]
    )
    if not set(cases) <= dev_ids:
        raise SystemExit("phase 3 runs development cases only")
    if args.provider == "claude" and args.max_usd is None:
        raise SystemExit("a paid run needs --max-usd")
    if args.capture:
        args.capture.mkdir(parents=True, exist_ok=True)
    new = make_conversation(
        args.provider,
        args.model,
        args.num_ctx,
        args.thinking_check,
        args.capture,
        args.json_answer,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    agent = agents()[args.agent]
    # What earlier runs into this folder spent, failed cases included.
    spent = sum(
        json.loads(p.read_text(encoding="utf-8"))["usage"]["usd"]
        for pattern in ("case-*.json", "failed-*.json")
        for p in args.out.glob(pattern)
    )

    for case_id in cases:
        path = args.out / f"{case_id}.json"
        if path.exists():
            print(f"{case_id}: done already")
            continue
        if args.max_usd is not None and spent >= args.max_usd:
            print(f"stopped: ${spent:.2f} spent of ${args.max_usd:.2f}")
            break
        truth = load_truth(args.root / "answers" / "dev", case_id)
        tools = Tools(CaseTelemetry(args.root / "telemetry" / "dev", case_id))
        case = CaseTelemetry(args.root / "telemetry" / "dev", case_id)
        conversation = new(agent.system, agent.first(case), case_id)
        limit = args.max_usd
        try:
            run = investigate(
                conversation,
                tools,
                agent=agent,
                max_calls=args.max_calls,
                budget=within(spent, limit),
            )
        except ModelFailed as error:
            # Recorded, with what it cost, so the spending limit counts it; the case
            # is tried again on the next run, and this file is replaced.
            lost = float(getattr(conversation, "spent", 0.0))
            spent += lost
            failure = {
                "case": case_id,
                "model": f"{args.provider}:{args.model}",
                "error": str(error),
                "usage": {"usd": lost},
                "transcript": conversation.transcript(),
            }
            (args.out / f"failed-{case_id}.json").write_text(
                json.dumps(failure, indent=1, default=str) + NEWLINE,
                encoding="utf-8",
                newline=NEWLINE,
            )
            print(f"{case_id}: the model failed (${lost:.3f} spent): {error}")
            continue
        (args.out / f"failed-{case_id}.json").unlink(missing_ok=True)
        spent += run.usage.usd
        scores = score(run.answer, truth)
        evidence = []
        if run.answer is not None:
            data = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", run.raw))
            for item in data.get("root_causes", []) + data.get("propagation", []):
                evidence += [
                    tools.sql_status(str(e.get("sql", "")))
                    for e in item.get("evidence", [])
                ]
        record = {
            "case": case_id,
            "system": truth.system,
            "model": f"{args.provider}:{args.model}",
            "agent": agent.name,
            "json_answer": args.json_answer,
            "num_ctx": args.num_ctx if args.provider == "ollama" else None,
            "stopped": run.stopped,
            "tool_calls": dict(run.calls),
            "turns": run.turns,
            "per_turn_tokens": run.per_turn,
            "seconds": round(run.seconds, 1),
            "usage": vars(run.usage),
            "notes": sorted(set(run.notes)),
            "answer_valid": run.answer is not None,
            "evidence_sql": dict(Counter(evidence)),
            "scores": scores,
            "answer": run.raw,
            "transcript": conversation.transcript(),
        }
        path.write_text(
            json.dumps(record, indent=1, default=str) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"{case_id} ({truth.system}): {sum(run.calls.values())} calls, {run.turns} turns, "
            f"{run.usage.prompt:,} prompt + {run.usage.output:,} output tokens, ${run.usage.usd:.3f}, "
            f"{run.seconds:.0f} s; acc {scores['acc']:.0f} f1 {scores['f1']:.2f} any-hit {scores['any_hit']:.0f}"
            + (f"; {'; '.join(sorted(set(run.notes)))}" if run.notes else "")
        )

    write_summary(args.out)
    return 0


def write_summary(out: Path) -> None:
    records = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(out.glob("case-*.json"))
    ]
    if not records:
        return
    means = summarise([r["scores"] for r in records])
    lines = [
        f"# Baseline run: {records[0]['model']}, {len(records)} development cases\n"
    ]
    lines.append("| Score | Mean |\n|---|---|")
    lines += [f"| {k} | {v:.3f} |" for k, v in means.items()]
    lines.append(
        "\n| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in records:
        s = r["scores"]
        lines.append(
            f"| {r['case']} | {r['system']} | {sum(r['tool_calls'].values())} | {r['turns']} | {r['usage']['prompt']:,} | "
            f"{r['usage']['output']:,} | {r['usage']['usd']:.3f} | {r['seconds']:.0f} | {s['acc']:.0f} | {s['f1']:.2f} | "
            f"{s['any_hit']:.0f} | {r['stopped']} | {'; '.join(r['notes'])} |"
        )
    usd = sum(r["usage"]["usd"] for r in records)
    lines.append(
        f"\nTotal: ${usd:.2f}, {sum(r['usage']['prompt'] for r in records):,} prompt tokens, "
        f"{sum(r['usage']['output'] for r in records):,} output tokens."
    )
    (out / "summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    sys.exit(main())
