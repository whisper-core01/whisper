from sol_anchored_hop_policy_v01 import (
    anchor_affinity,
    derive_sol_anchor_alias,
    deterministic_unit_interval,
    loop_safety,
    next_hop_weight,
    path_overlap_ratio,
    route_sol_anchored_hop_by_hop,
    weighted_random_choice,
)


class TinyGraph:
    def __init__(self, adj):
        self.adj = adj

    def neighbors(self, node):
        return self.adj.get(node, [])


def test_derive_sol_anchor_alias_deterministic_and_context_scoped():
    a = derive_sol_anchor_alias("eph", "sol", "1", "nonce")
    b = derive_sol_anchor_alias("eph", "sol", "1", "nonce")
    c = derive_sol_anchor_alias("eph", "sol", "2", "nonce")

    assert a == b
    assert a != c
    assert len(a) == 64


def test_deterministic_unit_interval_bounds():
    value = deterministic_unit_interval("a", "b", "c")
    assert 0.0 <= value <= 1.0
    assert value == deterministic_unit_interval("a", "b", "c")


def test_anchor_affinity_bounds_and_relation_sensitive():
    ab = anchor_affinity("a", "b", "alias", "seed")
    ac = anchor_affinity("a", "c", "alias", "seed")

    assert 0.05 <= ab <= 1.0
    assert 0.05 <= ac <= 1.0
    assert ab != ac


def test_loop_safety_penalizes_visited():
    assert loop_safety("b", {"a", "b"}) == 0.01
    assert loop_safety("c", {"a", "b"}) == 1.0


def test_weighted_random_choice_deterministic():
    items = [("a", 0.1), ("b", 0.9)]
    assert weighted_random_choice(items, "seed") == weighted_random_choice(items, "seed")


def test_next_hop_weight_bounds():
    weight = next_hop_weight(
        current="a",
        candidate_next_hop="b",
        neighbors_of_candidate=["c", "d"],
        sol_anchor_alias="alias",
        node_scores={"b": 0.5},
        seed="seed",
        visited={"a"},
    )

    assert weight > 0.0
    assert weight <= 1.0


def test_route_sol_anchored_hop_by_hop_shape():
    graph = TinyGraph({
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": [],
    })

    result = route_sol_anchored_hop_by_hop(
        graph=graph,
        source="a",
        target="d",
        receiver_ephemeral_id="receiver",
        sol_id="sol",
        epoch="1",
        session_nonce="nonce",
        node_scores={},
        seed="seed",
        hop_budget=4,
    )

    assert result["policy"] == "sol_anchored_hop_by_hop"
    assert result["source"] == "a"
    assert result["target"] == "d"
    assert result["path"][0] == "a"
    assert result["hop_count"] <= 4
    assert len(result["sol_anchor_alias"]) == 64


def test_route_respects_hop_budget():
    graph = TinyGraph({
        "a": ["b"],
        "b": ["c"],
        "c": ["d"],
        "d": [],
    })

    result = route_sol_anchored_hop_by_hop(
        graph=graph,
        source="a",
        target="d",
        receiver_ephemeral_id="receiver",
        sol_id="sol",
        epoch="1",
        session_nonce="nonce",
        node_scores={},
        seed="seed",
        hop_budget=2,
    )

    assert result["hop_count"] == 2
    assert result["delivered"] is False


def test_path_overlap_ratio():
    assert path_overlap_ratio(["a", "b"], ["b", "c"]) == 1 / 3
    assert path_overlap_ratio([], ["b", "c"]) == 0.0
