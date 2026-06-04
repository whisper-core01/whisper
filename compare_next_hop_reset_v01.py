"""
WHISPER v1.2.0 — Compare local degradation-aware Lemonade reselection.

This comparator tests whether relationship-scoped next-hop degradation
signals improve post-reset behavioral stability.

Conditions:
- random: random 20% compromised nodes
- targeted: high-degree 20% compromised nodes
- behavioral: no compromise oracle; evaluates behavioral degradation avoidance

Policies:
- lemonade_reset
- node_score_aware_delta_0.90
- degradation_aware_delta_0.90
- degradation_aware_delta_0.85
- degradation_aware_delta_0.80

Primary v1.2.0 success is behavioral:
- continuity_retention >= 0.80
- mean_node_score_risk_per_path < lemonade_reset
- mean_degradation_risk_per_path < lemonade_reset
- lane_collapse_rate <= 0.20

Adversarial exposure is observed, not required.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from adversary_v01 import evaluate_policy_exposure, random_compromise
from compare_reset_v01 import targeted_high_degree_compromise
from compare_node_score_reset_v01 import build_pre_reset_flv_scores
from flv_node_score_policy_v01 import (
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
from next_hop_degradation_policy_v01 import (
    build_degradation_table,
    mean_degradation_risk_per_path,
    select_degradation_aware_paths,
)
from path_sampler_v01 import candidate_paths, select_source_target
from state_aware_policy_v01 import select_greedy_diverse
from state_mapping_v01 import lane_collapse_rate
from topology_v01 import generate_topology


NodePath = List[str]
DegradationTable = Dict[Tuple[str, str], float]

DEFAULT_DELTAS = [0.90, 0.85, 0.80]
DEFAULT_PRE_RESET_EPOCHS = 5


def _compromised_nodes_for_condition(
    graph: Any,
    seed: str,
    compromise_fraction: float,
    condition_type: str,
) -> Set[str]:
    """
    Return compromised nodes for adversarial evaluation.

    behavioral condition intentionally uses no compromise oracle.
    It evaluates degradation avoidance as a behavioral property.
    """
    if condition_type == "random":
        return set(random_compromise(graph.node_count, compromise_fraction, seed))

    if condition_type == "targeted":
        return set(targeted_high_degree_compromise(graph, compromise_fraction))

    if condition_type == "behavioral":
        return set()

    raise ValueError(f"unsupported condition_type: {condition_type}")


def _policy_metrics(
    policy_name: str,
    paths: List[NodePath],
    states: List[str],
    pre_alarm_paths: List[NodePath],
    pre_alarm_states: List[str],
    compromised_nodes: Set[str],
    node_scores: Dict[str, float],
    degradation_table: DegradationTable,
    lemonade_path_break: float,
) -> Dict[str, Any]:
    """
    Compute continuity, exposure, FLV and degradation metrics.
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
        "mean_degradation_risk_per_path": mean_degradation_risk_per_path(
            paths,
            degradation_table,
        ),
    }


