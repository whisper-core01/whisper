from next_hop_degradation_policy_v01 import (
    build_degradation_table,
    deterministic_unit_interval,
    effective_degradation,
    mean_degradation_risk_per_path,
    path_degradation_risk,
    path_degradation_safety,
    path_health_component,
    score_degradation_aware_candidate,
    select_degradation_aware_paths,
    synthetic_behavioral_signal,
)


def test_deterministic_unit_interval_bounds_and_determinism():
    a = deterministic_unit_interval("seed", "a", "b", "timeout")
    b = deterministic_unit_interval("seed", "a", "b", "timeout")

    assert a == b
    assert 0.0 <= a <= 1.0


def test_synthetic_behavioral_signal_bounds_and_relation_scope():
    ab = synthetic_behavioral_signal("a", "b", "seed")
    ba = synthetic_behavioral_signal("b", "a", "seed")

    assert 0.0 <= ab <= 1.0
    assert 0.0 <= ba <= 1.0
    assert ab != ba


def test_effective_degradation_bounds():
    value = effective_degradation(
        observer="a",
        next_hop="b",
        node_scores={"b": 5.0},
        seed="seed",
    )

    assert 0.0 <= value <= 1.0


def test_build_degradation_table_uses_directed_relations():
    candidates = [
        ["a", "b", "c"],
        ["c", "b", "a"],
    ]

    table = build_degradation_table(
        candidates=candidates,
        node_scores={},
        seed="seed",
    )

    assert ("a", "b") in table
    assert ("b", "c") in table
    assert ("c", "b") in table
    assert ("b", "a") in table
    assert ("a", "c") not in table


def test_path_degradation_risk_uses_edges_not_nodes():
    table = {
        ("a", "b"): 1.0,
        ("b", "c"): 0.0,
    }

    assert path_degradation_risk(["a", "b", "c"], table) == 0.5


def test_path_degradation_risk_missing_relation_defaults_zero():
    assert path_degradation_risk(["a", "b"], {}) == 0.0
    assert path_degradation_safety(["a", "b"], {}) == 1.0


def test_path_health_component_bounds():
    table = {
        ("a", "b"): 1.0,
        ("b", "c"): 0.0,
    }

    value = path_health_component(
        path=["a", "b", "c"],
        node_scores={"a": 0.0, "b": 5.0, "c": 0.0},
        degradation_table=table,
    )

    assert 0.0 <= value <= 1.0


def test_score_degradation_aware_candidate_bounds():
    score = score_degradation_aware_candidate(
        candidate_path=["a", "b", "c"],
        candidate_state="f" * 64,
        selected_paths=[],
        selected_states=[],
        pre_alarm_paths=[["a", "d", "c"]],
        node_scores={"a": 0.0, "b": 2.0, "c": 0.0},
        degradation_table={("a", "b"): 0.5, ("b", "c"): 0.0},
        delta=0.90,
    )

    assert 0.0 <= score <= 1.0


def test_score_degradation_aware_candidate_rejects_bad_delta():
    try:
        score_degradation_aware_candidate(
            candidate_path=["a", "b"],
            candidate_state="f" * 64,
            selected_paths=[],
            selected_states=[],
            pre_alarm_paths=[],
            node_scores={},
            degradation_table={},
            delta=2.0,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid delta")


def test_select_degradation_aware_paths_shape():
    candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
    ]

    result = select_degradation_aware_paths(
        candidates=candidates,
        route_count=2,
        seed="seed",
        pre_alarm_paths=[["a", "b", "c"]],
        node_scores={"a": 0.0, "b": 5.0, "c": 0.0, "d": 0.0, "e": 0.0},
        delta=0.90,
        fractal_id=36,
    )

    assert result["policy"] == "degradation_aware_lemonade_reset"
    assert result["delta"] == 0.90
    assert len(result["selected_paths"]) == 2
    assert len(result["selected_states"]) == 2
    assert len(result["scores"]) == 2
    assert result["results"]["path_count"] == 2
    assert result["degradation_table"]


def test_mean_degradation_risk_per_path_bounds():
    paths = [["a", "b"], ["b", "c"]]
    table = {("a", "b"): 1.0, ("b", "c"): 0.0}

    value = mean_degradation_risk_per_path(paths, table)

    assert 0.0 <= value <= 1.0
    assert value == 0.5
