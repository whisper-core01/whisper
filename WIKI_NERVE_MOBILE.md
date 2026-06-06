# WHISPER Wiki — Nerve Mobile

## Status

Design doctrine.

Implementation pending.

Nerve Mobile is the mobile peripheral nerve of WHISPER.

It is not a client.

It is not a trusted device.

It is not a mobile Vault.

It is not an AI application.

It is a stateless sensory terminal that appears inside the Whisper Sol.

---

## 1. Core Definition

Nerve Mobile is a peripheral organ.

It does not connect to WHISPER like a classical app.

It appears in the Sol.

Whisper-Core decides whether this appearance is admissible.

The mobile does not own the decision.

The mobile does not hold sovereign secrets.

The mobile transmits.

The Sol challenges.

The Core remembers.

---

## 2. Core Doctrine

The mobile does not identify itself.

It produces an appearance code.

This appearance code is:

- bounded to a Sol challenge
- bounded to an admission epoch
- bounded to a boot nonce
- non-portable
- non-reusable
- revocable
- not a key
- not an identity

Short form:

The mobile does not identify itself.

It produces a code of appearance.

---

## 3. No Connection Screen

Nerve Mobile must not behave like a conventional client.

There is no account.

There is no login.

There is no pairing screen.

There is no QR-code requirement.

There is no persistent token.

There is no user identity stored on the mobile.

The mobile appears.

The Core decides.

If the Core ignores it, the mobile remains silent or waiting.

If the Core admits it, the mobile becomes a living Nerve.

If the Core revokes it, the mobile becomes inert.

---

## 4. Mobile Appearance Flow

When Nerve Mobile boots, it collects only weak local surface hints:

imei_hash_local:
  Local hash of IMEI or equivalent hardware surface if available.

carrier_hint:
  Coarse network environment hint such as carrier, country, or network type.

boot_nonce:
  Random value regenerated at every Nerve boot.

admission_epoch:
  Current Sol admission window.

The mobile waits for a sol_admission_challenge emitted by Whisper-Core.

Then it derives:

surface_seed =
  H(
    imei_hash_local,
    carrier_hint_hash,
    sol_admission_challenge,
    boot_nonce,
    admission_epoch,
    "NERVE_MOBILE_SURFACE_SEED_V1"
  )

The surface_seed is not sent.

The surface_seed is not stored permanently.

The surface_seed is used only as input material for Rotor admission.

---

## 5. Rotor Admission Code

Nerve Mobile injects surface_seed into RotorMachine to derive a bounded appearance code.

Conceptual derivation:

nerve_admission_code =
  RotorMachine(surface_seed).emit_code(
    mode = "nerve_admission",
    epoch = admission_epoch
  )

The mobile emits only the admission code and minimal capability metadata.

Example Sol appearance envelope:

{
  "nerve": "mobile",
  "kind": "admission_candidate",
  "admission_epoch": "...",
  "boot_nonce_commitment": "...",
  "capabilities": ["text", "audio", "image"],
  "nerve_admission_code": "..."
}

The mobile must never transmit:

- raw IMEI
- raw carrier identity
- static IMEI hash
- surface_seed
- master key
- session key
- Vault material
- Whisper identity

---

## 6. Core Admission

Whisper-Core receives the Nerve appearance code through the Sol.

The Core may:

- admit
- ignore
- revoke

If admitted, the Core creates or updates a local nerve_binding.

The nerve_binding is stored only inside Core-controlled local memory, FLV, and LUKS-bound state.

The mobile does not receive a durable secret.

The mobile does not become a sovereign identity.

The mobile becomes a revocable peripheral nerve.

---

## 7. FLV Binding

The Core may store a local commitment:

nerve_binding_commitment =
  H(
    local_master_binding_hash,
    nerve_admission_code,
    sol_epoch,
    nerve_binding_nonce,
    "WHISPER_NERVE_BINDING_COMMITMENT_V1"
  )

The FLV may record:

- nerve_binding_commitment
- nerve_birth_epoch
- nerve_capabilities
- nerve_revocation_state
- surface_commitment_version
- last_seen_epoch

The FLV must not record:

- IMEI
- raw carrier
- static IMEI hash
- surface_seed
- mobile secret
- session key
- payload
- Reticulum identity

---

## 8. Reboot Behavior

If the Core reboots:

- LUKS opens
- FLV wakes from dormancy
- Core reloads local nerve binding commitments
- mobile appears again in the Sol
- Core emits a fresh sol_admission_challenge
- mobile derives a fresh appearance code
- Core checks continuity against FLV commitments

A reboot may wake FLV memory.

A reboot must not reactivate an old closed session.

A Nerve may be admitted again.

The previous session must not be resumed.

---

## 9. Revocation Behavior

If Whisper-Core revokes a Nerve:

