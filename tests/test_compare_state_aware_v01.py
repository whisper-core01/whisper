from compare_state_aware_v01 import compare_state_aware


def _config():
    return {
        "experiment_id": "state-aware-test",
        "whisper_version": "v0.9.0",
        "topology": {"type": "erdos_renyi", "node_count": 80, "edge_probability": 0.08},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }


def test_compare_state_aware_shape():
    result = compare_state_aware(_config(), "state-aware-seed", compromise_fraction=0.2)

    assert result["schema_version"] == "0.9.0"
    assert result["compromise"]["type"] == "random_node_compromise"
    assert len(result["comparison"]) == 3

    policies = {row["policy"] for row in result["comparison"]}

    assert "whisper_candidate_paths" in policies
    assert "random_multipath" in policies
    assert "state_aware_whisper" in policies


def test_compare_state_aware_metric_bounds():
    result = compare_state_aware(_config(), "state-aware-seed", compromise_fraction=0.2)

    for row in result["comparison"]:
        assert 0.0 <= row["unique_path_ratio"] <= 1.0
        assert 0.0 <= row["path_overlap"] <= 1.0
        assert 0.0 <= row["clean_path_ratio"] <= 1.0
        assert 0.0 <= row["path_compromise_rate"] <= 1.0
        assert -1.0 <= row["state_to_path_correlation"] <= 1.0
        assert 0.0 <= row["lane_collapse_rate"] <= 1.0
