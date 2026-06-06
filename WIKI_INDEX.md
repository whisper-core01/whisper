# WHISPER Wiki Index

## Overview

WHISPER is a cryptographic organism for sovereign digital communication.

It is not a messaging application.

It is not a classical router.

It is not a simple encrypted file-transfer tool.

WHISPER is built around compartmentalization:

- no layer knows everything
- no route is fully precomputed
- no key survives beyond its role
- no FLV is portable outside its local machine context
- no session can resurrect after closure

Core rule:

VoxMesh qualifies.

WHISPER selects.

Reticulum transports.

Nerve senses.

Rotor seals.

FLV remembers.

LUKS protects.

---

## Root Manifesto

### Content vs Container

File:

DOCTRINE_CONTENT_VS_CONTAINER.md

Purpose:

This is the root doctrine of WHISPER.

It explains why WHISPER does not limit security to encrypted content.

Core idea:

Encryption protects what is said.

WHISPER protects what the communication reveals before it is even read.

The manifesto defines the architectural foundation for:

- VoxMesh
- Reticulum separation
- Sol-link routing
- pressure fields
- fragmentation
- decoys
- repair
- session lifecycle
- Rotor
- Nerve
- FLV
- LUKS-bound dormant memory
- key non-persistence
- anti-resurrection

Short form:

The content is encrypted.

The container is sovereignized.

Recommended for:

- first-time readers
- reviewers
- funding bodies
- anyone trying to understand why WHISPER is not a messaging app

---

## Recommended Reading Order

### 0. WHISPER Manifesto — Content vs Container

File:

DOCTRINE_CONTENT_VS_CONTAINER.md

Purpose:

The foundational manifesto of WHISPER.

It defines the distinction between protecting message content and protecting the full communication container.

Read this first.

---

### 1. v1.3 Series Report

File:

V1_3_SERIES_REPORT.md

Purpose:

This is the main narrative report for external review.

It explains the full v1.3.0 to v1.3.4 evolution:

- Sol-link magnetic routing
- pressure-field routing
- redundancy and custody
- adaptive network-aware redundancy
- reconstruction results
- layer-blindness invariants
- roadmap

Recommended for:

- NLnet
- Protocol Labs
- technical reviewers
- funding bodies
- first-time readers

---

### 2. v1.3.4 Adaptive Redundancy Report

File:

V1_3_4_ADAPTIVE_REDUNDANCY_REPORT.md

Purpose:

Documents the calibrated adaptive redundancy model.

Key result:

- 98.89% reconstruction on good network profiles
- 100% reconstruction on normal, bad, and very bad profiles
- stable exposure
- low loop rate
- low dead-end rate
- invariants preserved

Recommended for:

- performance / reliability review
- reconstruction metrics
- adaptive control validation

---

### 3. v1.3.3 Blind Repair Design

File:

V1_3_3_BLIND_REPAIR_DESIGN.md

Purpose:

Design document for the future blind repair and decoy-equivalent flow layer.

Status:

Design frozen.

Implementation pending.

Purpose:

Prevent observers from identifying:

- repair traffic
- missing fragment sets
- useful fragments
- decoys
- reconstruction failure patterns

Recommended for:

- privacy / anti-correlation review
- future roadmap review

---

### 4. v1.4.0 Session-Hash Design

File:

V1_4_0_SESSION_HASH_DESIGN.md

Purpose:

Defines session-scoped validity, local revocation, secure shutdown, zeroization, key destruction, rotor close code, and FLV dormancy.

Core rules:

- no valid session hash, no valid fragment
- no persistent keys
- no session resurrection
- no replay after close
- FLV sleeps inside LUKS

Recommended for:

- lifecycle review
- anti-replay review
- shutdown / zeroization review
- key non-persistence review

---

---

### 5. v1.4.0 Session Lifecycle Report

File:

V1_4_0_SESSION_LIFECYCLE_REPORT.md

Purpose:

Documents the complete v1.4.0 session lifecycle milestone.

It covers:

- session start seal
- session hash validity boundary
- local revocation
- rotor close code
- secure shutdown
- key destruction
- machine/LUKS-bound dormant FLV
- session reactivation prevention

