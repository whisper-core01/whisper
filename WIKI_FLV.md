# WHISPER Wiki — FLV

## Status

Core architectural concept.

Partially implemented through session closure records and lifecycle sealing primitives.

---

## 1. Definition

FLV is the local sealed memory layer of WHISPER.

It is not a portable archive.

It is not a recovery bundle.

It is not a key store.

It is not a message database.

FLV stores local lifecycle evidence and session-bound metadata inside the local protected environment.

The FLV belongs to the machine that produced it.

---

## 2. Storage Boundary

A WHISPER FLV must be stored only inside the local LUKS-protected partition.

The FLV must not be readable, reusable, validatable, or replayable outside that local environment.

A copied FLV must not become useful on another machine.

Required boundaries:

- LUKS storage boundary
- local master-key-derived FLV binding
- machine-local context binding
- session lifecycle binding

Short form:

The FLV never leaves LUKS as a usable object.

---

## 3. Dormancy Model

The FLV does not die when a session closes.

The session dies.

The keys are destroyed.

The FLV enters dormancy.

When the machine shuts down, the FLV becomes dormant inside LUKS.

It can only be awakened by the same local machine context capable of:

- opening the LUKS partition
- deriving the local master-key binding
- validating the machine-local context
- validating the session lifecycle seals

Short form:

The session dies.

The FLV sleeps.

LUKS is the chamber.

The local master key guards the door.

---

## 4. Machine Binding

A WHISPER FLV is cryptographically bound to a hash derived from the local master key.

The FLV must never store the master key.

It stores only binding commitments.

Conceptual binding:

flv_binding_digest =
  H(
    local_master_binding_hash,
    machine_context_digest,
    session_hash,
    session_start_seal,
    rotor_close_code,
    "WHISPER_FLV_MACHINE_BINDING_V1"
  )

Rule:

Bind to the master.

Never store the master.

---

## 5. Lifecycle Evidence

The FLV may store local lifecycle evidence such as:

- session_start_seal
- session_hash
- transfer profile commitment
- custody profile commitment
- repair profile commitment
- rotor_close_code
- closure state
- shutdown step digest
- closure record digest
- local revocation state
- dormancy state

The FLV must not store:

- master key
- session key
- fragment key
- repair key
- payload
- plaintext message
- Reticulum address
- physical route
- missing fragment set
- stable user identity

---

## 6. Relationship with Session Start Seal

The session start seal is the local act of birth.

It proves that the session was opened cleanly under local conditions.

The FLV may store the start seal as lifecycle evidence.

The start seal is not a key.

It is not a payload commitment.

It is not a stable identity.

---

## 7. Relationship with Session Hash

The session hash is the session validity boundary.

The FLV may store the session hash or a commitment to it.

The session hash is not a permanent identity.

It is not a route.

It is not a Reticulum address.

It defines whether session-bound material belongs to the local session context.

---

## 8. Relationship with Rotor Close Code

The rotor close code is the local act of death of a session.

It proves that the session entered shutdown through the expected sequence:

- custody freeze
- Wasm purge
- volatile zeroization
- key destruction commitment
- local revocation
- closure

The FLV may store the rotor close code as closure evidence.

The rotor close code cannot recover keys.

It cannot reopen the session.

It cannot resurrect the session.

---

## 9. Relationship with Nerve

Nerve may trigger lifecycle transitions that are recorded in FLV.

Examples:

- user leaves session
- transfer cancelled
- storage pressure detected
- invalid material received
- replay detected
- custody expired
- secure shutdown triggered

Nerve senses locally.

FLV records locally.

Neither becomes a global oracle.

---

## 10. Relationship with Rotor

Rotor creates lifecycle seals.

FLV stores lifecycle seals.

Rotor does not store keys.

FLV does not store keys.

Rotor seals birth and death events.

FLV preserves those seals as local dormant memory.

---

## 11. Security Properties

FLV is designed to provide:

- local lifecycle memory
- non-portable validation
- dormancy after shutdown
- binding to local protected storage
- binding to local master-key-derived material
- evidence of session start
- evidence of session closure
- evidence of key destruction commitment
- evidence of local revocation

FLV is not designed to provide:

- cross-machine portability
- recovery of destroyed keys
- global auditability
- plaintext inspection
- route reconstruction
- Reticulum identity recovery
- fragment reconstruction by itself

---

## 12. Failure Behavior

If the FLV is copied outside LUKS:

- it must not be readable
- it must not be validatable
- it must not be replayable
- it must not reopen a session
- it must not recover keys

If the local master-key-derived binding cannot be reproduced:

- FLV awakening fails

If the machine-local context does not match:

- FLV validation fails

If the session lifecycle seals do not match:

- FLV validation fails

---

## 13. Current Implementation Links

Current or related files:

- session_closure_flv_v01.py
- session_start_seal_v01.py
- session_hash_v01.py
- rotor_close_code_v01.py
- secure_session_shutdown_v01.py
- session_revocation_v01.py

Future expected files:

- session_lifecycle_flv_v01.py
- flv_machine_binding_v01.py
- flv_dormancy_v01.py
- tests/test_session_lifecycle_flv_v01.py
- tests/test_flv_machine_binding_v01.py

---

## 14. Final Rule

The session dies.

The keys are destroyed.

The FLV does not die.

The FLV sleeps inside LUKS.

Only the local machine context can wake it.

