from compare_sol_link_pressure_v01 import (
    compare_sol_link_pressure,
    flatten_result,
    run_sol_link_pressure_suite,
)


def _config():
    return {
        "experiment_id": "sol-link-pressure-test",
        "whisper_version": "v1.3.1",
        "topology": {
            "type": "erdos_renyi",
            "node_count": 40,
            "edge_probability": 0.12,
        },
        "policy": {
            "type": "whisper_logical_pressure",
            "route_count": 3,
            "fractal_count": 12,
        },
    }


def test_compare_sol_link_pressure_shape():
    result = compare_sol_link_pressure(
        config=_config(),
        seed="test-seed",
        condition="random",
        compromise_fraction=0.2,
        magnet_strengths=[4.0],
        wandering_strengths=[1.0, 2.0],
        hop_budget=8,
    )

    assert result["schema_version"] == "1.3.1"
    assert result["experiment"] == "sol-link-pressure-field-comparison"
    assert result["condition"] == "random"

    # 1 raw magnet + 2 pressure configs
    assert len(result["results"]) == 3


def test_compare_sol_link_pressure_invariants():
    result = compare_sol_link_pressure(
        config=_config(),
        seed="test-seed",
        condition="targeted",
        compromise_fraction=0.2,
        magnet_strengths=[4.0],
        wandering_strengths=[1.0],
        hop_budget=8,
    )

    for row in result["results"]:
        assert row["reticulum_graph_visible"] is False
        assert row["voxmesh_knows_reticulum_identity"] is False
        assert row["reticulum_knows_whisper_payload"] is False


def test_compare_sol_link_pressure_metric_bounds():
    result = compare_sol_link_pressure(
        config=_config(),
        seed="test-seed",
        condition="behavioral",
        compromise_fraction=0.2,
        magnet_strengths=[4.0, 6.0],
        wandering_strengths=[1.0],
        hop_budget=8,
    )

    for row in result["results"]:
        assert row["hop_count"] <= 8
        assert row["path_len"] >= 1
        assert row["transport_attempts"] >= 0
        assert row["successful_transport_attempts"] >= 0
        assert row["transport_failures"] >= 0
        assert 0.0 <= row["transport_delivery_ratio"] <= 1.0
        assert row["relay_reuse_count"] >= 0
        assert row["compromised_relays"] >= 0
        assert 0.0 <= row["path_compromise_rate"] <= 1.0


def test_flatten_result_shape():
    result = compare_sol_link_pressure(
        config=_config(),
        seed="test-seed",
        condition="behavioral",
        compromise_fraction=0.2,
        magnet_strengths=[4.0],
        wandering_strengths=[1.0],
        hop_budget=8,
    )

    rows = flatten_result(result)

    assert len(rows) == 2
    assert rows[0]["schema_version"] == "1.3.1"
    assert "transport_delivery_ratio" in rows[0]
    assert "compromised_relays" in rows[0]
    assert "policy" in rows[0]


def test_run_sol_link_pressure_suite_outputs(tmp_path):
    config_path = tmp_path / "config.json"
    csv_path = tmp_path / "out.csv"
    json_path = tmp_path / "out.json"

    config_path.write_text(
        """
{
  "experiment_id": "sol-link-pressure-suite-test",
  "whisper_version": "v1.3.1",
  "topology": {
    "type": "erdos_renyi",
    "node_count": 35,
    "edge_probability": 0.12
  },
  "policy": {
    "type": "whisper_logical_pressure",
    "route_count": 2,
    "fractal_count": 12
  }
}
""".strip()
    )

    run_sol_link_pressure_suite(
        config_path=str(config_path),
        seeds=["suite-001"],
        conditions=["random"],
        compromise_fractions=[0.20],
        magnet_strengths=[4.0],
        wandering_strengths=[1.0],
        hop_budget=8,
        csv_path=str(csv_path),
        json_path=str(json_path),
    )

    assert csv_path.exists()
    assert json_path.exists()
    assert "sol-link-pressure-field-comparison" in json_path.read_text()
    assert "v1.3.1_pressure_field" in csv_path.read_text()
