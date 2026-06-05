# WHISPER v1.3.3 — Blind Repair and Decoy-Equivalent Flow Design

## Status

Design frozen.

Implementation pending.

This document defines the v1.3.3 defensive repair layer.

v1.3.3 is not included in the tested v1.3.4 reconstruction metrics.

v1.3.4 handles adaptive delivery and reconstruction reliability.

v1.3.3 is intended to reduce long-term correlation risk around repair behavior.

---

## 1. Problem

If WHISPER directly retransmits missing fragments, an observer may infer:

- which fragments were missing
- when repair begins
- when repair ends
- which packets are useful
- which packets are recovery material
- which paths correlate with missing material
- whether the receiver failed to reconstruct

This would violate the unpredictability invariant.

The missing fragment set must never be exposed.

---

## 2. Core Principle

WHISPER never retransmits a missing fragment as-is.

WHISPER does not ask for specific fragment indices in clear form.

WHISPER does not emit a visibly distinct repair phase.

Repair must look like ordinary WHISPER traffic.

Short form:

WHISPER does not resend the missing piece.

WHISPER re-injects indistinguishable repair rain.

---

## 3. Blind Repair Signal

When reconstruction is incomplete, the receiver-side WHISPER instance emits only an opaque signal.

The signal means:

reconstruction threshold has not yet been reached

The signal must not reveal:

- missing fragment indices
- number of missing fragments
- fragment order
- file size
- reconstruction state
- repair target set

The signal is a protocol event, not a human action.

Paul does nothing.

Alice does nothing beyond the original intent.

WHISPER handles repair automatically.

---

## 4. Randomized Repair Material

Repair material is freshly derived.

It is not a copy of the original missing fragment.

Repair material should be derived from:

- message commitment
- Sol context
- epoch
- repair nonce
- repair counter
- local session material

The output is re-sliced into randomized chunks.

Repair chunks must use:

- variable sizes
- fresh padding
- fresh nonces
- fresh encapsulation
- independent pressure-field routing
- randomized scheduling
- disordering
- decoy-equivalent packet shaping

A repair chunk must not be linkable to an original fragment index.

---

## 5. Decoy-Equivalent Flow

WHISPER already supports the idea of decoy packets with the same observable signature as real fragments.

v1.3.3 formalizes this.

At the transport-observable layer, an observer must not distinguish:

- useful fragment
- recovery fragment
- repair shard
- decoy packet

Decoy-equivalent packets must match useful fragments in:

- size class
- padding behavior
- timing distribution
- entropy appearance
- capsule structure
- Reticulum transport behavior
- pressure-field routing behavior

A decoy may differ only after local cryptographic validation.

It must never differ at the transport-observable layer.

---

## 6. Repair Scheduling

Repair shards are injected into the same scheduler as ordinary WHISPER fragments.

They must not be sent as a visible burst.

They must not be grouped as a repair phase.

They must not follow a deterministic order.

They must use:

- randomized timers
- randomized order
- pressure-field routing
- local custody
- decoy interleaving

Therefore, an observer cannot identify:

- repair start
- repair end
- repair volume
- missing fragment set
- repair success

---

## 7. Relationship to v1.3.4

v1.3.4 solves reliability through:

- adaptive redundancy
- custody
- buffered receive mode
- streaming receive mode
- local network symptom adaptation

v1.3.3 solves a different problem:

- repair correlation
- missing fragment inference
- repair phase detection
- decoy indistinguishability

v1.3.4 improves reconstruction.

v1.3.3 protects the repair process from being observable.

---

## 8. Invariant

Repair shards must be indistinguishable from ordinary WHISPER fragments at the transport-observable layer.

A repair shard must not reveal:

- that it is repair
- which fragment it repairs
- what was missing
- how many fragments are missing
- whether reconstruction has failed
- whether reconstruction later succeeded

---

## 9. Security Interpretation

v1.3.3 protects against:

- correlation of repair bursts
- missing-set inference
- targeted dropping of recovery material
- traffic-shape analysis around repair
- distinguishing useful packets from decoys
- reconstruction-state leakage

It does not claim:

- perfect anonymity
- protection against all global passive analysis
- production-ready cryptographic erasure repair
- implemented results in the current v1.3.4 metrics

---

## 10. Future Implementation Plan

Implementation should add:

- repair_material_derivation_v01.py
- randomized_repair_slicer_v01.py
- decoy_equivalence_policy_v01.py
- repair_scheduler_v01.py
- tests for size and timing distribution
- tests for non-linkability to original fragment indices
- comparator for reconstruction after blind repair
- comparator for observer distinguishability

Required metrics:

- repair_success_rate
- repair_observer_distinguishability
- repair_overhead
- decoy_ratio
- missing_set_leakage_proxy
- reconstruction_after_repair
- clean_threshold_reconstruction

---

## 11. Final Summary

v1.3.3 is the defensive repair layer.

It ensures that repair does not expose what was missing.

It ensures that repair shards look like ordinary WHISPER fragments.

It ensures that decoys, useful fragments, recovery fragments, and repair shards share the same observable signature.

Final rule:

WHISPER does not reveal the missing set.

WHISPER does not retransmit missing fragments.

WHISPER re-injects indistinguishable repair rain.

