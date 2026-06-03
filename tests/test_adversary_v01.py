from adversary_v01 import (
    compare_under_adversary,
    evaluate_policy_exposure,
    random_compromise,
)


def _config():
    return {
        "experiment_id": "adversary-test",
        "whisper_version": "v0.7.3",
        "topology": {"type": "erdos_renyi", "node_count": 80, "edge_probability": 0.08},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }


def test_random_compromise_is_deterministic():
    c1 = random_compromise(100, 0.2, "seed")
    c2 = random_compromise(100, 0.2, "seed")

    assert c1 == c2
    assert len(c1) == 20


def test_random_compromise_zero_fraction():
    compromised = random_compromise(100, 0.0, "seed")

    assert compromised == set()


def test_evaluate_policy_exposure_clean_paths():
    paths = [
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]

    result = evaluate_policy_exposure(paths, {"x", "y"})

    assert result["path_count"] == 2
    assert result["compromised_path_count"] == 0
    assert result["path_compromise_rate"] == 0.0
    assert result["clean_path_ratio"] == 1.0


def test_evaluate_policy_exposure_compromised_paths():
    paths = [
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]

    result = evaluate_policy_exposure(paths, {"b", "e"})

    assert result["path_count"] == 2
    assert result["compromised_path_count"] == 2
    assert result["path_compromise_rate"] == 1.0
    assert result["clean_path_ratio"] == 0.0
    assert result["mean_compromised_nodes_per_path"] == 1.0


def test_compare_under_adversary_shape():
    result = compare_under_adversary(_config(), "adversary-seed", compromise_fraction=0.2)

    assert result["schema_version"] == "0.7.3"
    assert result["compromise"]["type"] == "random_node_compromise"
    assert result["compromise"]["compromise_fraction"] == 0.2
    assert len(result["exposure"]) == 3

    policies = {row["policy"] for row in result["exposure"]}

    assert "whisper_candidate_paths" in policies
    assert "single_path" in policies
    assert "random_multipath" in policies
