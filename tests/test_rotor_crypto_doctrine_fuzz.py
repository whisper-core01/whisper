from __future__ import annotations

import random

import pytest

try:
    import cryptography  # noqa: F401
except Exception as exc:
    pytest.skip(f"cryptography dependency missing: {exc}", allow_module_level=True)

from tests.rotor_crypto_doctrine_runner import (
    make_fuzz_context,
    make_fuzz_payload,
    run_rotor_crypto_doctrine_metrics,
)


def test_rotor_crypto_doctrine_fuzz_10k(monkeypatch):
    rng = random.Random(0x57_48_49_53_50_45_52)  # WHISPER

    def context_factory(i: int):
        return make_fuzz_context(rng, i)

    def payload_factory(i: int):
        return make_fuzz_payload(rng, i)

    run_rotor_crypto_doctrine_metrics(
        loops=10_000,
        test_name="ROTOR_CRYPTO_DOCTRINE_FUZZ_10K",
        report_name="rotor_crypto_doctrine_fuzz_10k.json",
        context_factory=context_factory,
        payload_factory=payload_factory,
        monkeypatch=monkeypatch,
    )
