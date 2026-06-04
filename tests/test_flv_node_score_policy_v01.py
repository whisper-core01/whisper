from flv_node_score_policy_v01 import (
    generate_synthetic_flv_scores,
    healthy_node_ratio,
    mean_node_score_risk_per_path,
    node_score_risk,
    path_node_score_risk,
    score_node_score_aware_candidate,
    select_node_score_aware_paths,
)


def test_node_score_risk_bands():
    assert node_score_risk(-1.0) == 1.0
    assert node_score_risk(-0.5) == 0.5
    assert node_score_risk(0.0) == 0.0
    assert node_score_risk(0.5) == 0.0
    assert node_score_risk(1.0) == 0.0
    assert node_score_risk(3.0) == 0.5
    assert node_score_risk(5.0) == 1.0


def test_node_score_risk_clamps():
    assert node_score_risk(-5.0) == 1.0
    assert node_score_risk(50.0) == 1.0


def test_generate_synthetic_flv_scores_deterministic():
    nodes = ["a", "b", "c"]
    selected = [
        [["a", "b"]],
        [["a", "c"]],
    ]

    x = generate_synthetic_flv_scores(nodes, selected)
    y = generate_synthetic_flv_scores(nodes, selected)

    assert x == y


def test_generate_synthetic_flv_scores_expected_values():
    nodes = ["a", "b", "c"]
    selected = [
        [["a", "b"]],
        [["a", "c"]],
    ]

    scores = generate_synthetic_flv_scores(nodes, selected)

    assert scores["a"] == 1.0
    assert scores["b"] == 0.4
    assert scores["c"] == 0.4


def test_path_node_score_risk_bounds():
    scores = {"a": 0.0, "b": 3.0, "c": -0.5}
    path = ["a", "b", "c"]

    value = path_node_score_risk(path, scores)

    assert 0.0 <= value <= 1.0


def test_score_node_score_aware_candidate_bounds():
    candidate_path = ["a", "b", "c"]
    candidate_state = "f" * 64
    selected_paths = [["a", "d", "c"]]
    selected_states = ["0" * 64]
    pre_alarm_paths = [["a", "e", "c"]]
    node_scores = {"a": 0.0, "b": 3.0, "c": 0.5, "d": 0.0, "e": 0.0}

    score = score_node_score_aware_candidate(
        candidate_path=candidate_path,
        candidate_state=candidate_state,
        selected_paths=selected_paths,
        selected_states=selected_states,
        pre_alarm_paths=pre_alarm_paths,
        node_scores=node_scores,
        delta=0.75,
    )

    assert 0.0 <= score <= 1.0


def test_score_node_score_aware_candidate_rejects_bad_delta():
    try:
        score_node_score_aware_candidate(
            candidate_path=["a", "b"],
            candidate_state="f" * 64,
            selected_paths=[],
            selected_states=[],
            pre_alarm_paths=[],
            node_scores={},
            delta=2.0,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid delta")


def test_select_node_score_aware_paths_shape():
    candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
    ]

    node_scores = {
        "a": 0.0,
        "b": 5.0,
        "c": 0.0,
        "d": 0.0,
        "e": 0.0,
    }

    result = select_node_score_aware_paths(
        candidates=candidates,
        route_count=2,
        seed="seed",
        pre_alarm_paths=[["a", "b", "c"]],
        node_scores=node_scores,
        delta=0.75,
    )

    assert result["policy"] == "node_score_aware_lemonade_reset"
    assert result["delta"] == 0.75
    assert len(result["selected_paths"]) == 2
    assert len(result["selected_states"]) == 2
    assert len(result["scores"]) == 2
    assert result["results"]["path_count"] == 2


def test_mean_node_score_risk_per_path_bounds():
    paths = [["a", "b"], ["c", "d"]]
    scores = {"a": 0.0, "b": 5.0, "c": -1.0, "d": 1.0}

    value = mean_node_score_risk_per_path(paths, scores)

    assert 0.0 <= value <= 1.0


def test_healthy_node_ratio():
    paths = [["a", "b"], ["c", "d"]]
    scores = {"a": 0.0, "b": 0.5, "c": 2.0, "d": -0.5}

    assert healthy_node_ratio(paths, scores) == 0.5
