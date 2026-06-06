# WHISPER Wiki — Rotor

## Status

Core concept.

Partially implemented through rotor-style primitives and v1.4.0 lifecycle seals.

---

## 1. Definition

Rotor is the WHISPER local transformation and lifecycle sealing mechanism.

It is not a cipher by itself.

It is not a persistent key store.

It is not a route selector.

It is not a Reticulum identity.

Rotor is used to produce deterministic, local, session-scoped transformation material and lifecycle seals.

In v1.4.0, Rotor is primarily used for:

- rotor close code
- key destruction commitment
- shutdown step digests
- session closure sealing

---

## 2. Role in WHISPER

Rotor provides local cryptographic structure around session lifecycle events.

It helps WHISPER express:

- session opening
- session validity
- session shutdown
- key destruction
- closure sealing
- non-resurrection

Rotor does not preserve keys.

Rotor does not recover sessions.

Rotor does not store payloads.

Rotor does not expose routes.

---

## 3. Rotor Close Code

The rotor close code is the local closure seal of a WHISPER session.

It is generated during secure session shutdown, before final key destruction.

It is bound to:

- session_hash
- shutdown_nonce
- close_reason
- Wasm purge digest
- volatile zeroization digest
- custody freeze digest
- key destruction commitment
- local close timestamp

It proves locally that the session was closed through the expected shutdown sequence.

It is not a recovery key.

It is not a session key.

It is not a payload commitment.

It cannot resurrect the session.

---

## 4. Key Destruction Commitment

Rotor can commit to the fact that keys were destroyed without storing the keys.

This commitment must never receive or preserve key material.

It only binds:

- session_hash
- key_epoch
- destruction_nonce
- destruction marker

Rule:

The key is destroyed.

The commitment remains.

The key cannot be recovered from the commitment.

---

## 5. Relationship with Session Hash

session_hash defines the validity boundary.

Rotor close code seals the end of that boundary.

The relationship is:

session_start_seal:
  local act of birth

session_hash:
  validity boundary

rotor_close_code:
  local act of death

The session hash may remain as a commitment.

The keys do not remain.

---

## 6. Relationship with FLV

The rotor close code may be recorded inside the FLV lifecycle record.

The FLV records the closure seal and final state.

The FLV must not contain:

- session keys
- fragment keys
- repair keys
- payload
- Reticulum identity
- route identity
- missing fragment set

The FLV stores local lifecycle evidence only.

---

## 7. Security Invariants

Rotor must respect the following invariants:

- no persistent keys
- no key recovery
- no route exposure
- no payload exposure
- no Reticulum identity exposure
- no stable identity exposure
- no session resurrection
- no replay after close

Rotor close code is a seal.

It is not a key.

---

## 8. Current Implementation

Implemented files:

- rotor_close_code_v01.py
- tests/test_rotor_close_code_v01.py

Connected files:

- session_hash_v01.py
- session_revocation_v01.py
- secure_session_shutdown_v01.py
- session_start_seal_v01.py
- session_closure_flv_v01.py

Current tested behavior:

- shutdown step digest derivation
- key destruction commitment
- rotor close code derivation
- close code validation
- secure shutdown orchestration
- closure FLV binding

---

## 9. Final Rule

Rotor does not keep the session alive.

Rotor proves that the session died properly.

The rotor close code seals the closure.

It does not reopen the door.