def compare_next_hop_reset(
    config: Dict[str, Any],
    seed: str,
    compromise_fraction: float = 0.20,
    condition_type: str = "random",
    deltas: List[float] | None = None,
    pre_reset_epochs: int = DEFAULT_PRE_RESET_EPOCHS,
) -> Dict[str, Any]:
    """
    Run one v1.2.0 comparison for a seed and condition.

    condition_type:
    - random
    - targeted
    - behavioral
    """
    if deltas is None:
        deltas = DEFAULT_DELTAS

    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:pair")

    policy_cfg = config.get("policy", {})
    route_count = int(policy_cfg.get("route_count", 3))
    fractal_id = int(policy_cfg.get("fractal_count", 36))

    compromised_nodes = _compromised_nodes_for_condition(
        graph=graph,
        seed=seed,
        compromise_fraction=compromise_fraction,
        condition_type=condition_type,
    )

    # Phase A: pre-alarm selection.
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

    # Local synthetic FLV warmup from v1.1.0.
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

    # Phase E: post-reset candidate pool shared by all policies.
    post_candidates = candidate_paths(
        graph=graph,
        source=source,
        target=target,
        seed=f"{seed}:post-reset:epoch-1",
        k=route_count * 4,
    )

    # Relationship-scoped degradation table for post-reset epoch.
    degradation_table = build_degradation_table(
        candidates=post_candidates,
        node_scores=node_scores,
        seed=f"{seed}:degradation:epoch-1",
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
        degradation_table=degradation_table,
        lemonade_path_break=lemonade_path_break,
    )
    baseline_metrics["delta"] = None
    baseline_metrics["success_continuity_retention"] = True
    baseline_metrics["success_node_score_risk_reduced"] = False
    baseline_metrics["success_degradation_risk_reduced"] = False
    baseline_metrics["success_candidate"] = False
    comparison.append(baseline_metrics)

    lemonade_node_score_risk = baseline_metrics["mean_node_score_risk_per_path"]
    lemonade_degradation_risk = baseline_metrics["mean_degradation_risk_per_path"]

    # v1.1.0 reference: node-score-aware delta 0.90
    node_score_result = select_node_score_aware_paths(
        candidates=post_candidates,
        route_count=route_count,
        seed=f"{seed}:node_score_aware:delta-0.90:epoch-1",
        pre_alarm_paths=pre_alarm_paths,
        node_scores=node_scores,
        delta=0.90,
        fractal_id=fractal_id,
    )

    node_score_metrics = _policy_metrics(
        policy_name="node_score_aware_delta_0.90",
        paths=node_score_result["selected_paths"],
        states=node_score_result["selected_states"],
        pre_alarm_paths=pre_alarm_paths,
        pre_alarm_states=pre_alarm_states,
        compromised_nodes=compromised_nodes,
        node_scores=node_scores,
        degradation_table=degradation_table,
        lemonade_path_break=lemonade_path_break,
    )
    node_score_metrics["delta"] = 0.90
    node_score_metrics["success_continuity_retention"] = (
        node_score_metrics["continuity_retention_vs_lemonade"] >= 0.80
    )
    node_score_metrics["success_node_score_risk_reduced"] = (
        node_score_metrics["mean_node_score_risk_per_path"] < lemonade_node_score_risk
    )
    node_score_metrics["success_degradation_risk_reduced"] = (
        node_score_metrics["mean_degradation_risk_per_path"] < lemonade_degradation_risk
    )
    node_score_metrics["success_candidate"] = False
    comparison.append(node_score_metrics)

    for delta in deltas:
        result = select_degradation_aware_paths(
            candidates=post_candidates,
            route_count=route_count,
            seed=f"{seed}:degradation_aware:delta-{delta}:epoch-1",
            pre_alarm_paths=pre_alarm_paths,
            node_scores=node_scores,
            delta=delta,
            fractal_id=fractal_id,
        )

        metrics = _policy_metrics(
            policy_name=f"degradation_aware_delta_{delta:.2f}",
            paths=result["selected_paths"],
            states=result["selected_states"],
            pre_alarm_paths=pre_alarm_paths,
            pre_alarm_states=pre_alarm_states,
            compromised_nodes=compromised_nodes,
            node_scores=node_scores,
            degradation_table=degradation_table,
            lemonade_path_break=lemonade_path_break,
        )

        metrics["delta"] = delta
        metrics["success_continuity_retention"] = (
            metrics["continuity_retention_vs_lemonade"] >= 0.80
        )
        metrics["success_node_score_risk_reduced"] = (
            metrics["mean_node_score_risk_per_path"] < lemonade_node_score_risk
        )
        metrics["success_degradation_risk_reduced"] = (
            metrics["mean_degradation_risk_per_path"] < lemonade_degradation_risk
        )
        metrics["success_candidate"] = (
            metrics["success_continuity_retention"]
            and metrics["success_node_score_risk_reduced"]
            and metrics["success_degradation_risk_reduced"]
            and metrics["lane_collapse_rate"] <= 0.20
        )

        comparison.append(metrics)

    return {
        "schema_version": "1.2.0",
        "experiment": "local-degradation-aware-lemonade-reselection",
        "seed": seed,
        "source": source,
        "target": target,
        "condition_type": condition_type,
        "compromise_fraction": compromise_fraction,
        "compromised_node_count": len(compromised_nodes),
        "total_node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "route_count": route_count,
        "fractal_id": fractal_id,
        "pre_reset_epochs": pre_reset_epochs,
        "delta_grid": deltas,
        "degradation_model": {
            "scope": "directed next-hop relationship",
            "behavioral_weights": {
                "timeout": 0.40,
                "latency": 0.30,
                "forwarding_failure": 0.30,
            },
            "effective_degradation": {
                "synthetic_behavioral_signal": 0.70,
                "node_score_risk": 0.30,
            },
            "oracle_labels_used": False,
        },
        "pre_alarm_path_count": len(pre_alarm_paths),
        "post_candidate_count": len(post_candidates),
        "comparison": comparison,
        "limitations": [
            "local selector-side relationship degradation only",
            "synthetic deterministic behavioral symptoms",
            "no harassment detection",
            "no revocation ladder",
            "no distributed FLV synchronization",
            "no global node reputation",
            "no oracle compromise knowledge",
        ],
    }


def flatten_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []

    base = {
        "schema_version": result["schema_version"],
        "experiment": result["experiment"],
        "seed": result["seed"],
        "source": result["source"],
        "target": result["target"],
        "condition_type": result["condition_type"],
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


def run_next_hop_reset_suite(
    config_path: str,
    seeds: List[str],
    compromise_fractions: List[float] | None = None,
    condition_types: List[str] | None = None,
    deltas: List[float] | None = None,
    pre_reset_epochs: int = DEFAULT_PRE_RESET_EPOCHS,
    csv_path: str = "outputs/compare_next_hop_reset_v01.csv",
    json_path: str = "outputs/compare_next_hop_reset_v01.json",
) -> None:
    config = json.loads(Path(config_path).read_text())

    if compromise_fractions is None:
        compromise_fractions = [0.20]

    if condition_types is None:
        condition_types = ["random", "targeted", "behavioral"]

    if deltas is None:
        deltas = DEFAULT_DELTAS

    results = []
    csv_rows = []

    for seed in seeds:
        for condition_type in condition_types:
            for compromise_fraction in compromise_fractions:
                result = compare_next_hop_reset(
                    config=config,
                    seed=seed,
                    compromise_fraction=compromise_fraction,
                    condition_type=condition_type,
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
        "schema_version": "1.2.0",
        "experiment": "local-degradation-aware-lemonade-reselection",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total experiment conditions: {len(results)}")
    print(f"Total CSV rows: {len(csv_rows)}")


if __name__ == "__main__":
    run_next_hop_reset_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        compromise_fractions=[0.20],
        condition_types=["random", "targeted", "behavioral"],
    )
