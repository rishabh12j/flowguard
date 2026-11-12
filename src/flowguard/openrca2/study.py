"""Phase 2 study: how far simple signals point at the faulty service.

Analysis only, on development cases; no agent uses this. The signals, measures
and cut-offs were written in brief.md, section 33 ("Phase 2 plan"), before
anything was measured against an answer.

Run: python -m flowguard.openrca2.study --root data/external/openrca2
     --out reports/openrca2-phase2
"""

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

import duckdb

from flowguard.openrca2.access import CaseTelemetry
from flowguard.openrca2.score import LOADGEN, Truth, load_truth, norm

SIGNALS = ("T1", "T2", "T3", "T4", "L1", "L2", "M1", "B0")
NAMES = {
    "T1": "error share",
    "T2": "latency",
    "T3": "own time",
    "T4": "trace silence",
    "L1": "error logs",
    "L2": "log silence",
    "M1": "loudest metric",
    "B0": "commonest root",
}
# Fixed in the plan before any measurement.
VISIBLE = {"T1": 0.05, "T2": 1.5, "T3": 1.5, "T4": 0.5, "L1": 2.0, "L2": 0.5, "M1": 3.0}
ERROR_LEVELS = "('ERROR', 'WARN', 'WARNING', 'SEVERE', 'FATAL', 'CRITICAL')"
MIN_SPANS = 5  # a latency quantile from fewer spans is not used
MIN_POINTS = 3  # nor a metric's spread from fewer points
# The services users' requests enter by, per the systems' published architecture.
ENTRY = frozenset({"tsuidashboard", "tsgatewayservice", "frontend", "frontendproxy"})

Scores = dict[str, dict[str, float]]  # signal -> service -> score


def _minutes(con: duckdb.DuckDBPyConnection, period: str) -> float:
    for table in ("traces", "logs", "metrics"):
        lo, hi = con.execute(
            f"SELECT epoch(min(time)), epoch(max(time)) FROM {period}_{table}"
        ).fetchone()  # type: ignore[misc]
        if lo is not None and hi is not None and hi > lo:
            return max((hi - lo) / 60, 0.5)
    return 1.0


def _by_service(con: duckdb.DuckDBPyConnection, sql: str) -> dict[str, float]:
    return {
        norm(s): float(v) for s, v in con.execute(sql).fetchall() if s and v is not None
    }


