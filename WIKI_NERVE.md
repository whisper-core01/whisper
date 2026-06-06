# WHISPER Wiki — Nerve

## Status

Core architectural concept.

Design-level documentation.

Implementation pending or distributed across existing routing and lifecycle modules.

---

## 1. Definition

Nerve is the WHISPER local signal system.

It is responsible for sensing local state and propagating internal protocol signals without exposing global truth.

Nerve is not a router.

Nerve is not a global coordinator.

Nerve is not a consensus layer.

Nerve is the internal reflex layer of the WHISPER organism.

---

## 2. Role in WHISPER

Nerve observes local symptoms and triggers local reactions.

It helps WHISPER decide when to:

- increase redundancy
- increase custody
- switch to streaming receive mode
- reject stale material
- revoke a local session
- initiate shutdown
- trigger repair
- freeze custody
- purge Wasm
- zeroize volatile state

Nerve does not need global knowledge.

Nerve does not accuse nodes.

Nerve reacts to local symptoms.

---

## 3. Local-Only Signals

Nerve may observe:

- latency risk
- jitter risk
- timeout risk
- signal loss risk
- receiver capacity risk
- repeated validation failures
- stale capsule attempts
- replay symptoms
- custody expiration
- storage pressure
- user session exit
- local policy events

These are symptoms.

They are not proof of attack.

---

## 4. Relationship with Adaptive Redundancy

In v1.3.4, adaptive redundancy already behaves like a Nerve function.

It observes local network symptoms and adjusts:

- redundancy factor
- custody rounds
- repair budget
- receive mode

The calibrated profile uses:

- minimum redundancy: 1.25
- maximum redundancy: 1.40
- minimum custody rounds: 5
- maximum custody rounds: 7

Nerve turns local symptoms into local adaptation.

---

## 5. Relationship with Revocation

In v1.4.0, Nerve can trigger local session revocation.

Examples:

- USER_LEFT_SESSION
- USER_CANCELLED_TRANSFER
- SESSION_EXPIRED
- REPLAY_DETECTED
- CUSTODY_EXPIRED
- INVALID_MATERIAL
- STORAGE_PRESSURE
- POLICY_VIOLATION

Revocation is local refusal.

It is not global accusation.

A session may die locally without requiring the rest of the network to agree.

---

## 6. Relationship with Secure Shutdown

Nerve can trigger secure shutdown when the local session context must end.

Shutdown sequence:

- block new material
- freeze custody
- purge Wasm
- zeroize volatile state
- generate rotor close code
- destroy keys
- revoke session hash locally
- close session

Nerve does not close the session directly.

Nerve triggers the shutdown reflex.

The shutdown module executes the ordered sequence.

---

## 7. Relationship with FLV

Nerve events may be recorded in FLV lifecycle records as local sealed memory.

The FLV is stored only inside the local LUKS partition.

The FLV is machine-bound through a local master-key-derived binding.

The FLV is not portable.

The FLV enters dormancy when the machine shuts down.

Nerve may wake FLV state only when the local machine context is valid.

---

## 8. Security Boundaries

Nerve must not expose:

- payload
- keys
- Reticulum identity
- route identity
- global topology
- missing fragment set
- stable user identity
- accusation of compromise

Nerve may expose only local bounded protocol state.

---

## 9. Current Implementation Links

Nerve behavior is currently distributed across:

- adaptive_redundancy_policy_v01.py
- session_revocation_v01.py
- secure_session_shutdown_v01.py
- session_hash_v01.py
- session_start_seal_v01.py
- rotor_close_code_v01.py

Future implementation may introduce:

- nerve_signal_v01.py
- nerve_policy_v01.py
- nerve_event_store_v01.py
- nerve_shutdown_bridge_v01.py

---

## 10. Final Rule

Nerve does not know everything.

Nerve senses locally.

Nerve reacts locally.

Nerve never becomes an oracle.

