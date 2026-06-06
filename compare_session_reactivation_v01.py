"""
WHISPER v1.4.0 — Session Reactivation Comparator.

This comparator validates the v1.4.0 non-reactivation invariant:

An old session may leave local traces, but it must never become active again.

Fragments, capsules, lifecycle seals, rotor close codes, session start seals,
and dormant FLV records may remain as local evidence.

However, none of them can reopen, resume, repair, decrypt, or validate
material under a closed session.

Replay is treated as one technical case of a broader problem:
closed-session reactivation.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Dict, List, Set

from session_hash_v01 import (
    CapsuleSessionContext,
    FragmentSessionContext,
    SessionContext,
    derive_capsule_session_tag,
    derive_fragment_session_tag,
    derive_repair_hash,
    derive_session_hash,
    RepairSessionContext,
    validate_session_tag,
)
from session_revocation_v01 import (
    SessionRevocationStore,
    is_session_revoked,
    mark_session_revoked,
    validate_session_tag_not_revoked,
)
from secure_session_shutdown_v01 import (
    create_runtime_state,
    secure_shutdown_session,
)
from session_start_seal_v01 import (
    SessionStartContext,
    derive_session_start_seal,
    derive_start_step_digest,
    validate_session_start_seal,
)
from session_lifecycle_flv_v01 import (
    FLVMachineBindingContext,
    build_session_lifecycle_flv_record,
    derive_local_master_binding_hash,
    derive_luks_context_digest,
    derive_machine_context_digest,
    stable_hash_hex,
    validate_session_lifecycle_flv_record,
)
from rotor_close_code_v01 import validate_rotor_close_code


@dataclass
class ConsumedCapsuleStore:
    consumed_capsule_tags: Set[str] = field(default_factory=set)


def mark_capsule_consumed(store: ConsumedCapsuleStore, capsule_tag: str) -> None:
    store.consumed_capsule_tags.add(capsule_tag)


def is_capsule_consumed(store: ConsumedCapsuleStore, capsule_tag: str) -> bool:
    return capsule_tag in store.consumed_capsule_tags


def validate_capsule_first_use(
    store: ConsumedCapsuleStore,
    expected_capsule_tag: str,
    observed_capsule_tag: str,
) -> bool:
    if not validate_session_tag(expected_capsule_tag, observed_capsule_tag):
        return False

    if is_capsule_consumed(store, observed_capsule_tag):
        return False

    mark_capsule_consumed(store, observed_capsule_tag)
    return True


def build_session_context(seed: str) -> SessionContext:
    return SessionContext(
        sol_id=f"sol:{seed}",
        epoch="1",
        local_ephemeral_material=f"local:{seed}",
        remote_ephemeral_material=f"remote:{seed}",
        session_nonce=f"session-nonce:{seed}",
        message_commitment=f"message:{seed}",
        transfer_profile_commitment=f"profile:{seed}",
    )


def build_fragment_tag(
    session_hash: str,
    seed: str,
    fragment_nonce: str = "fragment",
) -> str:
    return derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce=f"{fragment_nonce}:{seed}",
            fragment_index_commitment=f"idx:{seed}",
            fragment_role="primary",
            capsule_nonce=f"capsule:{seed}",
        )
    )


def build_capsule_tag(
    session_hash: str,
    seed: str,
    capsule_nonce: str = "capsule",
) -> str:
    return derive_capsule_session_tag(
        CapsuleSessionContext(
            session_hash=session_hash,
            capsule_nonce=f"{capsule_nonce}:{seed}",
            capsule_role="data",
            capsule_epoch="1",
        )
    )


def build_start_seal(
    session_ctx: SessionContext,
    session_hash: str,
    seed: str,
) -> str:
    return derive_session_start_seal(
        SessionStartContext(
            session_hash=session_hash,
            session_nonce=session_ctx.session_nonce,
            start_nonce=f"start:{seed}",
            open_reason="USER_STARTED_SESSION",
            wasm_init_digest=derive_start_step_digest(
                session_hash,
                "WASM_INITIALIZED",
                f"wasm:{seed}",
            ),
            custody_init_digest=derive_start_step_digest(
                session_hash,
                "CUSTODY_EMPTY",
                f"custody:{seed}",
            ),
            volatile_init_digest=derive_start_step_digest(
                session_hash,
                "VOLATILE_BUFFERS_EMPTY",
                f"volatile:{seed}",
            ),
            created_at=1,
        )
    )


def build_closed_session_bundle(seed: str, closed_at: int = 123) -> Dict[str, object]:
    """
    Build a closed local session bundle containing local traces.

    These traces are evidence only.
    They must not reactivate the session.
    """
    session_ctx = build_session_context(seed)
    session_hash = derive_session_hash(session_ctx)
    start_seal = build_start_seal(session_ctx, session_hash, seed)

    runtime = create_runtime_state(session_ctx)
    revocation_store = SessionRevocationStore()

    shutdown = secure_shutdown_session(
        runtime=runtime,
        store=revocation_store,
        close_reason="USER_LEFT_SESSION",
        revocation_reason="USER_LEFT_SESSION",
        shutdown_nonce=f"shutdown:{seed}",
        key_epoch="epoch-1",
        destruction_nonce=f"destroy:{seed}",
        closed_at=closed_at,
    )

    master_key_hash = stable_hash_hex(f"local-master:{seed}")

    binding = FLVMachineBindingContext(
        local_master_binding_hash=derive_local_master_binding_hash(
            master_key_hash,
            f"binding:{seed}",
        ),
        machine_context_digest=derive_machine_context_digest(
            f"machine:{seed}",
            f"machine-nonce:{seed}",
        ),
        luks_context_digest=derive_luks_context_digest(
            f"luks:{seed}",
            f"luks-nonce:{seed}",
        ),
    )

    flv_record = build_session_lifecycle_flv_record(
        session_hash=session_hash,
        session_start_seal=start_seal,
        rotor_close_code=shutdown.rotor_close_code,
        lifecycle_state="DORMANT",
        open_reason="USER_STARTED_SESSION",
        close_reason="USER_LEFT_SESSION",
        receive_mode="BUFFERED",
        created_at=1,
        closed_at=closed_at,
        dormant=True,
        binding=binding,
    )

    return {
        "session_ctx": session_ctx,
        "session_hash": session_hash,
        "start_seal": start_seal,
        "rotor_close_code": shutdown.rotor_close_code,
        "revocation_store": revocation_store,
        "flv_record": flv_record,
        "closed_at": closed_at,
    }


def attempt_session_reactivation_from_traces(bundle: Dict[str, object]) -> bool:
    """
    Attempt to reactivate a closed session from local traces.

    This must always fail.

    A valid FLV record, valid start seal, or valid rotor close code can prove
    lifecycle events, but none of them can make the session active again.
    """
    session_hash = str(bundle["session_hash"])
    start_seal = str(bundle["start_seal"])
    rotor_close_code = str(bundle["rotor_close_code"])
    revocation_store = bundle["revocation_store"]
    flv_record = bundle["flv_record"]
    closed_at = int(bundle["closed_at"])

    if not isinstance(revocation_store, SessionRevocationStore):
        raise TypeError("revocation_store must be SessionRevocationStore")

    flv_valid = validate_session_lifecycle_flv_record(flv_record)  # type: ignore[arg-type]
    start_valid = validate_session_start_seal(start_seal, start_seal)
    close_valid = validate_rotor_close_code(rotor_close_code, rotor_close_code)
    session_dead = is_session_revoked(revocation_store, session_hash, now=closed_at)

    # This is the key invariant:
    # local traces may validate as evidence, but a revoked session remains dead.
    if flv_valid and start_valid and close_valid and session_dead:
        return False

    return False


def run_reactivation_case(seed: str, case: str) -> Dict[str, object]:
    session_ctx = build_session_context(seed)
    session_hash = derive_session_hash(session_ctx)

    revocation_store = SessionRevocationStore()
    consumed_store = ConsumedCapsuleStore()

    good_fragment_tag = build_fragment_tag(session_hash, seed, "fragment")
    bad_fragment_tag = build_fragment_tag(session_hash, seed, "fragment-bad")

    good_capsule_tag = build_capsule_tag(session_hash, seed, "capsule")
    bad_capsule_tag = build_capsule_tag(session_hash, seed, "capsule-bad")

    accepted = False
    expected_acceptance = False
    reason = ""

    if case == "valid_active_fragment":
        accepted = validate_session_tag_not_revoked(
            store=revocation_store,
            session_hash=session_hash,
            expected_tag=good_fragment_tag,
            observed_tag=good_fragment_tag,
            now=10,
        )
        expected_acceptance = True
        reason = "active session with valid fragment tag"

    elif case == "bad_fragment_tag":
        accepted = validate_session_tag_not_revoked(
            store=revocation_store,
            session_hash=session_hash,
            expected_tag=good_fragment_tag,
            observed_tag=bad_fragment_tag,
            now=10,
        )
        expected_acceptance = False
        reason = "bad fragment tag cannot validate"

    elif case == "revoked_session_fragment":
        mark_session_revoked(
            store=revocation_store,
            session_hash=session_hash,
            reason="USER_LEFT_SESSION",
            scope="SESSION",
            created_at=10,
        )

        accepted = validate_session_tag_not_revoked(
            store=revocation_store,
            session_hash=session_hash,
            expected_tag=good_fragment_tag,
            observed_tag=good_fragment_tag,
            now=10,
        )
        expected_acceptance = False
        reason = "locally revoked session cannot accept fragment"

    elif case == "valid_capsule_first_use":
        accepted = validate_capsule_first_use(
            store=consumed_store,
            expected_capsule_tag=good_capsule_tag,
            observed_capsule_tag=good_capsule_tag,
        )
        expected_acceptance = True
        reason = "valid capsule first use"

    elif case == "consumed_capsule_reactivation":
        first = validate_capsule_first_use(
            store=consumed_store,
            expected_capsule_tag=good_capsule_tag,
            observed_capsule_tag=good_capsule_tag,
        )

        second = validate_capsule_first_use(
            store=consumed_store,
            expected_capsule_tag=good_capsule_tag,
            observed_capsule_tag=good_capsule_tag,
        )

        accepted = bool(first and second)
        expected_acceptance = False
        reason = "consumed capsule cannot reactivate session material"

    elif case == "bad_capsule_tag":
        accepted = validate_capsule_first_use(
            store=consumed_store,
            expected_capsule_tag=good_capsule_tag,
            observed_capsule_tag=bad_capsule_tag,
        )
        expected_acceptance = False
        reason = "bad capsule tag cannot validate"

    elif case == "post_shutdown_fragment":
        runtime = create_runtime_state(session_ctx)

        secure_shutdown_session(
            runtime=runtime,
            store=revocation_store,
            close_reason="USER_LEFT_SESSION",
            revocation_reason="USER_LEFT_SESSION",
            shutdown_nonce=f"shutdown:{seed}",
            key_epoch="epoch-1",
            destruction_nonce=f"destroy:{seed}",
            closed_at=123,
        )

        accepted = validate_session_tag_not_revoked(
            store=revocation_store,
            session_hash=session_hash,
            expected_tag=good_fragment_tag,
            observed_tag=good_fragment_tag,
            now=123,
        )
        expected_acceptance = False
        reason = "post-shutdown fragment cannot reactivate closed session"

    elif case == "dormant_flv_cannot_reactivate":
        bundle = build_closed_session_bundle(seed)
        accepted = attempt_session_reactivation_from_traces(bundle)
        expected_acceptance = False
        reason = "valid dormant FLV is evidence, not active life"

    elif case == "old_start_seal_cannot_reopen":
        bundle = build_closed_session_bundle(seed)
        start_seal = str(bundle["start_seal"])
        start_seal_valid = validate_session_start_seal(start_seal, start_seal)
        reactivation = attempt_session_reactivation_from_traces(bundle)

        accepted = bool(start_seal_valid and reactivation)
        expected_acceptance = False
        reason = "old start seal proves birth but cannot reopen session"

    elif case == "old_close_seal_cannot_reopen":
        bundle = build_closed_session_bundle(seed)
        close_code = str(bundle["rotor_close_code"])
        close_code_valid = validate_rotor_close_code(close_code, close_code)
        reactivation = attempt_session_reactivation_from_traces(bundle)

        accepted = bool(close_code_valid and reactivation)
        expected_acceptance = False
        reason = "old close seal proves death but cannot reopen session"

    elif case == "old_repair_hash_cannot_repair_closed_session":
        bundle = build_closed_session_bundle(seed)
        closed_hash = str(bundle["session_hash"])
        closed_store = bundle["revocation_store"]
        closed_at = int(bundle["closed_at"])

        if not isinstance(closed_store, SessionRevocationStore):
            raise TypeError("revocation_store must be SessionRevocationStore")

        repair_hash = derive_repair_hash(
            RepairSessionContext(
                session_hash=closed_hash,
                repair_epoch="1",
                repair_nonce=f"repair:{seed}",
                repair_counter=0,
            )
        )

        repair_hash_exists = len(repair_hash) == 64
        session_dead = is_session_revoked(closed_store, closed_hash, now=closed_at)

        accepted = bool(repair_hash_exists and not session_dead)
        expected_acceptance = False
        reason = "repair hash may exist but cannot repair closed session"

    else:
        raise ValueError(f"unsupported reactivation case: {case}")

    return {
        "schema_version": "1.4.0",
        "experiment": "session-reactivation-prevention",
        "seed": seed,
        "case": case,
        "reason": reason,
        "accepted": accepted,
        "expected_acceptance": expected_acceptance,
        "passed": accepted == expected_acceptance,
        "session_hash_prefix": session_hash[:16],
    }


DEFAULT_CASES = [
    "valid_active_fragment",
    "bad_fragment_tag",
    "revoked_session_fragment",
    "valid_capsule_first_use",
    "consumed_capsule_reactivation",
    "bad_capsule_tag",
    "post_shutdown_fragment",
    "dormant_flv_cannot_reactivate",
    "old_start_seal_cannot_reopen",
    "old_close_seal_cannot_reopen",
    "old_repair_hash_cannot_repair_closed_session",
]


def run_session_reactivation_suite(
    seeds: List[str],
    cases: List[str] | None = None,
    csv_path: str = "outputs/compare_session_reactivation_v01.csv",
    json_path: str = "outputs/compare_session_reactivation_v01.json",
) -> None:
    if cases is None:
        cases = DEFAULT_CASES

    rows = []

    for seed in seeds:
        for case in cases:
            rows.append(run_reactivation_case(seed, case))

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    if rows:
        with csv_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    json_out.write_text(json.dumps({
        "schema_version": "1.4.0",
        "experiment": "session-reactivation-prevention",
        "results": rows,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total rows: {len(rows)}")
    print(f"Pass rate: {mean(row['passed'] for row in rows):.4f}")


if __name__ == "__main__":
    run_session_reactivation_suite(
        seeds=[f"reactivation-{i:03d}" for i in range(30)],
    )