def service_scores(con: duckdb.DuckDBPyConnection) -> Scores:
    """T1 to M1 for every service in a case, from its telemetry alone."""
    minutes = {p: _minutes(con, p) for p in ("normal", "abnormal")}
    per: dict[str, dict[str, dict[str, float]]] = {}
    for p in ("normal", "abnormal"):
        error = '("attr.status_code" = \'Error\' OR coalesce("attr.http.response.status_code", 0) >= 500)'
        per[p] = {
            "spans": _by_service(
                con, f"SELECT service_name, count(*) FROM {p}_traces GROUP BY 1"
            ),
            "errors": _by_service(
                con,
                f"SELECT service_name, avg(CASE WHEN {error} THEN 1 ELSE 0 END) FROM {p}_traces GROUP BY 1",
            ),
            "p95": _by_service(
                con,
                f"SELECT service_name, quantile_cont(duration, 0.95) FROM {p}_traces "
                f"GROUP BY 1 HAVING count(*) >= {MIN_SPANS}",
            ),
            "own95": _by_service(
                con,
                f"""WITH s AS (SELECT trace_id, span_id, parent_span_id, service_name, duration FROM {p}_traces),
                    c AS (SELECT trace_id, parent_span_id AS span_id, sum(duration) AS child FROM s
                          WHERE coalesce(parent_span_id, '') <> '' GROUP BY 1, 2)
                    SELECT s.service_name, quantile_cont(greatest(s.duration - coalesce(c.child, 0), 0), 0.95)
                    FROM s LEFT JOIN c USING (trace_id, span_id)
                    GROUP BY 1 HAVING count(*) >= {MIN_SPANS}""",
            ),
            "lines": _by_service(
                con, f"SELECT service_name, count(*) FROM {p}_logs GROUP BY 1"
            ),
            "error_lines": _by_service(
                con,
                f"SELECT service_name, count(*) FROM {p}_logs WHERE upper(level) IN {ERROR_LEVELS} GROUP BY 1",
            ),
        }

    shift = _by_service(
        con,
        f"""WITH m AS (
              SELECT 'n' AS p, service_name, metric, value FROM normal_metrics
              UNION ALL SELECT 'n', service_name, metric, value FROM normal_metrics_sum
              UNION ALL SELECT 'a', service_name, metric, value FROM abnormal_metrics
              UNION ALL SELECT 'a', service_name, metric, value FROM abnormal_metrics_sum),
            s AS (
              SELECT service_name, metric,
                     avg(value) FILTER (WHERE p = 'n') AS mn, stddev_samp(value) FILTER (WHERE p = 'n') AS sd,
                     count(*) FILTER (WHERE p = 'n') AS nn, avg(value) FILTER (WHERE p = 'a') AS ma
              FROM m WHERE isfinite(value) GROUP BY 1, 2)
            SELECT service_name, max(abs(ma - mn) / greatest(coalesce(sd, 0), 0.01 * abs(mn), 1e-6))
            FROM s WHERE nn >= {MIN_POINTS} AND ma IS NOT NULL GROUP BY 1""",
    )

    n, a = per["normal"], per["abnormal"]
    services = set().union(
        *(d.keys() for side in (n, a) for d in side.values()), shift.keys()
    )
    services -= LOADGEN | {""}
    scores: Scores = {s: {} for s in SIGNALS if s != "B0"}
    for svc in services:
        if svc in a["errors"] or svc in n["errors"]:
            scores["T1"][svc] = a["errors"].get(svc, 0.0) - n["errors"].get(svc, 0.0)
        if svc in a["p95"] and n["p95"].get(svc):
            scores["T2"][svc] = a["p95"][svc] / n["p95"][svc]
        if svc in a["own95"] and n["own95"].get(svc):
            scores["T3"][svc] = a["own95"][svc] / n["own95"][svc]
        if n["spans"].get(svc):
            scores["T4"][svc] = 1 - (a["spans"].get(svc, 0) / minutes["abnormal"]) / (
                n["spans"][svc] / minutes["normal"]
            )
        if svc in a["lines"] or svc in n["lines"]:
            scores["L1"][svc] = (
                a["error_lines"].get(svc, 0) / minutes["abnormal"] + 1
            ) / (n["error_lines"].get(svc, 0) / minutes["normal"] + 1)
        if n["lines"].get(svc):
            scores["L2"][svc] = 1 - (a["lines"].get(svc, 0) / minutes["abnormal"]) / (
                n["lines"][svc] / minutes["normal"]
            )
        if svc in shift:
            scores["M1"][svc] = shift[svc]
    scores["_services"] = dict.fromkeys(services, 0.0)
    return scores


def rank_of(
    names: frozenset[str], ranking: dict[str, float], services: set[str]
) -> int:
    """Pessimistic rank of a fault's best-placed name: services scoring at least as high.

    A service with no score on this signal ranks after every scored one.
    """
    best = len(services) + 1
    for name in names & services:
        if name in ranking:
            mine = ranking[name]
            best = min(best, sum(1 for v in ranking.values() if v >= mine))
        else:
            best = min(best, len(ranking) + 1)
    return best


