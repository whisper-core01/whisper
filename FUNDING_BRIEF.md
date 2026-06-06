# WHISPER — Funding Brief

## 1. What is WHISPER?

WHISPER is a cryptographic organism for sovereign digital communication.

It is not a messaging application.

It is not a classical router.

It is not a simple encrypted file-transfer tool.

WHISPER is a local-first communication layer designed to protect not only message content, but the full communication container:

- routing
- rhythm
- fragmentation
- repair
- session lifecycle
- local memory
- closure
- dormancy
- disappearance

Core idea:

Encryption protects what is said.

WHISPER protects what the communication reveals before it is even read.

---

## 2. The Problem

Most secure messaging systems focus primarily on content encryption.

This is necessary, but insufficient.

Even when content is encrypted, metadata and infrastructure patterns may reveal:

- who communicates
- with whom
- when
- how often
- at what volume
- through which infrastructure
- from which endpoints
- with which behavioral patterns
- under which local context

A message can be unreadable and still expose the structure of communication.

This is the weakness WHISPER addresses.

---

## 3. What WHISPER Does Differently

WHISPER protects the container of communication.

It does this through compartmentalized architecture:

VoxMesh:
  qualifies logical relays without knowing Reticulum transport identities

WHISPER:
  fragments, encapsulates, scores, routes probabilistically, and reconstructs

Reticulum:
  transports opaque capsules without knowing the WHISPER payload

Nerve:
  senses local symptoms and triggers local reflexes

Rotor:
  seals lifecycle events such as session closure

FLV:
  stores dormant local lifecycle memory inside LUKS

No layer knows everything.

No route is fully precomputed.

No session can resurrect after closure.

No FLV is portable outside its local machine context.

---

## 4. Current Milestones

### v1.3.4 — Adaptive Reconstruction

WHISPER v1.3.4 validated adaptive network-aware redundancy.

It introduced:

- Sol-link pressure routing
- probabilistic hop-by-hop selection
- redundancy and custody
- adaptive reconstruction
- buffered and streaming receive modes

Key results:

- 98.89% reconstruction on good network profiles
- 100% reconstruction on normal, bad, and very bad profiles
- stable exposure
- low loop rate
- low dead-end rate
- layer-blindness invariants preserved

Stable tag:

https://github.com/whisper-core01/whisper/tree/v1.3.4

---

### v1.4.1 — Session Lifecycle and Non-Reactivation

WHISPER v1.4.1 validates the local session lifecycle layer.

It introduced:

- session start seal
- session hash validity boundary
- fragment, capsule, and repair session binding
- local session revocation
- rotor close code
- secure shutdown sequence
- key destruction commitment
- machine/LUKS-bound dormant FLV lifecycle record
- session reactivation prevention comparator

Key results:

- 297 tests passing
- 330 session reactivation cases
- 1.0000 pass rate
- old sessions may leave local traces but cannot become active again

Stable tag:

https://github.com/whisper-core01/whisper/tree/v1.4.1

---

## 5. Core Invariants

WHISPER is governed by strict invariants:

Layer blindness:

- VoxMesh does not know where the capsule goes
- Reticulum does not know what it transports
- no layer knows everything

Unpredictability:

- constraints reduce the space
- scores bend probability
- randomness chooses
- the path emerges

Key non-persistence:

- no session key survives the session
- no fragment key survives the fragment context
- no repair key survives the repair round
- no custody key survives its TTL

Session non-reactivation:

- old sessions may leave local traces
- old sessions must never become active again

FLV dormancy:

- the session dies
- the keys are destroyed
- the FLV sleeps inside LUKS
- only the local machine context can wake it

---

## 6. Why Funding Matters

WHISPER has reached the point where the core architecture is coherent, documented, and experimentally validated at prototype level.

Funding would enable the next phase:

- production-grade implementation of core primitives
- real erasure coding
- real cryptographic repair shards
- Reticulum integration
- secure memory handling beyond Python prototypes
- LUKS-bound FLV implementation
- formal threat model refinement
- independent security review
- real-world network testing
- documentation and packaging for external developers

---

## 7. Roadmap

### v1.5.0 — Distributed Temporal Immunity

Goal:

Add local temporal memory and recovery behavior without global blacklists or permanent accusation.

Planned properties:

- local degradation memory
- adaptive trust decay
- time-based recovery
- no global oracle
- no permanent blacklist
- no stable identity exposure

---

### v1.6.0 — Blind Repair Implementation

Goal:

Implement repair shards that are indistinguishable from ordinary WHISPER traffic.

Planned properties:

- randomized repair slicing
- decoy-equivalent repair flow
- no missing fragment disclosure
- anti-correlation repair behavior

---

### v1.7.0 — Reticulum Bridge Hardening

Goal:

Move from prototype bridge behavior toward hardened Reticulum integration.

Planned properties:

- opaque capsule transport
- route non-disclosure
- adapter-level resolution
- no Reticulum graph exposure to VoxMesh

---

## 8. What WHISPER Is Not

WHISPER is not:

- a Signal replacement
- a WhatsApp competitor
- a Telegram clone
- a classical overlay router
- a global consensus network
- a blockchain
- a permanent identity system

WHISPER is a sovereign communication layer.

Its purpose is to protect the lifecycle of communication, not merely the message body.

---

## 9. Repository Entry Points

Repository:

https://github.com/whisper-core01/whisper

Recommended reading:

1. DOCTRINE_CONTENT_VS_CONTAINER.md
2. WIKI_INDEX.md
3. V1_3_SERIES_REPORT.md
4. V1_4_0_SESSION_LIFECYCLE_REPORT.md
5. WIKI_ROTOR.md
6. WIKI_NERVE.md
7. WIKI_FLV.md

---

## 10. Final Statement

Most secure messengers protect the content of communication.

WHISPER protects the life of communication.

That is the difference between a protocol that protects a message and an organism that protects an entire lifecycle.

