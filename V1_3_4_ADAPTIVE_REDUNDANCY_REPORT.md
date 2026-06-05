# WHISPER v1.3.4 — Adaptive Network-Aware Redundancy Report

## Status

Experimental report.

This report documents the v1.3.4 adaptive redundancy calibration.

v1.3.4 builds on:

- v1.3.0 Sol-link magnetic logical routing
- v1.3.1 Sol-link pressure field
- v1.3.2 redundancy compensation with persistent custody
- v1.3.3 blind repair and decoy-equivalent flow concept

The goal of v1.3.4 is to replace fixed redundancy parameters with adaptive local control based on non-oracle network symptoms.

---

## 1. Core Principle

WHISPER does not use a single fixed redundancy value.

Instead, WHISPER adapts:

- redundancy factor
- custody rounds
- repair budget
- receive mode

from local network symptoms.

These symptoms are not adversarial attribution.

They are only local observations.

A bad signal does not mean a node is malicious.

It only means the local transport conditions are degraded.

---

## 2. Local Non-Oracle Symptoms

The adaptive profile uses local symptoms only:

- latency risk
- jitter risk
- timeout risk
- signal loss risk
- receiver capacity risk

These values are bounded in [0.0, 1.0].

They are never interpreted as proof of compromise.

They do not expose Reticulum topology.

They do not expose missing fragments.

They do not expose the destination.

They do not expose the payload.

---

## 3. Network Risk Model

The local network risk is computed as:

network_risk =
  0.25 * latency_risk
+ 0.25 * jitter_risk
+ 0.30 * timeout_risk
+ 0.20 * signal_loss_risk

Then receiver capacity is integrated as a local receive-mode pressure:

network_risk =
  0.85 * transport_risk
+ 0.15 * receiver_capacity_risk

Interpretation:

0.0:
  excellent local conditions

0.5:
  degraded but usable local conditions

1.0:
  very poor local conditions

This is not an attack detector.

It is a transmission strategy signal.

---

## 4. Calibrated Adaptive Profile

The first adaptive profile was too optimistic.

It used:

- minimum redundancy: 1.10
- maximum redundancy: 1.40
- minimum custody rounds: 3
- maximum custody rounds: 7

This produced poor reconstruction under good and normal profiles.

The calibrated profile now uses:

- minimum redundancy: 1.25
- maximum redundancy: 1.40
- minimum custody rounds: 5
- maximum custody rounds: 7

This prevents WHISPER from saving bandwidth at the cost of reconstruction reliability.

Final rule:

The adaptive layer may increase redundancy under poor conditions.

It must not reduce redundancy below the experimentally credible reconstruction floor.

---

## 5. Adaptive Parameters

Redundancy factor:

redundancy_factor =
  1.25 + 0.15 * network_risk

Custody rounds:

custody_rounds =
  5 + round(2 * network_risk)

Repair budget:

repair_budget_factor =
  0.05 + 0.15 * network_risk

Receive mode:

BUFFERED:
  used when receiver capacity risk is below threshold

STREAMING:
  used when receiver capacity is constrained

Streaming mode changes the receiver-side memory strategy only.

It does not expose fragment order.

It does not expose missing fragment indices.

It does not expose file size.

---

## 6. Tested Profiles

Four synthetic local network profiles were evaluated:

GOOD:
  low latency
  low jitter
  low timeout risk
  low signal loss risk
  buffered receive mode

NORMAL:
  moderate local network degradation
  buffered receive mode

BAD:
  high local degradation
  mixed buffered / streaming receive mode

VERY_BAD:
  very high local degradation
  streaming receive mode

All profiles are deterministic and non-oracle.

No compromise labels are used to generate network symptoms.

---

## 7. Experimental Setup

Run size:

- 30 seeds
- 3 conditions
- 4 network profiles
- total rows: 360

Conditions:

- random
- targeted
- behavioral

Fixed routing parameters:

- magnet_strength = 6.0
- wandering_strength = 0.5
- required_fragments = 100
- hop_budget = 12

Adaptive parameters:

- redundancy factor derived from network_risk
- custody rounds derived from network_risk
- receive mode derived from receiver_capacity_risk

---

## 8. Results

### GOOD profile

network_risk:
  0.1006

adaptive_redundancy:
  1.2651

adaptive_custody:
  5

streaming_ratio:
  0.0

message reconstruction:
  0.9889

delivered_total:
  107.47

reconstruction margin:
  +7.47

bandwidth overhead:
  1.27

mean exposure:
  1.0859

loop rate:
  0.0378

dead-end rate:
  0.0111

