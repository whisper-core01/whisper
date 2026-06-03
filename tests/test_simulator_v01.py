from pathlib import Path

from metrics_v01 import path_overlap, summarize_paths, unique_path_ratio
from path_sampler_v01 import candidate_paths, select_source_target
from simulation_runner_v01 import run_simulation
from topology_v01 import generate_topology


def test_generate_erdos_renyi_topology():
    cfg = {"topology": {"type": "erdos_renyi", "node_count": 30, "edge_probability": 0.15}}
    graph = generate_topology(cfg, "seed")

    assert graph.topology_type == "erdos_renyi"
    assert graph.node_count == 30
    assert graph.edge_count >= 0
    assert set(graph.adjacency.keys()) == set(graph.nodes)


def test_generate_barabasi_albert_topology():
    cfg = {"topology": {"type": "barabasi_albert", "node_count": 30, "m": 2}}
    graph = generate_topology(cfg, "seed")

    assert graph.topology_type == "barabasi_albert"
    assert graph.node_count == 30
    assert graph.edge_count > 0


def test_generate_watts_strogatz_topology():
    cfg = {"topology": {"type": "watts_strogatz", "node_count": 30, "k": 4, "beta": 0.1}}
    graph = generate_topology(cfg, "seed")

    assert graph.topology_type == "watts_strogatz"
    assert graph.node_count == 30
    assert graph.edge_count > 0


def test_candidate_paths_are_deterministic():
    cfg = {"topology": {"type": "erdos_renyi", "node_count": 40, "edge_probability": 0.2}}
    graph = generate_topology(cfg, "seed")
    source, target = select_source_target(graph, "pair")

    p1 = candidate_paths(graph, source, target, "paths", k=3)
    p2 = candidate_paths(graph, source, target, "paths", k=3)

    assert p1 == p2
    assert len(p1) >= 1


def test_metrics_summary():
    paths = [
        ["a", "b", "c"],
        ["a", "b", "d"],
        ["a", "e", "d"],
    ]

    summary = summarize_paths(paths)

    assert path_overlap(paths[0], paths[1]) == 0.5
    assert unique_path_ratio(paths) == 1.0
    assert summary["path_count"] == 3
    assert summary["unique_path_ratio"] == 1.0
    assert 0.0 <= summary["path_overlap"] <= 1.0


def test_run_simulation_minimal_output():
    cfg = {
        "experiment_id": "test-sim",
        "whisper_version": "v0.6.0",
        "topology": {"type": "erdos_renyi", "node_count": 50, "edge_probability": 0.1},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }

    result = run_simulation(cfg, "run-test")

    assert result["schema_version"] == "0.6.0"
    assert result["metadata"]["experiment_id"] == "test-sim"
    assert result["topology"]["node_count"] == 50
    assert result["policy"]["route_count"] == 3
    assert "paths" in result
    assert "results" in result
    assert 0.0 <= result["results"]["unique_path_ratio"] <= 1.0
    assert 0.0 <= result["results"]["path_overlap"] <= 1.0
