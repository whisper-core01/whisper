# WHISPER v1.4.0 — Session Lifecycle Report

## Status

Milestone report.

v1.4.0 documents and validates the WHISPER session lifecycle layer.

This milestone builds on the v1.3 series.

v1.3 established adaptive reconstruction.

v1.4 establishes session validity, local death, non-reactivation, and dormant local memory.

---

## 1. Executive Summary

WHISPER v1.4.0 introduces a complete local cryptographic lifecycle for sessions.

The goal is not only to reject replayed fragments.

The goal is to prevent an old closed session from ever becoming active again.

Core invariant:

An old session may leave local traces, but it must never become active again.

v1.4.0 implements and validates:

- session start seal
- session hash validity boundary
- fragment, capsule, and repair session binding
- local session revocation
- rotor close code
- secure shutdown sequence
- key destruction commitment
- machine/LUKS-bound dormant FLV lifecycle record
- session reactivation prevention comparator

Current validation status:

- 297 tests passing
- 330 session reactivation cases
- 1.0000 pass rate
- clean Git working tree
- GitHub master up to date

---

## 2. Core Doctrine

A session is not valid because old material exists.

A session is valid only while its local lifecycle state allows it.

Fragments, capsules, lifecycle seals, rotor close codes, session start seals, and dormant FLV records may remain as local evidence.

However, none of them can reopen, resume, repair, decrypt, or validate material under a closed session.

Short form:

Closed sessions leave evidence, not life.

---

## 3. Lifecycle Structure

WHISPER v1.4.0 models a session as a local lifecycle:

Birth:
  session_start_seal

Validity boundary:
  session_hash

Operational life:
  fragment tags
  capsule tags
  repair hashes
  custody
  adaptive transport context

Local death:
  local revocation
  secure shutdown
  Wasm purge
  volatile zeroization
  key destruction

Death seal:
  rotor_close_code

Dormant memory:
  session_lifecycle_flv

Non-reactivation:
  session reactivation prevention comparator

---

## 4. Implemented Modules

### session_start_seal_v01.py

Purpose:

Defines the local birth seal of a session.

A session start seal proves that a session was opened cleanly under a local context.

It is bound to:

- session_hash
- session_nonce
- start_nonce
- open_reason
- Wasm initialization digest
- custody initialization digest
- volatile buffer initialization digest
- creation time

It is not:

- a key
- a payload commitment
- a Reticulum identity
- a stable identifier
- a route identity

Implemented primitives:

- derive_start_step_digest()
- derive_session_start_seal()
- validate_session_start_seal()

---

### session_hash_v01.py

Purpose:

Defines the session-scoped validity boundary.

A fragment, capsule, or repair object is valid only if it belongs to the correct session context.

Implemented primitives:

- derive_session_hash()
- derive_fragment_session_tag()
- derive_capsule_session_tag()
- derive_repair_hash()
- validate_session_tag()

Core rule:

No valid session hash.

No valid fragment.

No valid capsule.

No valid repair.

---

### session_revocation_v01.py

Purpose:

Defines local-first session revocation.

Revocation is local refusal.

It is not global accusation.

A session may die locally without global consensus.

Implemented primitives:

- mark_session_revoked()
- is_session_revoked()
- get_revocation_entry()
- validate_not_revoked()
- expire_revocations()
- validate_session_tag_not_revoked()

Revocation reasons include:

- USER_LEFT_SESSION
- USER_CANCELLED_TRANSFER
- LOCAL_SESSION_CLOSED
- SESSION_EXPIRED
- REPLAY_DETECTED
- CUSTODY_EXPIRED
- REPAIR_ABUSE
- POLICY_VIOLATION
- INVALID_MATERIAL
- STORAGE_PRESSURE

---

### rotor_close_code_v01.py

Purpose:

Defines the local death seal of a session.

The rotor close code proves locally that a session entered shutdown through the expected sequence.

It is generated before final key destruction.

It is bound to:

- session_hash
- shutdown_nonce
- close_reason
- Wasm purge digest
- volatile zeroization digest
- custody freeze digest
- key destruction commitment
- close time

It is not:

- a recovery key
- a session key
- a fragment key
- a repair key
- a Reticulum identity
- a route identity
- a payload commitment

Implemented primitives:

- derive_shutdown_step_digest()
- derive_key_destruction_commitment()
- derive_rotor_close_code()
- validate_rotor_close_code()

Core rule:

The rotor close code seals the closure.

It does not reopen the door.

---

### secure_session_shutdown_v01.py

Purpose:

Orchestrates the ordered local death of a WHISPER session.

Shutdown sequence:

