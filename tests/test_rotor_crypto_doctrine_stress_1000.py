from __future__ import annotations

import hashlib
import socket
from dataclasses import dataclass

import pytest

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except Exception as exc:  # pragma: no cover
    pytest.skip(f"cryptography dependency missing: {exc}", allow_module_level=True)


LOOPS = 1000
KEY_MATERIAL_LEN = 64
DOMAIN = b"WHISPER::ROTOR_CRYPTO_DOCTRINE::v01"


@dataclass(frozen=True)
class RotorContext:
    local_seed: bytes
    internal_state: bytes
    session_id: int
    fragment_id: int
    cycle_id: int


def rotor_machine_key_material(ctx: RotorContext) -> bytes:
    """
    ADAPTATION POINT.

    Branche ici ta vraie RotorMachine si son API est différente.

    Doctrine testée :
    - RotorMachine produit du matériau interne local.
    - Elle ne chiffre pas directement.
    - Le matériau passe ensuite dans HKDF.
    """

    # Variante 1 : si tu as déjà une fonction dédiée.
    try:
        from rotor_machine_v01 import derive_key_material  # type: ignore

        return derive_key_material(
            seed=ctx.local_seed,
            state=ctx.internal_state,
            session_id=ctx.session_id,
            fragment_id=ctx.fragment_id,
            cycle_id=ctx.cycle_id,
            length=KEY_MATERIAL_LEN,
        )
    except ImportError:
        pass

    # Variante 2 : si tu as une classe RotorMachine.
    try:
        from rotor_machine_minimal import RotorMachine  # type: ignore

        rm = RotorMachine(seed=ctx.local_seed)

        if hasattr(rm, "derive_key_material"):
            return rm.derive_key_material(
                state=ctx.internal_state,
                session_id=ctx.session_id,
                fragment_id=ctx.fragment_id,
                cycle_id=ctx.cycle_id,
                length=KEY_MATERIAL_LEN,
            )

        if hasattr(rm, "derive"):
            return rm.derive(
                state=ctx.internal_state,
                session_id=ctx.session_id,
                fragment_id=ctx.fragment_id,
                cycle_id=ctx.cycle_id,
                length=KEY_MATERIAL_LEN,
            )

    except ImportError:
        pass

    # Fallback volontairement déterministe pour permettre le smoke-test doctrinal.
    # À remplacer par la vraie RotorMachine pour la validation finale.
    h = hashlib.blake2b(digest_size=KEY_MATERIAL_LEN, person=b"WHISPER_RM_V01")
    h.update(DOMAIN)
    h.update(ctx.local_seed)
    h.update(ctx.internal_state)
    h.update(ctx.session_id.to_bytes(8, "big"))
    h.update(ctx.fragment_id.to_bytes(8, "big"))
    h.update(ctx.cycle_id.to_bytes(8, "big"))
    return h.digest()


def hkdf_expand(material: bytes, *, info: bytes, length: int) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=DOMAIN,
        info=info,
    ).derive(material)


def derive_aead_key(material: bytes, ctx: RotorContext) -> bytes:
    info = (
        b"WHISPER::AEAD_KEY::"
        + ctx.session_id.to_bytes(8, "big")
        + ctx.fragment_id.to_bytes(8, "big")
        + ctx.cycle_id.to_bytes(8, "big")
    )
    return hkdf_expand(material, info=info, length=32)


def derive_nonce(material: bytes, ctx: RotorContext) -> bytes:
    """
    ChaCha20-Poly1305 nonce: 96 bits / 12 bytes.

    Ici on valide la doctrine ChaCha20-Poly1305 avec nonce strictement dérivé
    et unique par contexte. Pour XChaCha20-Poly1305, passer à 24 bytes
    avec libsodium/PyNaCl.
    """
    info = (
        b"WHISPER::AEAD_NONCE::"
        + ctx.session_id.to_bytes(8, "big")
        + ctx.fragment_id.to_bytes(8, "big")
        + ctx.cycle_id.to_bytes(8, "big")
    )
    return hkdf_expand(material, info=info, length=12)


def make_context(i: int) -> RotorContext:
    return RotorContext(
        local_seed=hashlib.sha256(b"local_seed::" + i.to_bytes(8, "big")).digest(),
        internal_state=hashlib.sha256(b"internal_state::" + i.to_bytes(8, "big")).digest(),
        session_id=10_000 + i,
        fragment_id=20_000 + i,
        cycle_id=30_000 + i,
    )


