# WHISPER v1.4.0 — Session-Hash Revocation

## Status

Design phase.

Implementation pending.

v1.4.0 introduces session-scoped validity and revocation.

The goal is to prevent fragments, capsules, repair material, custody entries, and transport hints from being reused outside their legitimate session context.

---

## 1. Objective

WHISPER must prevent:

- fragment replay
- capsule reuse
- repair shard reuse
- stale custody continuation
- cross-session injection
- old Sol-link alias reuse
- expired transport capsule reuse
- replay across epochs
- replay across receiver state transitions

A fragment that belongs to one session must be invalid in every other session.

A fragment that belongs to one epoch must be invalid outside that epoch.

A fragment that belongs to one Sol-link context must not be reusable in another Sol-link context.

---

## 2. Core Principle

Every WHISPER transfer session derives a unique session hash.

The session hash is not a public stable identifier.

It is a scoped cryptographic commitment derived from session-local material.

It binds:

- Sol context
- epoch
- local ephemeral material
- remote ephemeral material
- session nonce
- message commitment
- transfer mode
- redundancy profile
- custody profile

The session hash acts as a local validity boundary.

Short form:

No session hash.

No validity.

Wrong session hash.

Reject.

Expired session hash.

Reject.

---

## 3. Session Hash Derivation

Conceptual derivation:

session_hash =
  H(
    sol_id,
    epoch,
    local_ephemeral_material,
    remote_ephemeral_material,
    session_nonce,
    message_commitment,
    transfer_profile_commitment,
    "WHISPER_SESSION_HASH_V1"
  )

The session hash must be:

- epoch-scoped
- non-stable
- non-global
- non-human-visible
- non-linkable across sessions
- unsuitable as a permanent identity
- unsuitable as a Reticulum address
- unsuitable as a VoxMesh relay identity

It is not a node identity.

It is not a route identity.

It is not a transport identity.

It is only a validity boundary.

---

## 4. Fragment Binding

Every fragment must be bound to the session hash.

A valid fragment carries or derives a local validation tag:

fragment_session_tag =
  H(
    session_hash,
    fragment_nonce,
    fragment_index_commitment,
    fragment_role,
    capsule_nonce,
    "WHISPER_FRAGMENT_SESSION_TAG_V1"
  )

The receiver-side WHISPER instance validates this tag before accepting the fragment into custody or reconstruction state.

A fragment with a missing, expired, or mismatched session tag is rejected.

---

## 5. Capsule Binding

Every WHISPER capsule is bound to the session hash.

Capsule validation must ensure:

- the capsule belongs to the active session
- the capsule belongs to the current epoch
- the capsule has not already been consumed
- the capsule role is admissible
- the capsule is not revoked
- the capsule does not reuse stale nonce material

A replayed capsule must be rejected even if its payload structure is otherwise valid.

---

## 6. Custody Binding

Custody entries must be session-bound.

A relay may temporarily retain a fragment or repair shard only if:

- the session hash is active
- the custody TTL has not expired
- the local custody budget is not exceeded
- the fragment has not been revoked
- the fragment has not already been consumed
- the relay is still admissible for that session

Custody must not create permanent storage.

Custody is temporary persistence, not archival storage.

---

## 7. Repair Binding

Repair material must be derived under the same session hash or a session-authorized repair hash.

repair_hash =
  H(
    session_hash,
    repair_epoch,
    repair_nonce,
    repair_counter,
    "WHISPER_REPAIR_HASH_V1"
  )

Repair shards must be valid only for:

- the original session
- the authorized repair round
- the current repair epoch
- the current reconstruction state

Repair shards must not be reusable in later sessions.

Repair shards must not reveal missing fragment indices.

---

## 8. Revocation Model

v1.4.0 introduces local session-hash revocation.

A session hash may be revoked when WHISPER detects:

- replay attempt
- stale capsule
- expired epoch
- invalid custody continuation
- repeated validation failure
- repair abuse
- excessive duplicate material
- local policy violation
- user-side cancellation
- storage pressure cancellation
- receiver capacity failure