- block new material
- freeze custody
- purge Wasm
- zeroize volatile state
- generate rotor close code
- destroy keys
- revoke session locally
- close session

Validated state chain:

ACTIVE
  to CLOSING
  to WASM_PURGED
  to ZEROIZED
  to ROTOR_CLOSED
  to KEYS_DESTROYED
  to REVOKED
  to CLOSED

Core rule:

A session cannot close before active state is purged, keys are destroyed, and the session hash is locally revoked.

---

### session_lifecycle_flv_v01.py

Purpose:

Defines the machine-bound dormant FLV lifecycle record.

The FLV binds:

- session_start_seal
- session_hash
- rotor_close_code
- lifecycle state
- local master-key-derived binding
- machine context digest
- LUKS context digest
- dormancy state

The FLV is not:

- a portable archive
- a recovery bundle
- a key store
- a message database

The FLV stores local lifecycle evidence only.

Core rule:

The session dies.

The keys are destroyed.

The FLV does not die.

The FLV sleeps inside LUKS.

Only the local machine context can wake it.

---

### compare_session_reactivation_v01.py

Purpose:

Validates that closed sessions cannot be reactivated from old material or local traces.

This comparator tests the broader lifecycle threat, not only replay.

Replay is treated as one technical case of the larger problem:

closed-session reactivation.

Tested cases:

- valid active fragment
- bad fragment tag
- revoked session fragment
- valid capsule first use
- consumed capsule reactivation
- bad capsule tag
- post-shutdown fragment
- dormant FLV cannot reactivate
- old start seal cannot reopen
- old close seal cannot reopen
- old repair hash cannot repair closed session

---

## 5. Experimental Results

Session reactivation prevention comparator:

Total rows:
  330

Pass rate:
  1.0000

Meaning:

Every tested reactivation attempt behaved as expected.

Valid active material was accepted.

Invalid, stale, consumed, revoked, post-shutdown, or trace-only material was rejected.

Dormant FLV records validated as local evidence but did not reactivate closed sessions.

Old start seals proved birth but did not reopen the session.

Old rotor close codes proved death but did not reopen the session.

Old repair hashes could exist but could not repair a closed session.

---

## 6. Test Status

Current test suite:

- 297 tests passing

Important tested modules:

- session_hash_v01.py
- session_revocation_v01.py
- session_start_seal_v01.py
- rotor_close_code_v01.py
- secure_session_shutdown_v01.py
- session_closure_flv_v01.py
- session_lifecycle_flv_v01.py
- compare_session_reactivation_v01.py

---

## 7. Security Properties

v1.4.0 aims to provide:

- session-scoped validity
- local session revocation
- replay resistance
- closed-session non-reactivation
- key non-persistence
- secure shutdown ordering
- lifecycle evidence without key retention
- dormant FLV memory
- machine/LUKS-bound FLV records
- no session resurrection after closure

---

## 8. What v1.4.0 Does Not Claim

v1.4.0 does not claim:

- global malicious-node detection
- global revocation consensus
- perfect anonymity
- production-ready cryptography
- real secure memory erasure guarantees in Python
- hardware-backed key management
- formal proof of non-reactivation
- complete integration with production Reticulum

v1.4.0 claims only:

A closed local WHISPER session cannot be reactivated by the tested lifecycle traces, stale material, consumed capsule tags, repair hashes, dormant FLV records, start seals, or close seals.

---

## 9. Relationship to v1.3

v1.3 answered:

Can WHISPER deliver and reconstruct under probabilistic pressure routing?

v1.4 answers:

Can WHISPER prevent old session state from being reused after local closure?

v1.3 focused on movement and reconstruction.

v1.4 focuses on lifecycle, closure, dormancy, and non-reactivation.

Together:

v1.3 makes the communication survive the network.

v1.4 makes the session unable to survive its own death.

---

## 10. Relationship to the Content vs Container Doctrine

The v1.4 lifecycle layer directly follows the WHISPER content-vs-container doctrine.

The content is not the only secret.

The session lifecycle is also part of the secret.

The local memory trace is also part of the secret.

The closure process is also part of the secret.

The disappearance process is also part of the secret.

v1.4 protects the container by ensuring that a closed communication lifecycle cannot be rebuilt from traces.

---

## 11. Final Statement

WHISPER v1.4.0 completes the first tested session lifecycle layer.

A WHISPER session can now be described as:

- born locally
- bounded by session_hash
- validated through session tags
- revoked locally
- closed through ordered shutdown
- sealed by rotor close code
- remembered by a dormant FLV
- prevented from reactivation

Final rule:

An old session may leave local traces, but it must never become active again.