def make_payload(i: int) -> bytes:
    return (
        b"WHISPER_PAYLOAD::"
        + i.to_bytes(8, "big")
        + hashlib.sha512(b"payload::" + i.to_bytes(8, "big")).digest()
    )


def make_aad(ctx: RotorContext) -> bytes:
    return (
        b"WHISPER_AAD::v01::"
        + ctx.session_id.to_bytes(8, "big")
        + ctx.fragment_id.to_bytes(8, "big")
        + ctx.cycle_id.to_bytes(8, "big")
    )


def test_rotor_crypto_doctrine_stress_1000(monkeypatch):
    """
    ROTOR_CRYPTO_DOCTRINE_STRESS_1000

    Validates:
    - deterministic local derivation
    - context separation
    - HKDF before AEAD key usage
    - ChaCha20-Poly1305 AEAD roundtrip
    - tamper rejection
    - nonce uniqueness
    - no network / RPC / oracle dependency
    - RotorMachine is not used as direct cipher
    """

    def blocked_network(*args, **kwargs):
        raise AssertionError("External dependency forbidden: network access attempted")

    monkeypatch.setattr(socket, "socket", blocked_network)
    monkeypatch.setattr(socket, "create_connection", blocked_network)

    seen_materials: set[bytes] = set()
    seen_keys: set[bytes] = set()
    seen_nonces: set[bytes] = set()
    seen_ciphertexts: set[bytes] = set()

    for i in range(LOOPS):
        ctx = make_context(i)
        payload = make_payload(i)
        aad = make_aad(ctx)

        material_1 = rotor_machine_key_material(ctx)
        material_2 = rotor_machine_key_material(ctx)

        assert isinstance(material_1, bytes)
        assert len(material_1) >= 32

        # INVARIANT_DETERMINISTIC_LOCAL_DERIVATION
        assert material_1 == material_2

        # INVARIANT_CONTEXT_SEPARATION
        changed_ctx = RotorContext(
            local_seed=ctx.local_seed,
            internal_state=ctx.internal_state,
            session_id=ctx.session_id,
            fragment_id=ctx.fragment_id + 1,
            cycle_id=ctx.cycle_id,
        )
        changed_material = rotor_machine_key_material(changed_ctx)
        assert changed_material != material_1

        key = derive_aead_key(material_1, ctx)
        nonce = derive_nonce(material_1, ctx)

        assert len(key) == 32
        assert len(nonce) == 12

        # INVARIANT_RM_NOT_CIPHER
        # La clé AEAD ne doit pas être une tranche brute du matériau RotorMachine.
        assert key != material_1[:32]

        # INVARIANT_NONCE_UNIQUENESS
        assert nonce not in seen_nonces

        aead = ChaCha20Poly1305(key)
        ciphertext = aead.encrypt(nonce, payload, aad)

        # INVARIANT_AEAD_ROUNDTRIP
        plaintext = aead.decrypt(nonce, ciphertext, aad)
        assert plaintext == payload

        # INVARIANT_AUTHENTICATED_DECRYPTION_ONLY
        tampered_ciphertext = bytearray(ciphertext)
        tampered_ciphertext[0] ^= 0x01
        with pytest.raises(Exception):
            aead.decrypt(nonce, bytes(tampered_ciphertext), aad)

        tampered_tag = bytearray(ciphertext)
        tampered_tag[-1] ^= 0x01
        with pytest.raises(Exception):
            aead.decrypt(nonce, bytes(tampered_tag), aad)

        with pytest.raises(Exception):
            aead.decrypt(nonce, ciphertext, aad + b"::tampered")

        # INVARIANT_NO_CRITICAL_COLLISION_IN_1000
        assert material_1 not in seen_materials
        assert key not in seen_keys
        assert ciphertext not in seen_ciphertexts

        seen_materials.add(material_1)
        seen_keys.add(key)
        seen_nonces.add(nonce)
        seen_ciphertexts.add(ciphertext)

    assert len(seen_materials) == LOOPS
    assert len(seen_keys) == LOOPS
    assert len(seen_nonces) == LOOPS
    assert len(seen_ciphertexts) == LOOPS
