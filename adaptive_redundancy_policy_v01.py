"""
WHISPER v1.3.4 — Adaptive Network-Aware Redundancy.

Adapts:
- redundancy_factor
- custody_rounds
- repair_budget
- receive_mode

from local, non-oracle symptoms:
- latency
- jitter
- timeout rate
- signal loss
- receiver capacity

No adversarial attribution.
No Reticulum topology exposure.
No missing fragment disclosure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ReceiveMode = Literal["BUFFERED", "STREAMING"]


@dataclass(frozen=True)
class NetworkSymptoms:
    latency_risk: float
    jitter_risk: float
    timeout_risk: float
    signal_loss_risk: float
    receiver_capacity_risk: float = 0.0


@dataclass(frozen=True)
class AdaptiveRedundancyProfile:
    network_risk: float
    redundancy_factor: float
    custody_rounds: int
    repair_budget_factor: float
    receive_mode: ReceiveMode


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def compute_network_risk(symptoms: NetworkSymptoms) -> float:
    """
    Local non-oracle network risk.

    A high value means local delivery conditions are poor.
    It does not imply compromise or attack.
    """
    risk = (
        0.25 * clamp(symptoms.latency_risk)
        + 0.25 * clamp(symptoms.jitter_risk)
        + 0.30 * clamp(symptoms.timeout_risk)
        + 0.20 * clamp(symptoms.signal_loss_risk)
    )

    # Capacity does not mean network failure, but it influences receive mode
    # and repair pressure slightly.
    risk = 0.85 * risk + 0.15 * clamp(symptoms.receiver_capacity_risk)

    return clamp(risk)


def adaptive_redundancy_factor(
    network_risk: float,
    min_factor: float = 1.25,
    max_factor: float = 1.40,
) -> float:
    if min_factor < 1.0:
        raise ValueError("min_factor must be >= 1.0")
    if max_factor < min_factor:
        raise ValueError("max_factor must be >= min_factor")

    return min_factor + (max_factor - min_factor) * clamp(network_risk)


def adaptive_custody_rounds(
    network_risk: float,
    min_rounds: int = 5,
    max_rounds: int = 7,
) -> int:
    if min_rounds < 1:
        raise ValueError("min_rounds must be >= 1")
    if max_rounds < min_rounds:
        raise ValueError("max_rounds must be >= min_rounds")

    span = max_rounds - min_rounds
    return min_rounds + round(span * clamp(network_risk))


def adaptive_repair_budget_factor(
    network_risk: float,
    min_factor: float = 0.05,
    max_factor: float = 0.20,
) -> float:
    return min_factor + (max_factor - min_factor) * clamp(network_risk)


def adaptive_receive_mode(
    symptoms: NetworkSymptoms,
    threshold: float = 0.65,
) -> ReceiveMode:
    """
    If receiver capacity is constrained, use streaming/read-memory receive.
    """
    if clamp(symptoms.receiver_capacity_risk) >= threshold:
        return "STREAMING"

    return "BUFFERED"


def build_adaptive_redundancy_profile(
    symptoms: NetworkSymptoms,
    min_redundancy: float = 1.25,
    max_redundancy: float = 1.40,
    min_custody_rounds: int = 5,
    max_custody_rounds: int = 7,
) -> AdaptiveRedundancyProfile:
    network_risk = compute_network_risk(symptoms)

    return AdaptiveRedundancyProfile(
        network_risk=network_risk,
        redundancy_factor=adaptive_redundancy_factor(
            network_risk,
            min_factor=min_redundancy,
            max_factor=max_redundancy,
        ),
        custody_rounds=adaptive_custody_rounds(
            network_risk,
            min_rounds=min_custody_rounds,
            max_rounds=max_custody_rounds,
        ),
        repair_budget_factor=adaptive_repair_budget_factor(network_risk),
        receive_mode=adaptive_receive_mode(symptoms),
    )
