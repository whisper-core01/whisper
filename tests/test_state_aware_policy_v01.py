from state_aware_policy_v01 import (
    mean_path_distance,
    mean_state_distance,
    path_state_material,
    score_candidate,
    select_greedy_diverse,
)


def test_path_state_material_is_deterministic():
    path = ["a", "b", "c"]

    a = path_state_material(path, index=0, seed="seed", fractal_id=36)
    b = path_state_material(path, index=0, seed="seed", fractal_id=36)

    assert a == b
    assert len(a) == 64


def test_mean_state_distance_empty_selected():
    assert mean_state_distance("a" * 64, []) == 1.0


def test_mean_path_distance_empty_selected():
    assert mean_path_distance(["a", "b"], []) == 1.0


def test_score_candidate_bounds():
    candidate_path = ["a", "b", "c"]
    candidate_state = "f" * 64
    selected_paths = [["a", "d", "c"]]
    selected_states = ["0" * 64]

    score = score_candidate(
        candidate_path=candidate_path,
        candidate_state=candidate_state,
        selected_paths=selected_paths,
        selected_states=selected_states,
    )

    assert 0.0 <= score <= 1.0


def test_select_greedy_diverse_shape():
    candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
    ]

    result = select_greedy_diverse(
        candidates=candidates,
        route_count=2,
        seed="seed",
        fractal_id=36,
    )

    assert result["policy"] == "state_aware_whisper"
    assert len(result["selected_paths"]) == 2
    assert len(result["selected_states"]) == 2
    assert len(result["scores"]) == 2
    assert result["results"]["path_count"] == 2
