# tests/test_full_pipeline_v01.py

from pathlib import Path

from full_pipeline_v01 import FullPipeline
from vault_disk_v01 import VaultDisk


def test_full_pipeline_processes_payload():
    pipeline = FullPipeline(b"full-pipeline-seed")
    payload = b"final integration payload" * 100

    summary = pipeline.process(payload)

    assert summary["input_size"] == len(payload)
    assert summary["fragment_count"] > 0
    assert summary["bridge_packets"] == summary["fragment_count"]
    assert summary["vault_entries"] == summary["fragment_count"]
    assert summary["final_mce_counter"] == summary["fragment_count"]
    assert summary["blocked_reports"] == 0


def test_full_pipeline_persists_vaultdisk(tmp_path):
    path = tmp_path / "vault.json"
    pipeline = FullPipeline(b"full-pipeline-seed", persist_path=path)
    payload = b"persist me" * 100

    summary = pipeline.process(payload)

    assert summary["persisted"] is True
    assert Path(summary["persisted_path"]).exists()

    loaded = VaultDisk(path).load()

    assert len(loaded.entries) == summary["fragment_count"]


def test_full_pipeline_is_deterministic_for_same_seed():
    payload = b"deterministic final pipeline" * 50

    a = FullPipeline(b"same-seed").process(payload)
    b = FullPipeline(b"same-seed").process(payload)

    assert a["fragment_count"] == b["fragment_count"]
    assert a["route_count"] == b["route_count"]
    assert a["lane_loads"] == b["lane_loads"]
    assert a["final_mce_state_hex"] == b["final_mce_state_hex"]
