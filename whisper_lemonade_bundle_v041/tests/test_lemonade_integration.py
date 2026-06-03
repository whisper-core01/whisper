# tests/test_lemonade_integration.py

from dome_v01 import Dome
from lemonade_v01 import Lemonade
from mce_hardened_v01 import MCEHardened


def test_lemonade_dome_mcehardened_integration_clean_fragment():
    dome = Dome()
    lemonade = Lemonade()
    mce = MCEHardened(b"lemonade-integration-seed")
    fragment = b"clean fragment payload"

    wrapped = dome.wrap_fragment(fragment, metadata="clean")
    unwrapped, _metadata = dome.unwrap_fragment(wrapped)
    transformed, snapshot, validation = mce.digest_fragment_checked(unwrapped)

    report = lemonade.scan_fragment(
        fragment=transformed,
        fragment_id=snapshot.fragment_counter,
        queue_depth=1,
        fragment_rate=10.0,
        validation_report=validation,
    )

    assert validation["valid"] is True
    assert report.blocked is False


def test_lemonade_detects_dome_rejected_pattern():
    dome = Dome()
    lemonade = Lemonade()
    bad = b"WHISPER_POISON" + (b"\x00" * (Dome.MAX_NULL_RUN + 1))

    assert dome.should_accept(bad) is False

    report = lemonade.scan_fragment(
        fragment=bad,
        fragment_id=0,
        queue_depth=4096,
        fragment_rate=10000.0,
        validation_report={"valid": False, "issues": ["demo"]},
    )

    assert report.blocked is True
