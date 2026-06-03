# tests/test_week1_integration.py

from loader_v01 import Loader
from mce_hardened_v01 import MCEHardened
from pipeline_demo import fragment_payload


SEED = b"whisper-week1-integration-seed"


def test_mce_hardened_loader_integration():
    payload = b"Whisper week1 integration payload" * 100

    mce = MCEHardened(SEED)
    loader = Loader(mce)

    decisions = loader.decide_all(len(payload))
    fragment_size = decisions["fragment_size"]

    fragments = fragment_payload(payload, fragment_size)

    outputs = []

    for fragment in fragments:
        transformed, snapshot, validation = mce.digest_fragment_checked(fragment)
        outputs.append(transformed)
        assert validation["valid"] is True
        assert snapshot.fragment_counter == len(outputs)

    assert sum(len(x) for x in outputs) == len(payload)
    assert mce.coherence_check()["valid"] is True
    assert mce.fragment_counter == len(fragments)
