# WHISPER v1.3.0 — Architecture Invariants

## Status

Frozen architecture notes before implementation.

v1.3.0 introduces Sol-link magnetic hop-by-hop routing while preserving strict layer separation and the unpredictability invariant.

This document freezes the architectural boundaries before further code changes.

---

## 1. Layer Separation

WHISPER is separated into three major layers:

VoxMesh:
  Logical WHISPER tissue.
  Relay admissibility.
  Local logical state.

WHISPER:
  Encapsulation.
  Scoring.
  Local probabilistic decision.
  Fragment handling.

Reticulum:
  Opportunistic transport substrate.
  Real-time transport decoding.
  Opaque capsule carriage.

Core rule:

VoxMesh qualifies.
WHISPER selects.
Reticulum transports.
No layer knows everything.

---

## 2. VoxMesh / Reticulum Boundary

VoxMesh does not know Reticulum transport identities.

VoxMesh does not store:

- plaintext Reticulum addresses
- Reticulum node identities
- Reticulum routes
- physical location
- IP-level distance
- global transport graph state

VoxMesh stores only WHISPER logical state, such as:

- logical relay aliases
- Sol compatibility
- local admissibility
- FLV state
- degradation state
- observability state
- revocation state
- opaque transport capsules or references

A Reticulum node may carry WHISPER traffic without becoming a WHISPER node.

A Reticulum transport failure returns only as a local degradation symptom.

It does not become global address knowledge.

---

## 3. Reticulum Transport Capsule

VoxMesh does not open transport resolver material.

VoxMesh may reference an opaque transport capsule associated with a logical WHISPER relay.

When transport is attempted, Reticulum decodes the transport capsule in real time and performs delivery without exposing the transport identity back to VoxMesh.

Therefore:

VoxMesh does not know where the capsule goes.
Reticulum does not know what it carries.
WHISPER does not expose the full truth to any single layer.

---

## 4. Sol-Link Magnetic Routing

WHISPER does not route toward:

- a physical destination
- a stable node identity
- a Reticulum address
- a global graph position
- a precomputed full path

When a live Sol-compatible link exists, WHISPER derives an epoch-scoped Sol-link alias.

This Sol-link alias acts as a magnetic attractor for pressure-weighted hop-by-hop routing.

The link attracts the flow.

It does not define a route.

The next-hop weight is conceptually:

next_hop_weight(u, v) =
  random_pressure
  * sol_link_affinity(u, v)
  * flv_health_safety(v)
  * degradation_safety(u, v)
  * structural_exposure_safety(u, v)
  * loop_safety(v)
  * wandering_safety(v)

The Sol creates the context.

The live link creates the magnet.

Pressure moves the fragment.

The path emerges.

---

## 5. Unpredictability Invariant

WHISPER must never expose enough information for any layer, node, endpoint, or observer to:

- predict the complete route
- anticipate the future hop sequence
- reconstruct the fragment distribution
- infer the underlying transport path

Routing decisions must remain:

- local
- probabilistic
- epoch-scoped
- context-dependent

Scores may bend probability.

They must never deterministically define the path.

Short form:

Constraints reduce the space.
Scores bend probability.
Randomness chooses.
The path emerges.
No layer knows everything.

---

## 6. Forbidden by the Invariant

The following are forbidden:

- precomputed complete route
- next_hop = argmax(score)
- visible Reticulum graph
- plaintext Reticulum address stored in VoxMesh
- stable or recognizable fragment identity
- identical decisions from identical visible parameters
- fixed fragment distribution
- deterministic best-path routing

---

## 7. Required by the Invariant

The following are required:

- hop-by-hop selection
- weighted random choice
- controlled random pressure
- epoch-scoped aliases
- opaque capsules
- non-predictable fragmentation
- Reticulum blindness to WHISPER payload
- VoxMesh blindness to transport destination
- strict layer separation
- no single layer knows the full routing, transport, and payload truth

---

## 8. Security Interpretation

The unpredictability invariant is not a liability shield.

It is a security boundary.

WHISPER deliberately prevents any single layer from holding enough information to reconstruct the complete routing, transport, or payload truth.

This limits:

- correlation
- replay
- coercion
- insider misuse
- global path reconstruction
- single-point knowledge exposure

The principle is:

No layer knows everything.
No layer chooses everything.
No layer reveals everything.

---

## 9. Final Architecture Summary

Sol:
  Creates context.

VoxMesh:
  Qualifies logical relays.
  Does not know Reticulum nodes.
  Does not know where the capsule goes.

WHISPER:
  Encapsulates.
  Scores admissible logical relays.
  Performs probabilistic hop-by-hop selection.

Sol-link magnet:
  Attracts the flow without defining a route.

Reticulum:
  Decodes transport capsule in real time.
  Transports opaque WHISPER capsules.
  Does not know WHISPER payload.

Transport result:
  Success or local degradation symptom.

Final rule:

VoxMesh qualifies.
WHISPER selects.
Reticulum transports.
The Sol-link attracts.
The path emerges.
No layer knows everything.