def study_case(
    con: duckdb.DuckDBPyConnection, truth: Truth, commonest: Counter[str]
) -> dict[str, Any]:
    scores = service_scores(con)
    services = set(scores.pop("_services"))
    scores["B0"] = {s: float(commonest.get(s, 0)) for s in services}
    faults = []
    for fault in truth.faults:
        ranks = {sig: rank_of(fault.names, scores[sig], services) for sig in SIGNALS}
        values = {
            sig: max(
                (scores[sig][n] for n in fault.names if n in scores[sig]), default=None
            )
            for sig in VISIBLE
        }
        visible = {
            sig: v is not None and v >= VISIBLE[sig] for sig, v in values.items()
        }
        faults.append(
            {
                "role": fault.role,
                "kind": fault.kind,
                "service": fault.service,
                "present": bool(fault.names & services),
                "ranks": ranks,
                "values": {
                    k: (round(v, 4) if v is not None and math.isfinite(v) else None)
                    for k, v in values.items()
                },
                "visible": visible,
            }
        )
    top = {
        sig: sorted(scores[sig], key=lambda s: -scores[sig][s])[:5] for sig in SIGNALS
    }
    # Added after the first run, to read the measures above against: the same
    # measures for services named by no fault of the case.
    named = frozenset().union(*(f.names for f in truth.faults))
    others = sorted(services - named)
    telemetry = [sig for sig in SIGNALS if sig != "B0"]
    best = [
        min(rank_of(frozenset({s}), scores[sig], services) for sig in telemetry)
        for s in others
    ]
    background = {
        "services": len(others),
        "visible": {
            sig: sum(scores[sig].get(s, -math.inf) >= cut for s in others) / len(others)
            for sig, cut in VISIBLE.items()
        },
        "visible_any": sum(
            any(scores[sig].get(s, -math.inf) >= cut for sig, cut in VISIBLE.items())
            for s in others
        )
        / len(others),
        "some_top1": sum(b <= 1 for b in best) / len(others),
        "some_top3": sum(b <= 3 for b in best) / len(others),
    }
    # Also added after the first run: where each signal's first service sits.
    required = frozenset().union(*(f.names for f in truth.required))
    path = {s for edge in truth.edges for s in edge}
    first = {}
    for sig in telemetry:
        pick = top[sig][0] if top[sig] else None
        first[sig] = (
            None
            if pick is None
            else "required fault"
            if pick in required
            else "other fault"
            if pick in named
            else "entry service"
            if pick in ENTRY
            else "on the true path"
            if pick in path
            else "elsewhere"
        )
    return {
        "case": truth.case_id,
        "system": truth.system,
        "services": len(services),
        "faults": faults,
        "background": background,
        "first": first,
        "top5": top,
    }


def _pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.0f}%" if whole else "-"


