from compare_node_score_reset_v01 import (
    build_pre_reset_flv_scores,
    compare_node_score_reset,
    flatten_result,
)
from topology_v01 import generate_topology
from path_sampler_v01 import select_source_target


def _config():
    return {
        "experiment_id": "node-score-reset-test",
        "whisper_version": "v1.1.0",
        "topology": {"type": "erdos_renyi", "node_count": 80, "edge_probability": 0.08},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }


def test_build_pre_reset_flv_scores_shape():
    config = _config()
    graph = generate_topology(config, "flv-score-test")
    source, target = select_source_target(graph, "flv-score-test:pair")

    result = build_pre_reset_flv_scores(
        graph=graph,
        source=source,
        target=target,
        route_count=3,
        fractal_id=36,
        seed="flv-score-test",
        pre_reset_epochs=5,
    )

    assert result["pre_reset_epochs"] == 5
    assert len(result["selected_paths_by_epoch"]) == 5
    assert len(result["node_scores"]) == graph.node_count

    for score in result["node_scores"].values():
        assert -1.0 <= score <= 5.0


def test_compare_node_score_reset_shape_random():
    result = compare_node_score_reset(
        config=_config(),
        seed="node-score-test",
        compromise_fraction=0.2,
        compromise_type="random",
        deltas=[0.90, 0.75],
    )

    assert result["schema_version"] == "1.1.0"
    assert result["experiment"] == "node-score-aware-lemonade-reselection"
    assert result["compromise_type"] == "random"
    assert result["pre_reset_epochs"] == 5
    assert result["delta_grid"] == [0.90, 0.75]

    policies = [row["policy"] for row in result["comparison"]]

    assert "lemonade_reset" in policies
    assert "node_score_aware_delta_0.90" in policies
    assert "node_score_aware_delta_0.75" in policies


def test_compare_node_score_reset_shape_targeted():
    result = compare_node_score_reset(
        config=_config(),
        seed="node-score-test",
        compromise_fraction=0.2,
        compromise_type="targeted",
        deltas=[0.90],
    )

    assert result["schema_version"] == "1.1.0"
    assert result["compromise_type"] == "targeted"
    assert len(result["comparison"]) == 2


def test_compare_node_score_reset_metric_bounds():
    result = compare_node_score_reset(
        config=_config(),
        seed="node-score-test",
        compromise_fraction=0.2,
        compromise_type="random",
        deltas=[0.90, 0.75],
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


def test_flatten_result_shape():
    result = compare_node_score_reset(
        config=_config(),
        seed="node-score-test",
        compromise_fraction=0.2,
        compromise_type="random",
        deltas=[0.90],
    )

    rows = flatten_result(result)

    assert len(rows) == 2
    assert rows[0]["schema_version"] == "1.1.0"
    assert "policy" in rows[0]
    assert "mean_node_score_risk_per_path" in rows[0]
