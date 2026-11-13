"""The survey: what code can say about a case before any agent reads it.

Part 2 of the design (docs/openrca2-design.md). It is a hint for the agents,
never a limit on their answer: it ranks nothing out and filters nothing. It reads
only the case's ten tables, through the locked connection, and takes well under
a second for most cases.

It covers:

- every service: request rate, error share, p95 latency and own time, log errors,
  its largest metric shift and which metric it was, restarts, and when in the
  abnormal window its first deviation showed;
- the calls between services, from parent and child spans, with how each changed;
- the entry services, where users' requests arrive;
- per-connection network traffic where the case records it (`hubble_*` metrics);
  where it does not, the survey says so.
"""

import math
import re
from typing import Any

import duckdb

from flowguard.openrca2.score import LOADGEN, norm

ERROR = '("attr.status_code" = \'Error\' OR coalesce("attr.http.response.status_code", 0) >= 500)'
ERROR_LEVELS = "('ERROR', 'WARN', 'WARNING', 'SEVERE', 'FATAL', 'CRITICAL')"
MAX_CALLS = 30
MAX_CONNECTIONS = 15
POD_SUFFIX = re.compile(r"(-[a-z0-9]{6,10})?-[a-z0-9]{4,5}$|-\d+$")


def pod_service(pod: str | None) -> str:
    """`ts2/ts-price-service-6b784db86c-68ks4` -> `ts-price-service`; `ts2/mysql-0` -> `mysql`."""
    if not pod:
        return ""
    return POD_SUFFIX.sub("", pod.split("/")[-1])


def _minutes(con: duckdb.DuckDBPyConnection, period: str) -> float:
    for table in ("traces", "logs", "metrics"):
        row = con.execute(
            f"SELECT epoch(min(time)), epoch(max(time)) FROM {period}_{table}"
        ).fetchone()
        if row and row[0] is not None and row[1] is not None and row[1] > row[0]:
            return max((row[1] - row[0]) / 60, 0.5)
    return 1.0


def _rows(
    con: duckdb.DuckDBPyConnection, sql: str, params: list[Any] | None = None
) -> list[tuple[Any, ...]]:
    return con.execute(sql, params or []).fetchall()


def _num(value: float | None, digits: int = 1) -> str:
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return "-"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:.{digits}f}"


def _pair(normal: float | None, abnormal: float | None, digits: int = 1) -> str:
    return f"{_num(normal, digits)} → {_num(abnormal, digits)}"


