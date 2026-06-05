from sol_link_magnetic_policy_v01 import (
    LogicalRelay,
    admissible_logical_neighbors,
    derive_sol_link_alias,
    deterministic_unit_interval,
    logical_next_hop_weight,
    reticulum_transport_attempt,
    route_sol_link_magnetic_hop_by_hop,
    select_logical_next_hop,
    sol_link_affinity,
    weighted_random_choice,
)


def _relays():
    return {
        "a": LogicalRelay("a", opaque_transport_capsule="capsule:a"),
        "b": LogicalRelay("b", opaque_transport_capsule="capsule:b"),
        "c": LogicalRelay("c", opaque_transport_capsule="capsule:c"),
        "d": LogicalRelay("d", opaque_transport_capsule="capsule:d"),
        "revoked": LogicalRelay("revoked", revoked=True, opaque_transport_capsule="capsule:r"),
        "unfit": LogicalRelay("unfit", unfit=True, opaque_transport_capsule="capsule:u"),
        "missing": LogicalRelay("missing", opaque_transport_capsule=None),
    }


def test_derive_sol_link_alias_is_deterministic_and_scoped():
    a = derive_sol_link_alias("local", "remote", "sol", "1", "nonce")
    b = derive_sol_link_alias("local", "remote", "sol", "1", "nonce")
    c = derive_sol_link_alias("local", "remote", "sol", "2", "nonce")

    assert a == b
    assert a != c
    assert len(a) == 64


def test_deterministic_unit_interval_bounds():
    value = deterministic_unit_interval("a", "b", "c")

    assert 0.0 <= value <= 1.0
    assert value == deterministic_unit_interval("a", "b", "c")


def test_sol_link_affinity_bounds_and_context_sensitive():
    ab = sol_link_affinity("a", "b", "alias", "seed")
    ac = sol_link_affinity("a", "c", "alias", "seed")

    assert 0.05 <= ab <= 1.0
    assert 0.05 <= ac <= 1.0
    assert ab != ac


def test_admissible_logical_neighbors_filters_non_admissible():
    relays = _relays()
    known = {
        "a": ["b", "revoked", "unfit", "missing", "unknown"],
    }

    out = admissible_logical_neighbors("a", known, relays)
    aliases = [relay.relay_alias for relay in out]

    assert aliases == ["b"]


def test_logical_next_hop_weight_positive():
    relays = _relays()
    weight = logical_next_hop_weight(
        current_relay="a",
        candidate=relays["b"],
        sol_link_alias="alias",
        node_scores={"b": 0.0},
        degradation_scores={},
        known_neighbors={"b": ["d"]},
        visited={"a"},
        seed="seed",
        magnet_strength=2.0,
    )

    assert weight > 0.0


def test_logical_next_hop_weight_rejects_negative_magnet_strength():
    relays = _relays()

    try:
        logical_next_hop_weight(
            current_relay="a",
            candidate=relays["b"],
            sol_link_alias="alias",
            node_scores={},
            degradation_scores={},
            known_neighbors={},
            visited={"a"},
            seed="seed",
            magnet_strength=-1.0,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for negative magnet_strength")


def test_weighted_random_choice_deterministic():
    relays = _relays()
    items = [(relays["b"], 0.1), (relays["c"], 0.9)]

    a = weighted_random_choice(items, "seed")
    b = weighted_random_choice(items, "seed")

    assert a == b


def test_select_logical_next_hop_shape():
    relays = _relays()
    known = {"a": ["b", "c"]}

    decision = select_logical_next_hop(
        current_relay="a",
        known_neighbors=known,
        relays=relays,
        sol_link_alias="alias",
        node_scores={},
        degradation_scores={},
        visited={"a"},
        seed="seed",
        magnet_strength=2.0,
    )

    assert decision is not None
    assert decision.current_relay == "a"
    assert decision.selected_relay in {"b", "c"}
    assert decision.selected_weight > 0.0
    assert set(decision.candidate_weights) == {"b", "c"}


def test_reticulum_transport_attempt_keeps_blindness_flags():
    relay = LogicalRelay("b", opaque_transport_capsule="capsule:b")

    result = reticulum_transport_attempt(
        relay=relay,
        opaque_whisper_capsule="opaque",
        seed="seed",
    )

    assert result["attempted"] is True
    assert result["reticulum_identity_exposed_to_voxmesh"] is False
    assert result["whisper_payload_visible_to_reticulum"] is False


def test_route_sol_link_magnetic_hop_by_hop_shape_and_invariants():
    relays = {
        "a": LogicalRelay("a", opaque_transport_capsule="capsule:a"),
        "b": LogicalRelay("b", opaque_transport_capsule="capsule:b"),
        "c": LogicalRelay("c", opaque_transport_capsule="capsule:c"),
        "d": LogicalRelay("d", opaque_transport_capsule="capsule:d"),
    }
    known = {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": [],
    }

    result = route_sol_link_magnetic_hop_by_hop(
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
        magnet_strength=2.0,
    )

    assert result["policy"] == "sol_link_magnetic_hop_by_hop"
    assert result["path"][0] == "a"
    assert result["hop_count"] <= 4
    assert result["reticulum_graph_visible"] is False
    assert result["voxmesh_knows_reticulum_identity"] is False
    assert result["reticulum_knows_whisper_payload"] is False
    assert len(result["sol_link_alias"]) == 64
