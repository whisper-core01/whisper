# WHISPER v1.5.0 — Nerve Mobile Report

## Status

Milestone report.

v1.5.0 documents and validates the Nerve Mobile architecture.

Nerve Mobile is the mobile peripheral nerve of WHISPER.

It is not a client.

It is not a trusted device.

It is not a mobile Vault.

It is not a messaging app.

It is a sensory organ that appears in the Sol, emits impulses, receives responses, and never becomes sovereign.

---

## 1. Executive Summary

WHISPER v1.5.0 introduces the first complete Nerve Mobile prototype model.

The objective is to allow a mobile device to act as a peripheral Nerve without becoming:

- a client
- an identity
- a session holder
- a key holder
- a Core replica
- a sovereign storage device

Nerve Mobile has continuity, but not sovereignty.

It may keep a local scar in a Mobile Vault, but the Core keeps the truth.

Core result:

- 417 tests passing
- Nerve Mobile admission validated
- Vault boot sequence validated
- reappearance after reboot validated
- revocation validated
- runtime statelessness validated
- capabilities model validated
- transport model validated
- UI membrane validated
- permissions model validated
- Wasm bridge boundary validated

---

## 2. Core Doctrine

Nerve Mobile follows a simple rule:

The mobile does not identify itself.

It produces a code of appearance.

The Sol challenges.

Rotor transforms.

The Core admits, ignores, or revokes.

The FLV remembers.

The mobile forgets.

---

## 3. Organ Model

Nerve Mobile is not a conventional application.

It is modeled as an organ.

Birth:
  Mobile Vault boot

Appearance:
  Rotor-derived admission code

Continuity:
  origin_hint and nerve_local_material

Reappearance:
  fresh Sol challenge

Death:
  Core-side revocation

Life:
  stateless runtime loop

Senses:
  capabilities and permissions

Impulses:
  transport layer

Membrane:
  UI

Boundary:
  Wasm bridge

---

## 4. Implemented Modules

### nerve_mobile_admission_v01.py

Purpose:

Defines the first appearance of a mobile Nerve in the Sol.

The mobile does not send an IMEI.

The mobile does not send a static identity hash.

The mobile does not send a secret.

Instead, it derives:

- surface_seed
- Rotor-style nerve_admission_code
- Sol admission envelope
- Core-side binding commitment

Key rule:

The mobile does not identify itself.

It produces a code of appearance.

---

### nerve_mobile_vault_boot_v01.py

Purpose:

Defines the birth of the mobile nerve.

Nerve Mobile may have continuity through a local Mobile Vault.

The Vault is opened only during boot/admission.

The Vault is closed immediately.

Admission buffers are zeroized.

After boot, the Nerve runs without an open Vault.

Key rule:

The Vault opens for birth.

It closes before life.

---

### nerve_mobile_reappearance_v01.py

Purpose:

Defines reappearance after reboot.

A Nerve Mobile may reappear, but it cannot replay its old appearance.

Reappearance requires:

- fresh Sol challenge
- fresh boot nonce
- fresh admission epoch
- continuity commitment
- Core-side binding recognition

Key rule:

The nerve may reappear.

It cannot replay its old appearance.

---

### nerve_mobile_revocation_v01.py

Purpose:

Defines Core-side Nerve Mobile revocation.

Once a Nerve binding is revoked by the Core, it must never be admitted again by that Core.

Even with:

- the same Mobile Vault
- a clean new appearance
- a fresh Sol challenge
- a fresh Rotor-derived code
- a reboot
- an old admission code
- a copied Mobile Vault

Key rule:

The nerve may die.

It cannot come back from the dead.

---

### nerve_mobile_runtime_v01.py

Purpose:

Defines the life of the Nerve after birth.

The runtime does not think.

It transmits.

It:

- receives user events
- wraps them into runtime envelopes
- sends them into the Sol
- receives Core responses
- renders responses
- updates a minimal status

It does not:

- reopen the Vault
- perform admission
- handle identity
- handle sessions
- hold WHISPER secrets

Key rule:

The Vault opens for birth.

It closes before life.

The runtime only lets current pass.

---

### nerve_mobile_capabilities_v01.py

Purpose:

Defines the sensory map of the Nerve.

Capabilities are not identity.

Capabilities are not rights.

Capabilities are not admission.

Capabilities are only sensory declarations.

Base capabilities:

- text
- audio
- image
- video
- event

Optional capabilities:

- location_hint
- file

Forbidden capabilities:

- crypto
- identity
- session

Key rule:

The nerve does not choose its role.

It declares what it can sense.

The Core decides what it wants to hear.

---

### nerve_mobile_transport_v01.py

Purpose:

