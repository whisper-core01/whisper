"""
WHISPER v1.8.0 — Network Adaptive Switch v0.1

Purpose:
Select the most viable network medium automatically while preserving WHISPER
Core invariants.

Core doctrine:
The network is opportunistic.
The organs are stable.

Internet first.
4G/5G next.
LoRa last resort.

Switching is automatic and transparent to the user.

A switch must be justified by sustained degradation, not by a single spike.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Set


BearerName = Literal[
    "PRIMARY_INTERNET",
    "MOBILE_DATA_4G_5G",
    "LORA_RNODE",
    "NONE",
]

SwitchMode = Literal[
    "CONNECTED",
    "DEGRADED_SURVIVAL",
    "OFFLINE",
]

TransportStack = Literal[
    "RETICULUM_VOXMESH",
    "LORA_TEXT",
    "NONE",
]

PayloadKind = Literal[
    "text",
    "audio",
    "image",
    "video",
    "file",
    "event",
]


FULL_PAYLOADS: Set[str] = {
    "text",
    "audio",
    "image",
    "video",
    "file",
    "event",
}

TEXT_ONLY_PAYLOADS: Set[str] = {"text"}

IP_BEARERS: Set[str] = {
    "PRIMARY_INTERNET",
    "MOBILE_DATA_4G_5G",
}

BEARER_PRIORITY: List[str] = [
    "PRIMARY_INTERNET",
    "MOBILE_DATA_4G_5G",
    "LORA_RNODE",
]


@dataclass(frozen=True)
class BearerSample:
    bearer: BearerName
    available: bool
    latency_ms: int | None = None
    packet_loss_percent: int | None = None


@dataclass(frozen=True)
class AdaptiveThresholds:
    max_good_latency_ms: int = 250
    max_acceptable_loss_percent: int = 20
    sustained_bad_required: int = 3
    stable_recovery_required: int = 3


@dataclass
class BearerHistory:
    samples: Dict[str, List[BearerSample]] = field(default_factory=dict)

    def add(self, sample: BearerSample) -> None:
        self.samples.setdefault(sample.bearer, []).append(sample)

    def recent(self, bearer: BearerName, count: int) -> List[BearerSample]:
        return self.samples.get(bearer, [])[-count:]


@dataclass(frozen=True)
class SwitchDecision:
    bearer: BearerName
    mode: SwitchMode
    stack: TransportStack
    allowed_payloads: Set[str]
    switched: bool
    reason: str


@dataclass
class NetworkSwitchState:
    current_bearer: BearerName = "PRIMARY_INTERNET"
    mode: SwitchMode = "CONNECTED"
    stack: TransportStack = "RETICULUM_VOXMESH"
    allowed_payloads: Set[str] = field(default_factory=lambda: set(FULL_PAYLOADS))
    user_selected_network: bool = False
    exposed_wasm: bool = False
    changed_core_rails: bool = False
    touched_dome: bool = False
    participated_in_immunity: bool = False


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "network_adaptive_switch::"
        f"{test_name}"
    )


def sample_is_viable(sample: BearerSample, thresholds: AdaptiveThresholds) -> bool:
    if not sample.available:
        return False

    if sample.latency_ms is not None and sample.latency_ms < 0:
        return False

    if sample.packet_loss_percent is not None and sample.packet_loss_percent < 0:
        return False

    if sample.packet_loss_percent is not None:
        if sample.packet_loss_percent > thresholds.max_acceptable_loss_percent:
            return False

    return True


def sample_is_good(sample: BearerSample, thresholds: AdaptiveThresholds) -> bool:
    if not sample_is_viable(sample, thresholds):
        return False

    if sample.latency_ms is not None:
        if sample.latency_ms > thresholds.max_good_latency_ms:
            return False

    return True


def sustained_bad(
    history: BearerHistory,
    bearer: BearerName,
    thresholds: AdaptiveThresholds,
) -> bool:
    recent = history.recent(bearer, thresholds.sustained_bad_required)

    if len(recent) < thresholds.sustained_bad_required:
        return False

    return all(not sample_is_good(sample, thresholds) for sample in recent)


def stable_recovery(
    history: BearerHistory,
    bearer: BearerName,
    thresholds: AdaptiveThresholds,
) -> bool:
    recent = history.recent(bearer, thresholds.stable_recovery_required)

    if len(recent) < thresholds.stable_recovery_required:
        return False

    return all(sample_is_good(sample, thresholds) for sample in recent)


def latest_sample(
    history: BearerHistory,
    bearer: BearerName,
) -> BearerSample | None:
    recent = history.recent(bearer, 1)
    if not recent:
        return None
    return recent[0]


def bearer_capabilities(bearer: BearerName) -> tuple[SwitchMode, TransportStack, Set[str]]:
    if bearer in {"PRIMARY_INTERNET", "MOBILE_DATA_4G_5G"}:
        return "CONNECTED", "RETICULUM_VOXMESH", set(FULL_PAYLOADS)

    if bearer == "LORA_RNODE":
        return "DEGRADED_SURVIVAL", "LORA_TEXT", set(TEXT_ONLY_PAYLOADS)

    return "OFFLINE", "NONE", set()


def choose_best_available_bearer(
    history: BearerHistory,
    thresholds: AdaptiveThresholds,
) -> BearerName:
    for bearer in BEARER_PRIORITY:
        sample = latest_sample(history, bearer)  # type: ignore[arg-type]
        if sample is None:
            continue

        if sample_is_viable(sample, thresholds):
            return bearer  # type: ignore[return-value]

    return "NONE"


def decide_adaptive_switch(
    state: NetworkSwitchState,
    history: BearerHistory,
    thresholds: AdaptiveThresholds | None = None,
) -> SwitchDecision:
    if thresholds is None:
        thresholds = AdaptiveThresholds()

    current = state.current_bearer

    # Prefer recovered primary only after stable recovery.
    #
    # This must be checked before the current-bearer hysteresis gate.
    # Otherwise a mobile-data state with no fresh mobile samples can block
    # a legitimate return to a stably recovered primary Internet path.
    if current == "MOBILE_DATA_4G_5G":
        if stable_recovery(history, "PRIMARY_INTERNET", thresholds):
            mode, stack, payloads = bearer_capabilities("PRIMARY_INTERNET")
            return SwitchDecision(
                bearer="PRIMARY_INTERNET",
                mode=mode,
                stack=stack,
                allowed_payloads=payloads,
                switched=True,
                reason="primary_internet_stably_recovered",
            )

    # If current bearer is still good, do not switch.
    current_sample = latest_sample(history, current)
    if current_sample is not None and sample_is_good(current_sample, thresholds):
        mode, stack, payloads = bearer_capabilities(current)
        return SwitchDecision(
            bearer=current,
            mode=mode,
            stack=stack,
            allowed_payloads=payloads,
            switched=False,
            reason="current_bearer_still_good",
        )

    # Avoid switching on a single spike.
    if current != "NONE" and not sustained_bad(history, current, thresholds):
        mode, stack, payloads = bearer_capabilities(current)
        return SwitchDecision(
            bearer=current,
            mode=mode,
            stack=stack,
            allowed_payloads=payloads,
            switched=False,
            reason="waiting_for_sustained_degradation",
        )

    best = choose_best_available_bearer(history, thresholds)

    mode, stack, payloads = bearer_capabilities(best)

    return SwitchDecision(
        bearer=best,
        mode=mode,
        stack=stack,
        allowed_payloads=payloads,
        switched=best != current,
        reason=f"selected_{best.lower()}",
    )


def apply_switch_decision(
    state: NetworkSwitchState,
    decision: SwitchDecision,
) -> NetworkSwitchState:
    state.current_bearer = decision.bearer
    state.mode = decision.mode
    state.stack = decision.stack
    state.allowed_payloads = set(decision.allowed_payloads)
    return state


def switch_is_user_transparent(state: NetworkSwitchState) -> bool:
    return state.user_selected_network is False


def switch_changes_core_rails(state: NetworkSwitchState) -> bool:
    return state.changed_core_rails


def switch_exposes_wasm(state: NetworkSwitchState) -> bool:
    return state.exposed_wasm


def switch_touches_dome(state: NetworkSwitchState) -> bool:
    return state.touched_dome


def switch_participates_in_immunity(state: NetworkSwitchState) -> bool:
    return state.participated_in_immunity


def adaptive_switch_summary() -> Dict[str, object]:
    thresholds = AdaptiveThresholds()
    history = BearerHistory()
    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    for _ in range(3):
        history.add(
            BearerSample(
                bearer="PRIMARY_INTERNET",
                available=True,
                latency_ms=900,
                packet_loss_percent=30,
            )
        )
        history.add(
            BearerSample(
                bearer="MOBILE_DATA_4G_5G",
                available=True,
                latency_ms=80,
                packet_loss_percent=2,
            )
        )
        history.add(
            BearerSample(
                bearer="LORA_RNODE",
                available=True,
                latency_ms=900,
                packet_loss_percent=5,
            )
        )

    decision = decide_adaptive_switch(state, history, thresholds)
    apply_switch_decision(state, decision)

    return {
        "bearer": state.current_bearer,
        "mode": state.mode,
        "stack": state.stack,
        "allowed_payloads": sorted(state.allowed_payloads),
        "switched": decision.switched,
        "reason": decision.reason,
        "user_transparent": switch_is_user_transparent(state),
        "core_rails_changed": switch_changes_core_rails(state),
        "wasm_exposed": switch_exposes_wasm(state),
    }


if __name__ == "__main__":
    summary = adaptive_switch_summary()

    print("Selected bearer:", summary["bearer"])
    print("Mode:", summary["mode"])
    print("Stack:", summary["stack"])
    print("Allowed payloads:", summary["allowed_payloads"])
    print("Switched:", summary["switched"])
    print("Reason:", summary["reason"])
    print("User transparent:", summary["user_transparent"])
    print("Core rails changed:", summary["core_rails_changed"])
    print("Wasm exposed:", summary["wasm_exposed"])
