from __future__ import annotations

import hashlib
import json
import socket
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

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
REPORT_DIR = Path("reports")
REPORT_PATH = REPORT_DIR / "rotor_crypto_doctrine_metrics_1000.json"


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

    Branche ici la vraie RotorMachine.
    Le fallback permet seulement un smoke-test doctrinal.
    """

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


def ms(seconds: float) -> float:
    return seconds * 1000.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = int(round((len(ordered) - 1) * p))
    return ordered[k]


def test_rotor_crypto_doctrine_metrics_1000(monkeypatch):
    external_dependency_calls = 0

    def blocked_network(*args, **kwargs):
        nonlocal external_dependency_calls
        external_dependency_calls += 1
        raise AssertionError("External dependency forbidden: network access attempted")

    monkeypatch.setattr(socket, "socket", blocked_network)
    monkeypatch.setattr(socket, "create_connection", blocked_network)

    seen_materials: set[bytes] = set()
    seen_keys: set[bytes] = set()
    seen_nonces: set[bytes] = set()
    seen_ciphertexts: set[bytes] = set()

    material_derivation_ms: list[float] = []
    hkdf_key_ms: list[float] = []
    hkdf_nonce_ms: list[float] = []
    encrypt_ms: list[float] = []
    decrypt_ms: list[float] = []
    cycle_ms: list[float] = []

    metrics = {
        "test_name": "ROTOR_CRYPTO_DOCTRINE_METRICS_1000",
        "loops": LOOPS,
        "passed_cycles": 0,
        "failed_cycles": 0,
        "material_collisions": 0,
        "key_collisions": 0,
        "nonce_reuse": 0,
        "ciphertext_collisions": 0,
        "tamper_ciphertext_accepted": 0,
        "tamper_tag_accepted": 0,
        "tamper_aad_accepted": 0,
        "roundtrip_failures": 0,
        "context_separation_failures": 0,
        "rm_direct_key_usage_detected": 0,
        "external_dependency_calls": 0,
    }

    test_started = time.perf_counter()

    for i in range(LOOPS):
        cycle_started = time.perf_counter()

        try:
            ctx = make_context(i)
            payload = make_payload(i)
            aad = make_aad(ctx)

            t0 = time.perf_counter()
            material_1 = rotor_machine_key_material(ctx)
            material_2 = rotor_machine_key_material(ctx)
            material_derivation_ms.append(ms(time.perf_counter() - t0))

            assert material_1 == material_2
            assert isinstance(material_1, bytes)
            assert len(material_1) >= 32

            changed_ctx = RotorContext(
                local_seed=ctx.local_seed,
                internal_state=ctx.internal_state,
                session_id=ctx.session_id,
                fragment_id=ctx.fragment_id + 1,
                cycle_id=ctx.cycle_id,
            )
            changed_material = rotor_machine_key_material(changed_ctx)

            if changed_material == material_1:
                metrics["context_separation_failures"] += 1
            assert changed_material != material_1

            t0 = time.perf_counter()
            key = derive_aead_key(material_1, ctx)
            hkdf_key_ms.append(ms(time.perf_counter() - t0))

            t0 = time.perf_counter()
            nonce = derive_nonce(material_1, ctx)
            hkdf_nonce_ms.append(ms(time.perf_counter() - t0))

            assert len(key) == 32
            assert len(nonce) == 12

            if key == material_1[:32]:
                metrics["rm_direct_key_usage_detected"] += 1
            assert key != material_1[:32]

            if material_1 in seen_materials:
                metrics["material_collisions"] += 1
            if key in seen_keys:
                metrics["key_collisions"] += 1
            if nonce in seen_nonces:
                metrics["nonce_reuse"] += 1

            assert material_1 not in seen_materials
            assert key not in seen_keys
            assert nonce not in seen_nonces

            aead = ChaCha20Poly1305(key)

            t0 = time.perf_counter()
            ciphertext = aead.encrypt(nonce, payload, aad)
            encrypt_ms.append(ms(time.perf_counter() - t0))

            if ciphertext in seen_ciphertexts:
                metrics["ciphertext_collisions"] += 1
            assert ciphertext not in seen_ciphertexts

            t0 = time.perf_counter()
            plaintext = aead.decrypt(nonce, ciphertext, aad)
            decrypt_ms.append(ms(time.perf_counter() - t0))

            if plaintext != payload:
                metrics["roundtrip_failures"] += 1
            assert plaintext == payload

            tampered_ciphertext = bytearray(ciphertext)
            tampered_ciphertext[0] ^= 0x01
            try:
                aead.decrypt(nonce, bytes(tampered_ciphertext), aad)
                metrics["tamper_ciphertext_accepted"] += 1
            except Exception:
                pass

            tampered_tag = bytearray(ciphertext)
            tampered_tag[-1] ^= 0x01
            try:
                aead.decrypt(nonce, bytes(tampered_tag), aad)
                metrics["tamper_tag_accepted"] += 1
            except Exception:
                pass

            try:
                aead.decrypt(nonce, ciphertext, aad + b"::tampered")
                metrics["tamper_aad_accepted"] += 1
            except Exception:
                pass

            assert metrics["tamper_ciphertext_accepted"] == 0
            assert metrics["tamper_tag_accepted"] == 0
            assert metrics["tamper_aad_accepted"] == 0

            seen_materials.add(material_1)
            seen_keys.add(key)
            seen_nonces.add(nonce)
            seen_ciphertexts.add(ciphertext)

            metrics["passed_cycles"] += 1

        except Exception:
            metrics["failed_cycles"] += 1
            raise

        finally:
            cycle_ms.append(ms(time.perf_counter() - cycle_started))

    total_ms = ms(time.perf_counter() - test_started)
    metrics["external_dependency_calls"] = external_dependency_calls
    metrics["success_rate_percent"] = round((metrics["passed_cycles"] / LOOPS) * 100, 6)
    metrics["total_ms"] = round(total_ms, 6)
    metrics["throughput_cycles_per_sec"] = round(LOOPS / (total_ms / 1000.0), 6)

    timing_groups = {
        "material_derivation_ms": material_derivation_ms,
        "hkdf_key_ms": hkdf_key_ms,
        "hkdf_nonce_ms": hkdf_nonce_ms,
        "encrypt_ms": encrypt_ms,
        "decrypt_ms": decrypt_ms,
        "cycle_ms": cycle_ms,
    }

    for name, values in timing_groups.items():
        metrics[f"{name}_mean"] = round(statistics.mean(values), 6)
        metrics[f"{name}_median"] = round(statistics.median(values), 6)
        metrics[f"{name}_p95"] = round(percentile(values, 0.95), 6)
        metrics[f"{name}_p99"] = round(percentile(values, 0.99), 6)
        metrics[f"{name}_max"] = round(max(values), 6)

    REPORT_DIR.mkdir(exist_ok=True)
    REPORT_PATH.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    print("\nROTOR_CRYPTO_DOCTRINE_METRICS_1000")
    print(json.dumps(metrics, indent=2, sort_keys=True))

    assert metrics["passed_cycles"] == LOOPS
    assert metrics["failed_cycles"] == 0
    assert metrics["material_collisions"] == 0
    assert metrics["key_collisions"] == 0
    assert metrics["nonce_reuse"] == 0
    assert metrics["ciphertext_collisions"] == 0
    assert metrics["tamper_ciphertext_accepted"] == 0
    assert metrics["tamper_tag_accepted"] == 0
    assert metrics["tamper_aad_accepted"] == 0
    assert metrics["roundtrip_failures"] == 0
    assert metrics["context_separation_failures"] == 0
    assert metrics["rm_direct_key_usage_detected"] == 0
    assert metrics["external_dependency_calls"] == 0
