"""
WHISPER — Nerve Mobile Reappearance v0.1

Purpose:
Validate Nerve Mobile continuity after reboot without allowing replay.

Core doctrine:
The mobile does not carry a stable identity.
It carries a revocable scar in its Mobile Vault.

After reboot:
- the Mobile Vault opens briefly
- continuity material is read
- a fresh Sol challenge is required
- a fresh reappearance code is derived
- the old appearance code must not work
- revoked nerves must not reappear

Short form:
The nerve may reappear.
It cannot replay its old appearance.
"""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from typing import Literal

from nerve_mobile_admission_v01 import (
    NerveBindingContext,
    NerveMobileSurfaceContext,
    build_admission_envelope,
    build_nerve_binding_record,
    decide_nerve_admission,
    derive_nerve_binding_commitment,
    stable_hash_hex,
)
from nerve_mobile_vault_boot_v01 import (
    NerveBootResult,
    boot_sequence,
)


ReappearanceDecision = Literal["admit", "ignore", "revoke"]


@dataclass(frozen=True)
class NerveContinuityRecord:
    nerve_binding_commitment: str
    origin_hint_commitment: str
    birth_epoch: str
    last_seen_epoch: str
    revocation_state: str
    surface_commitment_version: str


@dataclass(frozen=True)
class ReappearanceAttempt:
    previous_epoch: str
    current_epoch: str
    previous_challenge: str
    current_challenge: str
    previous_code: str
    current_code: str
    continuity_commitment: str
    decision: ReappearanceDecision
    old_code_reused: bool


@dataclass(frozen=True)
class ReappearanceValidationResult:
    continuity_preserved: bool
    old_code_rejected: bool
    current_code_accepted: bool
    revoked_rejected: bool
    passed: bool


def derive_origin_hint_commitment(
    origin_hint: str,
    local_master_binding_hash: str,
    birth_epoch: str,
) -> str:
    """
    Commit to the mobile scar without exposing the scar itself.
    """
    if not origin_hint:
        raise ValueError("origin_hint must be non-empty")
    if not local_master_binding_hash:
        raise ValueError("local_master_binding_hash must be non-empty")
    if not birth_epoch:
        raise ValueError("birth_epoch must be non-empty")

    return stable_hash_hex(
        origin_hint,
        local_master_binding_hash,
        birth_epoch,
        "WHISPER_NERVE_ORIGIN_HINT_COMMITMENT_V1",
    )


def build_continuity_record(
    nerve_binding_commitment: str,
    origin_hint_commitment: str,
    birth_epoch: str,
    last_seen_epoch: str,
    revoked: bool = False,
) -> NerveContinuityRecord:
    if not nerve_binding_commitment:
        raise ValueError("nerve_binding_commitment must be non-empty")
    if not origin_hint_commitment:
        raise ValueError("origin_hint_commitment must be non-empty")
    if not birth_epoch:
        raise ValueError("birth_epoch must be non-empty")
    if not last_seen_epoch:
        raise ValueError("last_seen_epoch must be non-empty")

    return NerveContinuityRecord(
        nerve_binding_commitment=nerve_binding_commitment,
        origin_hint_commitment=origin_hint_commitment,
        birth_epoch=birth_epoch,
        last_seen_epoch=last_seen_epoch,
        revocation_state="revoked" if revoked else "active",
        surface_commitment_version="NERVE_MOBILE_SURFACE_SEED_V1",
    )


def derive_reappearance_continuity_commitment(
    record: NerveContinuityRecord,
    current_epoch: str,
    current_challenge: str,
    current_code: str,
) -> str:
    """
    Bind current reappearance to existing Core-side continuity.

    This commitment is Core-side evidence, not a mobile secret.
    """
    if not current_epoch:
        raise ValueError("current_epoch must be non-empty")
    if not current_challenge:
        raise ValueError("current_challenge must be non-empty")
    if not current_code:
        raise ValueError("current_code must be non-empty")

    return stable_hash_hex(
        record.nerve_binding_commitment,
        record.origin_hint_commitment,
        record.birth_epoch,
        record.last_seen_epoch,
        current_epoch,
        current_challenge,
        current_code,
        "WHISPER_NERVE_REAPPEARANCE_CONTINUITY_V1",
    )


def build_surface_context(
    challenge: str,
    boot_nonce: str,
    epoch: str,
    imei_material: str = "imei-local",
    carrier_material: str = "carrier",
) -> NerveMobileSurfaceContext:
    return NerveMobileSurfaceContext(
        imei_hash_local=stable_hash_hex(imei_material),
        carrier_hint_hash=stable_hash_hex(carrier_material),
        sol_admission_challenge=challenge,
        boot_nonce=boot_nonce,
        admission_epoch=epoch,
    )


def boot_for_epoch(
    challenge: str,
    boot_nonce: str,
    epoch: str,
) -> NerveBootResult:
    return boot_sequence(
        build_surface_context(
            challenge=challenge,
            boot_nonce=boot_nonce,
            epoch=epoch,
        )
    )