def report(results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    systems = ("ts", "hs", "otel-demo")
    groups = {s: [r for r in results if r["system"] == s] for s in systems} | {
        "all": results
    }

    def required(r: dict[str, Any]) -> list[dict[str, Any]]:
        return [f for f in r["faults"] if f["role"] == "required"]

    def best(r: dict[str, Any], sig: str) -> int:
        return min(f["ranks"][sig] for f in required(r))

    lines.append("## Services per case\n")
    lines.append("| System | Cases | Services, median [min, max] |\n|---|---|---|")
    for g, rs in groups.items():
        n = [r["services"] for r in rs]
        lines.append(f"| {g} | {len(rs)} | {median(n):.0f} [{min(n)}, {max(n)}] |")

    lines.append(
        "\n## Top 1 and top 3: a required fault's service ranked first, or in the first three\n"
    )
    lines.append(
        "| Signal | "
        + " | ".join(f"{g} top 1 | {g} top 3" for g in groups)
        + " | all: median rank |"
    )
    lines.append("|---|" + "---|---|" * len(groups) + "---|")
    for sig in SIGNALS:
        cells = []
        for rs in groups.values():
            cells.append(_pct(sum(best(r, sig) == 1 for r in rs), len(rs)))
            cells.append(_pct(sum(best(r, sig) <= 3 for r in rs), len(rs)))
        med = median(best(r, sig) for r in results)
        lines.append(f"| {sig} {NAMES[sig]} | " + " | ".join(cells) + f" | {med:.0f} |")
    for k in (1, 3):
        cells = []
        for rs in groups.values():
            hit = sum(
                any(best(r, sig) <= k for sig in SIGNALS if sig != "B0") for r in rs
            )
            cells.append(_pct(hit, len(rs)))
        lines.append(
            f"\nSome telemetry signal (T1 to M1) puts it in the first {k}: "
            + ", ".join(f"{g} {c}" for g, c in zip(groups, cells, strict=True))
        )

    lines.append(
        "\n## By kind of fault: required faults whose service is in a signal's first three\n"
    )
    kinds = Counter(f["kind"] for r in results for f in required(r))
    lines.append("| Kind | Faults | " + " | ".join(SIGNALS) + " | Visible on any |")
    lines.append("|---|---|" + "---|" * (len(SIGNALS) + 1))
    for kind, count in sorted(kinds.items(), key=lambda x: (-x[1], x[0])):
        fs = [f for r in results for f in required(r) if f["kind"] == kind]
        cells = [_pct(sum(f["ranks"][sig] <= 3 for f in fs), count) for sig in SIGNALS]
        vis = _pct(sum(any(f["visible"].values()) for f in fs), count)
        lines.append(f"| {kind} | {count} | " + " | ".join(cells) + f" | {vis} |")

    lines.append("\n## Visibility: share of faults past a signal's cut-off, by role\n")
    lines.append("| System | Role | Faults | " + " | ".join(VISIBLE) + " | Any |")
    lines.append("|---|---|---|" + "---|" * (len(VISIBLE) + 1))
    for g, rs in groups.items():
        for role in ("required", "optional", "not_effective"):
            fs = [f for r in rs for f in r["faults"] if f["role"] == role]
            if not fs:
                continue
            cells = [
                _pct(sum(f["visible"][sig] for f in fs), len(fs)) for sig in VISIBLE
            ]
            lines.append(
                f"| {g} | {role} | {len(fs)} | "
                + " | ".join(cells)
                + f" | {_pct(sum(any(f['visible'].values()) for f in fs), len(fs))} |"
            )
    all_vis = [
        r for r in results if all(any(f["visible"].values()) for f in required(r))
    ]
    lines.append(
        f"\nCases with every required fault visible on some signal: {len(all_vis)} of {len(results)}."
    )

    telemetry = [sig for sig in SIGNALS if sig != "B0"]
    lines.append(
        "\n## Some telemetry signal ranks the fault's service first, or in its first three, by role"
        " (added after the first run)\n"
    )
    lines.append("| System | Role | Faults | First | First 3 |\n|---|---|---|---|---|")
    for g, rs in groups.items():
        for role in ("required", "optional", "not_effective"):
            fs = [f for r in rs for f in r["faults"] if f["role"] == role]
            if fs:
                b = [min(f["ranks"][s] for s in telemetry) for f in fs]
                lines.append(
                    f"| {g} | {role} | {len(fs)} | {_pct(sum(x <= 1 for x in b), len(fs))} | "
                    f"{_pct(sum(x <= 3 for x in b), len(fs))} |"
                )

    places = (
        "required fault",
        "other fault",
        "entry service",
        "on the true path",
        "elsewhere",
    )
    lines.append(
        "\n## Where each signal's first service sits (added after the first run)\n"
    )
    lines.append("| System | Signal | Cases | " + " | ".join(places) + " |")
    lines.append("|---|---|---|" + "---|" * len(places))
    for g in systems:
        for sig in telemetry:
            picks = Counter(r["first"][sig] for r in groups[g] if r["first"][sig])
            cases = sum(picks.values())
            lines.append(
                f"| {g} | {sig} | {cases} | "
                + " | ".join(str(picks[p]) for p in places)
                + " |"
            )

    lines.append(
        "\n## Against services with no fault (added after the first run)\n\n"
        "The same cut-offs and ranks for the services that no fault of the case names, "
        "averaged over services and then over cases.\n"
    )
    lines.append(
        "| System | "
        + " | ".join(VISIBLE)
        + " | Any | Some signal's first | Some signal's first 3 |"
    )
    lines.append("|---|" + "---|" * (len(VISIBLE) + 3))
    for g, rs in groups.items():
        bg = [r["background"] for r in rs]
        cells = [f"{100 * mean(b['visible'][sig] for b in bg):.0f}%" for sig in VISIBLE]
        cells += [
            f"{100 * mean(b[k] for b in bg):.0f}%"
            for k in ("visible_any", "some_top1", "some_top3")
        ]
        lines.append(f"| {g} | " + " | ".join(cells) + " |")

    multi = [r for r in results if len(required(r)) > 1]
    lines.append(f"\n## Cases with more than one required fault ({len(multi)})\n")
    for r in multi:
        ranks = "; ".join(
            f"{f['kind']}: best rank {min(f['ranks'][s] for s in SIGNALS if s != 'B0')}"
            for f in required(r)
        )
        lines.append(
            f"- {r['case']} ({r['system']}, {r['services']} services): {ranks}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    split = json.loads((args.root / "split.json").read_text(encoding="utf-8"))["cases"]
    dev = sorted(c["id"] for c in split if c["split"] == "dev")
    truths = {case: load_truth(args.root / "answers" / "dev", case) for case in dev}

    roots: dict[str, Counter[str]] = defaultdict(Counter)  # system -> service -> cases
    for t in truths.values():
        roots[t.system].update({norm(f.service) for f in t.required})
    results = []
    for case in dev:
        truth = truths[case]
        others = roots[truth.system] - Counter(
            {norm(f.service) for f in truth.required}
        )
        con = CaseTelemetry(args.root / "telemetry" / "dev", case).connect()
        results.append(study_case(con, truth, others))
        con.close()

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "cases.json").write_text(
        json.dumps(results, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    text = report(results)
    (args.out / "summary.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
