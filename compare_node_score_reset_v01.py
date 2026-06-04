"""
WHISPER v1.1.0 — Compare node-score-aware Lemonade reselection.

This comparator tests whether local FLV node-score-aware reselection can
preserve Lemonade's continuity-break effect while reducing traversal
through high-risk node-score regions.

Scope:
- local selector-side FLV score table
- deterministic synthetic FLV warmup
- no oracle compromise knowledge
- no distributed consensus
- no gossip
- no revocation ladder
- no harassment detection
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from adversary_v01 import evaluate_policy_exposure, random_compromise
from compare_reset_v01 import targeted_high_degree_compromise
from flv_node_score_policy_v01 import (
    generate_synthetic_flv_scores,
    healthy_node_ratio,
    mean_node_score_risk_per_path,
    mean_raw_node_score_per_path,
    select_node_score_aware_paths,
)
from lemonade_reset_policy_v01 import (
    post_reset_path_distance_from_pre_alarm,
    select_lemonade_reset_paths,
    state_break_distance,
)
from metrics_v01 import summarize_paths
from path_sampler_v01 import candidate_paths, select_source_target
from state_aware_policy_v01 import select_greedy_diverse
from state_mapping_v01 import lane_collapse_rate
from topology_v01 import generate_topology


NodePath = List[str]

DEFAULT_DELTAS = [0.90, 0.75, 0.60, 0.50]
DEFAULT_PRE_RESET_EPOCHS = 5


def _policy_metrics(
    policy_name: str,
    paths: List[NodePath],
    states: List[str],
    pre_alarm_paths: List[NodePath],
    pre_alarm_states: List[str],
    compromised_nodes: set[str],
    node_scores: Dict[str, float],
    lemonade_path_break: float,
) -> Dict[str, Any]:
    """
    Compute path, continuity, exposure and FLV node-score metrics.
    """
    path_break = post_reset_path_distance_from_pre_alarm(paths, pre_alarm_paths)
    state_break = state_break_distance(pre_alarm_states, states)
    summary = summarize_paths(paths)
    exposure = evaluate_policy_exposure(paths, compromised_nodes)

    continuity_retention = (
        path_break / lemonade_path_break
        if lemonade_path_break > 0.0
        else 0.0
    )

    return {
        "policy": policy_name,
        "path_count": len(paths),
        "post_reset_path_distance_from_pre_alarm": path_break,
        "continuity_retention_vs_lemonade": continuity_retention,
        "state_break_distance": state_break,
        "state_continuity_score": 1.0 - state_break,
        "lane_collapse_rate": lane_collapse_rate(paths),
        "path_overlap": summary.get("path_overlap", 0.0),
        "unique_path_ratio": summary.get("unique_path_ratio", 0.0),
        "clean_path_ratio": exposure.get("clean_path_ratio", 0.0),
        "path_compromise_rate": exposure.get("path_compromise_rate", 0.0),
        "mean_compromised_nodes_per_path": exposure.get(
            "mean_compromised_nodes_per_path",
            0.0,
        ),
        "mean_node_score_risk_per_path": mean_node_score_risk_per_path(
            paths,
            node_scores,
        ),
        "mean_raw_node_score_per_path": mean_raw_node_score_per_path(
            paths,
            node_scores,
        ),
        "healthy_node_ratio": healthy_node_ratio(paths, node_scores),
    }


def build_pre_reset_flv_scores(
    graph: Any,
    source: str,
    target: str,
    route_count: int,
    fractal_id: int,
    seed: str,
    pre_reset_epochs: int = DEFAULT_PRE_RESET_EPOCHS,
) -> Dict[str, Any]:
    """
    Build deterministic synthetic FLV scores using pre-reset path usage.

    All nodes start at 0.0. For each pre-reset epoch, standard WHISPER
    state/path-diverse selection picks route_count paths. Selected nodes
    receive +0.5; unselected nodes receive -0.1.
    """
    selected_paths_by_epoch: List[List[NodePath]] = []

    for epoch in range(pre_reset_epochs):
        candidates = candidate_paths(
            graph=graph,
            source=source,
            target=target,
            seed=f"{seed}:flv-warmup:{epoch}",
            k=route_count * 4,
        )

        selection = select_greedy_diverse(
            candidates=candidates,
            route_count=route_count,
            seed=f"{seed}:flv-warmup:{epoch}",
            fractal_id=fractal_id,
            alpha=0.5,
            beta=0.5,
        )

        selected_paths_by_epoch.append(selection["selected_paths"])

    node_scores = generate_synthetic_flv_scores(
        all_nodes=list(graph.nodes),
        selected_paths_by_epoch=selected_paths_by_epoch,
    )

    return {
        "pre_reset_epochs": pre_reset_epochs,
        "selected_paths_by_epoch": selected_paths_by_epoch,
        "node_scores": node_scores,
    }


def compare_node_score_reset(
    config: Dict[str, Any],
    seed: str,
    compromise_fraction: float = 0.20,
    compromise_type: str = "random",
    deltas: List[float] | None = None,
    pre_reset_epochs: int = DEFAULT_PRE_RESET_EPOCHS,
) -> Dict[str, Any]:
    """
    Run one v1.1.0 comparison for a seed and adversary condition.

    Compares:
    - lemonade_reset baseline
    - node_score_aware_lemonade_reset for each delta
    """
    if deltas is None:
        deltas = DEFAULT_DELTAS

    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:pair")

    policy_cfg = config.get("policy", {})
    route_count = int(policy_cfg.get("route_count", 3))
    fractal_id = int(policy_cfg.get("fractal_count", 36))

    if compromise_type == "random":
        compromised_nodes = random_compromise(
            graph.node_count,
            compromise_fraction,
            seed,
        )
    elif compromise_type == "targeted":
        compromised_nodes = targeted_high_degree_compromise(
            graph,
            compromise_fraction,
        )
    else:
        raise ValueError(f"unsupported compromise_type: {compromise_type}")

    # Phase A: pre-alarm paths.
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

    # Synthetic local FLV warmup.
    flv = build_pre_reset_flv_scores(
        graph=graph,
        source=source,
        target=target,
        route_count=route_count,
        fractal_id=fractal_id,
        seed=seed,
        pre_reset_epochs=pre_reset_epochs,
    )
    node_scores = flv["node_scores"]

    # Phase E: post-reset candidate pool, same for all policies.
    post_candidates = candidate_paths(
        graph=graph,
        source=source,
        target=target,
        seed=f"{seed}:post-reset:epoch-1",
        k=route_count * 4,
    )

    lemonade_result = select_lemonade_reset_paths(
        candidates=post_candidates,
        route_count=route_count,
        seed=f"{seed}:lemonade_reset:epoch-1",
        pre_alarm_paths=pre_alarm_paths,
        fractal_id=fractal_id,
        alpha=0.35,
        beta=0.35,
        gamma=0.30,
    )

    lemonade_paths = lemonade_result["selected_paths"]
    lemonade_states = lemonade_result["selected_states"]
    lemonade_path_break = post_reset_path_distance_from_pre_alarm(
        lemonade_paths,
        pre_alarm_paths,
    )

    comparison: List[Dict[str, Any]] = []

    baseline_metrics = _policy_metrics(
        policy_name="lemonade_reset",
        paths=lemonade_paths,
        states=lemonade_states,
        pre_alarm_paths=pre_alarm_paths,
        pre_alarm_states=pre_alarm_states,
        compromised_nodes=compromised_nodes,
        node_scores=node_scores,
        lemonade_path_break=lemonade_path_break,
    )
    baseline_metrics["delta"] = None
    baseline_metrics["success_continuity_retention"] = True
    baseline_metrics["success_node_score_risk_reduced"] = False
    baseline_metrics["success_candidate"] = False
    comparison.append(baseline_metrics)

    lemonade_node_score_risk = baseline_metrics["mean_node_score_risk_per_path"]

    for delta in deltas:
        result = select_node_score_aware_paths(
            candidates=post_candidates,
            route_count=route_count,
            seed=f"{seed}:node_score_aware:delta-{delta}:epoch-1",
            pre_alarm_paths=pre_alarm_paths,
            node_scores=node_scores,
            delta=delta,
            fractal_id=fractal_id,
        )

        metrics = _policy_metrics(
            policy_name=f"node_score_aware_delta_{delta:.2f}",
            paths=result["selected_paths"],
            states=result["selected_states"],
            pre_alarm_paths=pre_alarm_paths,
            pre_alarm_states=pre_alarm_states,
            compromised_nodes=compromised_nodes,
            node_scores=node_scores,
            lemonade_path_break=lemonade_path_break,
        )

        metrics["delta"] = delta
        metrics["success_continuity_retention"] = (
            metrics["continuity_retention_vs_lemonade"] >= 0.80
        )
        metrics["success_node_score_risk_reduced"] = (
            metrics["mean_node_score_risk_per_path"] < lemonade_node_score_risk
        )
        metrics["success_candidate"] = (
            metrics["success_continuity_retention"]
            and metrics["success_node_score_risk_reduced"]
            and metrics["lane_collapse_rate"] <= 0.20
            and metrics["path_overlap"] <= baseline_metrics["path_overlap"] * 1.25 + 1e-12
        )

        comparison.append(metrics)

    return {
        "schema_version": "1.1.0",
        "experiment": "node-score-aware-lemonade-reselection",
        "seed": seed,
        "source": source,
        "target": target,
        "compromise_type": compromise_type,
        "compromise_fraction": compromise_fraction,
        "compromised_node_count": len(compromised_nodes),
        "total_node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "route_count": route_count,
        "fractal_id": fractal_id,
        "pre_reset_epochs": pre_reset_epochs,
        "delta_grid": deltas,
        "node_score_model": {
            "initial_score": 0.0,
            "selected_path_node_increment": 0.5,
            "inactive_decay": -0.1,
            "clamp": [-1.0, 5.0],
            "healthy_band": [0.0, 1.0],
        },
        "pre_alarm_path_count": len(pre_alarm_paths),
        "post_candidate_count": len(post_candidates),
        "comparison": comparison,
        "limitations": [
            "local selector-side FLV only",
            "synthetic deterministic load warmup",
            "no harassment detection",
            "no revocation ladder",
            "no distributed FLV synchronization",
            "no global node reputation",
            "no oracle compromise knowledge",
        ],
    }


def flatten_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flatten nested comparison rows for CSV output.
    """
    rows = []

    base = {
        "schema_version": result["schema_version"],
        "experiment": result["experiment"],
        "seed": result["seed"],
        "source": result["source"],
        "target": result["target"],
        "compromise_type": result["compromise_type"],
        "compromise_fraction": result["compromise_fraction"],
        "compromised_node_count": result["compromised_node_count"],
        "total_node_count": result["total_node_count"],
        "edge_count": result["edge_count"],
        "route_count": result["route_count"],
        "fractal_id": result["fractal_id"],
        "pre_reset_epochs": result["pre_reset_epochs"],
        "pre_alarm_path_count": result["pre_alarm_path_count"],
        "post_candidate_count": result["post_candidate_count"],
    }

    for row in result["comparison"]:
        out = dict(base)
        out.update(row)
        rows.append(out)

    return rows


