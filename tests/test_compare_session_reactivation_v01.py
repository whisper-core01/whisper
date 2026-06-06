from compare_session_reactivation_v01 import (
    DEFAULT_CASES,
    ConsumedCapsuleStore,
    attempt_session_reactivation_from_traces,
    build_capsule_tag,
    build_closed_session_bundle,
    build_session_context,
    run_reactivation_case,
    run_session_reactivation_suite,
    validate_capsule_first_use,
)
from session_hash_v01 import derive_session_hash


def test_valid_active_fragment_accepted():
    row = run_reactivation_case("seed", "valid_active_fragment")

    assert row["accepted"] is True
    assert row["expected_acceptance"] is True
    assert row["passed"] is True


def test_bad_fragment_tag_rejected():
    row = run_reactivation_case("seed", "bad_fragment_tag")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_revoked_session_fragment_rejected():
    row = run_reactivation_case("seed", "revoked_session_fragment")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_valid_capsule_first_use_accepted():
    row = run_reactivation_case("seed", "valid_capsule_first_use")

    assert row["accepted"] is True
    assert row["expected_acceptance"] is True
    assert row["passed"] is True


def test_consumed_capsule_reactivation_rejected():
    row = run_reactivation_case("seed", "consumed_capsule_reactivation")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_bad_capsule_tag_rejected():
    row = run_reactivation_case("seed", "bad_capsule_tag")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_post_shutdown_fragment_rejected():
    row = run_reactivation_case("seed", "post_shutdown_fragment")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_dormant_flv_cannot_reactivate():
    row = run_reactivation_case("seed", "dormant_flv_cannot_reactivate")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_old_start_seal_cannot_reopen():
    row = run_reactivation_case("seed", "old_start_seal_cannot_reopen")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_old_close_seal_cannot_reopen():
    row = run_reactivation_case("seed", "old_close_seal_cannot_reopen")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_old_repair_hash_cannot_repair_closed_session():
    row = run_reactivation_case("seed", "old_repair_hash_cannot_repair_closed_session")

    assert row["accepted"] is False
    assert row["expected_acceptance"] is False
    assert row["passed"] is True


def test_consumed_capsule_store_rejects_second_use():
    ctx = build_session_context("seed")
    session_hash = derive_session_hash(ctx)
    capsule_tag = build_capsule_tag(session_hash, "seed")

    store = ConsumedCapsuleStore()

    first = validate_capsule_first_use(store, capsule_tag, capsule_tag)
    second = validate_capsule_first_use(store, capsule_tag, capsule_tag)

    assert first is True
    assert second is False


def test_attempt_session_reactivation_from_closed_bundle_fails():
    bundle = build_closed_session_bundle("seed")

    assert attempt_session_reactivation_from_traces(bundle) is False


def test_all_default_cases_pass():
    for case in DEFAULT_CASES:
        row = run_reactivation_case("seed", case)
        assert row["passed"] is True


def test_run_session_reactivation_suite_outputs(tmp_path):
    csv_path = tmp_path / "reactivation.csv"
    json_path = tmp_path / "reactivation.json"

    run_session_reactivation_suite(
        seeds=["a", "b"],
        csv_path=str(csv_path),
        json_path=str(json_path),
    )

    assert csv_path.exists()
    assert json_path.exists()
    assert "session-reactivation-prevention" in json_path.read_text()
