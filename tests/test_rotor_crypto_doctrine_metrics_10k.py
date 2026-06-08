from __future__ import annotations

import pytest

try:
    import cryptography  # noqa: F401
except Exception as exc:
    pytest.skip(f"cryptography dependency missing: {exc}", allow_module_level=True)

from tests.rotor_crypto_doctrine_runner import run_rotor_crypto_doctrine_metrics


def test_rotor_crypto_doctrine_metrics_10k(monkeypatch):
    run_rotor_crypto_doctrine_metrics(
        loops=10_000,
        test_name="ROTOR_CRYPTO_DOCTRINE_METRICS_10K",
        report_name="rotor_crypto_doctrine_metrics_10k.json",
        monkeypatch=monkeypatch,
    )
