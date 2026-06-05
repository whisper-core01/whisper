from compare_next_hop_reset_v01 import (
    compare_next_hop_reset,
    flatten_result,
    run_next_hop_reset_suite,
)


def _config():
    return {
        "experiment_id": "next-hop-reset-test",
        "whisper_version": "v1.2.0",
        "topology": {
            "type": "erdos_renyi",
            "node_count": 80,
            "edge_probability": 0.08,
        },
        "policy": {
            "type": "whisper_structural_divergence",
            "route_count": 3,
            "fractal_count": 36,
        },
    }


def test_compare_next_hop_reset_shape_random():
    result = compare_next_hop_reset(
        config=_config(),
        seed="next-hop-test",
        compromise_fraction=0.2,
        condition_type="random",
        deltas=[0.90, 0.85],
    )

    assert result["schema_version"] == "1.2.0"
    assert result["experiment"] == "local-degradation-aware-lemonade-reselection"
    assert result["condition_type"] == "random"
    assert result["pre_reset_epochs"] == 5
    assert result["delta_grid"] == [0.90, 0.85]

    policies = [row["policy"] for row in result["comparison"]]

    assert "lemonade_reset" in policies
    assert "node_score_aware_delta_0.90" in policies
    assert "degradation_aware_delta_0.90" in policies
    assert "degradation_aware_delta_0.85" in policies


def test_compare_next_hop_reset_shape_targeted():
    result = compare_next_hop_reset(
        config=_config(),
        seed="next-hop-test",
        compromise_fraction=0.2,
        condition_type="targeted",
        deltas=[0.90],
    )

    assert result["schema_version"] == "1.2.0"
    assert result["condition_type"] == "targeted"
    assert len(result["comparison"]) == 3


def test_compare_next_hop_reset_shape_behavioral():
    result = compare_next_hop_reset(
        config=_config(),
        seed="next-hop-test",
        compromise_fraction=0.2,
        condition_type="behavioral",
        deltas=[0.90],
    )

    assert result["schema_version"] == "1.2.0"
    assert result["condition_type"] == "behavioral"
    assert result["compromised_node_count"] == 0
    assert len(result["comparison"]) == 3


def test_compare_next_hop_reset_metric_bounds():
    result = compare_next_hop_reset(
        config=_config(),
        seed="next-hop-test",
        compromise_fraction=0.2,
        condition_type="random",
        deltas=[0.90, 0.85, 0.80],
    )

    for row in result["comparison"]:
        assert 0.0 <= row["post_reset_path_distance_from_pre_alarm"] <= 1.0
        assert row["continuity_retention_vs_lemonade"] >= 0.0
        assert 0.0 <= row["state_break_distance"] <= 1.0
        assert 0.0 <= row["state_continuity_score"] <= 1.0
        assert 0.0 <= row["lane_collapse_rate"] <= 1.0
        assert 0.0 <= row["path_overlap"] <= 1.0
        assert 0.0 <= row["unique_path_ratio"] <= 1.0
        assert 0.0 <= row["clean_path_ratio"] <= 1.0
        assert 0.0 <= row["path_compromise_rate"] <= 1.0
        assert row["mean_compromised_nodes_per_path"] >= 0.0
        assert 0.0 <= row["mean_node_score_risk_per_path"] <= 1.0
        assert row["mean_raw_node_score_per_path"] >= -1.0
        assert 0.0 <= row["healthy_node_ratio"] <= 1.0
        assert 0.0 <= row["mean_degradation_risk_per_path"] <= 1.0


def test_flatten_result_shape():
    result = compare_next_hop_reset(
        config=_config(),
        seed="next-hop-test",
        compromise_fraction=0.2,
        condition_type="random",
        deltas=[0.90],
    )

    rows = flatten_result(result)

    assert len(rows) == 3
    assert rows[0]["schema_version"] == "1.2.0"
    assert "condition_type" in rows[0]
    assert "policy" in rows[0]
    assert "mean_degradation_risk_per_path" in rows[0]


def test_run_next_hop_reset_suite_outputs(tmp_path):
    config_path = tmp_path / "config.json"
    csv_path = tmp_path / "out.csv"
    json_path = tmp_path / "out.json"

    config_path.write_text(
        """
{
  "experiment_id": "next-hop-suite-test",
  "whisper_version": "v1.2.0",
  "topology": {
    "type": "erdos_renyi",
    "node_count": 50,
    "edge_probability": 0.10
  },
  "policy": {
    "type": "whisper_structural_divergence",
    "route_count": 2,
    "fractal_count": 12
  }
}
""".strip()
    )

    run_next_hop_reset_suite(
        config_path=str(config_path),
        seeds=["suite-001"],
        compromise_fractions=[0.20],
        condition_types=["random", "behavioral"],
        deltas=[0.90],
        csv_path=str(csv_path),
        json_path=str(json_path),
    )

    assert csv_path.exists()
    assert json_path.exists()
    assert "degradation_aware_delta_0.90" in csv_path.read_text()
    assert "local-degradation-aware-lemonade-reselection" in json_path.read_text()