Defines how Nerve Mobile emits impulses into the Sol.

The Nerve does not connect.

It emits.

The Sol responds, or stays silent.

Transport v01 introduces no:

- connection semantics
- session
- identity
- handshake
- token
- secret
- persistent state

Key rule:

The nerve does not connect.

It emits.

The Sol responds, or stays silent.

---

### nerve_mobile_ui_v01.py

Purpose:

Defines the minimal human-facing membrane of Nerve Mobile.

The UI is not an app shell.

It is not a client.

It is not a configuration surface.

It is a sensory membrane.

It shows:

- what the human sends
- what WHISPER returns
- status

Only three statuses exist:

- WHISPER_RESPONDING
- WHISPER_SILENT
- OFFLINE

Key rule:

The UI of the nerve explains nothing.

It shows what WHISPER says.

It stays silent when WHISPER is silent.

---

### nerve_mobile_permissions_v01.py

Purpose:

Defines OS-level sensor permissions required by Nerve Mobile capabilities.

Permissions open senses.

They do not grant identity.

They do not grant admission.

They do not grant Core trust.

They do not open the Vault.

They do not create a session.

Key rule:

The Nerve may ask the OS for senses.

The Core decides what it wants to hear.

---

### nerve_mobile_wasm_bridge_v01.py

Purpose:

Defines the host/Wasm boundary for Nerve Mobile.

The Wasm may request.

The host filters.

The Nerve must never escape its role.

Allowed host calls:

- load Mobile Vault during boot only
- close Mobile Vault
- zeroize admission buffers
- emit Sol impulse
- poll Sol response
- request sensor permission

Forbidden host calls:

- open Vault during runtime
- read Core Vault
- read FLV
- read identity
- read session
- read keys
- configure network
- derive WHISPER crypto

Key rule:

The Wasm asks.

The host filters.

The Nerve never leaves its role.

---

## 5. Security Invariants

### No Mobile Sovereignty

The mobile is not sovereign.

It does not own admission.

It does not own identity.

It does not own memory truth.

It does not own revocation truth.

The Core remains the source of truth.

---

### No Persistent WHISPER Secret on Mobile

The mobile must never store:

- Core master key
- Core Vault
- session keys
- fragment keys
- repair keys
- FLV master binding
- route identity
- Core Reticulum identity
- sovereign WHISPER secrets

---

### Mobile Vault as Scar

The Mobile Vault may contain continuity artifacts.

It keeps the scar.

It does not keep the brain.

The Mobile Vault is opened only during boot/admission.

It is closed before runtime life.

---

### No Client Semantics

Nerve Mobile is not a client.

There is no:

- login
- account
- QR requirement
- server picker
- session token
- persistent connection identity

The Nerve appears in the Sol.

---

### Runtime Statelessness

During runtime:

- no Vault reopening
- no admission
- no identity
- no session
- no WHISPER secret
- no internal state persistence

The runtime only emits and receives impulses.

---

## 6. Test Status

Current suite:

- 417 tests passing

Nerve Mobile validated modules include:

- nerve_mobile_admission_v01.py
- nerve_mobile_vault_boot_v01.py
- nerve_mobile_reappearance_v01.py
- nerve_mobile_revocation_v01.py
- nerve_mobile_runtime_v01.py
- nerve_mobile_capabilities_v01.py
- nerve_mobile_transport_v01.py
- nerve_mobile_ui_v01.py
- nerve_mobile_permissions_v01.py
- nerve_mobile_wasm_bridge_v01.py

---

## 7. Relationship to Earlier WHISPER Milestones

v1.3 established adaptive routing and reconstruction.

v1.4 established session lifecycle, FLV dormancy, and non-reactivation.

v1.5 extends the organism to the mobile edge.

It introduces a peripheral Nerve that can appear, live, reappear, die, emit, sense, and render without becoming a client or carrying sovereign secrets.

---

## 8. What v1.5.0 Does Not Claim

v1.5.0 does not claim:

- production mobile implementation
- real Android/iOS integration
- real hardware secure storage
- real Wasm sandbox hardening
- real OS permission enforcement
- real Reticulum mobile transport
- formal proof of mobile non-cloning
- protection against fully compromised mobile OS
- secure memory erasure guarantees in Python

v1.5.0 claims only:

The prototype Nerve Mobile model preserves the intended invariants under tested scenarios.

---

## 9. Final Statement

Nerve Mobile is a peripheral organ.

It has a scar, but not a sovereign identity.

It has senses, but not authority.

It has a membrane, but not a control panel.

It emits, but does not connect.

It can reappear, but cannot replay.

It can die, but cannot resurrect.

Final rule:

The mobile is not the brain.

The mobile is a nerve.

