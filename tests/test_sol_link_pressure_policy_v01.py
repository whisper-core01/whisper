from sol_link_magnetic_policy_v01 import LogicalRelay
from sol_link_pressure_policy_v01 import (
    pressure_next_hop_weight,
    randomness_dissipation,
    route_sol_link_pressure_hop_by_hop,
    routing_basin_safety,
    select_pressure_next_hop,
    wandering_safety,
)


def _relays():
    return {
        "a": LogicalRelay("a", opaque_transport_capsule="capsule:a"),
        "b": LogicalRelay("b", opaque_transport_capsule="capsule:b"),
        "c": LogicalRelay("c", opaque_transport_capsule="capsule:c"),
        "d": LogicalRelay("d", opaque_transport_capsule="capsule:d"),
    }


def test_randomness_dissipation_decreases_with_hop_index():
    early = randomness_dissipation(0, 10)
    late = randomness_dissipation(9, 10)

    assert early == 1.0
    assert 0.35 <= late < early


def test_wandering_safety_bounds():
    good = wandering_safety(affinity=0.9, hop_index=8, hop_budget=10)
    bad = wandering_safety(affinity=0.1, hop_index=8, hop_budget=10)

    assert 0.0 <= good <= 1.0
    assert 0.0 <= bad <= 1.0
    assert good >= bad


def test_routing_basin_safety_penalizes_dead_end():
    relays = _relays()

    dead = routing_basin_safety(relays["d"], {"d": []})
    open_node = routing_basin_safety(relays["b"], {"b": ["c", "d", "a"]})

    assert dead < open_node


def test_pressure_next_hop_weight_positive():
    relays = _relays()

    weight = pressure_next_hop_weight(
        current_relay="a",
        candidate=relays["b"],
        sol_link_alias="alias",
        node_scores={},
        degradation_scores={},
        known_neighbors={"b": ["d"]},
        visited={"a"},
        seed="seed",
        hop_index=0,
        hop_budget=4,
        magnet_strength=4.0,
        wandering_strength=1.0,
    )

    assert weight > 0.0


def test_pressure_next_hop_weight_rejects_negative_magnet_strength():
    relays = _relays()

    try:
        pressure_next_hop_weight(
            current_relay="a",
            candidate=relays["b"],
            sol_link_alias="alias",
            node_scores={},
            degradation_scores={},
            known_neighbors={"b": ["d"]},
            visited={"a"},
            seed="seed",
            hop_index=0,
            hop_budget=4,
            magnet_strength=-1.0,
            wandering_strength=1.0,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for negative magnet_strength")


def test_select_pressure_next_hop_shape():
    relays = _relays()
    known = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}

    decision = select_pressure_next_hop(
        current_relay="a",
        known_neighbors=known,
        relays=relays,
        sol_link_alias="alias",
        node_scores={},
        degradation_scores={},
        visited={"a"},
        seed="seed",
        hop_index=0,
        hop_budget=4,
        magnet_strength=4.0,
        wandering_strength=1.0,
    )

    assert decision is not None
    assert decision.selected_relay in {"b", "c"}
    assert decision.selected_weight > 0.0


def test_route_sol_link_pressure_hop_by_hop_shape_and_invariants():
    relays = _relays()
    known = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}

    result = route_sol_link_pressure_hop_by_hop(
        source_relay="a",
        relays=relays,
        known_neighbors=known,
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        sol_id="sol",
        epoch="1",
        session_nonce="nonce",
        opaque_whisper_capsule="opaque",
        node_scores={},
        degradation_scores={},
        seed="seed",
        hop_budget=4,
        magnet_strength=4.0,
        wandering_strength=1.0,
    )

    assert result["policy"] == "sol_link_pressure_hop_by_hop"
    assert result["path"][0] == "a"
    assert result["hop_count"] <= 4
    assert result["transport_delivery_ratio"] >= 0.0
    assert result["mean_candidate_count"] >= 0.0
    assert result["reticulum_graph_visible"] is False
    assert result["voxmesh_knows_reticulum_identity"] is False
    assert result["reticulum_knows_whisper_payload"] is False
