# tests/test_loader_v01.py

import pytest

from loader_v01 import Loader
from mce_v01 import MCE


SEED = b"whisper-loader-seed"


def test_fragment_size_scales_with_payload():
    loader = Loader(MCE(SEED))

    assert loader.decide_fragment_size(0) == 64
    assert loader.decide_fragment_size(100) == 64
    assert loader.decide_fragment_size(1024) == 64
    assert loader.decide_fragment_size(1025) == 256
    assert loader.decide_fragment_size(8192) == 256
    assert loader.decide_fragment_size(8193) == 512
    assert loader.decide_fragment_size(65536) == 512
    assert loader.decide_fragment_size(65537) == 1024


def test_route_count_varies_based_on_mce_state():
    loader = Loader(MCE(SEED))

    results = {
        loader.decide_route_count(state)
        for state in [
            "00000000",
            "00000001",
            "00000002",
            "00000003",
            "abcdef12",
        ]
    }

    assert results.issubset({1, 2, 3})
    assert len(results) >= 2


def test_retry_policy_is_deterministic_per_seed():
    loader_a = Loader(MCE(SEED))
    loader_b = Loader(MCE(SEED))

    assert loader_a.decide_retry_policy() == loader_b.decide_retry_policy()


def test_all_decisions_are_reversible_same_input_same_output():
    # "Reversible" here means deterministic/idempotent for same visible inputs.
    mce_a = MCE(SEED)
    mce_b = MCE(SEED)

    loader_a = Loader(mce_a)
    loader_b = Loader(mce_b)

    assert loader_a.decide_all(4096) == loader_b.decide_all(4096)


def test_loader_state_changes_after_mce_digest():
    mce = MCE(SEED)
    loader = Loader(mce)

    before = loader.decide_all(4096)

    mce.digest_fragment(b"fragment")
    after = loader.decide_all(4096)

    assert before["mce_state_hex"] != after["mce_state_hex"]


def test_loader_rejects_invalid_payload_size():
    loader = Loader(MCE(SEED))

    with pytest.raises(ValueError):
        loader.decide_fragment_size(-1)

    with pytest.raises(TypeError):
        loader.decide_fragment_size("bad")  # type: ignore[arg-type]
