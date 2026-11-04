from datetime import UTC, datetime

from flowguard.domain.metrics import metric_evidence, within

POINTS = [
    {"timestamp": "2026-08-10T13:50:00Z", "value": 61},
    {"timestamp": "2026-08-10T14:00:00Z", "value": 140},
    {"timestamp": "2026-08-10T14:10:00Z", "value": 590},
]


def series(points=POINTS):
    return metric_evidence(
        series_id="METRIC-1",
        service="order-sync-worker",
        metric="outbound_requests_per_minute",
        unit="requests/min",
        threshold=100,
        points=points,
    )


def test_the_timestamp_is_when_the_metric_first_crossed_its_threshold():
    item = series()

    assert item.timestamp == datetime(2026, 8, 10, 14, tzinfo=UTC)
    assert item.source_type == "metric"
    assert "peaked at 590 requests/min" in item.content
    assert "first went above the threshold at 2026-08-10T14:00:00Z" in item.content


def test_a_metric_below_its_threshold_has_no_timestamp():
    item = series(POINTS[:1])

    assert item.timestamp is None
    assert "stayed below the threshold" in item.content


def test_no_points_is_no_evidence():
    assert series([]) is None


def test_a_shorter_period_is_summarised_again():
    before_the_spike = within(
        series(),
        datetime(2026, 8, 10, 13, tzinfo=UTC),
        datetime(2026, 8, 10, 13, 55, tzinfo=UTC),
    )

    assert before_the_spike.metadata["points"] == POINTS[:1]
    assert before_the_spike.timestamp is None


def test_a_period_with_no_points_is_no_evidence():
    assert (
        within(
            series(),
            datetime(2026, 8, 11, tzinfo=UTC),
            datetime(2026, 8, 12, tzinfo=UTC),
        )
        is None
    )
