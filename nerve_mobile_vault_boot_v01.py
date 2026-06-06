"""
WHISPER — Nerve Mobile Vault Boot v0.1

Single responsibility:
birth of the mobile nerve.

The Mobile Vault opens only during boot/admission.

The module:
- loads revocable continuity artifacts from the Mobile Vault
- derives admission material from local surface + Vault material + Sol challenge
- emits a Rotor-style Nerve admission code
- zeroizes admission buffers
- returns only the admission code and capabilities

After boot_sequence(), Nerve continues in stateless mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from nerve_mobile_admission_v01 import (
    NerveMobileSurfaceContext,
    build_admission_envelope,
    derive_nerve_admission_code,
    derive_surface_seed,
    stable_hash_hex,
)


@dataclass(frozen=True)
class MobileVaultMaterial:
    origin_hint: str
    nerve_local_material: str
    birth_epoch: str
    last_seen_epoch: str
    revocation_marker: str
    capabilities: List[str]


@dataclass
class AdmissionMaterial:
    surface_seed: str
    vault_mix: str
    rotor_seed: str
    admission_epoch: str


@dataclass(frozen=True)
class NerveBootResult:
    nerve_admission_code: str
    admission_epoch: str
    capabilities: List[str]
    vault_closed: bool
    buffers_zeroized: bool


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _require_capabilities(capabilities: List[str]) -> None:
    if not capabilities:
        raise ValueError("capabilities must not be empty")


def load_mobile_vault() -> MobileVaultMaterial:
    """
    Load Mobile Vault continuity artifacts.

    Prototype note:
    In production, this function is a Wasm-side host call.

    It must only return revocable continuity artifacts.
    It must not return sovereign WHISPER secrets.
    """
    return MobileVaultMaterial(
        origin_hint=stable_hash_hex("origin-hint"),
        nerve_local_material=stable_hash_hex("nerve-local-material"),
        birth_epoch="epoch-0",
        last_seen_epoch="epoch-0",
        revocation_marker="active",
        capabilities=["text", "audio", "image"],
    )


def close_mobile_vault() -> bool:
    """
    Close the Mobile Vault immediately after reading.

    Prototype note:
    In production, this is a host-side Vault close operation.
    """
    return True


def derive_admission_material(
    surface_context: NerveMobileSurfaceContext,
    vault_material: MobileVaultMaterial,
) -> AdmissionMaterial:
    """
    Derive admission material for Rotor.

    Combines:
    - surface seed
    - origin hint
    - nerve local material
    - Sol challenge epoch

    This material must be zeroized after use.
    """
    _require_non_empty("origin_hint", vault_material.origin_hint)
    _require_non_empty("nerve_local_material", vault_material.nerve_local_material)
    _require_non_empty("admission_epoch", surface_context.admission_epoch)
    _require_capabilities(vault_material.capabilities)

    if vault_material.revocation_marker == "revoked":
        raise ValueError("mobile vault material is revoked")

    surface_seed = derive_surface_seed(surface_context)

    vault_mix = stable_hash_hex(
        vault_material.origin_hint,
        vault_material.nerve_local_material,
        vault_material.birth_epoch,
        vault_material.last_seen_epoch,
        "WHISPER_NERVE_MOBILE_VAULT_MIX_V1",
    )

    rotor_seed = stable_hash_hex(
        surface_seed,
        vault_mix,
        surface_context.sol_admission_challenge,
        surface_context.boot_nonce,
        surface_context.admission_epoch,
        "WHISPER_NERVE_MOBILE_ROTOR_SEED_V1",
    )

    return AdmissionMaterial(
        surface_seed=surface_seed,
        vault_mix=vault_mix,
        rotor_seed=rotor_seed,
        admission_epoch=surface_context.admission_epoch,
    )


def emit_nerve_admission_code(admission_material: AdmissionMaterial) -> str:
    """
    Emit the Nerve admission code.

    This models RotorMachine in nerve_admission mode.
    """
    _require_non_empty("rotor_seed", admission_material.rotor_seed)

    return derive_nerve_admission_code(
        surface_seed=admission_material.rotor_seed,
        admission_epoch=admission_material.admission_epoch,
    )


def zeroize_admission_buffers(
    admission_material: AdmissionMaterial,
    vault_material: MobileVaultMaterial,
) -> bool:
    """
    Zeroize admission buffers.

    Python cannot guarantee real memory erasure.

    This function models the required invariant:
    Vault-derived material and admission material must not remain live after
    deriving the Nerve admission code.
    """
    admission_material.surface_seed = ""
    admission_material.vault_mix = ""
    admission_material.rotor_seed = ""
    admission_material.admission_epoch = ""

    object.__setattr__(vault_material, "origin_hint", "")
    object.__setattr__(vault_material, "nerve_local_material", "")
    object.__setattr__(vault_material, "birth_epoch", "")
    object.__setattr__(vault_material, "last_seen_epoch", "")
    object.__setattr__(vault_material, "revocation_marker", "")
    object.__setattr__(vault_material, "capabilities", [])

    return True


def boot_sequence(
    surface_context: NerveMobileSurfaceContext,
) -> NerveBootResult:
    """
    Execute the Nerve Mobile boot/admission sequence.

    Order:
    - load Mobile Vault
    - derive admission material
    - close Mobile Vault
    - emit Nerve admission code
    - zeroize Vault/admission buffers
    - return only code + capabilities
    """
    vault_material = load_mobile_vault()
    capabilities = list(vault_material.capabilities)

    admission_material = derive_admission_material(
        surface_context=surface_context,
        vault_material=vault_material,
    )

    vault_closed = close_mobile_vault()

    if not vault_closed:
        raise RuntimeError("Mobile Vault did not close")

    nerve_admission_code = emit_nerve_admission_code(admission_material)

    buffers_zeroized = zeroize_admission_buffers(
        admission_material=admission_material,
        vault_material=vault_material,
    )

    return NerveBootResult(
        nerve_admission_code=nerve_admission_code,
        admission_epoch=surface_context.admission_epoch,
        capabilities=capabilities,
        vault_closed=vault_closed,
        buffers_zeroized=buffers_zeroized,
    )


if __name__ == "__main__":
    surface_context = NerveMobileSurfaceContext(
        imei_hash_local=stable_hash_hex("imei-local"),
        carrier_hint_hash=stable_hash_hex("carrier"),
        sol_admission_challenge="sol-challenge",
        boot_nonce="boot-nonce",
        admission_epoch="epoch-1",
    )

    result = boot_sequence(surface_context)

    envelope = build_admission_envelope(
        admission_epoch=result.admission_epoch,
        boot_nonce="boot-nonce",
        capabilities=result.capabilities,
        nerve_admission_code=result.nerve_admission_code,
    )

    print("Nerve boot admission code:", result.nerve_admission_code[:16])
    print("Vault closed:", result.vault_closed)
    print("Buffers zeroized:", result.buffers_zeroized)
    print("Envelope nerve:", envelope.nerve)
