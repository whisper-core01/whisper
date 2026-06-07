"""
WHISPER v1.8.0 — Verve Pre-LUKS Boot Stage v0.1

Purpose:
Model the pre-LUKS boot stage.

Before LUKS unlock, WHISPER Core does not exist.

Only a minimal threshold exists:
- minimal NixOS stage
- minimal Reticulum stage
- external RotorMachine
- Verve

This stage may help unlock LUKS.
It must never contain WHISPER Core secrets or organs.

Doctrine:
Before LUKS, there is no body.
There is only the threshold.

The pre-LUKS stage may open the door.
It must never contain the house.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Literal, Set


BootPhase = Literal[
    "PRE_LUKS",
    "LUKS_UNLOCKED",
    "PARTITION_MOUNTED",
    "FULL_NIXOS_LOADED",
    "WHISPER_STARTED",
]

UnlockDecision = Literal[
    "unlock_allowed",
    "unlock_rejected",
]

StageComponent = Literal[
    "minimal_nixos",
    "minimal_reticulum",
    "external_rotor",
    "verve",
]

ForbiddenComponent = Literal[
    "vault_core",
    "flv",
    "raw_luks_key_persistent",
    "whisper_session",
    "sovereign_identity",
    "daemon_complete",
    "dome",
    "courier",
    "bal",
    "membrane",
    "wasm_core",
    "lemonade",
]


REQUIRED_PRELUKS_COMPONENTS: Set[str] = {
    "minimal_nixos",
    "minimal_reticulum",
    "external_rotor",
    "verve",
}

FORBIDDEN_PRELUKS_COMPONENTS: Set[str] = {
    "vault_core",
    "flv",
    "raw_luks_key_persistent",
    "whisper_session",
    "sovereign_identity",
    "daemon_complete",
    "dome",
    "courier",
    "bal",
    "membrane",
    "wasm_core",
    "lemonade",
}


@dataclass
class PreLuksStage:
    phase: BootPhase = "PRE_LUKS"
    components: Set[str] = field(default_factory=lambda: set(REQUIRED_PRELUKS_COMPONENTS))
    forbidden_components: Set[str] = field(default_factory=set)

    network_required_for_unlock: bool = False
    can_access_vault: bool = False
    can_access_flv: bool = False
    can_start_whisper_session: bool = False
    can_touch_core_organs: bool = False
    contains_raw_luks_key_persistent: bool = False


@dataclass
class VerveThreshold:
    has_unlock_material: bool = True
    unlock_material_zeroized: bool = False
    unlock_attempts: int = 0
    max_unlock_attempts: int = 3
    reads_vault: bool = False
    reads_flv: bool = False
    starts_whisper_directly: bool = False
    depends_on_network: bool = False


@dataclass
class LuksMock:
    locked: bool = True
    mounted: bool = False
    accepted_factor: str = "valid-verve-factor"


@dataclass
class FullNixOSMock:
    loaded: bool = False
    network_stack_available: bool = False


@dataclass
class WhisperBootMock:
    started: bool = False
    vault_accessible: bool = False
    rotor_available: bool = False
    daemon_started: bool = False


@dataclass(frozen=True)
class BootHandoffResult:
    unlock_decision: UnlockDecision
    phase: BootPhase
    luks_locked: bool
    luks_mounted: bool
    full_nixos_loaded: bool
    whisper_started: bool
    verve_zeroized: bool


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "verve_preluks_boot_stage::"
        f"{test_name}"
    )


def preluks_has_required_components(stage: PreLuksStage) -> bool:
    return REQUIRED_PRELUKS_COMPONENTS.issubset(stage.components)


def preluks_contains_forbidden_components(stage: PreLuksStage) -> bool:
    return bool(stage.components & FORBIDDEN_PRELUKS_COMPONENTS) or bool(stage.forbidden_components)


def preluks_is_not_whisper_core(stage: PreLuksStage) -> bool:
    return (
        not stage.can_access_vault
        and not stage.can_access_flv
        and not stage.can_start_whisper_session
        and not stage.can_touch_core_organs
        and not stage.contains_raw_luks_key_persistent
        and not preluks_contains_forbidden_components(stage)
    )


def preluks_unlock_requires_no_network(stage: PreLuksStage, verve: VerveThreshold) -> bool:
    return not stage.network_required_for_unlock and not verve.depends_on_network


def verve_does_not_access_core(verve: VerveThreshold) -> bool:
    return (
        not verve.reads_vault
        and not verve.reads_flv
        and not verve.starts_whisper_directly
    )


def verve_can_attempt_unlock(verve: VerveThreshold) -> bool:
    return (
        verve.has_unlock_material
        and not verve.unlock_material_zeroized
        and verve.unlock_attempts < verve.max_unlock_attempts
    )


def verve_zeroize(verve: VerveThreshold) -> None:
    verve.has_unlock_material = False
    verve.unlock_material_zeroized = True


def luks_attempt_unlock(
    luks: LuksMock,
    verve: VerveThreshold,
    presented_factor: str,
) -> UnlockDecision:
    if not verve_can_attempt_unlock(verve):
        return "unlock_rejected"

    verve.unlock_attempts += 1

    if presented_factor != luks.accepted_factor:
        verve_zeroize(verve)
        return "unlock_rejected"

    luks.locked = False
    return "unlock_allowed"


def mount_luks_partition(luks: LuksMock, stage: PreLuksStage) -> bool:
    if luks.locked:
        return False

    luks.mounted = True
    stage.phase = "PARTITION_MOUNTED"

    return True


def load_full_nixos(
    luks: LuksMock,
    nixos: FullNixOSMock,
    stage: PreLuksStage,
) -> bool:
    if not luks.mounted:
        return False

    nixos.loaded = True
    nixos.network_stack_available = True
    stage.phase = "FULL_NIXOS_LOADED"

    return True


def start_whisper_after_nixos(
    nixos: FullNixOSMock,
    whisper: WhisperBootMock,
    stage: PreLuksStage,
) -> bool:
    if not nixos.loaded:
        return False

    whisper.started = True
    whisper.vault_accessible = True
    whisper.rotor_available = True
    whisper.daemon_started = True
    stage.phase = "WHISPER_STARTED"

    return True


def full_boot_handoff(
    presented_factor: str,
) -> BootHandoffResult:
    stage = PreLuksStage()
    verve = VerveThreshold()
    luks = LuksMock()
    nixos = FullNixOSMock()
    whisper = WhisperBootMock()

    decision = luks_attempt_unlock(luks, verve, presented_factor)

    if decision == "unlock_allowed":
        mount_luks_partition(luks, stage)
        load_full_nixos(luks, nixos, stage)
        start_whisper_after_nixos(nixos, whisper, stage)

    verve_zeroize(verve)

    return BootHandoffResult(
        unlock_decision=decision,
        phase=stage.phase,
        luks_locked=luks.locked,
        luks_mounted=luks.mounted,
        full_nixos_loaded=nixos.loaded,
        whisper_started=whisper.started,
        verve_zeroized=verve.unlock_material_zeroized,
    )


def pre_luks_boot_summary() -> Dict[str, object]:
    stage = PreLuksStage()
    verve = VerveThreshold()
    result = full_boot_handoff("valid-verve-factor")

    return {
        "preluks_required_components": sorted(stage.components),
        "preluks_has_required_components": preluks_has_required_components(stage),
        "preluks_is_not_whisper_core": preluks_is_not_whisper_core(stage),
        "preluks_unlock_requires_no_network": preluks_unlock_requires_no_network(stage, verve),
        "verve_does_not_access_core": verve_does_not_access_core(verve),
        "unlock_decision": result.unlock_decision,
        "final_phase": result.phase,
        "luks_mounted": result.luks_mounted,
        "full_nixos_loaded": result.full_nixos_loaded,
        "whisper_started": result.whisper_started,
        "verve_zeroized": result.verve_zeroized,
    }


if __name__ == "__main__":
    summary = pre_luks_boot_summary()

    print("Pre-LUKS components:", summary["preluks_required_components"])
    print("Pre-LUKS has required components:", summary["preluks_has_required_components"])
    print("Pre-LUKS is not WHISPER Core:", summary["preluks_is_not_whisper_core"])
    print("Unlock requires network:", not summary["preluks_unlock_requires_no_network"])
    print("Verve accesses Core:", not summary["verve_does_not_access_core"])
    print("Unlock decision:", summary["unlock_decision"])
    print("Final phase:", summary["final_phase"])
    print("LUKS mounted:", summary["luks_mounted"])
    print("Full NixOS loaded:", summary["full_nixos_loaded"])
    print("WHISPER started:", summary["whisper_started"])
    print("Verve zeroized:", summary["verve_zeroized"])
