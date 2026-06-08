from __future__ import annotations

import os

import pytest

try:
    import cryptography  # noqa: F401
except Exception as exc:
    pytest.skip(f"cryptography dependency missing: {exc}", allow_module_level=True)

from tests.rotor_crypto_doctrine_runner import run_rotor_crypto_doctrine_metrics


@pytest.mark.slow
def test_rotor_crypto_doctrine_metrics_100k(monkeypatch):
    if os.environ.get("WHISPER_RUN_100K") != "1":
        pytest.skip("Set WHISPER_RUN_100K=1 to run the 100k endurance test")

    run_rotor_crypto_doctrine_metrics(
        loops=100_000,
        test_name="ROTOR_CRYPTO_DOCTRINE_METRICS_100K",
        report_name="rotor_crypto_doctrine_metrics_100k.json",
        monkeypatch=monkeypatch,
    )