def simulate_initial_admission(
    local_master_binding_hash: str,
    epoch: str = "epoch-1",
    challenge: str = "challenge-1",
    boot_nonce: str = "boot-1",
) -> tuple[NerveBootResult, NerveContinuityRecord]:
    """
    Simulate first Nerve admission and Core-side continuity storage.
    """
    boot = boot_for_epoch(
        challenge=challenge,
        boot_nonce=boot_nonce,
        epoch=epoch,
    )

    binding_commitment = derive_nerve_binding_commitment(
        NerveBindingContext(
            local_master_binding_hash=local_master_binding_hash,
            nerve_admission_code=boot.nerve_admission_code,
            sol_epoch=epoch,
            nerve_binding_nonce="binding-nonce",
        )
    )

    origin_hint_commitment = derive_origin_hint_commitment(
        origin_hint="origin-hint",
        local_master_binding_hash=local_master_binding_hash,
        birth_epoch=epoch,
    )

    # Build record once to exercise the existing admission module path.
    build_nerve_binding_record(
        binding_commitment=binding_commitment,
        nerve_birth_epoch=epoch,
        capabilities=boot.capabilities,
        last_seen_epoch=epoch,
        revoked=False,
    )

    record = build_continuity_record(
        nerve_binding_commitment=binding_commitment,
        origin_hint_commitment=origin_hint_commitment,
        birth_epoch=epoch,
        last_seen_epoch=epoch,
        revoked=False,
    )

    return boot, record


def attempt_reappearance(
    record: NerveContinuityRecord,
    expected_current_code: str,
    current_boot: NerveBootResult,
    current_challenge: str,
    previous_boot: NerveBootResult,
    previous_challenge: str,
    existing_revoked: bool = False,
) -> ReappearanceAttempt:
    """
    Attempt to reappear using a fresh boot result.

    The old code is tested separately and must be rejected.
    """
    envelope = build_admission_envelope(
        admission_epoch=current_boot.admission_epoch,
        boot_nonce="boot-current",
        capabilities=current_boot.capabilities,
        nerve_admission_code=current_boot.nerve_admission_code,
    )

    decision = decide_nerve_admission(
        expected_code=expected_current_code,
        envelope=envelope,
        existing_revoked=existing_revoked or record.revocation_state == "revoked",
    )

    continuity_commitment = derive_reappearance_continuity_commitment(
        record=record,
        current_epoch=current_boot.admission_epoch,
        current_challenge=current_challenge,
        current_code=current_boot.nerve_admission_code,
    )

    old_code_reused = hmac.compare_digest(
        previous_boot.nerve_admission_code,
        current_boot.nerve_admission_code,
    )

    return ReappearanceAttempt(
        previous_epoch=previous_boot.admission_epoch,
        current_epoch=current_boot.admission_epoch,
        previous_challenge=previous_challenge,
        current_challenge=current_challenge,
        previous_code=previous_boot.nerve_admission_code,
        current_code=current_boot.nerve_admission_code,
        continuity_commitment=continuity_commitment,
        decision=decision,
        old_code_reused=old_code_reused,
    )


def validate_reappearance_scenario() -> ReappearanceValidationResult:
    """
    Validate the normal reboot/reappearance scenario.
    """
    local_master_binding_hash = stable_hash_hex("local-master")

    previous_boot, record = simulate_initial_admission(
        local_master_binding_hash=local_master_binding_hash,
        epoch="epoch-1",
        challenge="challenge-1",
        boot_nonce="boot-1",
    )

    current_boot = boot_for_epoch(
        challenge="challenge-2",
        boot_nonce="boot-2",
        epoch="epoch-2",
    )

    expected_current_code = current_boot.nerve_admission_code

    attempt = attempt_reappearance(
        record=record,
        expected_current_code=expected_current_code,
        current_boot=current_boot,
        current_challenge="challenge-2",
        previous_boot=previous_boot,
        previous_challenge="challenge-1",
    )

    old_envelope = build_admission_envelope(
        admission_epoch=current_boot.admission_epoch,
        boot_nonce="boot-current",
        capabilities=current_boot.capabilities,
        nerve_admission_code=previous_boot.nerve_admission_code,
    )

    old_decision = decide_nerve_admission(
        expected_code=expected_current_code,
        envelope=old_envelope,
        existing_revoked=False,
    )

    revoked_record = build_continuity_record(
        nerve_binding_commitment=record.nerve_binding_commitment,
        origin_hint_commitment=record.origin_hint_commitment,
        birth_epoch=record.birth_epoch,
        last_seen_epoch=record.last_seen_epoch,
        revoked=True,
    )

    revoked_attempt = attempt_reappearance(
        record=revoked_record,
        expected_current_code=expected_current_code,
        current_boot=current_boot,
        current_challenge="challenge-2",
        previous_boot=previous_boot,
        previous_challenge="challenge-1",
        existing_revoked=True,
    )

    continuity_preserved = bool(attempt.continuity_commitment)
    old_code_rejected = old_decision == "ignore"
    current_code_accepted = attempt.decision == "admit"
    revoked_rejected = revoked_attempt.decision == "revoke"

    return ReappearanceValidationResult(
        continuity_preserved=continuity_preserved,
        old_code_rejected=old_code_rejected,
        current_code_accepted=current_code_accepted,
        revoked_rejected=revoked_rejected,
        passed=all([
            continuity_preserved,
            old_code_rejected,
            current_code_accepted,
            revoked_rejected,
            not attempt.old_code_reused,
        ]),
    )


if __name__ == "__main__":
    result = validate_reappearance_scenario()

    print("Continuity preserved:", result.continuity_preserved)
    print("Old code rejected:", result.old_code_rejected)
    print("Current code accepted:", result.current_code_accepted)
    print("Revoked rejected:", result.revoked_rejected)
    print("Passed:", result.passed)
