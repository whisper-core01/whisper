"""
WHISPER v1.3.2 — Redundancy Compensation.

This module models controlled over-fragmentation.

Goal:
- compensate pressure-field delivery loss
- preserve lower exposure
- avoid deterministic retransmission
- reconstruct from threshold N out of ceil(N * redundancy_factor)

This is a simulation layer, not a cryptographic erasure coding implementation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RedundancyPlan:
    required_fragments: int
    redundancy_factor: float
    emitted_fragments: int
    recovery_fragments: int
    reconstruction_threshold: int


def build_redundancy_plan(
    required_fragments: int,
    redundancy_factor: float = 1.10,
) -> RedundancyPlan:
    if required_fragments < 1:
        raise ValueError("required_fragments must be >= 1")

    if redundancy_factor < 1.0:
        raise ValueError("redundancy_factor must be >= 1.0")

    emitted = math.ceil(required_fragments * redundancy_factor)
    recovery = emitted - required_fragments

    return RedundancyPlan(
        required_fragments=required_fragments,
        redundancy_factor=redundancy_factor,
        emitted_fragments=emitted,
        recovery_fragments=recovery,
        reconstruction_threshold=required_fragments,
    )


def fragment_role(index: int, plan: RedundancyPlan) -> str:
    if index < 0 or index >= plan.emitted_fragments:
        raise ValueError("fragment index out of range")

    if index < plan.required_fragments:
        return "primary"

    return "recovery"


def can_reconstruct(delivered_fragments: int, plan: RedundancyPlan) -> bool:
    return delivered_fragments >= plan.reconstruction_threshold


def reconstruction_margin(delivered_fragments: int, plan: RedundancyPlan) -> int:
    return delivered_fragments - plan.reconstruction_threshold


def effective_reconstruction_ratio(
    delivered_fragments: int,
    plan: RedundancyPlan,
) -> float:
    if plan.reconstruction_threshold <= 0:
        return 0.0

    return min(delivered_fragments / plan.reconstruction_threshold, 1.0)


def summarize_fragment_delivery(
    delivered_by_index: Dict[int, bool],
    plan: RedundancyPlan,
) -> Dict[str, object]:
    delivered_total = sum(1 for ok in delivered_by_index.values() if ok)

    primary_delivered = sum(
        1
        for index, ok in delivered_by_index.items()
        if ok and fragment_role(index, plan) == "primary"
    )

    recovery_delivered = sum(
        1
        for index, ok in delivered_by_index.items()
        if ok and fragment_role(index, plan) == "recovery"
    )

    return {
        "required_fragments": plan.required_fragments,
        "emitted_fragments": plan.emitted_fragments,
        "recovery_fragments": plan.recovery_fragments,
        "redundancy_factor": plan.redundancy_factor,
        "delivered_total": delivered_total,
        "primary_delivered": primary_delivered,
        "recovery_delivered": recovery_delivered,
        "message_reconstructed": can_reconstruct(delivered_total, plan),
        "reconstruction_margin": reconstruction_margin(delivered_total, plan),
        "effective_reconstruction_ratio": effective_reconstruction_ratio(delivered_total, plan),
    }
