# WHISPER v1.6.0 — Core Organ Pipelines Report

## Status

Milestone report.

v1.6.0 defines the first complete Core organ pipeline model for WHISPER.

It formalizes:

- inbound isolation
- outbound isolation
- upstream retention
- downstream acknowledgement
- Lemonade / Dôme immunity
- abnormal Lemonade closure reflex
- organ restart safety
- minimal-role reintegration
- no-shortcut invariants

Current validated state:

- 509 tests passing

---

## 1. Executive Summary

WHISPER v1.6.0 introduces the Core organ circulation model.

The purpose is to prevent any external material from reaching Wasm directly and to prevent any Wasm output from reaching the network directly.

The Core is split into two strict, dissociated circuits:

INBOUND:

External
→ Daemon
→ Dôme
→ Coursier
→ BAL In
→ Membrane
→ Wasm

OUTBOUND:

Wasm
→ Membrane
→ BAL Out
→ Transporteur
→ Daemon
→ Network

The two circuits are not interchangeable.

The Transporteur never participates in intake.

The Dôme, Coursier, BAL In, and Lemonade never participate in outbound emission.

The Daemon is a network boundary organ, not an immune decision organ.

---

## 2. Central Doctrine

The Wasm does not know the outside.

It only knows what the Membrane gives it.

An upstream organ never releases material until the downstream organ has confirmed custody.

A dead organ never becomes a shortcut.

A restarted organ never comes back more powerful.

Lemonade recommends.

The Dôme applies.

---

## 3. Inbound Pipeline

The inbound path is:

External
→ Daemon
→ Dôme
→ Coursier
→ BAL In
→ Membrane
→ Wasm

Each organ has a minimal role.

Daemon:
  receives without understanding.

Dôme:
  validates coherence without reading content.

Coursier:
  carries without knowing.

BAL In:
  retains without knowing.

Membrane:
  absorbs without interpreting.

Wasm:
  transforms without touching origin.

The Wasm never receives from:

- External
- Daemon
- Dôme
- Coursier
- BAL In

The only valid direct source for Wasm is the Membrane.

---

## 4. Inbound Upstream Retention

The inbound chain is not only sequential.

It is sequential with downstream acknowledgement and upstream retention.

Rule:

An upstream organ never releases material until the downstream organ has confirmed custody.

Daemon-to-Dôme:

The Daemon retains external material until the Dôme acknowledges reception.

If the Dôme falls before acknowledgement, the Daemon keeps the material.

If the Dôme restarts, the Daemon may resend.

Dôme-to-BAL In:

The Dôme retains validated material until BAL In acknowledges deposit through the Coursier.

If the Coursier falls before BAL acknowledgement, the Dôme keeps the validated material.

If the Coursier restarts, the Dôme may resend.

BAL In-to-Membrane:

BAL In retains material until the Membrane absorbs it.

BAL In is not a passive buffer.

It is a retention zone.

---

## 5. Outbound Pipeline

The outbound path is:

Wasm
→ Membrane
→ BAL Out
→ Transporteur
→ Daemon
→ Network

Each organ has a minimal role.

Wasm:
  produces without touching the network.

Membrane:
  exports without exposing origin.

BAL Out:
  retains without knowing.

Transporteur:
  carries without interpreting.

Daemon:
  emits without understanding.

Network:
  receives only Daemon emission.

The Wasm never emits directly to the network.

The network only receives from the Daemon.

---

## 6. Outbound Upstream Retention

The outbound chain also uses downstream acknowledgement and upstream retention.

Membrane-to-BAL Out:

The Membrane retains exported Wasm material until BAL Out acknowledges custody.

BAL Out-to-Transporteur:

BAL Out retains material until the Transporteur acknowledges pickup.

Transporteur-to-Daemon:

The Transporteur retains material until the Daemon acknowledges custody.

Daemon-to-Network:

The Daemon retains material until the network emission is acknowledged.

The rule is identical to inbound:

No release without downstream custody confirmation.

---

## 7. Lemonade / Dôme Immunity

Lemonade is the immune observation organ.

The Dôme is the defensive application organ.

Lemonade observes symptoms.

The Dôme applies defense.

Lemonade never transports material.

Lemonade never validates content.

