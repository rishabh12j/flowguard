"""The phase 2 signal study, on a small synthetic case."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from flowguard.openrca2 import TELEMETRY_FILES
from flowguard.openrca2.access import CaseTelemetry

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("duckdb")

from flowguard.openrca2.study import rank_of, service_scores  # noqa: E402

T0 = datetime(2026, 5, 1, tzinfo=UTC)


def spans(start: datetime, rows: list[tuple[str, int, str]]) -> dict[str, list]:  # type: ignore[type-arg]
    """One span per row: (service, duration, status), a minute apart over the window."""
    n = len(rows)
    return {
        "time": [start + timedelta(seconds=300 * i / max(n - 1, 1)) for i in range(n)],
        "trace_id": [f"t{i}" for i in range(n)],
        "span_id": [f"s{i}" for i in range(n)],
        "parent_span_id": [""] * n,
        "service_name": [r[0] for r in rows],
        "duration": [r[1] for r in rows],
        "attr.status_code": [r[2] for r in rows],
        "attr.http.response.status_code": [200] * n,
    }


@pytest.fixture
def case(tmp_path: Path) -> CaseTelemetry:
    folder = tmp_path / "dev" / "case-001"
    folder.mkdir(parents=True)
    normal = [(s, 100, "Unset") for s in ("a", "b", "gone") for _ in range(10)]
    abnormal = [("a", 100, "Error")] * 10 + [("b", 400, "Unset")] * 10
    tables = {
        "normal_traces": spans(T0, normal),
        "abnormal_traces": spans(T0 + timedelta(minutes=5), abnormal),
    }
    empty_logs = {"time": pa.array([], pa.timestamp("us", tz="UTC")), "service_name": pa.array([], pa.string()), "level": pa.array([], pa.string())}  # fmt: skip
    empty_metrics = {"time": pa.array([], pa.timestamp("us", tz="UTC")), "service_name": pa.array([], pa.string()), "metric": pa.array([], pa.string()), "value": pa.array([], pa.float64())}  # fmt: skip
    for name in TELEMETRY_FILES:
        view = name.removesuffix(".parquet")
        data = tables.get(view) or (
            empty_logs if view.endswith("logs") else empty_metrics
        )
        pq.write_table(pa.table(data), folder / name)
    return CaseTelemetry(tmp_path / "dev", "case-001")


def test_each_signal_points_at_what_changed(case: CaseTelemetry) -> None:
    scores = service_scores(case.connect())
    assert max(scores["T1"], key=scores["T1"].get) == "a"  # its spans now fail
    assert scores["T2"]["b"] == pytest.approx(4.0)  # four times slower
    assert scores["T4"]["gone"] == 1.0  # no spans at all in the abnormal window
    assert set(scores["_services"]) == {"a", "b", "gone"}


def test_a_tie_counts_against_the_fault() -> None:
    ranking = {"a": 1.0, "b": 1.0, "c": 0.5}
    assert rank_of(frozenset({"a"}), ranking, set(ranking)) == 2
    assert rank_of(frozenset({"c"}), ranking, set(ranking)) == 3
    assert (
        rank_of(frozenset({"d"}), ranking, set(ranking) | {"d"}) == 4
    )  # unscored: after the scored ones
    assert (
        rank_of(frozenset({"x", "c"}), ranking, set(ranking) | {"x"}) == 3
    )  # best-placed name counts
