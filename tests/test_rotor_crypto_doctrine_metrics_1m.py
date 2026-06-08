from __future__ import annotations

import os

import pytest

try:
    import cryptography  # noqa: F401
except Exception as exc:
    pytest.skip(f"cryptography dependency missing: {exc}", allow_module_level=True)

from tests.rotor_crypto_doctrine_runner import run_rotor_crypto_doctrine_metrics


@pytest.mark.slow
@pytest.mark.soak
def test_rotor_crypto_doctrine_metrics_1m(monkeypatch):
    if os.environ.get("WHISPER_RUN_1M") != "1":
        pytest.skip("Set WHISPER_RUN_1M=1 to run the 1M soak test")

    run_rotor_crypto_doctrine_metrics(
        loops=1_000_000,
        test_name="ROTOR_CRYPTO_DOCTRINE_METRICS_1M",
        report_name="rotor_crypto_doctrine_metrics_1m.json",
        monkeypatch=monkeypatch,
    )
