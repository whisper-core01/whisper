"""
WHISPER — Nerve Mobile Admission v0.1

Nerve Mobile is not a client.

It does not connect.
It appears in the Sol.

The mobile does not identify itself with a persistent secret.
It derives a bounded admission code from local surface hints, a Sol challenge,
a boot nonce, and an admission epoch.

The Core may then bind that appearance locally through a revocable,
FLV/LUKS-bound commitment.

Core rule:

The mobile does not identify itself.
It produces a code of appearance.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, List, Literal


NerveKind = Literal["mobile"]
AdmissionKind = Literal["admission_candidate"]
AdmissionDecision = Literal["admit", "ignore", "revoke"]


@dataclass(frozen=True)
class NerveMobileSurfaceContext:
    imei_hash_local: str
    carrier_hint_hash: str
    sol_admission_challenge: str
    boot_nonce: str
    admission_epoch: str


@dataclass(frozen=True)
class NerveAdmissionEnvelope:
    nerve: NerveKind
    kind: AdmissionKind
    admission_epoch: str
    boot_nonce_commitment: str
    capabilities: List[str]
    nerve_admission_code: str


@dataclass(frozen=True)
class NerveBindingContext:
    local_master_binding_hash: str
    nerve_admission_code: str
    sol_epoch: str
    nerve_binding_nonce: str


@dataclass(frozen=True)
class NerveBindingRecord:
    nerve_binding_commitment: str
    nerve_birth_epoch: str
    nerve_capabilities: List[str]
    nerve_revocation_state: str
    surface_commitment_version: str
    last_seen_epoch: str


VALID_CAPABILITIES = {"text", "audio", "image", "file"}


def stable_hash_hex(*parts: str) -> str:
    return hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _require_hex_hash(name: str, value: str) -> None:
    _require_non_empty(name, value)

    if len(value) != 64:
        raise ValueError(f"{name} must be a 64-char hex hash")

    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hex") from exc


def _require_capabilities(capabilities: List[str]) -> None:
    if not capabilities:
        raise ValueError("capabilities must not be empty")

    for capability in capabilities:
        if capability not in VALID_CAPABILITIES:
            raise ValueError(f"unsupported capability: {capability}")


def derive_surface_seed(ctx: NerveMobileSurfaceContext) -> str:
    """
    Derive an ephemeral surface seed.

    The surface seed must not be transmitted.

    It must not be stored permanently.

    It is input material for the admission code only.
    """
    _require_hex_hash("imei_hash_local", ctx.imei_hash_local)
    _require_hex_hash("carrier_hint_hash", ctx.carrier_hint_hash)
    _require_non_empty("sol_admission_challenge", ctx.sol_admission_challenge)
    _require_non_empty("boot_nonce", ctx.boot_nonce)
    _require_non_empty("admission_epoch", ctx.admission_epoch)

    return stable_hash_hex(
        ctx.imei_hash_local,
        ctx.carrier_hint_hash,
        ctx.sol_admission_challenge,
        ctx.boot_nonce,
        ctx.admission_epoch,
        "NERVE_MOBILE_SURFACE_SEED_V1",
    )


def derive_boot_nonce_commitment(
    boot_nonce: str,
    admission_epoch: str,
) -> str:
    """
    Commit to the boot nonce without exposing it directly.
    """
    _require_non_empty("boot_nonce", boot_nonce)
    _require_non_empty("admission_epoch", admission_epoch)

    return stable_hash_hex(
        boot_nonce,
        admission_epoch,
        "NERVE_MOBILE_BOOT_NONCE_COMMITMENT_V1",
    )


def derive_nerve_admission_code(
    surface_seed: str,
    admission_epoch: str,
    rotor_rounds: int = 3,
) -> str:
    """
    Derive a bounded Nerve admission code.

    This models RotorMachine admission behavior using deterministic rounds.

    The result is not a key.

    It is not an identity.

    It is a bounded appearance code.
    """
    _require_hex_hash("surface_seed", surface_seed)
    _require_non_empty("admission_epoch", admission_epoch)

    if rotor_rounds <= 0:
        raise ValueError("rotor_rounds must be > 0")

    current = surface_seed

    for round_id in range(rotor_rounds):
        current = stable_hash_hex(
            current,
            admission_epoch,
            str(round_id),
            "WHISPER_NERVE_ROTOR_ADMISSION_ROUND_V1",
        )

    return stable_hash_hex(
        current,
        admission_epoch,
        "WHISPER_NERVE_ADMISSION_CODE_V1",
    )


def build_admission_envelope(
    admission_epoch: str,
    boot_nonce: str,
    capabilities: List[str],
    nerve_admission_code: str,
) -> NerveAdmissionEnvelope:
    """
    Build the minimal Sol appearance envelope.

    This is what Nerve Mobile may emit into the Sol.

    It must not contain:
    - raw IMEI
    - static IMEI hash
    - carrier identity
    - surface_seed
    - mobile secret
    - Whisper identity
    """
    _require_non_empty("admission_epoch", admission_epoch)
    _require_non_empty("boot_nonce", boot_nonce)
    _require_capabilities(capabilities)
    _require_hex_hash("nerve_admission_code", nerve_admission_code)

    return NerveAdmissionEnvelope(
        nerve="mobile",
        kind="admission_candidate",
        admission_epoch=admission_epoch,
        boot_nonce_commitment=derive_boot_nonce_commitment(
            boot_nonce=boot_nonce,
            admission_epoch=admission_epoch,
        ),
        capabilities=list(capabilities),
        nerve_admission_code=nerve_admission_code,
    )


def derive_nerve_binding_commitment(ctx: NerveBindingContext) -> str:
    """
    Derive the Core-side local binding commitment.

    This is stored only inside Core-controlled FLV/LUKS-bound state.

    The mobile does not store this commitment as a secret.
    """
    _require_hex_hash("local_master_binding_hash", ctx.local_master_binding_hash)
    _require_hex_hash("nerve_admission_code", ctx.nerve_admission_code)
    _require_non_empty("sol_epoch", ctx.sol_epoch)
    _require_non_empty("nerve_binding_nonce", ctx.nerve_binding_nonce)

    return stable_hash_hex(
        ctx.local_master_binding_hash,
        ctx.nerve_admission_code,
        ctx.sol_epoch,
        ctx.nerve_binding_nonce,
        "WHISPER_NERVE_BINDING_COMMITMENT_V1",
    )


def build_nerve_binding_record(
    binding_commitment: str,
    nerve_birth_epoch: str,
    capabilities: List[str],
    last_seen_epoch: str,
    revoked: bool = False,
) -> NerveBindingRecord:
    _require_hex_hash("binding_commitment", binding_commitment)
    _require_non_empty("nerve_birth_epoch", nerve_birth_epoch)
    _require_non_empty("last_seen_epoch", last_seen_epoch)
    _require_capabilities(capabilities)

    return NerveBindingRecord(
        nerve_binding_commitment=binding_commitment,
        nerve_birth_epoch=nerve_birth_epoch,
        nerve_capabilities=list(capabilities),
        nerve_revocation_state="revoked" if revoked else "active",
        surface_commitment_version="NERVE_MOBILE_SURFACE_SEED_V1",
        last_seen_epoch=last_seen_epoch,
    )


def validate_nerve_admission_code(
    expected_code: str,
    observed_code: str,
) -> bool:
    _require_non_empty("expected_code", expected_code)
    _require_non_empty("observed_code", observed_code)

    return hmac.compare_digest(expected_code, observed_code)


def decide_nerve_admission(
    expected_code: str,
    envelope: NerveAdmissionEnvelope,
    existing_revoked: bool = False,
) -> AdmissionDecision:
    """
    Core-side admission decision.

    A revoked Nerve is rejected even if the code matches.

    A bad code is ignored.

    A valid non-revoked appearance is admitted.
    """
    if envelope.nerve != "mobile":
        raise ValueError("unsupported nerve kind")

    if envelope.kind != "admission_candidate":
        raise ValueError("unsupported admission kind")

    _require_capabilities(envelope.capabilities)

    if existing_revoked:
        return "revoke"

    if validate_nerve_admission_code(
        expected_code=expected_code,
        observed_code=envelope.nerve_admission_code,
    ):
        return "admit"

    return "ignore"


def binding_record_to_safe_summary(record: NerveBindingRecord) -> Dict[str, object]:
    """
    Export a safe summary without exposing the full binding commitment.
    """
    return {
        "nerve_binding_prefix": record.nerve_binding_commitment[:16],
        "nerve_birth_epoch": record.nerve_birth_epoch,
        "nerve_capabilities": list(record.nerve_capabilities),
        "nerve_revocation_state": record.nerve_revocation_state,
        "surface_commitment_version": record.surface_commitment_version,
        "last_seen_epoch": record.last_seen_epoch,
    }


if __name__ == "__main__":
    imei_hash_local = stable_hash_hex("local-imei-material")
    carrier_hint_hash = stable_hash_hex("carrier-hint")

    surface = NerveMobileSurfaceContext(
        imei_hash_local=imei_hash_local,
        carrier_hint_hash=carrier_hint_hash,
        sol_admission_challenge="sol-challenge",
        boot_nonce="boot-nonce",
        admission_epoch="epoch-1",
    )

    surface_seed = derive_surface_seed(surface)
    admission_code = derive_nerve_admission_code(surface_seed, "epoch-1")

    envelope = build_admission_envelope(
        admission_epoch="epoch-1",
        boot_nonce="boot-nonce",
        capabilities=["text", "audio", "image"],
        nerve_admission_code=admission_code,
    )

    decision = decide_nerve_admission(
        expected_code=admission_code,
        envelope=envelope,
    )

    local_master_binding_hash = stable_hash_hex("local-master-binding")
    binding_commitment = derive_nerve_binding_commitment(
        NerveBindingContext(
            local_master_binding_hash=local_master_binding_hash,
            nerve_admission_code=admission_code,
            sol_epoch="epoch-1",
            nerve_binding_nonce="binding-nonce",
        )
    )

    record = build_nerve_binding_record(
        binding_commitment=binding_commitment,
        nerve_birth_epoch="epoch-1",
        capabilities=["text", "audio", "image"],
        last_seen_epoch="epoch-1",
    )

    print("Nerve admission code:", admission_code[:16])
    print("Admission decision:", decision)
    print("Binding prefix:", record.nerve_binding_commitment[:16])
