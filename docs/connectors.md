# Adding a connector

FlowGuard gets every piece of evidence through three read-only MCP servers. The built-in servers read the synthetic incidents in [`data/`](../data). A **connector** is a server that offers the same tools over a real system, such as Grafana Loki for logs or GitHub for deployments.

This guide is the contract a connector must meet. If you build one, see [CONTRIBUTING.md](../CONTRIBUTING.md) for how to send it.

## How evidence reaches FlowGuard

```
investigation graph
   → McpEvidenceTools            src/flowguard/mcp/evidence_tools.py
   → GuardedClient + ToolGuard   allowed tools, allowed arguments, call limits, timeouts
   → MCP server                  built-in today; your connector here
   → your system                 Loki, Prometheus, GitHub, ...
```

On the way back, FlowGuard checks every result against the `EvidenceItem` model and redacts known secret patterns. A tool that fails, is denied, or returns something invalid is recorded in the investigation's errors, and the investigation carries on with less confidence. A broken connector makes FlowGuard less sure, not wrong.

**What's missing today:** `open_evidence_tools` starts the three built-in servers in-process, so there's no setting yet to point FlowGuard at an external server. That plug-in setting is the first contribution wanted (see [Wanted connectors](#wanted-connectors)). Until it exists, a connector can be developed and tested on its own against the contract below.

## The three servers and their tools

A connector replaces one server, so it must offer the tools that server offers, with the **same names and arguments**. The tool guard refuses any argument a tool's schema doesn't list, and [`permissions.py`](../src/flowguard/mcp/permissions.py) sets each tool's call limit and its **10-second timeout**.

The investigation calls the tools in **bold** today. The rest exist for completeness and for future use.

### Observability: logs, alerts, metrics

| Tool | Arguments | Returns |
|---|---|---|
| **`search_logs`** | `start_time`, `end_time`, optional `service`, `query`, `correlation_id` | `{items, truncated}`: logs in the range, **oldest first**, at most 50. `truncated` is true when more matched. |
| **`search_alerts`** | `start_time`, `end_time`, optional `service` | `{items}`: alerts that fired in the range, oldest first. |
| `get_alert` | `alert_id` | `{items}`: that alert, or nothing. |
| **`get_metrics`** | `service`, `start_time`, `end_time`, optional `metric_names` | `{items}`: one item per metric, summarised over the range. |

### Operations: deployments and past incidents

| Tool | Arguments | Returns |
|---|---|---|
| **`get_deployments`** | `start_time`, `end_time`, optional `service` | `{items, truncated}`: deployments in the range, **newest first**, at most 50. |
| `get_incident` | `incident_id` | `{items}`: that past incident, or nothing. |
| `search_incidents` | `query`, `system`, `top_k` (1 to 10, default 3) | `{items}`: similar past incidents, best first. |

### Knowledge: dependency maps and documents

| Tool | Arguments | Returns |
|---|---|---|
| **`get_dependency_map`** | `service` | `{items}`: every map that contains the service. |
| `get_api_spec` | `service`, optional `version` | `{items}`: the current contract, or the given version. |
| **`search_runbooks`** | `query`, `system`, `top_k` (1 to 10, default 5) | `{items}`: current runbooks, specs, and past incidents, best first. |

Times are ISO 8601 with a time zone. If `end_time` is before `start_time`, a tool must raise an error.

## The evidence format

Every item a tool returns is an `EvidenceItem` ([`domain/evidence.py`](../src/flowguard/domain/evidence.py)):

| Field | Meaning |
|---|---|
| `evidence_id` | Unique, stable, no spaces. Plans cite it, and a rollback targets a deployment's ID, so the same record must always get the same ID. |
| `source_type` | One of `log`, `metric`, `alert`, `runbook`, `api_spec`, `deployment`, `dependency_map`, `historical_incident`. |
| `source_name` | The service the item is about. |
| `timestamp` | When it happened, with a time zone. Required for logs, alerts, and deployments. |
| `title`, `content` | Human-readable text. Keep the system's own wording: the model cites it, and people check it. |
| `metadata` | Structured details. Some keys are required, as listed below. |
| `correlation_id` | Optional. Links log lines from one transaction across services. |

### Metadata the investigation relies on

| Source type | Required | How it's used |
|---|---|---|
| `log` | `level` (`ERROR`, `WARN`, `INFO`, ...) | The earliest `ERROR` is taken as the first failure, and only `ERROR` lines earn confidence. |
| `metric` | `metric`, `unit`, `threshold`, `points` (a list of `{timestamp, value}`) | The item's `timestamp` must be when the metric first went above its threshold, or empty if it never did. Build it with `metric_evidence` in [`domain/metrics.py`](../src/flowguard/domain/metrics.py) so this rule holds. |
| `alert` | none | The `timestamp` is when it fired. |
| `deployment` | none | The `timestamp` is when it was deployed. Its `evidence_id` is what a rollback targets. |
| `dependency_map` | `nodes` (each with a `name`), `edges` (each with `from` and `to`) | An edge from A to B means B depends on A. FlowGuard walks `from` to find what's upstream of a failure. |
| `runbook`, `api_spec`, `historical_incident` | `system`, `version`, `effective_date`, `is_current` | Documents are indexed for search, and superseded versions are never returned. |

Documents work differently from the other sources: they're chunked, embedded, and searched through Qdrant rather than queried live. A Confluence or Notion connector therefore produces `EvidenceItem` documents for [`rag/ingestion.py`](../src/flowguard/rag/ingestion.py) to index.

## Rules every connector must follow

1. **Read-only.** Mark every tool `read_only_hint=True`, and connect with credentials that can only read. FlowGuard's guard refuses write tools anyway, but a connector must not depend on that.
2. **Same contract.** Use the names, arguments, ordering, and result limits above. Answer within 10 seconds. If the backend is slower, narrow the query or return a truncated result.
3. **Nothing found is not an error.** Return an empty list when nothing matched. Raise an MCP `ToolError` with a clear message only for bad input or a backend failure. Never make up items.
4. **No secrets in results.** Never put credentials, tokens, or connection strings in evidence or in error messages. FlowGuard's redaction is a safety net for what slips through, not a filter to rely on.
5. **Credentials from the environment.** Read them from environment variables, document them in [`.env.example`](../.env.example) with the lines commented out, and never commit a value.
6. **Return the system's own data.** Don't summarise or rewrite it, with a model or otherwise. The investigation must be able to cite the original text.

## Testing a connector

- **No live calls in CI.** Test against recorded responses or a local container, such as Loki or Prometheus in Docker, so the tests run without an account or a network.
- **Cover the contract:** time-range filtering, ordering, the 50-item limit with `truncated`, empty results, bad input, and a backend that fails or times out.
- **Follow the built-in tests:** [`test_observability_server.py`](../tests/integration/test_observability_server.py) tests a server through an MCP client, and [`test_mcp_evidence_tools.py`](../tests/integration/test_mcp_evidence_tools.py) tests the guarded path the investigation uses.
- **Validate every item** with `EvidenceItem.model_validate`, and check that redaction leaves ordinary items unchanged.
- **Before claiming accuracy on real incidents,** write their ground truth in the [`data/`](../data) format and run `python -m flowguard.evaluation.investigations --data-dir <your data>`. Report the results together with the set they came from.

## Wanted connectors

| Priority | What | Notes |
|---|---|---|
| 1 | **Plug-in setting** | Settings that replace a built-in server with an external MCP server, by command or URL, such as `FLOWGUARD_OBSERVABILITY_MCP`. Add a shared contract test any connector can run. This touches `open_evidence_tools` and `config.py`, so describe the design in an issue first. |
| 2 | **Logs** | Grafana Loki, Elasticsearch or OpenSearch, AWS CloudWatch Logs, Datadog, Splunk. |
| 2 | **Metrics** | Prometheus, CloudWatch Metrics, Datadog. |
| 2 | **Deployments** | GitHub deployments or releases, Argo CD, Kubernetes rollout history. |
| 3 | **Alerts** | Prometheus Alertmanager, PagerDuty, Opsgenie. |
| 3 | **Dependency map** | An OpenTelemetry service graph from Tempo or Jaeger, or a Backstage catalogue. |
| 3 | **Documents and past incidents** | Markdown in a Git repository, Confluence, Notion, Jira. |

A good first set is **Loki, Prometheus, and GitHub**: all three are free and run locally, so a contributor can build, test, and demo FlowGuard on a real stack without a paid account.
