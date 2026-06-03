import json
from pathlib import Path

from baseline_v01 import compare_whisper_vs_single_path, single_path_baseline


def test_single_path_baseline_repeats_same_path():
    config = {
        "experiment_id": "baseline-test",
        "whisper_version": "v0.7.0",
        "topology": {"type": "erdos_renyi", "node_count": 80, "edge_probability": 0.08},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }

    result = single_path_baseline(config, "baseline-seed")

    assert result["policy"] == "single_path"
    assert result["results"]["path_count"] == 3
    assert result["results"]["unique_path_ratio"] == 1 / 3
    assert result["results"]["path_overlap"] == 1.0


def test_compare_whisper_vs_single_path_shape():
    config = {
        "experiment_id": "baseline-test",
        "whisper_version": "v0.7.0",
        "topology": {"type": "erdos_renyi", "node_count": 80, "edge_probability": 0.08},
        "policy": {"type": "whisper_structural_divergence", "route_count": 3, "fractal_count": 36},
    }

    result = compare_whisper_vs_single_path(config, "baseline-seed")

    assert result["schema_version"] == "0.7.0"
    assert result["seed"] == "baseline-seed"
    assert len(result["comparison"]) == 2

    policies = {row["policy"] for row in result["comparison"]}

    assert "whisper_candidate_paths" in policies
    assert "single_path" in policies


def test_baseline_output_files_exist_after_script_run():
    assert Path("outputs/baseline_comparison.csv").exists()
    assert Path("outputs/baseline_comparison.json").exists()

    data = json.loads(Path("outputs/baseline_comparison.json").read_text())

    assert data["schema_version"] == "0.7.0"
    assert len(data["comparisons"]) >= 3