Revocation is local-first.

A node does not need global consensus to reject a revoked session hash.

---

## 9. Revocation State

A local revocation entry contains:

- revoked_session_hash_commitment
- reason code
- local timestamp or logical clock
- expiry
- scope
- optional relay-local evidence digest

It must not contain:

- plaintext payload
- Reticulum address
- physical route
- missing fragment set
- stable identity
- global attribution claim

Revocation is not accusation.

Revocation is local refusal.

---

## 10. Revocation Scope

Possible scopes:

SESSION:
  reject the current session only

EPOCH:
  reject all material from the same session epoch

SOL_LINK:
  reject material tied to the same Sol-link alias

RELAY_LOCAL:
  reject only at the local relay

TEMPORARY:
  reject until expiry

PERMANENT_LOCAL:
  reject locally until explicit cleanup

Default scope should be SESSION or TEMPORARY.

Global revocation is out of scope for v1.4.0.

---

## 11. Anti-Replay Rules

A fragment or capsule is rejected if:

- session hash mismatch
- epoch mismatch
- nonce already consumed
- custody TTL expired
- repair round invalid
- revocation entry exists
- role is not admissible
- fragment arrives after reconstruction finalization
- capsule arrives after session closure

This prevents old material from being injected into new sessions.

---

## 12. Interaction with v1.3 Series

v1.3.0:
  Sol-link magnet creates routing attraction.

v1.3.1:
  pressure field canalizes next-hop selection.

v1.3.2:
  redundancy and custody improve reconstruction.

v1.3.3:
  blind repair and decoys hide repair patterns.

v1.3.4:
  adaptive redundancy adjusts rain to local conditions.

v1.4.0:
  session-hash revocation prevents stale material from surviving across session boundaries.

v1.4.0 is therefore the boundary cleanup layer.

It makes sure that adaptive custody and repair do not become replay surfaces.

---

## 13. Security Properties

v1.4.0 aims to provide:

- session-scoped validity
- replay resistance
- stale material rejection
- custody expiration
- repair-round containment
- local revocation
- no global blacklist dependency
- no stable identity exposure
- no Reticulum address exposure
- no payload exposure

---

## 14. What v1.4.0 Does Not Claim

v1.4.0 does not claim:

- global malicious-node detection
- global revocation consensus
- legal attribution
- proof of compromise
- perfect anonymity
- permanent blacklisting
- immunity to all replay variants

v1.4.0 only claims:

Material outside its valid session boundary can be rejected locally.

---

## 15. Implementation Plan

Expected files:

- session_hash_v01.py
- tests/test_session_hash_v01.py
- session_revocation_v01.py
- tests/test_session_revocation_v01.py
- compare_session_replay_v01.py

Core functions:

- derive_session_hash(...)
- derive_fragment_session_tag(...)
- derive_repair_hash(...)
- validate_session_tag(...)
- mark_session_revoked(...)
- is_session_revoked(...)
- validate_capsule_session(...)
- expire_session_state(...)

---

## 16. Metrics

Initial v1.4.0 metrics:

- replay_rejection_rate
- stale_capsule_rejection_rate
- valid_capsule_acceptance_rate
- false_rejection_rate
- revoked_session_rejection_rate
- custody_expiry_rejection_rate
- repair_round_replay_rejection_rate
- session_hash_collision_count
- validation_time_per_capsule

Success criteria:

- valid capsules accepted
- replayed capsules rejected
- expired custody rejected
- repair round replay rejected
- no plaintext Reticulum identity stored
- no payload exposure
- no global oracle required

---

## 17. Final Summary

v1.4.0 introduces the session boundary.

A WHISPER fragment is not valid because it looks valid.

It is valid only if it belongs to the active session, epoch, custody state, and repair context.

Final rule:

No valid session hash.

No valid fragment.

No valid custody.

No valid repair.

No replay.