Key result:

- 297 tests passing
- 330 session reactivation cases
- 1.0000 pass rate

Core invariant:

An old session may leave local traces, but it must never become active again.

Recommended for:

- lifecycle review
- anti-reactivation review
- secure shutdown review
- FLV dormancy review

## Organ Wiki Pages

### Rotor

File:

WIKI_ROTOR.md

Role:

Rotor is the local lifecycle sealing mechanism.

It provides:

- rotor close code
- shutdown step digests
- key destruction commitment
- session closure sealing

Rotor does not store keys.

Rotor does not recover sessions.

Rotor proves that lifecycle events occurred locally.

Short form:

Rotor seals.

---

### Nerve

File:

WIKI_NERVE.md

Role:

Nerve is the local signal and reflex layer.

It observes local symptoms and triggers local reactions.

Nerve can trigger:

- adaptive redundancy
- custody increase
- streaming receive mode
- local revocation
- secure shutdown
- repair
- Wasm purge
- zeroization

Nerve does not accuse globally.

Nerve does not become an oracle.

Short form:

Nerve senses.

---

### FLV

File:

WIKI_FLV.md

Role:

FLV is local sealed dormant memory.

It is:

- stored only inside LUKS
- bound to local master-key-derived material
- machine-bound
- non-portable
- not a key store
- not a recovery bundle
- not a message database

The FLV does not die.

The FLV sleeps.

Short form:

FLV remembers.

---

## Core Code Modules

### v1.3 Routing and Reconstruction

Files:

- sol_link_magnetic_policy_v01.py
- sol_link_pressure_policy_v01.py
- redundancy_compensation_v01.py
- adaptive_redundancy_policy_v01.py
- compare_sol_link_magnetic_v01.py
- compare_sol_link_pressure_v01.py
- compare_redundancy_pressure_v01.py
- compare_adaptive_redundancy_v01.py

Purpose:

These files implement and evaluate:

- Sol-link routing
- pressure-field routing
- redundancy compensation
- custody
- adaptive network-aware reconstruction

---

### v1.4 Session Lifecycle

Files:

- session_hash_v01.py
- session_revocation_v01.py
- session_start_seal_v01.py
- rotor_close_code_v01.py
- secure_session_shutdown_v01.py
- session_closure_flv_v01.py

Purpose:

These files implement:

- session hash derivation
- fragment / capsule / repair session tags
- local session revocation
- session start seal
- rotor close code
- secure shutdown orchestration
- FLV closure records

---

## Current Test Status

Current suite status at last documented point:

- 277 tests passing

The exact number may increase as new modules are added.

Run:

pytest -q tests

---

## Architectural Invariants

### Layer Blindness

VoxMesh does not know where the capsule goes.

Reticulum does not know what it transports.

WHISPER does not expose the full route.

No layer knows everything.

---

### Unpredictability

Constraints reduce the space.

Scores bend probability.

Randomness chooses.

The path emerges.

---

### Key Non-Persistence

No session key survives the session.

No fragment key survives the fragment context.

No repair key survives the repair round.

No custody key survives its TTL.

No key is recoverable from the rotor close code.

---

### FLV Dormancy

The session dies.

The keys are destroyed.

The FLV does not die.

The FLV sleeps inside LUKS.

Only the local machine context can wake it.

---

### Local Revocation

Revocation is local refusal.

It is not global accusation.

A session may die locally without global consensus.

---

## Funding-Oriented Summary

WHISPER is a local-first cryptographic organism for sovereign communication.

It combines:

- probabilistic hop-by-hop routing
- adaptive reconstruction
- compartmentalized transport
- local session lifecycle management
- strict key non-persistence
- machine-bound dormant local memory

Current milestone:

v1.3 demonstrated adaptive reconstruction.

v1.4 introduces lifecycle validity, anti-replay boundaries, local revocation, and secure shutdown.

---

## Final Statement

WHISPER protects communication by preventing any single layer from owning the full truth.

Nerve senses.

Rotor seals.

FLV remembers.

LUKS protects.

The session dies.

The keys never return.

