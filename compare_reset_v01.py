"""
WHISPER v1.0.0: Compare reset-based path selection policies.

Implements full 5-phase experiment:
  Phase A: Pre-alarm baseline using state-aware policy
  Phase B: Wasm anomaly detection, simulated
  Phase C: Lemonade defensive response, simulated
  Phase D: Dome/Nix reset, simulated
  Phase E: Post-reset path re-selection

Policies compared post-reset:
  1. random_multipath_reset
  2. state_aware_reset
  3. lemonade_reset

Primary metric:
  - post_reset_path_distance_from_pre_alarm

Secondary metrics:
  - state_break_distance
  - state_continuity_score
  - path_overlap
  - lane_collapse_rate
  - clean_path_ratio
  - path_compromise_rate
  - mean_compromised_nodes_per_path
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Set

from adversary_v01 import evaluate_policy_exposure, random_compromise
from lemonade_reset_policy_v01 import (
    post_reset_path_distance_from_pre_alarm,
    select_lemonade_reset_paths,
    state_break_distance,
)
from metrics_v01 import summarize_paths
from path_sampler_v01 import candidate_paths, select_source_target
from state_aware_policy_v01 import path_state_material, select_greedy_diverse
from state_mapping_v01 import lane_collapse_rate
from topology_v01 import generate_topology


NodePath = List[str]


def targeted_high_degree_compromise(graph: Any, compromise_fraction: float) -> Set[str]:
    """
    Compromise the highest-degree nodes.

    Node names are expected to be n0, n1, ...
    """
    if not 0.0 <= compromise_fraction <= 1.0:
        raise ValueError("compromise_fraction must be between 0.0 and 1.0")

    nodes = list(graph.nodes)
    if not nodes:
        return set()

    compromise_count = int(len(nodes) * compromise_fraction)
    if compromise_fraction > 0.0:
        compromise_count = max(1, compromise_count)

    compromise_count = min(len(nodes), compromise_count)

    # Count degree by iterating edges
    node_degrees = {node: 0 for node in nodes}
    for u, v in graph.edges:
        node_degrees[u] = node_degrees.get(u, 0) + 1
        node_degrees[v] = node_degrees.get(v, 0) + 1

    sorted_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)

    return {node for node, _ in sorted_nodes[:compromise_count]}


def random_select_paths(candidates: List[NodePath], route_count: int, seed: str) -> List[NodePath]:
    """
    Deterministic random multipath reset selection.
    """
    if route_count < 1:
        raise ValueError("route_count must be >= 1")

    if not candidates:
        return []

    rng = random.Random(seed)
    shuffled = list(candidates)
    rng.shuffle(shuffled)

    selected: List[NodePath] = []
    seen = set()

    for path in shuffled:
        key = tuple(path)
        if key in seen:
            continue
        seen.add(key)
        selected.append(path)

        if len(selected) >= route_count:
            break

    return selected


def derive_path_states(paths: List[NodePath], seed: str, fractal_id: int = 36) -> List[str]:
    """
    Derive deterministic diagnostic state material for paths.
    """
    return [
        path_state_material(path=path, index=i, seed=seed, fractal_id=fractal_id)
        for i, path in enumerate(paths)
    ]


def run_reset_experiment_phases(
    config: Dict[str, Any],
    seed: str,
    compromise_fraction: float = 0.20,
    compromise_type: str = "random",
) -> Dict[str, Any]:
    """
    Run full 5-phase Lemonade reset experiment.

    Reset is applied to every post-reset policy.
    Only lemonade_reset uses pre_alarm_paths directly in scoring.
    """
    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:pair")

    policy_cfg = config.get("policy", {})
    route_count = int(policy_cfg.get("route_count", 3))
    fractal_id = int(policy_cfg.get("fractal_count", 36))

    if compromise_type == "random":
        compromised = random_compromise(graph.node_count, compromise_fraction, seed)
    elif compromise_type == "targeted":
        compromised = targeted_high_degree_compromise(graph, compromise_fraction)
    else:
        raise ValueError(f"unsupported compromise_type: {compromise_type}")

    # Phase A: pre-alarm baseline.
    pre_candidates = candidate_paths(
        graph=graph,
        source=source,
        target=target,
        seed=f"{seed}:pre-alarm",
        k=route_count * 4,
    )

    pre_alarm_result = select_greedy_diverse(
        candidates=pre_candidates,
        route_count=route_count,
        seed=f"{seed}:pre-alarm",
        fractal_id=fractal_id,
        alpha=0.5,
        beta=0.5,
    )

    pre_alarm_paths = pre_alarm_result["selected_paths"]
    pre_alarm_states = pre_alarm_result["selected_states"]

    # Phase B/C/D: anomaly -> Lemonade purge/rewrite -> Dome/Nix reset.
    anomaly_detected = True
    memory_rewrite = True
    purge_triggered = True
    reset_epoch_pre = 0
    reset_epoch_post = 1

    # Phase E: post-reset candidates. Same pool for all reset policies.
    post_candidates = candidate_paths(
        graph=graph,
        source=source,
        target=target,
        seed=f"{seed}:post-reset:epoch-{reset_epoch_post}",
        k=route_count * 4,
    )

    random_reset_paths = random_select_paths(
        candidates=post_candidates,
        route_count=route_count,
        seed=f"{seed}:random_multipath_reset:epoch-{reset_epoch_post}",
    )
    random_reset_states = derive_path_states(
        random_reset_paths,
        seed=f"{seed}:random_multipath_reset:epoch-{reset_epoch_post}",
        fractal_id=fractal_id,
    )

    state_aware_reset_result = select_greedy_diverse(
        candidates=post_candidates,
        route_count=route_count,
        seed=f"{seed}:state_aware_reset:epoch-{reset_epoch_post}",
        fractal_id=fractal_id,
        alpha=0.5,
        beta=0.5,
    )
    state_aware_reset_paths = state_aware_reset_result["selected_paths"]
    state_aware_reset_states = state_aware_reset_result["selected_states"]

    lemonade_reset_result = select_lemonade_reset_paths(
        candidates=post_candidates,
        route_count=route_count,
        seed=f"{seed}:lemonade_reset:epoch-{reset_epoch_post}",
        pre_alarm_paths=pre_alarm_paths,
        fractal_id=fractal_id,
        alpha=0.35,
        beta=0.35,
        gamma=0.30,
    )
    lemonade_reset_paths = lemonade_reset_result["selected_paths"]
    lemonade_reset_states = lemonade_reset_result["selected_states"]

    result: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "seed": seed,
        "source": source,
        "target": target,
        "compromise_type": compromise_type,
        "compromise_fraction": compromise_fraction,
        "compromised_node_count": len(compromised),
        "total_node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "route_count": route_count,
        "fractal_id": fractal_id,
        "anomaly_detected": anomaly_detected,
        "memory_rewrite": memory_rewrite,
        "purge_triggered": purge_triggered,
        "reset_epoch_pre": reset_epoch_pre,
        "reset_epoch_post": reset_epoch_post,
        "pre_alarm_path_count": len(pre_alarm_paths),
        "post_candidate_count": len(post_candidates),
    }

    policies = [
        ("random_multipath_reset", random_reset_paths, random_reset_states),
        ("state_aware_reset", state_aware_reset_paths, state_aware_reset_states),
        ("lemonade_reset", lemonade_reset_paths, lemonade_reset_states),
    ]

    for policy_name, paths, states in policies:
        path_break = post_reset_path_distance_from_pre_alarm(paths, pre_alarm_paths)
        state_break = state_break_distance(pre_alarm_states, states)
        state_continuity = 1.0 - state_break

        exposure = evaluate_policy_exposure(paths, compromised)
        lane_collapse = lane_collapse_rate(paths)
        summary = summarize_paths(paths)

        result[f"{policy_name}:post_reset_path_distance_from_pre_alarm"] = path_break
        result[f"{policy_name}:state_break_distance"] = state_break
        result[f"{policy_name}:state_continuity_score"] = state_continuity
        result[f"{policy_name}:lane_collapse_rate"] = lane_collapse
        result[f"{policy_name}:path_overlap"] = summary.get("path_overlap", 0.0)
        result[f"{policy_name}:unique_path_ratio"] = summary.get("unique_path_ratio", 0.0)
        result[f"{policy_name}:clean_path_ratio"] = exposure.get("clean_path_ratio", 0.0)
        result[f"{policy_name}:path_compromise_rate"] = exposure.get("path_compromise_rate", 0.0)
        result[f"{policy_name}:mean_compromised_nodes_per_path"] = exposure.get(
            "mean_compromised_nodes_per_path",
            0.0,
        )

    # Convenience deltas for success evaluation.
    result["delta_lemonade_vs_state_aware:path_break"] = (
        result["lemonade_reset:post_reset_path_distance_from_pre_alarm"]
        - result["state_aware_reset:post_reset_path_distance_from_pre_alarm"]
    )
    result["delta_lemonade_vs_random:path_break"] = (
        result["lemonade_reset:post_reset_path_distance_from_pre_alarm"]
        - result["random_multipath_reset:post_reset_path_distance_from_pre_alarm"]
    )

    return result


def run_reset_experiment_suite(
    config_path: str,
    seeds: List[str],
    compromise_fractions: List[float] | None = None,
    compromise_types: List[str] | None = None,
    csv_path: str = "outputs/compare_reset_v01.csv",
    json_path: str = "outputs/compare_reset_v01.json",
) -> None:
    """
    Run reset experiment suite and output CSV + JSON.
    """
    config = json.loads(Path(config_path).read_text())

    if compromise_fractions is None:
        compromise_fractions = [0.20]

    if compromise_types is None:
        compromise_types = ["random", "targeted"]

    results = []

    for seed in seeds:
        for compromise_type in compromise_types:
            for compromise_fraction in compromise_fractions:
                results.append(
                    run_reset_experiment_phases(
                        config=config,
                        seed=seed,
                        compromise_fraction=compromise_fraction,
                        compromise_type=compromise_type,
                    )
                )

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    if results:
        with csv_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)

    json_out.write_text(json.dumps({
        "schema_version": "1.0.0",
        "experiment": "lemonade-reset-continuity-break",
        "results": results,
        "limitations": [
            "v1.0.0 models memory rewrite and purge as simulation-level continuity break",
            "no oracle compromise knowledge is used by lemonade_reset",
            "adversarial exposure metrics are secondary diagnostics",
            "no physical cold-boot resistance claim",
            "no security or resilience claim",
        ],
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total runs: {len(results)}")


if __name__ == "__main__":
    run_reset_experiment_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        compromise_fractions=[0.20],
        compromise_types=["random", "targeted"],
    )