- the local nerve_binding is marked revoked
- future appearance codes from that surface are ignored or rejected
- the mobile receives no secret to erase
- the mobile becomes an inert terminal

The mobile remains stateless.

The Core remembers.

Revocation is local refusal, not global accusation.

---

## 10. Security Model

Main threat:

A hostile phone attempts to appear as a Nerve.

Response:

The phone cannot rely on a static identifier.

It must answer a fresh Sol challenge during a bounded admission epoch.

The Core stores only local, LUKS-bound, master-key-derived commitments.

Secondary threat:

A copied appearance code is replayed.

Response:

Admission codes are challenge-bound, epoch-bound, boot-bound, and non-reusable.

Secondary threat:

A phone is lost.

Response:

The Core revokes the local nerve_binding.

The phone contains no Whisper secret.

---

## 11. Invariants

Nerve Mobile Admission Invariant:

A mobile Nerve is never trusted because it stores a secret.

It is admitted only when the local Whisper Sol recognizes it during a bounded admission window and binds it to a local, revocable nerve_binding stored inside the Core environment.

Nerve Mobile Appearance Invariant:

A mobile Nerve never appears in the Sol by exposing a stable hardware identity.

It appears by deriving an ephemeral admission code from local surface hints, a Core-issued Sol challenge, a boot nonce, and the current admission epoch.

Nerve Mobile Statelessness Invariant:

The mobile stores no sovereign Whisper secret.

It may keep UX preferences or optional local history, but it must not store keys, seeds, Vault material, session state, or irreversible identity.

---

## 12. User Experience

The user should not see technical pairing.

No debug panel.

No raw JSON panel.

No connection wizard.

No account screen.

The mobile UI should expose only simple states:

- Whisper is silent
- Whisper is responding
- Waiting for the Core
- This Nerve is no longer admitted

The mobile should explain:

This phone is a Nerve.

The intelligence, memory, and secrets are elsewhere.

---

## 13. Final Rule

The mobile does not connect.

The mobile appears.

The Sol challenges.

The Core admits.

The FLV remembers.

The Nerve transmits.


---

## 14. Final Nerve Mobile Model

Nerve Mobile has continuity, but that continuity is not carried by the app itself.

Continuity is carried by a local Mobile Vault.

The Mobile Vault contains only revocable continuity artifacts.

It must never contain sovereign WHISPER secrets.

---

## 15. Mobile Vault Continuity

The Mobile Vault may contain:

- origin_hint
- nerve_local_material
- nerve_birth_epoch
- last_seen_epoch
- capability_profile
- revocation_marker
- surface_commitment_version

The Mobile Vault must not contain:

- Core master key
- Core Vault
- session keys
- fragment keys
- repair keys
- payload
- route
- FLV master binding
- Core Reticulum identity
- sovereign WHISPER secrets

Short form:

The Mobile Vault keeps the scar.

The Core keeps the truth.

---

## 16. Wasm and Vault Boot Sequence

Nerve Mobile runs inside a Wasm runtime.

At boot/admission time:

- the Wasm runtime starts
- the Mobile Vault is opened
- origin_hint, nerve_local_material, and continuity artifacts are read
- the Mobile Vault is closed immediately
- Vault read buffers are zeroized
- Sol challenge material is received
- admission material is derived
- Nerve continues in stateless mode

The Mobile Vault must not remain open during normal use.

The Wasm runtime must not retain Vault material after admission derivation.

Short form:

The Vault opens for birth.

It closes before life.

---

## 17. Final Appearance Derivation

The mobile never identifies itself.

It produces a code of appearance.

Conceptual derivation:

surface_seed =
  H(
    local_surface,
    sol_admission_challenge,
    boot_nonce,
    admission_epoch,
    "NERVE_MOBILE_SURFACE_SEED_V1"
  )

nerve_admission_code =
  RotorMachine(
    surface_seed,
    origin_hint
  ).emit_code(
    mode = "nerve_admission",
    epoch = admission_epoch
  )

The admission code is:

- bounded
- non-portable
- non-reusable
- revocable
- not a key
- not an identity
- not a persistent token

---

## 18. Final Role Separation

Mobile Vault:
  keeps the scar.

Core / FLV / LUKS:
  keeps the truth.

Sol:
  challenges.

Rotor:
  transforms appearance material.

Nerve:
  answers.

Core:
  admits, ignores, or revokes.

---

## 19. Wasm/Vault Nerve Mobile Invariant

A Nerve Mobile may read a local Vault only during the boot/admission phase.

The Vault is opened briefly, used to load revocable continuity artifacts, and closed immediately.

Vault material must be zeroized after deriving admission material.

During normal operation, Nerve Mobile runs without an open Vault and without persistent WHISPER secrets in memory.

Final rule:

The Mobile Vault recognizes the nerve.

It never carries the brain.

