# tests/test_regression_v043.py

"""
Regression tests for Whisper MVP v0.4.x.

Purpose:
    Lock deterministic behavior across core components.

These tests are intentionally "golden-style":
    - same seed;
    - same payload;
    - same fragment IDs;
    - same expected structural invariants.

They do not prove security. They protect against accidental behavioral drift.
"""

import json
from pathlib import Path

from dome_v01 import Dome
from full_pipeline_v01 import FullPipeline
from lemonade_v01 import Lemonade
from loader_v01 import Loader
from mce_hardened_v01 import MCEHardened
from reticulum_bridge_v01 import ReticulumBridge
from rotor_machine_v01 import RotorMachine
from vault_disk_v01 import VaultDisk
from vault_v01 import Vault
from voxmesh_v01 import VoxMesh


REGRESSION_SEED = b"whisper-regression-seed-v043"
REGRESSION_PAYLOAD = b"Whisper regression payload v0.4.3" * 32


def test_regression_rotor_machine_roundtrip_and_determinism():
    rm_a = RotorMachine(REGRESSION_SEED)
    rm_b = RotorMachine(REGRESSION_SEED)

    payload = b"rotor-regression-payload"
    fragment_id = 42

    encoded_a = rm_a.transform_bytes(payload, fragment_id)
    encoded_b = rm_b.transform_bytes(payload, fragment_id)

    assert encoded_a == encoded_b
    assert encoded_a != payload
    assert rm_a.inverse_transform_bytes(encoded_a, fragment_id) == payload


def test_regression_mce_hardened_state_sequence_is_stable():
    mce_a = MCEHardened(REGRESSION_SEED)
    mce_b = MCEHardened(REGRESSION_SEED)

    fragments = [b"fragment_%d" % i for i in range(25)]

    out_a = []
    out_b = []

    for fragment in fragments:
        transformed_a, snapshot_a, validation_a = mce_a.digest_fragment_checked(fragment)
        transformed_b, snapshot_b, validation_b = mce_b.digest_fragment_checked(fragment)

        out_a.append(transformed_a)
        out_b.append(transformed_b)

        assert validation_a["valid"] is True
        assert validation_b["valid"] is True
        assert snapshot_a == snapshot_b

    assert out_a == out_b
    assert mce_a.snapshot() == mce_b.snapshot()
    assert mce_a.fragment_counter == 25


def test_regression_loader_decision_is_stable():
    mce = MCEHardened(REGRESSION_SEED)
    loader = Loader(mce)

    decisions_a = loader.decide_all(len(REGRESSION_PAYLOAD))
    decisions_b = loader.decide_all(len(REGRESSION_PAYLOAD))

    assert decisions_a == decisions_b
    assert decisions_a["fragment_size"] in {64, 256, 512, 1024}
    assert decisions_a["route_count"] in {1, 2, 3}
    assert set(decisions_a["retry_policy"]) == {"max_retries", "backoff"}


def test_regression_dome_envelope_roundtrip_is_stable():
    dome = Dome()
    fragment = b"dome-regression-fragment"
    metadata = "fragment_id=7"

    wrapped = dome.wrap_fragment(fragment, metadata=metadata)
    unwrapped, recovered_metadata = dome.unwrap_fragment(wrapped)

    assert unwrapped == fragment
    assert recovered_metadata == metadata
    assert wrapped.startswith(Dome.MAGIC)
    assert dome.get_rejection_rate() == 0.0


def test_regression_lemonade_stateless_does_not_accumulate():
    lemonade = Lemonade()

    bad = b"WHISPER_POISON" + (b"\x00" * 1001)

    report = lemonade.scan_fragment_stateless(
        fragment=bad,
        fragment_id=1,
        queue_depth=Lemonade.MAX_QUEUE_DEPTH + 1,
        fragment_rate=Lemonade.MAX_FRAGMENT_RATE + 1,
        validation_report={"valid": False, "issues": ["regression"]},
    )

    assert report.blocked is True
    assert report.threat_level == 10
    assert lemonade.get_threat_level() == 0
    assert lemonade.report().signals == []


def test_regression_voxmesh_deterministic_states():
    mesh_a = VoxMesh(REGRESSION_SEED)
    mesh_b = VoxMesh(REGRESSION_SEED)

    for i in range(20):
        entropy = b"entropy_%d" % i
        mesh_a.mutate_all(entropy)
        mesh_b.mutate_all(entropy)

    assert mesh_a.coherence_check() is True
    assert mesh_b.coherence_check() is True
    assert mesh_a.get_states_hex() == mesh_b.get_states_hex()
    assert mesh_a.get_divergence_score() == mesh_b.get_divergence_score()


def test_regression_reticulum_bridge_packet_roundtrip():
    bridge = ReticulumBridge()

    packet = bridge.encapsulate(
        payload=b"bridge-regression-payload",
        lane_id=2,
        sequence_id=99,
        metadata="regression",
    )
    decoded = bridge.decapsulate(packet)

    assert decoded.payload == b"bridge-regression-payload"
    assert decoded.lane_id == 2
    assert decoded.sequence_id == 99
    assert decoded.metadata == "regression"


def test_regression_vaultdisk_roundtrip(tmp_path):
    mce = MCEHardened(REGRESSION_SEED)
    vault = Vault()

    for i in range(10):
        fragment = b"vault-fragment_%d" % i
        transformed, snapshot, validation = mce.digest_fragment_checked(fragment)
        assert validation["valid"] is True
        vault.store(i, len(fragment), len(transformed), snapshot, timestamp=1000.0 + i)

    path = tmp_path / "vault.json"
    disk = VaultDisk(path)
    disk.save(vault)
    loaded = disk.load()

    assert loaded.dump() == vault.dump()

    raw = json.loads(path.read_text())
    assert raw["format"] == "whisper-vaultdisk"
    assert raw["version"] == 1
    assert len(raw["entries"]) == 10


def test_regression_full_pipeline_summary_is_stable_shape(tmp_path):
    path = tmp_path / "vault.json"

    pipeline_a = FullPipeline(REGRESSION_SEED, persist_path=path)
    summary_a = pipeline_a.process(REGRESSION_PAYLOAD)

    pipeline_b = FullPipeline(REGRESSION_SEED)
    summary_b = pipeline_b.process(REGRESSION_PAYLOAD)

    stable_keys = [
        "input_size",
        "fragment_size",
        "fragment_count",
        "route_count",
        "lane_count",
        "lane_loads",
        "bridge_packets",
        "vault_entries",
        "blocked_reports",
        "max_threat_level",
        "final_mce_counter",
        "final_mce_state_hex",
        "dome_rejection_rate",
    ]

    for key in stable_keys:
        assert summary_a[key] == summary_b[key]

    assert summary_a["persisted"] is True
    assert Path(summary_a["persisted_path"]).exists()
    assert summary_b["persisted"] is False

    assert summary_a["fragment_count"] == summary_a["bridge_packets"]
    assert summary_a["fragment_count"] == summary_a["vault_entries"]
    assert summary_a["fragment_count"] == summary_a["final_mce_counter"]
    assert summary_a["blocked_reports"] == 0
