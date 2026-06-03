from lemonade_reset_policy_v01 import (
    mean_path_distance_to_set,
    post_reset_path_distance_from_pre_alarm,
    score_lemonade_reset_candidate,
    select_lemonade_reset_paths,
    state_break_distance,
)


def test_mean_path_distance_to_set_empty():
    assert mean_path_distance_to_set(["a", "b"], []) == 1.0


def test_mean_path_distance_to_set_bounds():
    candidate = ["a", "b", "c"]
    paths = [["a", "b", "c"], ["a", "d", "c"]]

    value = mean_path_distance_to_set(candidate, paths)

    assert 0.0 <= value <= 1.0


def test_score_lemonade_reset_candidate_bounds():
    candidate_path = ["a", "b", "c"]
    candidate_state = "f" * 64
    selected_paths = [["a", "d", "c"]]
    selected_states = ["0" * 64]
    pre_alarm_paths = [["a", "e", "c"]]

    score = score_lemonade_reset_candidate(
        candidate_path=candidate_path,
        candidate_state=candidate_state,
        selected_paths=selected_paths,
        selected_states=selected_states,
        pre_alarm_paths=pre_alarm_paths,
    )

    assert 0.0 <= score <= 1.0


def test_select_lemonade_reset_paths_shape():
    candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
    ]

    result = select_lemonade_reset_paths(
        candidates=candidates,
        route_count=2,
        seed="seed",
        pre_alarm_paths=[["a", "b", "c"]],
    )

    assert result["policy"] == "lemonade_reset"
    assert len(result["selected_paths"]) == 2
    assert len(result["selected_states"]) == 2
    assert len(result["scores"]) == 2
    assert result["results"]["path_count"] == 2


def test_state_break_distance_bounds():
    pre = ["0" * 64, "f" * 64]
    post = ["f" * 64, "0" * 64]

    value = state_break_distance(pre, post)

    assert 0.0 <= value <= 1.0
    assert value == 1.0


def test_state_break_distance_mismatch_raises():
    pre = ["0" * 64]
    post = ["f" * 64, "0" * 64]

    try:
        state_break_distance(pre, post)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for state count mismatch")


def test_post_reset_path_distance_from_pre_alarm_bounds():
    post = [["a", "d", "c"], ["a", "e", "c"]]
    pre = [["a", "b", "c"]]

    value = post_reset_path_distance_from_pre_alarm(post, pre)

    assert 0.0 <= value <= 1.0