Lemonade never blocks material directly.

Lemonade never touches the payload.

Lemonade produces defensive recommendations.

The Dôme applies those recommendations because it is already the organ that accepts, rejects, holds, or quarantines material in the intake path.

The Daemon is not in the immunity loop.

---

## 8. Lemonade Failure Reflex

Lemonade is not a single point of failure.

It is advisory and lateral.

If Lemonade falls, intake continues.

The Dôme falls back to strict local coherence mode.

Adaptive immunity is degraded.

Innate Dôme defense remains active.

On abnormal closure, Lemonade emits a panic flag to the Dôme.

The panic flag contains:

- type
- organ_id
- timestamp
- cause
- priority

It contains no material.

It contains no payload.

It contains no secret.

It does not pass through the Daemon.

After receiving the panic flag, the Dôme:

- enters fallback strict local coherence mode
- disables adaptive recommendations
- avoids automatic quarantine
- avoids automatic revocation
- requests Lemonade restart

Canonical rule:

Lemonade recommends.

The Dôme applies.

If Lemonade falls, it calls.

The Dôme raises it.

---

## 9. Organ Restart Safety

An organ may fall.

It may be restarted.

It must never return with more privileges.

A restarted organ resumes only its minimal role.

Restart safety validates:

- restart only for failed, suspect, or quarantined organs
- revoked organs cannot restart
- healthy organs do not restart unnecessarily
- restarted organs regain only base privileges
- privilege drift blocks reintegration
- restart never changes rails
- restart never creates shortcut
- restart never exposes Wasm
- restart never exposes network
- restart never exposes Vault or FLV

Canonical rule:

A restarted organ does not come back stronger.

It comes back only able to perform its role.

---

## 10. Implemented Modules

### core_intake_isolation_v01.py

Defines inbound rails, upstream retention, ACK states, direct-delivery rejection, and Membrane-only Wasm delivery.

Validated properties:

- external material must pass the full inbound chain
- Wasm cannot receive directly from Daemon
- Wasm cannot receive directly from Dôme
- Wasm cannot receive directly from Coursier
- Wasm cannot read BAL In directly
- rejected material never reaches Coursier
- Coursier cannot carry unvalidated material
- BAL In cannot receive external material directly
- Membrane cannot absorb external material directly
- Transporteur never participates in intake
- Daemon retains until Dôme ACK
- Dôme retains until BAL In ACK
- BAL In retains until Membrane absorption
- organ failure does not create shortcut
- organ restart does not change intake path

---

### lemonade_dome_immunity_v01.py

Defines Lemonade symptom observation, defensive recommendations, Dôme application, panic flag emission, fallback mode, and Lemonade restart request.

Validated properties:

- Lemonade recommendation is applied by Dôme
- Lemonade emits panic flag on abnormal closure
- Dôme enters fallback on Lemonade failure
- Dôme triggers Lemonade restart
- panic flag is urgent and priority
- intake continues without Lemonade via local coherence
- Lemonade never blocks material directly
- Lemonade never touches payload
- Lemonade failure opens no shortcut
- Lemonade failure exposes no Wasm
- Daemon is not notified

---

### core_outbound_isolation_v01.py

Defines outbound rails, upstream retention, ACK states, direct network shortcut rejection, and Daemon-only network emission.

Validated properties:

- Wasm output must pass full outbound chain
- Wasm cannot emit to network directly
- network receives only from Daemon
- Dôme, Coursier, BAL In, and Lemonade never participate in outbound
- Membrane retains until BAL Out ACK
- BAL Out retains until Transporteur ACK
- Transporteur retains until Daemon ACK
- Daemon retains until network ACK
- invalid direct steps are rejected
- organ failure does not create outbound shortcut
- organ restart does not change outbound path

---

### organ_restart_safety_v01.py

Defines organ roles, base privileges, forbidden privileges, runtime records, quarantine, failure, restart, reintegration, revocation, and privilege drift detection.

Validated properties:

- each organ has minimal privileges
- failed organ can request restart
- quarantined organ can request restart
- healthy organ restart is denied
- revoked organ cannot restart
- restart mismatch is denied
- restarted organ reintegrates only after minimal role check
- privilege drift blocks reintegration
- restart preserves minimal role for all organs
- restart adds no privileges
- forbidden privileges are never base privileges
- restart does not expose Wasm, network, Vault, or FLV

