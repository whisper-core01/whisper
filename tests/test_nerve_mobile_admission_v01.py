from nerve_mobile_admission_v01 import (
    NerveBindingContext,
    NerveMobileSurfaceContext,
    binding_record_to_safe_summary,
    build_admission_envelope,
    build_nerve_binding_record,
    decide_nerve_admission,
    derive_nerve_admission_code,
    derive_nerve_binding_commitment,
    derive_surface_seed,
    stable_hash_hex,
    validate_nerve_admission_code,
)


def _surface_context(
    challenge="challenge",
    boot_nonce="boot",
    epoch="epoch-1",
):
    return NerveMobileSurfaceContext(
        imei_hash_local=stable_hash_hex("imei-local"),
        carrier_hint_hash=stable_hash_hex("carrier"),
        sol_admission_challenge=challenge,
        boot_nonce=boot_nonce,
        admission_epoch=epoch,
    )


def _admission_code(epoch="epoch-1", challenge="challenge", boot_nonce="boot"):
    surface_seed = derive_surface_seed(
        _surface_context(
            challenge=challenge,
            boot_nonce=boot_nonce,
            epoch=epoch,
        )
    )

    return derive_nerve_admission_code(
        surface_seed=surface_seed,
        admission_epoch=epoch,
    )


def test_surface_seed_is_deterministic():
    ctx = _surface_context()

    a = derive_surface_seed(ctx)
    b = derive_surface_seed(ctx)

    assert a == b
    assert len(a) == 64


def test_surface_seed_changes_with_challenge():
    a = derive_surface_seed(_surface_context(challenge="a"))
    b = derive_surface_seed(_surface_context(challenge="b"))

    assert a != b


def test_surface_seed_changes_with_boot_nonce():
    a = derive_surface_seed(_surface_context(boot_nonce="a"))
    b = derive_surface_seed(_surface_context(boot_nonce="b"))

    assert a != b


def test_admission_code_is_deterministic():
    code_a = _admission_code()
    code_b = _admission_code()

    assert code_a == code_b
    assert len(code_a) == 64


def test_admission_code_changes_with_epoch():
    code_a = _admission_code(epoch="epoch-a")
    code_b = _admission_code(epoch="epoch-b")

    assert code_a != code_b


def test_admission_envelope_does_not_expose_surface_seed():
    code = _admission_code()

    envelope = build_admission_envelope(
        admission_epoch="epoch-1",
        boot_nonce="boot",
        capabilities=["text", "audio"],
        nerve_admission_code=code,
    )

    assert envelope.nerve == "mobile"
    assert envelope.kind == "admission_candidate"
    assert envelope.nerve_admission_code == code
    assert len(envelope.boot_nonce_commitment) == 64
    assert not hasattr(envelope, "surface_seed")
    assert not hasattr(envelope, "imei_hash_local")


def test_valid_nerve_admission_is_admitted():
    code = _admission_code()

    envelope = build_admission_envelope(
        admission_epoch="epoch-1",
        boot_nonce="boot",
        capabilities=["text", "audio"],
        nerve_admission_code=code,
    )

    assert decide_nerve_admission(code, envelope) == "admit"


def test_bad_nerve_admission_is_ignored():
    code = _admission_code()
    bad_code = _admission_code(challenge="other")

    envelope = build_admission_envelope(
        admission_epoch="epoch-1",
        boot_nonce="boot",
        capabilities=["text", "audio"],
        nerve_admission_code=bad_code,
    )

    assert decide_nerve_admission(code, envelope) == "ignore"


def test_revoked_nerve_is_rejected_even_with_valid_code():
    code = _admission_code()

    envelope = build_admission_envelope(
        admission_epoch="epoch-1",
        boot_nonce="boot",
        capabilities=["text", "audio"],
        nerve_admission_code=code,
    )

    assert decide_nerve_admission(code, envelope, existing_revoked=True) == "revoke"


def test_binding_commitment_is_deterministic():
    code = _admission_code()
    master = stable_hash_hex("local-master")

    ctx = NerveBindingContext(
        local_master_binding_hash=master,
        nerve_admission_code=code,
        sol_epoch="epoch-1",
        nerve_binding_nonce="binding",
    )

    a = derive_nerve_binding_commitment(ctx)
    b = derive_nerve_binding_commitment(ctx)

    assert a == b
    assert len(a) == 64


def test_binding_commitment_changes_with_nonce():
    code = _admission_code()
    master = stable_hash_hex("local-master")

    a = derive_nerve_binding_commitment(
        NerveBindingContext(
            local_master_binding_hash=master,
            nerve_admission_code=code,
            sol_epoch="epoch-1",
            nerve_binding_nonce="a",
        )
    )

    b = derive_nerve_binding_commitment(
        NerveBindingContext(
            local_master_binding_hash=master,
            nerve_admission_code=code,
            sol_epoch="epoch-1",
            nerve_binding_nonce="b",
        )
    )

    assert a != b


def test_binding_record_safe_summary_does_not_expose_full_commitment():
    code = _admission_code()
    master = stable_hash_hex("local-master")

    commitment = derive_nerve_binding_commitment(
        NerveBindingContext(
            local_master_binding_hash=master,
            nerve_admission_code=code,
            sol_epoch="epoch-1",
            nerve_binding_nonce="binding",
        )
    )

    record = build_nerve_binding_record(
        binding_commitment=commitment,
        nerve_birth_epoch="epoch-1",
        capabilities=["text", "audio"],
        last_seen_epoch="epoch-1",
    )

    summary = binding_record_to_safe_summary(record)

    assert len(summary["nerve_binding_prefix"]) == 16
    assert "nerve_binding_commitment" not in summary
    assert summary["nerve_revocation_state"] == "active"


def test_validate_nerve_admission_code_true_and_false():
    code = _admission_code()
    other = _admission_code(challenge="other")

    assert validate_nerve_admission_code(code, code) is True
    assert validate_nerve_admission_code(code, other) is False


def test_invalid_capability_rejected():
    code = _admission_code()

    try:
        build_admission_envelope(
            admission_epoch="epoch-1",
            boot_nonce="boot",
            capabilities=["text", "gps"],  # unsupported
            nerve_admission_code=code,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid capability")
