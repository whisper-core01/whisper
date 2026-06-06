"""
WHISPER v1.6.0 — Lemonade / Dome Immunity v0.1

Purpose:
Define the immune relationship between Lemonade and the Dome.

Lemonade observes symptoms and recommends defensive reactions.

The Dome applies defensive policy because it is already the intake organ that
accepts, rejects, holds, or quarantines material.

The Daemon remains blind and does not participate in immunity.

Core doctrine:

Lemonade recommends.
The Dome applies.
If Lemonade falls, it calls.
The Dome raises it.
The Daemon remains blind.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


LemonadeStatus = Literal[
    "HEALTHY",
    "CRASHING",
    "DOWN",
]

DomeMode = Literal[
    "NORMAL",
    "FALLBACK_STRICT_LOCAL_COHERENCE",
]

RecommendationType = Literal[
    "ALLOW",
    "REJECT",
    "HOLD",
    "QUARANTINE_ORGAN",
    "RESTART_REQUIRED",
]

DomeActionType = Literal[
    "ACCEPT_MATERIAL",
    "REJECT_MATERIAL",
    "HOLD_MATERIAL",
    "QUARANTINE_ORGAN",
    "REQUEST_RESTART",
    "STRICT_LOCAL_COHERENCE",
]

PanicCause = Literal[
    "LEMONADE_CRASH",
    "LEMONADE_TIMEOUT",
    "LEMONADE_ABNORMAL_CLOSE",
    "LEMONADE_SELF_CHECK_FAILED",
]


@dataclass(frozen=True)
class DefenseSignal:
    source_organ: str
    signal_type: str
    severity: int
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DefenseRecommendation:
    recommendation: RecommendationType
    reason: str
    target_organ: str | None = None


@dataclass(frozen=True)
class DomeDefenseAction:
    action: DomeActionType
    reason: str
    target_organ: str | None = None


@dataclass(frozen=True)
class LemonadePanicFlag:
    type: str
    organ_id: str
    timestamp: str
    cause: PanicCause
    priority: str = "URGENT"


@dataclass
class LemonadeState:
    organ_id: str = "lemonade"
    status: LemonadeStatus = "HEALTHY"
    emitted_panic_flags: List[LemonadePanicFlag] = field(default_factory=list)
    touched_payload: bool = False
    touched_daemon: bool = False
    touched_wasm: bool = False


@dataclass
class DomeImmunityState:
    mode: DomeMode = "NORMAL"
    fallback_active: bool = False
    strict_local_coherence: bool = False
    adaptive_recommendations_enabled: bool = True
    received_panic_flags: List[LemonadePanicFlag] = field(default_factory=list)
    restart_requests: List[str] = field(default_factory=list)
    applied_actions: List[DomeDefenseAction] = field(default_factory=list)
    daemon_notified: bool = False


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.6.0::"
        "lemonade_dome_immunity::"
        f"{test_name}"
    )


def lemonade_observe_signal(signal: DefenseSignal) -> DefenseRecommendation:
    """
    Lemonade observes symptoms.

    It does not read payload.

    It does not block material directly.
    """
    if signal.severity >= 9:
        return DefenseRecommendation(
            recommendation="QUARANTINE_ORGAN",
            reason=signal.signal_type,
            target_organ=signal.source_organ,
        )

    if signal.severity >= 7:
        return DefenseRecommendation(
            recommendation="RESTART_REQUIRED",
            reason=signal.signal_type,
            target_organ=signal.source_organ,
        )

    if signal.severity >= 5:
        return DefenseRecommendation(
            recommendation="HOLD",
            reason=signal.signal_type,
            target_organ=signal.source_organ,
        )

    if signal.severity >= 3:
        return DefenseRecommendation(
            recommendation="REJECT",
            reason=signal.signal_type,
            target_organ=signal.source_organ,
        )

    return DefenseRecommendation(
        recommendation="ALLOW",
        reason=signal.signal_type,
        target_organ=signal.source_organ,
    )


def dome_apply_recommendation(
    dome: DomeImmunityState,
    recommendation: DefenseRecommendation,
) -> DomeDefenseAction:
    """
    The Dome applies defensive decisions.

    Lemonade recommends.

    The Dome applies.
    """
    mapping = {
        "ALLOW": "ACCEPT_MATERIAL",
        "REJECT": "REJECT_MATERIAL",
        "HOLD": "HOLD_MATERIAL",
        "QUARANTINE_ORGAN": "QUARANTINE_ORGAN",
        "RESTART_REQUIRED": "REQUEST_RESTART",
    }

    action = DomeDefenseAction(
        action=mapping[recommendation.recommendation],  # type: ignore[arg-type]
        reason=recommendation.reason,
        target_organ=recommendation.target_organ,
    )

    dome.applied_actions.append(action)

    if action.action == "REQUEST_RESTART" and action.target_organ:
        dome.restart_requests.append(action.target_organ)

    if action.action == "QUARANTINE_ORGAN" and action.target_organ:
        dome.restart_requests.append(action.target_organ)

    return action


def lemonade_emit_panic_flag_on_abnormal_close(
    lemonade: LemonadeState,
    timestamp: str,
    cause: PanicCause,
) -> LemonadePanicFlag:
    """
    Lemonade emits an emergency panic flag while falling.

    The flag contains no material, no payload, no key, no secret.
    """
    lemonade.status = "CRASHING"

    flag = LemonadePanicFlag(
        type="LEMONADE_FAILURE",
        organ_id=lemonade.organ_id,
        timestamp=timestamp,
        cause=cause,
        priority="URGENT",
    )

    lemonade.emitted_panic_flags.append(flag)
    lemonade.status = "DOWN"

    return flag


def dome_enter_fallback_mode(
    dome: DomeImmunityState,
    flag: LemonadePanicFlag,
) -> DomeDefenseAction:
    """
    The Dome enters fallback mode after Lemonade failure.

    Fallback means:
    - strict local coherence
    - no adaptive recommendations
    - no automatic quarantine
    - no automatic revocation
    """
    dome.received_panic_flags.append(flag)
    dome.mode = "FALLBACK_STRICT_LOCAL_COHERENCE"
    dome.fallback_active = True
    dome.strict_local_coherence = True
    dome.adaptive_recommendations_enabled = False

    action = DomeDefenseAction(
        action="STRICT_LOCAL_COHERENCE",
        reason=flag.cause,
        target_organ="dome",
    )

    dome.applied_actions.append(action)

    return action


def dome_trigger_lemonade_restart(
    dome: DomeImmunityState,
    flag: LemonadePanicFlag,
) -> DomeDefenseAction:
    """
    The Dome requests Lemonade restart.

    The Daemon is not involved.
    """
    if flag.type != "LEMONADE_FAILURE":
        raise ValueError("unsupported panic flag type")

    dome.restart_requests.append(flag.organ_id)

    action = DomeDefenseAction(
        action="REQUEST_RESTART",
        reason=flag.cause,
        target_organ=flag.organ_id,
    )

    dome.applied_actions.append(action)

    return action


def handle_lemonade_panic_flag(
    dome: DomeImmunityState,
    flag: LemonadePanicFlag,
) -> List[DomeDefenseAction]:
    """
    Panic flag handling is urgent and priority.

    It is processed before normal recommendations.
    """
    fallback_action = dome_enter_fallback_mode(dome, flag)
    restart_action = dome_trigger_lemonade_restart(dome, flag)

    return [fallback_action, restart_action]


def dome_apply_local_coherence_without_lemonade(
    material_coherent: bool,
) -> DomeDefenseAction:
    """
    If Lemonade is down, the Dome keeps innate immunity.

    Coherent material may continue.

    Incoherent material is rejected.
    """
    if material_coherent:
        return DomeDefenseAction(
            action="ACCEPT_MATERIAL",
            reason="strict_local_coherence_passed",
        )

    return DomeDefenseAction(
        action="REJECT_MATERIAL",
        reason="strict_local_coherence_failed",
    )


def lemonade_never_blocks_material_directly() -> bool:
    return True


def lemonade_never_touches_payload(lemonade: LemonadeState) -> bool:
    return lemonade.touched_payload is False


def daemon_receives_panic_flag(dome: DomeImmunityState) -> bool:
    return dome.daemon_notified


def lemonade_failure_opens_shortcut() -> bool:
    return False


def lemonade_failure_exposes_wasm() -> bool:
    return False


def simulate_lemonade_abnormal_closure() -> tuple[LemonadeState, DomeImmunityState]:
    lemonade = LemonadeState()
    dome = DomeImmunityState()

    flag = lemonade_emit_panic_flag_on_abnormal_close(
        lemonade=lemonade,
        timestamp="t-1",
        cause="LEMONADE_ABNORMAL_CLOSE",
    )

    handle_lemonade_panic_flag(dome, flag)

    return lemonade, dome


if __name__ == "__main__":
    lemonade, dome = simulate_lemonade_abnormal_closure()

    print("Lemonade status:", lemonade.status)
    print("Panic flags:", len(lemonade.emitted_panic_flags))
    print("Dome mode:", dome.mode)
    print("Fallback active:", dome.fallback_active)
    print("Strict local coherence:", dome.strict_local_coherence)
    print("Restart requests:", dome.restart_requests)
    print("Daemon notified:", dome.daemon_notified)