invariants:
  OK

---

### NORMAL profile

network_risk:
  0.3604

adaptive_redundancy:
  1.3041

adaptive_custody:
  6

streaming_ratio:
  0.0

message reconstruction:
  1.0000

delivered_total:
  110.98

reconstruction margin:
  +10.98

bandwidth overhead:
  1.31

mean exposure:
  1.0898

loop rate:
  0.0332

dead-end rate:
  0.0106

invariants:
  OK

---

### BAD profile

network_risk:
  0.6524

adaptive_redundancy:
  1.3479

adaptive_custody:
  6

streaming_ratio:
  0.6333

message reconstruction:
  1.0000

delivered_total:
  114.71

reconstruction margin:
  +14.71

bandwidth overhead:
  1.3527

mean exposure:
  1.0525

loop rate:
  0.0345

dead-end rate:
  0.0081

invariants:
  OK

---

### VERY_BAD profile

network_risk:
  0.9005

adaptive_redundancy:
  1.3851

adaptive_custody:
  7

streaming_ratio:
  1.0

message reconstruction:
  1.0000

delivered_total:
  118.10

reconstruction margin:
  +18.10

bandwidth overhead:
  1.3907

mean exposure:
  1.0691

loop rate:
  0.0376

dead-end rate:
  0.0104

invariants:
  OK

---

## 9. Interpretation

The first adaptive profile proved that WHISPER could react to network conditions.

However, it was too aggressive in saving bandwidth under good and normal profiles.

The calibrated profile fixes this by enforcing a reliability floor:

- redundancy cannot fall below 1.25
- custody cannot fall below 5 rounds

This produces near-complete reconstruction across all tested profiles.

The result is important:

WHISPER can adapt redundancy and custody to local network conditions while preserving layer blindness invariants.

---

## 10. Key Findings

Finding 1:
  Adaptive redundancy works.

Finding 2:
  The adaptive floor matters more than the adaptive slope.

Finding 3:
  Good networks still require a reliability floor.

Finding 4:
  Bad networks benefit from increased redundancy and custody.

Finding 5:
  Streaming receive mode activates naturally under capacity pressure.

Finding 6:
  Exposure remains stable.

Finding 7:
  Loop and dead-end rates remain low.

Finding 8:
  VoxMesh / Reticulum / payload blindness invariants are preserved.

---

## 11. Security Boundaries

v1.3.4 preserves the architectural invariants:

VoxMesh:
  qualifies logical relays
  does not know Reticulum nodes
  does not know where the capsule goes

WHISPER:
  selects among admissible logical relays
  does not precompute full paths
  does not route over the Reticulum graph

Reticulum:
  transports opaque capsules
  does not know the WHISPER payload

No layer knows everything.

---

## 12. What v1.3.4 Does Not Claim

v1.3.4 does not claim:

- adversarial detection
- proof of anonymity
- guaranteed delivery under all network failures
- optimal redundancy
- production readiness
- cryptographic erasure coding implementation

v1.3.4 only claims:

Adaptive redundancy and custody can improve reconstruction reliability using local non-oracle network symptoms while preserving WHISPER layer separation.

---

## 13. Current Calibrated Parameters

Recommended pilot parameters:

magnet_strength:
  6.0

wandering_strength:
  0.5

minimum redundancy:
  1.25

maximum redundancy:
  1.40

minimum custody rounds:
  5

maximum custody rounds:
  7

receive mode:
  BUFFERED unless receiver capacity is constrained

streaming threshold:
  receiver_capacity_risk >= 0.65

---

## 14. Operational Interpretation

WHISPER does not try to force the path.

WHISPER adapts the rain.

Under good conditions:
  moderate redundancy
  stable custody
  buffered receive

Under degraded conditions:
  more redundancy
  more custody
  possible streaming receive

Under very poor conditions:
  high redundancy
  high custody
  streaming receive

The route remains emergent.

The payload remains opaque.

The transport identity remains hidden from VoxMesh.

---

## 15. Final Summary

v1.3.4 validates adaptive network-aware redundancy.

Using local non-oracle symptoms, WHISPER adjusts redundancy, custody, repair budget, and receive mode.

In the n360 pilot, the calibrated profile reaches:

- 98.9% reconstruction on good profiles
- 100% reconstruction on normal profiles
- 100% reconstruction on bad profiles
- 100% reconstruction on very bad profiles
- stable exposure
- low loop rates
- low dead-end rates
- full layer-blindness invariants

Final rule:

WHISPER does not use fixed rain.

WHISPER adapts the rain to the sky.

