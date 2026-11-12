"""Working on OpenRCA 2.0 (brief, section 33).

Phase 0 only: check the download, separate the answers, make the split, and
guard what tool code may open. Nothing here reads a case's telemetry or answers.
"""

DATASET = "anon-ops/ops-lite"
COMMIT = "581eba39d0bfd2d397eded6cd7cbe3303255521a"

# The only files an agent or a tool may open, per the dataset's README.
TELEMETRY_FILES = frozenset(
    f"{period}_{table}.parquet"
    for period in ("normal", "abnormal")
    for table in ("traces", "metrics", "metrics_histogram", "metrics_sum", "logs")
)

# The answer key. The README says these must be withheld from the agent.
ANSWER_FILES = frozenset(
    {"env.json", "injection.json", "label.json", "causal_graph.json"}
)
