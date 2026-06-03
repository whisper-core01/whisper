from state_mapping_v01 import (
    analyze_state_mapping,
    hamming_distance_hex,
    lane_collapse_rate,
    normalized_state_distance,
    path_distance,
    pearson_correlation,
    state_material,
    state_to_path_correlation,
)


def _config():
    return {
        "experiment_id": "state-mapping-test",
        "whisper_version": "v0.8.0",
        "topology": {"type": "erdos_renyi", "node_count": 80, "edge_probability": 0.08},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }


def test_state_material_is_deterministic():
    a = state_material("seed", "policy", 1, 36)
    b = state_material("seed", "policy", 1, 36)

    assert a == b
    assert len(a) == 64


def test_state_distance_bounds():
    a = "0" * 64
    b = "f" * 64

    assert hamming_distance_hex(a, b) == 256
    assert normalized_state_distance(a, b) == 1.0
    assert normalized_state_distance(a, a) == 0.0


def test_path_distance_bounds():
    p1 = ["a", "b", "c"]
    p2 = ["a", "b", "c"]
    p3 = ["a", "d", "c"]

    assert path_distance(p1, p2) == 0.0
    assert 0.0 <= path_distance(p1, p3) <= 1.0


def test_pearson_correlation_bounds():
    corr = pearson_correlation([0.0, 0.5, 1.0], [0.0, 0.5, 1.0])

    assert 0.99 <= corr <= 1.0


def test_state_to_path_correlation_shape():
    states = [
        state_material("seed", "policy", 0),
        state_material("seed", "policy", 1),
        state_material("seed", "policy", 2),
    ]

    paths = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
    ]

    corr = state_to_path_correlation(states, paths)

    assert -1.0 <= corr <= 1.0


def test_lane_collapse_rate_bounds():
    paths = [
        ["a", "b", "c"],
        ["a", "b", "c"],
        ["a", "d", "c"],
    ]

    rate = lane_collapse_rate(paths)

    assert 0.0 <= rate <= 1.0


def test_analyze_state_mapping_output_shape():
    result = analyze_state_mapping(_config(), "state-seed")

    assert result["schema_version"] == "0.8.0"
    assert result["path_count"] >= 1
    assert "state_to_path_correlation" in result
    assert "lane_collapse_rate" in result
    assert -1.0 <= result["state_to_path_correlation"] <= 1.0
    assert 0.0 <= result["lane_collapse_rate"] <= 1.0
