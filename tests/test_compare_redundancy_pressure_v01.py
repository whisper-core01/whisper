from compare_redundancy_pressure_v01 import (
    custody_adjusted_delivery_probability,
    custody_adjusted_fragment_delivered,
    simulate_redundant_message,
)


def _config():
    return {
        "experiment_id": "redundancy-pressure-test",
        "whisper_version": "v1.3.2",
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


def test_custody_adjusted_delivery_probability_increases_with_rounds():
    p1 = custody_adjusted_delivery_probability(0.50, 1)
    p3 = custody_adjusted_delivery_probability(0.50, 3)

    assert p1 == 0.50
    assert p3 > p1
    assert p3 <= 1.0


def test_custody_adjusted_delivery_probability_bounds():
    assert custody_adjusted_delivery_probability(0.0, 3) == 0.0
    assert custody_adjusted_delivery_probability(1.0, 3) == 1.0


def test_custody_adjusted_fragment_delivered_is_deterministic():
    a = custody_adjusted_fragment_delivered("seed", 1, 0.75, 3)
    b = custody_adjusted_fragment_delivered("seed", 1, 0.75, 3)

    assert a == b


def test_simulate_redundant_message_shape_with_custody():
    row = simulate_redundant_message(
        config=_config(),
        seed="test-seed",
        condition="random",
        compromise_fraction=0.20,
        required_fragments=10,
        redundancy_factor=1.10,
        magnet_strength=6.0,
        wandering_strength=0.5,
        hop_budget=8,
        custody_rounds=3,
    )

    assert row["schema_version"] == "1.3.2"
    assert row["custody_rounds"] == 3
    assert row["required_fragments"] == 10
    assert row["emitted_fragments"] >= 10
    assert 0.0 <= row["effective_reconstruction_ratio"] <= 1.0
    assert row["reticulum_graph_visible"] is False
    assert row["voxmesh_knows_reticulum_identity"] is False
    assert row["reticulum_knows_whisper_payload"] is False