def services(con: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    """One row per service, with normal and abnormal values side by side."""
    minutes = {p: _minutes(con, p) for p in ("normal", "abnormal")}
    found: dict[str, dict[str, Any]] = {}

    def row(name: str) -> dict[str, Any]:
        return found.setdefault(name, {"service": name})

    for p in ("normal", "abnormal"):
        for name, n, err, p95 in _rows(
            con,
            f"SELECT service_name, count(*), avg(CASE WHEN {ERROR} THEN 1 ELSE 0 END), "
            f"quantile_cont(duration, 0.95) / 1e6 FROM {p}_traces GROUP BY 1",
        ):
            if name:
                r = row(name)
                r[f"{p}_rate"] = n / minutes[p]
                r[f"{p}_errors"] = err
                r[f"{p}_p95"] = p95
        for name, own in _rows(
            con,
            f"""WITH s AS (SELECT trace_id, span_id, parent_span_id, service_name, duration FROM {p}_traces),
                c AS (SELECT trace_id, parent_span_id AS span_id, sum(duration) AS child FROM s
                      WHERE coalesce(parent_span_id, '') <> '' GROUP BY 1, 2)
                SELECT s.service_name, quantile_cont(greatest(s.duration - coalesce(c.child, 0), 0), 0.95) / 1e6
                FROM s LEFT JOIN c USING (trace_id, span_id) GROUP BY 1""",
        ):
            if name:
                row(name)[f"{p}_own"] = own
        for name, total, bad in _rows(
            con,
            f"SELECT service_name, count(*), count(*) FILTER (WHERE upper(level) IN {ERROR_LEVELS}) FROM {p}_logs GROUP BY 1",
        ):
            if name:
                r = row(name)
                r[f"{p}_logs"] = total / minutes[p]
                r[f"{p}_log_errors"] = bad / minutes[p]

    for name, metric, z in _rows(
        con,
        """WITH m AS (
              SELECT 'n' AS p, service_name, metric, value FROM normal_metrics
              UNION ALL SELECT 'n', service_name, metric, value FROM normal_metrics_sum
              UNION ALL SELECT 'a', service_name, metric, value FROM abnormal_metrics
              UNION ALL SELECT 'a', service_name, metric, value FROM abnormal_metrics_sum),
            s AS (
              SELECT service_name, metric,
                     abs(avg(value) FILTER (WHERE p = 'a') - avg(value) FILTER (WHERE p = 'n'))
                     / greatest(coalesce(stddev_samp(value) FILTER (WHERE p = 'n'), 0),
                                0.01 * abs(avg(value) FILTER (WHERE p = 'n')), 1e-6) AS z,
                     count(*) FILTER (WHERE p = 'n') AS nn
              FROM m WHERE isfinite(value) AND metric NOT LIKE 'hubble%' GROUP BY 1, 2)
            SELECT service_name, arg_max(metric, z), max(z) FROM s WHERE nn >= 3 AND z IS NOT NULL GROUP BY 1""",
    ):
        if name:
            r = row(name)
            r["metric"], r["metric_z"] = metric, z

    for name, before, after in _rows(
        con,
        """SELECT service_name,
                  max(value) FILTER (WHERE p = 'n'), max(value) FILTER (WHERE p = 'a')
           FROM (SELECT 'n' AS p, service_name, value FROM normal_metrics WHERE metric = 'k8s.container.restarts'
                 UNION ALL SELECT 'a', service_name, value FROM abnormal_metrics WHERE metric = 'k8s.container.restarts')
           GROUP BY 1""",
    ):
        if name and before is not None and after is not None and after > before:
            row(name)["restarts"] = after - before
    for name, new_pods in _rows(
        con,
        """SELECT service_name, count(DISTINCT pod) FROM (
             SELECT service_name, "attr.k8s.pod.name" AS pod FROM abnormal_traces
             UNION SELECT service_name, "attr.k8s.pod.name" FROM abnormal_metrics) a
           WHERE pod IS NOT NULL AND pod NOT IN (
             SELECT "attr.k8s.pod.name" FROM normal_traces WHERE "attr.k8s.pod.name" IS NOT NULL
             UNION SELECT "attr.k8s.pod.name" FROM normal_metrics WHERE "attr.k8s.pod.name" IS NOT NULL)
           GROUP BY 1""",
    ):
        if name:
            row(name)["new_pods"] = new_pods

    _onsets(con, found)
    return [r for name, r in sorted(found.items()) if norm(name) not in LOADGEN]


def _onsets(con: duckdb.DuckDBPyConnection, found: dict[str, dict[str, Any]]) -> None:
    """Seconds into the abnormal window of each service's first minute outside its normal range."""
    start = con.execute("SELECT epoch(min(time)) FROM abnormal_traces").fetchone()
    if not start or start[0] is None:
        return
    normal = {
        name: (lo_n, hi_err, hi_p95)
        for name, lo_n, hi_err, hi_p95 in _rows(
            con,
            f"""SELECT service_name, min(n), max(err), max(p95) FROM (
                  SELECT service_name, date_trunc('minute', time) AS m, count(*) AS n,
                         avg(CASE WHEN {ERROR} THEN 1 ELSE 0 END) AS err, quantile_cont(duration, 0.95) AS p95
                  FROM normal_traces GROUP BY 1, 2) GROUP BY 1""",
        )
    }
    minutes = _rows(
        con,
        f"""SELECT service_name, epoch(min(time)), count(*), avg(CASE WHEN {ERROR} THEN 1 ELSE 0 END),
                   quantile_cont(duration, 0.95)
            FROM abnormal_traces GROUP BY service_name, date_trunc('minute', time) ORDER BY 2""",
    )
    for name, at, n, err, p95 in minutes:
        if name not in normal or name not in found or "onset" in found[name]:
            continue
        lo_n, hi_err, hi_p95 = normal[name]
        if (
            err > hi_err + 0.05
            or (hi_p95 and p95 > 1.5 * hi_p95)
            or (lo_n and n < 0.5 * lo_n)
        ):
            found[name]["onset"] = max(0.0, at - start[0])


def calls(con: duckdb.DuckDBPyConnection) -> list[tuple[Any, ...]]:
    """Calls between services: (caller, callee, rate n, rate a, callee errors n, a, callee p95 n, a)."""
    minutes = {p: _minutes(con, p) for p in ("normal", "abnormal")}
    out: dict[tuple[str, str], list[Any]] = {}
    for p, i in (("normal", 0), ("abnormal", 1)):
        for caller, callee, n, err, p95 in _rows(
            con,
            f"""SELECT parent.service_name, child.service_name, count(*),
                       avg(CASE WHEN {ERROR.replace('"attr.', 'child."attr.')} THEN 1 ELSE 0 END),
                       quantile_cont(child.duration, 0.95) / 1e6
                FROM {p}_traces child JOIN {p}_traces parent
                  ON child.trace_id = parent.trace_id AND child.parent_span_id = parent.span_id
                WHERE child.service_name <> parent.service_name
                GROUP BY 1, 2""",
        ):
            if norm(caller) in LOADGEN:
                continue
            values = out.setdefault((caller, callee), [None] * 6)
            values[i] = n / minutes[p]
            values[2 + i] = err
            values[4 + i] = p95
    return [(a, b, *v) for (a, b), v in out.items()]


def entries(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Where users' requests arrive.

    The services taking at least 5% of a load generator's calls; where no load
    generator appears in the traces, the services starting at least 25% of the
    traces. Internal jobs also start traces, so a service starting a few is not
    an entry.
    """
    loadgen = "lower(replace(replace(parent.service_name, '-', ''), '_', '')) IN ('loadgenerator', 'locust', 'wrk2', 'dsbwrk2', 'k6')"
    called = _rows(
        con,
        f"""SELECT child.service_name, count(*) FROM normal_traces child
            JOIN normal_traces parent ON child.trace_id = parent.trace_id AND child.parent_span_id = parent.span_id
            WHERE {loadgen} GROUP BY 1""",
    )
    rows = [(s, n) for s, n in called if s and norm(s) not in LOADGEN]
    if not rows:
        roots = _rows(
            con,
            """SELECT child.service_name, count(*) FROM normal_traces child
               LEFT JOIN normal_traces parent ON child.trace_id = parent.trace_id AND child.parent_span_id = parent.span_id
               WHERE coalesce(child.parent_span_id, '') = '' OR parent.span_id IS NULL GROUP BY 1""",
        )
        rows = [(s, n) for s, n in roots if s and norm(s) not in LOADGEN]
        share = 0.25
    else:
        share = 0.05
    total = sum(n for _, n in rows) or 1
    return sorted(s for s, n in rows if n / total >= share)


def connections(
    con: duckdb.DuckDBPyConnection,
) -> list[tuple[str, str, float | None, float | None, float, float]] | None:
    """Per-connection traffic, by service pair: (source, destination, flows n, flows a, drops n, drops a).

    None when the case records no per-connection metrics.
    """
    rows = _rows(
        con,
        """SELECT p, metric, "attr.source", "attr.destination", avg(value) FROM (
             SELECT 'n' AS p, * FROM normal_metrics_sum UNION ALL SELECT 'a', * FROM abnormal_metrics_sum)
           WHERE metric IN ('hubble_flows_processed_total', 'hubble_drop_total')
             AND "attr.source" IS NOT NULL AND "attr.destination" IS NOT NULL
           GROUP BY 1, 2, 3, 4""",
    )
    if not rows:
        return None
    pairs: dict[tuple[str, str], dict[str, float]] = {}
    for p, metric, src, dst, value in rows:
        a, b = pod_service(src), pod_service(dst)
        if (
            not a
            or not b
            or a == b
            or norm(a) in LOADGEN
            or norm(b) in LOADGEN
            or "/" in a
        ):
            continue
        key = (
            ("flows" if metric == "hubble_flows_processed_total" else "drops") + "_" + p
        )
        pairs.setdefault((a, b), {})
        pairs[(a, b)][key] = pairs[(a, b)].get(key, 0.0) + (value or 0.0)
    return [
        (
            a,
            b,
            v.get("flows_n"),
            v.get("flows_a"),
            v.get("drops_n", 0.0),
            v.get("drops_a", 0.0),
        )
        for (a, b), v in pairs.items()
    ]


def _change(normal: float | None, abnormal: float | None) -> float:
    """How far a value moved, as the size of its log ratio; a value that appears or vanishes counts as large."""
    if not normal and not abnormal:
        return 0.0
    if not normal or not abnormal:
        return 5.0
    return abs(math.log(abnormal / normal))


def survey(con: duckdb.DuckDBPyConnection) -> str:
    """The survey as text for the agents."""
    lines = [
        "## Survey of this case, computed by code",
        "",
        "A starting point, not the answer: it ranks nothing out. Check what it shows, and look beyond it.",
        "Pairs are normal → abnormal. Rates are per minute; latencies are p95 in milliseconds; "
        "`own` is a span's time minus its children's; `metric` is the service's largest shift in "
        "normal-period standard deviations; `onset` is seconds into the abnormal window of the first minute "
        "outside the service's normal range.",
        "",
        "### Services",
        "",
        "| Service | Spans/min | Error share | p95 ms | Own p95 ms | Log errors/min | Largest metric shift | Restarts | New pods | Onset s |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in services(con):
        metric = f"{r['metric']} ({_num(r['metric_z'])})" if r.get("metric") else "-"
        lines.append(
            f"| {r['service']} | {_pair(r.get('normal_rate'), r.get('abnormal_rate'))} "
            f"| {_pair(r.get('normal_errors'), r.get('abnormal_errors'), 2)} "
            f"| {_pair(r.get('normal_p95'), r.get('abnormal_p95'))} "
            f"| {_pair(r.get('normal_own'), r.get('abnormal_own'))} "
            f"| {_pair(r.get('normal_log_errors'), r.get('abnormal_log_errors'))} "
            f"| {metric} | {_num(r.get('restarts'), 0) if r.get('restarts') else '-'} "
            f"| {r.get('new_pods') or '-'} | {_num(r.get('onset'), 0) if r.get('onset') is not None else '-'} |"
        )

    lines += [
        "",
        f"### Entry services (requests arrive here): {', '.join(entries(con)) or 'none found'}",
        "",
    ]

    found = calls(con)

    def moved(c: tuple[Any, ...]) -> float:
        return max(
            _change(c[2], c[3]), 5 * abs((c[5] or 0) - (c[4] or 0)), _change(c[6], c[7])
        )

    shown = sorted(found, key=moved, reverse=True)[:MAX_CALLS]
    lines += [
        f"### Calls between services, the {len(shown)} that changed most of {len(found)}",
        "",
        "| Caller | Callee | Calls/min | Callee error share | Callee p95 ms |",
        "|---|---|---|---|---|",
    ]
    lines += [
        f"| {c[0]} | {c[1]} | {_pair(c[2], c[3])} | {_pair(c[4], c[5], 2)} | {_pair(c[6], c[7])} |"
        for c in shown
    ]

    pairs = connections(con)
    lines += [
        "",
        "### Network connections (hubble metrics, by pod pair mapped to services)",
        "",
    ]
    if pairs is None:
        lines.append("Per-connection network metrics are not recorded in this case.")
    else:
        shown_pairs = sorted(
            pairs,
            key=lambda p: max(_change(p[2], p[3]), _change(p[4], p[5])),
            reverse=True,
        )
        lines += [
            f"The {min(len(pairs), MAX_CONNECTIONS)} that changed most of {len(pairs)}.",
            "",
            "| Source | Destination | Flows | Drops |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| {p[0]} | {p[1]} | {_pair(p[2], p[3])} | {_pair(p[4], p[5])} |"
            for p in shown_pairs[:MAX_CONNECTIONS]
        ]
    return "\n".join(lines) + "\n"
