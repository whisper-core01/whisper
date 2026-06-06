"""
WHISPER — Nerve Mobile Revocation v0.1

Purpose:
Once a Nerve Mobile binding is revoked by the Core, it must never be admitted
again by that Core.

Even with:
- the same Mobile Vault
- a clean new appearance
- a fresh Sol challenge
- a fresh Rotor-derived admission code
- a reboot
- an old admission code
- a copied Mobile Vault

Core doctrine:
The Core keeps the truth.
The Mobile Vault may reflect death, but it cannot undo revocation.

Short form:
The nerve may reappear.
It cannot come back from the dead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

from nerve_mobile_admission_v01 import (
    NerveBindingContext,
    derive_nerve_binding_commitment,
    stable_hash_hex,
)
from nerve_mobile_reappearance_v01 import (
    NerveContinuityRecord,
    attempt_reappearance,
    boot_for_epoch,
    build_continuity_record,
    derive_origin_hint_commitment,
    simulate_initial_admission,
)


RevocationDecision = Literal["admit", "ignore", "reject"]
RevocationReason = Literal[
    "USER_REVOKED",
    "DEVICE_LOST",
    "POLICY_REVOKED",
    "SURFACE_MISMATCH",
    "CLONE_DETECTED",
]


@dataclass(frozen=True)
class NerveRevocationEntry:
    nerve_binding_commitment: str
    revocation_flag: bool
    revocation_epoch: str
    revocation_reason: RevocationReason


@dataclass
class NerveRevocationStore:
    entries: Dict[str, NerveRevocationEntry]


def create_revocation_store() -> NerveRevocationStore:
    return NerveRevocationStore(entries={})


def revoke_nerve_binding(
    store: NerveRevocationStore,
    nerve_binding_commitment: str,
    revocation_epoch: str,
    reason: RevocationReason,
) -> NerveRevocationEntry:
    if not nerve_binding_commitment:
        raise ValueError("nerve_binding_commitment must be non-empty")
    if not revocation_epoch:
        raise ValueError("revocation_epoch must be non-empty")

    entry = NerveRevocationEntry(
        nerve_binding_commitment=nerve_binding_commitment,
        revocation_flag=True,
        revocation_epoch=revocation_epoch,
        revocation_reason=reason,
    )

    store.entries[nerve_binding_commitment] = entry
    return entry


def is_nerve_binding_revoked(
    store: NerveRevocationStore,
    nerve_binding_commitment: str,
) -> bool:
    entry = store.entries.get(nerve_binding_commitment)

    if entry is None:
        return False

    return entry.revocation_flag is True


def get_revocation_entry(
    store: NerveRevocationStore,
    nerve_binding_commitment: str,
) -> NerveRevocationEntry | None:
    return store.entries.get(nerve_binding_commitment)


def decide_nerve_reappearance_with_revocation(
    store: NerveRevocationStore,
    record: NerveContinuityRecord,
    expected_current_code: str,
    current_challenge: str,
    previous_challenge: str,
    previous_epoch: str = "epoch-1",
    current_epoch: str = "epoch-2",
    previous_boot_nonce: str = "boot-1",
    current_boot_nonce: str = "boot-2",
) -> RevocationDecision:
    """
    Core-side decision for a reappearing Nerve.

    If the binding is revoked, reject without exception.
    """
    if is_nerve_binding_revoked(store, record.nerve_binding_commitment):
        return "reject"

    previous_boot = boot_for_epoch(
        challenge=previous_challenge,
        boot_nonce=previous_boot_nonce,
        epoch=previous_epoch,
    )

    current_boot = boot_for_epoch(
        challenge=current_challenge,
        boot_nonce=current_boot_nonce,
        epoch=current_epoch,
    )

    attempt = attempt_reappearance(
        record=record,
        expected_current_code=expected_current_code,
        current_boot=current_boot,
        current_challenge=current_challenge,
        previous_boot=previous_boot,
        previous_challenge=previous_challenge,
        existing_revoked=False,
    )

    if attempt.decision == "admit":
        return "admit"

    return "ignore"


def build_revoked_continuity_record(
    record: NerveContinuityRecord,
) -> NerveContinuityRecord:
    return build_continuity_record(
        nerve_binding_commitment=record.nerve_binding_commitment,
        origin_hint_commitment=record.origin_hint_commitment,
        birth_epoch=record.birth_epoch,
        last_seen_epoch=record.last_seen_epoch,
        revoked=True,
    )


def simulate_revocation_flow() -> dict:
    """
    Admission -> revocation -> fresh reappearance rejected.
    """
    local_master_binding_hash = stable_hash_hex("local-master")
    store = create_revocation_store()

    previous_boot, record = simulate_initial_admission(
        local_master_binding_hash=local_master_binding_hash,
        epoch="epoch-1",
        challenge="challenge-1",
        boot_nonce="boot-1",
    )

    revoke_nerve_binding(
        store=store,
        nerve_binding_commitment=record.nerve_binding_commitment,
        revocation_epoch="epoch-2",
        reason="USER_REVOKED",
    )

    current_boot = boot_for_epoch(
        challenge="challenge-2",
        boot_nonce="boot-2",
        epoch="epoch-2",
    )

    decision = decide_nerve_reappearance_with_revocation(
        store=store,
        record=record,
        expected_current_code=current_boot.nerve_admission_code,
        current_challenge="challenge-2",
        previous_challenge="challenge-1",
    )

    return {
        "previous_code": previous_boot.nerve_admission_code,
        "current_code": current_boot.nerve_admission_code,
        "revoked": is_nerve_binding_revoked(store, record.nerve_binding_commitment),
        "decision": decision,
        "passed": decision == "reject",
    }


def simulate_non_revoked_reappearance_flow() -> dict:
    """
    Non-revoked continuity should still admit with a fresh challenge.
    """
    local_master_binding_hash = stable_hash_hex("local-master")
    store = create_revocation_store()

    _previous_boot, record = simulate_initial_admission(
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

    decision = decide_nerve_reappearance_with_revocation(
        store=store,
        record=record,
        expected_current_code=current_boot.nerve_admission_code,
        current_challenge="challenge-2",
        previous_challenge="challenge-1",
    )

    return {
        "revoked": is_nerve_binding_revoked(store, record.nerve_binding_commitment),
        "decision": decision,
        "passed": decision == "admit",
    }


def simulate_old_code_after_revocation_flow() -> dict:
    """
    Old code replay after revocation must be rejected.
    """
    local_master_binding_hash = stable_hash_hex("local-master")
    store = create_revocation_store()

    previous_boot, record = simulate_initial_admission(
        local_master_binding_hash=local_master_binding_hash,
        epoch="epoch-1",
        challenge="challenge-1",
        boot_nonce="boot-1",
    )

    revoke_nerve_binding(
        store=store,
        nerve_binding_commitment=record.nerve_binding_commitment,
        revocation_epoch="epoch-2",
        reason="USER_REVOKED",
    )

    decision = decide_nerve_reappearance_with_revocation(
        store=store,
        record=record,
        expected_current_code=previous_boot.nerve_admission_code,
        current_challenge="challenge-2",
        previous_challenge="challenge-1",
    )

    return {
        "revoked": True,
        "old_code_attempted": True,
        "decision": decision,
        "passed": decision == "reject",
    }


def simulate_clone_after_revocation_flow() -> dict:
    """
    A copied Mobile Vault on another device must not bypass revocation.

    v01 rule:
    if the candidate maps to a revoked binding, reject without exception.
    """
    local_master_binding_hash = stable_hash_hex("local-master")
    store = create_revocation_store()

    _previous_boot, record = simulate_initial_admission(
        local_master_binding_hash=local_master_binding_hash,
        epoch="epoch-1",
        challenge="challenge-1",
        boot_nonce="boot-1",
    )

    revoke_nerve_binding(
        store=store,
        nerve_binding_commitment=record.nerve_binding_commitment,
        revocation_epoch="epoch-2",
        reason="CLONE_DETECTED",
    )

    clone_current_boot = boot_for_epoch(
        challenge="challenge-2-clone",
        boot_nonce="boot-2-clone",
        epoch="epoch-2",
    )

    decision = decide_nerve_reappearance_with_revocation(
        store=store,
        record=record,
        expected_current_code=clone_current_boot.nerve_admission_code,
        current_challenge="challenge-2-clone",
        previous_challenge="challenge-1",
        current_boot_nonce="boot-2-clone",
    )

    return {
        "revoked": True,
        "clone_attempted": True,
        "decision": decision,
        "passed": decision == "reject",
    }


if __name__ == "__main__":
    revoked = simulate_revocation_flow()
    non_revoked = simulate_non_revoked_reappearance_flow()
    old_code = simulate_old_code_after_revocation_flow()
    clone = simulate_clone_after_revocation_flow()

    print("Revoked reappearance rejected:", revoked["passed"])
    print("Non-revoked reappearance admitted:", non_revoked["passed"])
    print("Old code after revocation rejected:", old_code["passed"])
    print("Clone after revocation rejected:", clone["passed"])