def run_node_score_reset_suite(
    config_path: str,
    seeds: List[str],
    compromise_fractions: List[float] | None = None,
    compromise_types: List[str] | None = None,
    deltas: List[float] | None = None,
    pre_reset_epochs: int = DEFAULT_PRE_RESET_EPOCHS,
    csv_path: str = "outputs/compare_node_score_reset_v01.csv",
    json_path: str = "outputs/compare_node_score_reset_v01.json",
) -> None:
    """
    Run v1.1.0 comparison suite and output CSV + JSON.
    """
    config = json.loads(Path(config_path).read_text())

    if compromise_fractions is None:
        compromise_fractions = [0.20]

    if compromise_types is None:
        compromise_types = ["random", "targeted"]

    if deltas is None:
        deltas = DEFAULT_DELTAS

    results = []
    csv_rows = []

    for seed in seeds:
        for compromise_type in compromise_types:
            for compromise_fraction in compromise_fractions:
                result = compare_node_score_reset(
                    config=config,
                    seed=seed,
                    compromise_fraction=compromise_fraction,
                    compromise_type=compromise_type,
                    deltas=deltas,
                    pre_reset_epochs=pre_reset_epochs,
                )
                results.append(result)
                csv_rows.extend(flatten_result(result))

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    if csv_rows:
        with csv_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)

    json_out.write_text(json.dumps({
        "schema_version": "1.1.0",
        "experiment": "node-score-aware-lemonade-reselection",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total experiment conditions: {len(results)}")
    print(f"Total CSV rows: {len(csv_rows)}")


if __name__ == "__main__":
    run_node_score_reset_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        compromise_fractions=[0.20],
        compromise_types=["random", "targeted"],
    )
