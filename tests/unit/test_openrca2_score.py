"""The draft OpenRCA 2.0 scorer, on hand-made answers and truths."""

import json
from pathlib import Path

import pytest

from flowguard.openrca2.access import NotAllowed
from flowguard.openrca2.score import Answer, Claim, load_truth, score, summarise


def write_case(
    root: Path,
    split: str,
    case_id: str,
    faults: list[dict],
    edges,
    alarms,
    applicable=True,
) -> Path:  # type: ignore[no-untyped-def]
    folder = root / split / case_id
    folder.mkdir(parents=True)
    label = {
        "case": "x",
        "system": "ts",
        "faults": faults,
        "process_applicable": applicable,
        "service_edges": edges,
    }
    (folder / "label.json").write_text(json.dumps(label), encoding="utf-8")
    graph = {
        "alarm_nodes": [{"component": f"span|{a}::GET /"} for a in alarms],
        "component_to_service": {f"span|{a}::GET /": a for a in alarms},
    }
    (folder / "causal_graph.json").write_text(json.dumps(graph), encoding="utf-8")
    return root / split


def fault(service: str, chaos: str, role: str = "required", **extra) -> dict:  # type: ignore[no-untyped-def]
    return {
        "index": 0,
        "service": service,
        "chaos_type": chaos,
        "role": role,
        "container": [service],
        **extra,
    }


@pytest.fixture
def one_fault(tmp_path: Path):  # type: ignore[no-untyped-def]
    edges = [
        ["ts-station-service", "ts-travel-service"],
        ["ts-travel-service", "ts-ui-dashboard"],
    ]
    root = write_case(
        tmp_path,
        "dev",
        "case-001",
        [fault("ts-station-service", "PodKill")],
        edges,
        ["ts-ui-dashboard"],
    )
    return load_truth(root, "case-001")


def answer(*claims: tuple[str, str], edges=()) -> Answer:  # type: ignore[no-untyped-def]
    return Answer(tuple(Claim(s, k) for s, k in claims), tuple(edges))


def test_a_right_answer_scores_full_marks(one_fault) -> None:  # type: ignore[no-untyped-def]
    path = [
        ("ts-station-service", "ts-travel-service"),
        ("ts-travel-service", "ts-ui-dashboard"),
    ]
    s = score(answer(("ts-station-service", "pod_failure"), edges=path), one_fault)
    assert s == {
        "f1": 1.0, "precision": 1.0, "recall": 1.0, "acc": 1.0, "any_hit": 1.0, "all_hit": 1.0, "type_acc": 1.0,
        "node_f1": 1.0, "edge_f1": 1.0, "path_acc": 1.0, "path_acc_service": 1.0,
    }  # fmt: skip


def test_names_are_compared_without_case_hyphens_or_underscores(one_fault) -> None:  # type: ignore[no-untyped-def]
    assert score(answer(("TS_Station_Service", "pod_failure")), one_fault)["acc"] == 1.0


def test_pod_kinds_count_as_the_same_answer(one_fault) -> None:  # type: ignore[no-untyped-def]
    assert (
        score(answer(("ts-station-service", "pod_unavailable")), one_fault)["acc"]
        == 1.0
    )


def test_a_wrong_kind_keeps_the_service_but_loses_f1_and_acc(one_fault) -> None:  # type: ignore[no-untyped-def]
    s = score(answer(("ts-station-service", "container_cpu_saturated")), one_fault)
    assert (s["f1"], s["acc"], s["any_hit"], s["all_hit"], s["type_acc"]) == (
        0.0,
        0.0,
        1.0,
        1.0,
        0.0,
    )


def test_an_extra_claim_breaks_acc_and_halves_precision(one_fault) -> None:  # type: ignore[no-untyped-def]
    s = score(
        answer(
            ("ts-station-service", "pod_failure"), ("ts-order-service", "pod_failure")
        ),
        one_fault,
    )
    assert (s["precision"], s["recall"], s["acc"]) == (0.5, 1.0, 0.0)


def test_reversed_edges_lose_edge_f1_but_still_reach_the_alarm(one_fault) -> None:  # type: ignore[no-untyped-def]
    path = [
        ("ts-travel-service", "ts-station-service"),
        ("ts-ui-dashboard", "ts-travel-service"),
    ]
    s = score(answer(("ts-station-service", "pod_failure"), edges=path), one_fault)
    assert (s["edge_f1"], s["node_f1"], s["path_acc"]) == (0.0, 1.0, 1.0)


def test_path_acc_needs_a_hit_and_the_service_variant_does_not(one_fault) -> None:  # type: ignore[no-untyped-def]
    path = [("ts-station-service", "ts-ui-dashboard")]
    s = score(answer(("ts-station-service", "network_delay"), edges=path), one_fault)
    assert (s["path_acc"], s["path_acc_service"]) == (0.0, 1.0)


def test_load_generators_are_dropped_from_the_graph(one_fault) -> None:  # type: ignore[no-untyped-def]
    path = [("ts-station-service", "ts-travel-service"), ("ts-travel-service", "ts-ui-dashboard"), ("loadgenerator", "ts-ui-dashboard")]  # fmt: skip
    s = score(answer(("ts-station-service", "pod_failure"), edges=path), one_fault)
    assert s["node_f1"] == 1.0 and s["edge_f1"] == 1.0


def test_an_answer_that_is_not_valid_scores_zero(one_fault) -> None:  # type: ignore[no-untyped-def]
    assert Answer.from_json("not json") is None
    assert (
        Answer.from_json(
            '{"root_causes": [{"service": "a", "fault_kind": "pod_failure", "evidence": []}]}'
        )
        is None
    )
    s = score(None, one_fault)
    assert s["acc"] == 0.0 and s["path_acc"] == 0.0 and s["type_acc"] is None


