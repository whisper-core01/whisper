"""
WHISPER v1.3.4 — Compare adaptive network-aware redundancy.

Compares adaptive redundancy profiles over synthetic local network conditions.

The simulator reuses v1.3.2 custody/redundancy pressure routing, but derives:
- redundancy_factor
- custody_rounds
- receive_mode

from local non-oracle network symptoms.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List

from adaptive_redundancy_policy_v01 import (
    NetworkSymptoms,
    build_adaptive_redundancy_profile,
)
from compare_redundancy_pressure_v01 import simulate_redundant_message
from sol_link_magnetic_policy_v01 import deterministic_unit_interval


DEFAULT_NETWORK_PROFILES = ["good", "normal", "bad", "very_bad"]


def synthetic_network_symptoms(profile: str, seed: str) -> NetworkSymptoms:
    """
    Deterministic local symptom generator.
    Non-oracle: does not use compromise labels.
    """
    if profile == "good":
        base = 0.10
    elif profile == "normal":
        base = 0.35
    elif profile == "bad":
        base = 0.65
    elif profile == "very_bad":
        base = 0.90
    else:
        raise ValueError(f"unsupported profile: {profile}")

    def jittered(name: str) -> float:
        noise = deterministic_unit_interval(seed, profile, name) * 0.20 - 0.10
        return max(0.0, min(1.0, base + noise))

    return NetworkSymptoms(
        latency_risk=jittered("latency"),
        jitter_risk=jittered("jitter"),
        timeout_risk=jittered("timeout"),
        signal_loss_risk=jittered("signal"),
        receiver_capacity_risk=jittered("capacity"),
    )


def compare_adaptive_redundancy(
    config: Dict,
    seed: str,
    condition: str,
    network_profile: str,
    compromise_fraction: float = 0.20,
    required_fragments: int = 100,
    magnet_strength: float = 6.0,
    wandering_strength: float = 0.5,
    hop_budget: int = 12,
) -> Dict:
    symptoms = synthetic_network_symptoms(network_profile, seed)
    profile = build_adaptive_redundancy_profile(symptoms)

    row = simulate_redundant_message(
        config=config,
        seed=f"{seed}:{network_profile}",
        condition=condition,
        compromise_fraction=compromise_fraction,
        required_fragments=required_fragments,
        redundancy_factor=profile.redundancy_factor,
        magnet_strength=magnet_strength,
        wandering_strength=wandering_strength,
        hop_budget=hop_budget,
        custody_rounds=profile.custody_rounds,
    )

    row["network_profile"] = network_profile
    row["network_risk"] = profile.network_risk
    row["adaptive_redundancy_factor"] = profile.redundancy_factor
    row["adaptive_custody_rounds"] = profile.custody_rounds
    row["adaptive_repair_budget_factor"] = profile.repair_budget_factor
    row["receive_mode"] = profile.receive_mode

    return row


def run_adaptive_redundancy_suite(
    config_path: str,
    seeds: List[str],
    conditions: List[str],
    network_profiles: List[str] | None = None,
    compromise_fraction: float = 0.20,
    required_fragments: int = 100,
    magnet_strength: float = 6.0,
    wandering_strength: float = 0.5,
    hop_budget: int = 12,
    csv_path: str = "outputs/compare_adaptive_redundancy_v01.csv",
    json_path: str = "outputs/compare_adaptive_redundancy_v01.json",
) -> None:
    config = json.loads(Path(config_path).read_text())

    if network_profiles is None:
        network_profiles = DEFAULT_NETWORK_PROFILES

    rows = []

    for seed in seeds:
        for condition in conditions:
            for network_profile in network_profiles:
                rows.append(
                    compare_adaptive_redundancy(
                        config=config,
                        seed=seed,
                        condition=condition,
                        network_profile=network_profile,
                        compromise_fraction=compromise_fraction,
                        required_fragments=required_fragments,
                        magnet_strength=magnet_strength,
                        wandering_strength=wandering_strength,
                        hop_budget=hop_budget,
                    )
                )

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    if rows:
        with csv_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    json_out.write_text(json.dumps({
        "schema_version": "1.3.4",
        "experiment": "adaptive-network-aware-redundancy",
        "results": rows,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total rows: {len(rows)}")


if __name__ == "__main__":
    run_adaptive_redundancy_suite(
        config_path="experiments/example.json",
        seeds=[f"adaptive-{i:03d}" for i in range(30)],
        conditions=["random", "targeted", "behavioral"],
        network_profiles=DEFAULT_NETWORK_PROFILES,
        compromise_fraction=0.20,
        required_fragments=100,
        magnet_strength=6.0,
        wandering_strength=0.5,
        hop_budget=12,
    )
