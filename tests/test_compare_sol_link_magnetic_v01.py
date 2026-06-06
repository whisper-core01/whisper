from compare_sol_link_magnetic_v01 import (
    build_logical_relays,
    build_known_neighbors,
    compare_sol_link_magnetic,
    flatten_result,
    run_sol_link_magnetic_suite,
)


def _config():
    return {
        "experiment_id": "sol-link-magnetic-test",
        "whisper_version": "v1.3.0",
        "topology": {
            "type": "erdos_renyi",
            "node_count": 50,
            "edge_probability": 0.10,
        },
        "policy": {
            "type": "whisper_logical_relay",
            "route_count": 3,
            "fractal_count": 12,
        },
    }


def test_compare_sol_link_magnetic_shape_random():
    result = compare_sol_link_magnetic(
        config=_config(),
        seed="test-seed",
        condition="random",
        compromise_fraction=0.2,
        magnet_strengths=[0.0, 2.0],
        hop_budget=8,
    )

    assert result["schema_version"] == "1.3.0"
    assert result["experiment"] == "sol-link-magnetic-logical-routing"
    assert result["condition"] == "random"
    assert result["hop_budget"] == 8
    assert len(result["results"]) == 2


def test_compare_sol_link_magnetic_invariants():
    result = compare_sol_link_magnetic(
        config=_config(),
        seed="test-seed",
        condition="targeted",
        compromise_fraction=0.2,
        magnet_strengths=[4.0],
        hop_budget=8,
    )

    row = result["results"][0]

    assert row["reticulum_graph_visible"] is False
    assert row["voxmesh_knows_reticulum_identity"] is False
    assert row["reticulum_knows_whisper_payload"] is False


def test_compare_sol_link_magnetic_metric_bounds():
    result = compare_sol_link_magnetic(
        config=_config(),
        seed="test-seed",
        condition="behavioral",
        compromise_fraction=0.2,
        magnet_strengths=[0.0, 1.0, 2.0],
        hop_budget=8,
    )

    for row in result["results"]:
        assert row["hop_count"] <= 8
        assert row["path_len"] >= 1
        assert row["transport_attempts"] >= 0
        assert row["transport_failures"] >= 0
        assert row["compromised_relays"] >= 0
        assert 0.0 <= row["path_compromise_rate"] <= 1.0


def test_flatten_result_shape():
    result = compare_sol_link_magnetic(
        config=_config(),
        seed="test-seed",
        condition="random",
        compromise_fraction=0.2,
        magnet_strengths=[0.0, 2.0],
        hop_budget=8,
    )

    rows = flatten_result(result)

    assert len(rows) == 2
    assert rows[0]["schema_version"] == "1.3.0"
    assert "magnet_strength" in rows[0]
    assert "transport_success" in rows[0]


def test_run_sol_link_magnetic_suite_outputs(tmp_path):
    config_path = tmp_path / "config.json"
    csv_path = tmp_path / "out.csv"
    json_path = tmp_path / "out.json"

    config_path.write_text(
        """
{
  "experiment_id": "sol-link-suite-test",
  "whisper_version": "v1.3.0",
  "topology": {
    "type": "erdos_renyi",
    "node_count": 40,
    "edge_probability": 0.12
  },
  "policy": {
    "type": "whisper_logical_relay",
    "route_count": 2,
    "fractal_count": 12
  }
}
""".strip()
    )

    run_sol_link_magnetic_suite(
        config_path=str(config_path),
        seeds=["suite-001"],
        conditions=["random", "behavioral"],
        compromise_fractions=[0.20],
        magnet_strengths=[0.0, 2.0],
        hop_budget=8,
        csv_path=str(csv_path),
        json_path=str(json_path),
    )

    assert csv_path.exists()
    assert json_path.exists()
    assert "sol_link_magnetic_hop_by_hop" in csv_path.read_text()
    assert "sol-link-magnetic-logical-routing" in json_path.read_text()
