from nerve_mobile_revocation_v01 import (
    build_revoked_continuity_record,
    create_revocation_store,
    decide_nerve_reappearance_with_revocation,
    get_revocation_entry,
    is_nerve_binding_revoked,
    revoke_nerve_binding,
    simulate_clone_after_revocation_flow,
    simulate_non_revoked_reappearance_flow,
    simulate_old_code_after_revocation_flow,
    simulate_revocation_flow,
)
from nerve_mobile_admission_v01 import stable_hash_hex
from nerve_mobile_reappearance_v01 import (
    boot_for_epoch,
    simulate_initial_admission,
)


def test_revocation_store_starts_empty():
    store = create_revocation_store()

    assert store.entries == {}


def test_revoke_nerve_binding_sets_flag():
    store = create_revocation_store()
    binding = stable_hash_hex("binding")

    entry = revoke_nerve_binding(
        store=store,
        nerve_binding_commitment=binding,
        revocation_epoch="epoch-2",
        reason="USER_REVOKED",
    )

    assert entry.revocation_flag is True
    assert is_nerve_binding_revoked(store, binding) is True


def test_get_revocation_entry_returns_entry():
    store = create_revocation_store()
    binding = stable_hash_hex("binding")

    revoke_nerve_binding(
        store=store,
        nerve_binding_commitment=binding,
        revocation_epoch="epoch-2",
        reason="DEVICE_LOST",
    )

    entry = get_revocation_entry(store, binding)

    assert entry is not None
    assert entry.revocation_reason == "DEVICE_LOST"


def test_non_revoked_binding_is_not_revoked():
    store = create_revocation_store()
    binding = stable_hash_hex("binding")

    assert is_nerve_binding_revoked(store, binding) is False


def test_revoked_continuity_record_marks_revoked():
    master = stable_hash_hex("local-master")
    _boot, record = simulate_initial_admission(master)

    revoked = build_revoked_continuity_record(record)

    assert revoked.revocation_state == "revoked"
    assert revoked.nerve_binding_commitment == record.nerve_binding_commitment


def test_revoked_reappearance_is_rejected():
    flow = simulate_revocation_flow()

    assert flow["revoked"] is True
    assert flow["decision"] == "reject"
    assert flow["passed"] is True


def test_non_revoked_reappearance_is_admitted():
    flow = simulate_non_revoked_reappearance_flow()

    assert flow["revoked"] is False
    assert flow["decision"] == "admit"
    assert flow["passed"] is True


def test_old_code_after_revocation_is_rejected():
    flow = simulate_old_code_after_revocation_flow()

    assert flow["old_code_attempted"] is True
    assert flow["decision"] == "reject"
    assert flow["passed"] is True


def test_clone_after_revocation_is_rejected():
    flow = simulate_clone_after_revocation_flow()

    assert flow["clone_attempted"] is True
    assert flow["decision"] == "reject"
    assert flow["passed"] is True


def test_direct_decision_rejects_revoked_binding_before_code_validation():
    master = stable_hash_hex("local-master")
    store = create_revocation_store()

    _previous_boot, record = simulate_initial_admission(master)

    revoke_nerve_binding(
        store=store,
        nerve_binding_commitment=record.nerve_binding_commitment,
        revocation_epoch="epoch-2",
        reason="POLICY_REVOKED",
    )

    current_boot = boot_for_epoch(
        challenge="challenge-2",
        boot_nonce="boot-2",
        epoch="epoch-2",
    )

    decision = decide_nerve_reappearance_with_revocation(
        store=store,
        record=record,
        expected_current_code=current_boot.nerve_admission_code,
        current_challenge="challenge-2",
        previous_challenge="challenge-1",
    )

    assert decision == "reject"
