from nerve_mobile_admission_v01 import NerveMobileSurfaceContext, stable_hash_hex
from nerve_mobile_vault_boot_v01 import (
    MobileVaultMaterial,
    boot_sequence,
    derive_admission_material,
    emit_nerve_admission_code,
    load_mobile_vault,
    zeroize_admission_buffers,
)


def _surface_context(challenge="challenge", boot_nonce="boot", epoch="epoch-1"):
    return NerveMobileSurfaceContext(
        imei_hash_local=stable_hash_hex("imei-local"),
        carrier_hint_hash=stable_hash_hex("carrier"),
        sol_admission_challenge=challenge,
        boot_nonce=boot_nonce,
        admission_epoch=epoch,
    )


def test_load_mobile_vault_returns_continuity_material():
    material = load_mobile_vault()

    assert material.origin_hint
    assert material.nerve_local_material
    assert material.revocation_marker == "active"
    assert material.capabilities == ["text", "audio", "image"]


def test_derive_admission_material_is_deterministic():
    surface = _surface_context()
    vault = load_mobile_vault()

    a = derive_admission_material(surface, vault)

    vault = load_mobile_vault()
    b = derive_admission_material(surface, vault)

    assert a.surface_seed == b.surface_seed
    assert a.vault_mix == b.vault_mix
    assert a.rotor_seed == b.rotor_seed


def test_derive_admission_material_changes_with_challenge():
    vault_a = load_mobile_vault()
    vault_b = load_mobile_vault()

    a = derive_admission_material(_surface_context(challenge="a"), vault_a)
    b = derive_admission_material(_surface_context(challenge="b"), vault_b)

    assert a.surface_seed != b.surface_seed
    assert a.rotor_seed != b.rotor_seed


def test_emit_nerve_admission_code_is_deterministic():
    surface = _surface_context()
    vault = load_mobile_vault()
    material = derive_admission_material(surface, vault)

    a = emit_nerve_admission_code(material)
    b = emit_nerve_admission_code(material)

    assert a == b
    assert len(a) == 64


def test_zeroize_admission_buffers_clears_material():
    surface = _surface_context()
    vault = load_mobile_vault()
    material = derive_admission_material(surface, vault)

    assert material.rotor_seed
    assert vault.origin_hint

    result = zeroize_admission_buffers(material, vault)

    assert result is True
    assert material.surface_seed == ""
    assert material.vault_mix == ""
    assert material.rotor_seed == ""
    assert material.admission_epoch == ""
    assert vault.origin_hint == ""
    assert vault.nerve_local_material == ""
    assert vault.capabilities == []


def test_boot_sequence_returns_code_and_closes_vault():
    result = boot_sequence(_surface_context())

    assert len(result.nerve_admission_code) == 64
    assert result.admission_epoch == "epoch-1"
    assert result.capabilities == ["text", "audio", "image"]
    assert result.vault_closed is True
    assert result.buffers_zeroized is True


def test_boot_sequence_changes_with_epoch():
    a = boot_sequence(_surface_context(epoch="epoch-a"))
    b = boot_sequence(_surface_context(epoch="epoch-b"))

    assert a.nerve_admission_code != b.nerve_admission_code


def test_revoked_vault_material_rejected():
    surface = _surface_context()
    vault = MobileVaultMaterial(
        origin_hint=stable_hash_hex("origin"),
        nerve_local_material=stable_hash_hex("local"),
        birth_epoch="epoch-0",
        last_seen_epoch="epoch-0",
        revocation_marker="revoked",
        capabilities=["text"],
    )

    try:
        derive_admission_material(surface, vault)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for revoked vault material")