---

## 11. Security Invariants

### Wasm Isolation Invariant

The Wasm never touches the outside.

The Wasm never touches the network.

The Wasm receives only Membrane-absorbed material.

The Wasm emits only through the Membrane.

---

### No Shortcut Invariant

No organ failure creates a shortcut.

No organ restart creates a shortcut.

No organ may skip another organ in the inbound or outbound rails.

---

### Upstream Retention Invariant

An upstream organ never releases material until the downstream organ has confirmed custody.

Material does not disappear because an organ falls.

It remains retained until confirmed absorption or custody.

---

### Minimal Role Restart Invariant

A restarted organ resumes only its minimal role.

It does not gain privileges.

It does not gain new edges.

It does not gain direct access to Wasm, network, Vault, FLV, or other organ sandboxes.

---

### Immunity Separation Invariant

Lemonade observes symptoms.

The Dôme applies defense.

The Daemon does not govern immunity.

Lemonade is advisory and lateral.

The Dôme remains the defensive admission organ.

---

## 12. What v1.6.0 Does Not Claim

v1.6.0 does not claim:

- production daemon implementation
- real network daemon binding
- real Wasm runtime sandbox hardening
- real inter-process isolation
- real queue persistence
- real crash recovery on disk
- real authenticated ACKs
- real Reticulum integration
- formal verification
- protection against a fully compromised host OS

v1.6.0 claims only:

The Core organ pipeline model preserves its tested invariants under simulated scenarios.

---

## 13. Test Status

Current suite:

- 509 tests passing

Validated v1.6.0 modules:

- core_intake_isolation_v01.py
- lemonade_dome_immunity_v01.py
- core_outbound_isolation_v01.py
- organ_restart_safety_v01.py

---

---

## 14. End-to-End Integration Tests

v1.6.0 also includes Core pipeline end-to-end integration tests.

File:

tests/test_core_pipelines_e2e_v01.py

Purpose:

Validate that the Core organ rails work together as integrated flows, not only as isolated module units.

Covered scenarios:

- valid external material reaches Wasm only through the full inbound chain
- Wasm output reaches the network only through the full outbound chain
- rejected inbound material never produces outbound flow
- inbound organ failure never creates shortcuts
- Transporteur failure preserves retention and allows resend after restart
- Lemonade failure falls back to Dôme strict local coherence
- restarted organs preserve minimal privileges
- inbound and outbound roles never cross

Core result:

The organism can route material through both rails without shortcut, without unauthorized role crossing, without expanded restart privileges, and without making Lemonade a single point of failure.

---

## Core Session Revocation

v1.6.x adds Core-side session revocation validation.

File:

core_session_revocation_v01.py

Tests:

tests/test_core_session_revocation_v01.py

Purpose:

Validate that a Core-revoked session cannot become active again.

A revoked session is rejected through:

- old session seal replay
- new seal reactivation attempt
- inbound retry
- outbound retry
- organ restart
- Lemonade fallback
- Daemon resend
- close-after-revocation attempts

Core rule:

A session may die.

It must not resurrect.

Validated properties:

- active session can be registered
- active session can be revoked
- revocation is Core-side truth
- revocation is idempotent
- revoked session cannot reactivate with old seal
- revoked session cannot reactivate with new seal
- closed session cannot reactivate
- revoked session blocks inbound
- revoked session blocks outbound
- unknown session is denied
- unknown revoked session creates a revoked record
- organ restart does not restore revoked session
- Lemonade fallback does not restore revoked session
- Daemon resend does not restore revoked session
- close after revocation is ignored

Canonical invariant:

A revoked Core session never becomes active again.

Not through the past.

Not through restart.

Not through network retry.

Not through immunity fallback.

## 15. Final Statement

WHISPER v1.6.0 gives the Core its circulation rules.

The outside cannot touch Wasm.

Wasm cannot touch the network.

Material cannot vanish on organ failure.

Lemonade can fall without breaking intake.

Organs can restart without gaining power.

Final rule:

The organism survives because no organ is allowed to become the whole organism.