def test_the_official_format_is_read() -> None:
    text = json.dumps({
        "root_causes": [{"service": "a", "fault_kind": "pod_failure", "evidence": [{"kind": "trace", "sql": "SELECT 1", "claim": "x"}]}],
        "propagation": [{"from": "a", "to": "b", "evidence": []}],
    })  # fmt: skip
    assert Answer.from_json(text) == Answer((Claim("a", "pod_failure"),), (("a", "b"),))


@pytest.fixture
def roles(tmp_path: Path):  # type: ignore[no-untyped-def]
    faults = [
        fault("search", "PodFailure"),
        fault("profile", "CPUStress", role="optional"),
        fault("geo", "JVMRuntimeMutator", role="not_effective"),
    ]
    root = write_case(
        tmp_path, "dev", "case-002", faults, [["search", "frontend"]], ["frontend"]
    )
    return load_truth(root, "case-002")


def test_naming_an_optional_fault_costs_and_gains_nothing(roles) -> None:  # type: ignore[no-untyped-def]
    s = score(
        answer(("search", "pod_unavailable"), ("profile", "container_cpu_saturated")),
        roles,
    )
    assert (s["precision"], s["recall"], s["acc"]) == (1.0, 1.0, 1.0)


def test_naming_only_an_optional_fault_is_not_a_hit(roles) -> None:  # type: ignore[no-untyped-def]
    s = score(answer(("profile", "container_cpu_saturated")), roles)
    assert (s["precision"], s["recall"], s["acc"], s["any_hit"]) == (0.0, 0.0, 0.0, 0.0)


def test_naming_a_not_effective_fault_is_a_wrong_claim(roles) -> None:  # type: ignore[no-untyped-def]
    s = score(
        answer(("search", "pod_unavailable"), ("geo", "wrong_return_value")), roles
    )
    assert (s["precision"], s["acc"]) == (0.5, 0.0)


def test_either_end_of_a_network_link_counts(tmp_path: Path) -> None:
    item = fault(
        "ts-route-service", "NetworkLoss", container=["mysql", "ts-route-service"]
    )
    truth = load_truth(
        write_case(
            tmp_path, "dev", "case-003", [item], [["mysql", "ts-route-service"]], []
        ),
        "case-003",
    )
    assert score(answer(("mysql", "network_partition")), truth)["acc"] == 1.0


def test_also_accept_counts_and_a_callee_otherwise_does_not(tmp_path: Path) -> None:
    item = fault(
        "ts-order-service", "HTTPRequestAbort", also_accept=["ts-payment-service"]
    )
    other = fault("ts-food-service", "HTTPRequestDelay")
    truth = load_truth(
        write_case(tmp_path, "dev", "case-004", [item, other], [["a", "b"]], []),
        "case-004",
    )
    s = score(
        answer(
            ("ts-payment-service", "http_aborted"), ("ts-station-service", "http_slow")
        ),
        truth,
    )
    assert (s["recall"], s["any_hit"], s["all_hit"]) == (0.5, 1.0, 0.0)


def test_two_required_faults_need_two_claims(tmp_path: Path) -> None:
    faults = [fault("search", "PodFailure"), fault("profile", "PodFailure")]
    truth = load_truth(
        write_case(tmp_path, "dev", "case-005", faults, [["search", "frontend"]], []),
        "case-005",
    )
    one = score(answer(("search", "pod_unavailable")), truth)
    both = score(
        answer(("search", "pod_unavailable"), ("profile", "pod_failure")), truth
    )
    assert (one["recall"], one["acc"], one["all_hit"]) == (0.5, 0.0, 0.0)
    assert (both["recall"], both["acc"], both["all_hit"]) == (1.0, 1.0, 1.0)


def test_graph_scores_are_left_out_where_the_case_has_no_edges(tmp_path: Path) -> None:
    truth = load_truth(
        write_case(
            tmp_path,
            "dev",
            "case-006",
            [fault("a", "PodKill")],
            [],
            [],
            applicable=False,
        ),
        "case-006",
    )
    s = score(answer(("a", "pod_failure")), truth)
    assert s["acc"] == 1.0 and s["node_f1"] is None and s["path_acc"] is None
    assert summarise([s, score(None, truth)])["acc"] == 0.5
    assert summarise([s])["node_f1"] != summarise([s])["node_f1"]  # nan: no case counts


def test_held_out_answers_are_refused(tmp_path: Path) -> None:
    root = write_case(tmp_path, "held-out", "case-007", [fault("a", "PodKill")], [], [])
    with pytest.raises(NotAllowed):
        load_truth(root, "case-007")
    assert (
        load_truth(root, "case-007", final_test=True).required[0].kind == "pod_failure"
    )


def test_the_other_end_of_a_link_is_read_from_the_injection(tmp_path: Path) -> None:
    item = fault(
        "search", "NetworkDelay", container=["hotel-reserv-rate", "hotel-reserv-search"]
    )
    root = write_case(tmp_path, "dev", "case-008", [item], [["search", "frontend"]], [])
    leaf = {"app": "search", "chaos_type": "NetworkDelay", "target_service": "rate"}
    (root / "case-008" / "injection.json").write_text(
        json.dumps({"engine_config": [leaf]}), encoding="utf-8"
    )
    truth = load_truth(root, "case-008")
    assert score(answer(("rate", "network_delay")), truth)["acc"] == 1.0
