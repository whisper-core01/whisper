# WHISPER Threat Model v2.0

**Local-Sovereign, Wasm-Sandboxed, No External-Truth Architecture**

## 1. Scope

WHISPER is a sovereign communication and storage architecture designed to preserve confidentiality, integrity, local control, and operational resilience under hostile network conditions.

This threat model covers the following WHISPER components:

* local boot authority and pre-LUKS logic;
* Verve wake seed rotation;
* RotorMachine local derivation layer;
* HKDF-based key derivation;
* AEAD encryption for serious data;
* Vault storage;
* fragment generation and handling;
* channel/session material derivation;
* Wasm sandbox execution;
* external bearers such as Reticulum or other transport media.

This model explicitly separates:

> **transport from trust**
> **signal from authority**
> **external input from external truth**
> **local derivation from cryptographic encryption**

WHISPER does not import external truth into its security core.

---

## 2. Core Security Doctrine

WHISPER follows a local-sovereignty execution model.

All security-critical state, entropy derivation, validation, boot authority, and cryptographic authorization remain local.

External bearers may transport opaque packets, but they never validate, authorize, unlock, mint, derive, or define system state.

The RotorMachine is not used as a cryptographic cipher. It acts as a local sovereign derivation and structural diversification engine. Serious confidentiality and authentication rely on standard cryptographic primitives.

Canonical crypto path:

```text
local seed
+ internal state
+ session context
+ fragment context
+ cycle context
        ↓
RotorMachine
        ↓
internal key material
        ↓
HKDF-SHA-256
        ↓
ChaCha20-Poly1305 / XChaCha20-Poly1305 AEAD
        ↓
ciphertext + authentication tag
```

---

## 3. Explicit Non-Dependencies

WHISPER does not depend on:

* external RPC endpoints;
* bridges;
* third-party validators;
* cloud services;
* centralized servers;
* external oracles;
* external entropy feeds;
* GPS / GLONASS / satellite entropy;
* weather, tide, market, gold, or environmental feeds;
* external consensus systems;
* remote attestation as a root of trust;
* phone presence as a mandatory boot condition.

External systems may exist as optional bearers or convenience signals, but they are never part of the trusted computing base.

---

## 4. Trusted Computing Base

The trusted computing base is intentionally local and minimal.

The TCB includes:

* local machine state;
* local seed material;
* local user-controlled secrets;
* local Verve / pre-LUKS boot logic;
* local RotorMachine derivation logic;
* HKDF-SHA-256 implementation;
* ChaCha20-Poly1305 or XChaCha20-Poly1305 implementation;
* Wasm runtime isolation assumptions;
* local Vault integrity rules.

The TCB excludes:

* network providers;
* relays;
* transport peers;
* Reticulum nodes;
* phone connectivity;
* RPC endpoints;
* cloud infrastructure;
* external randomness;
* external validators.

---

## 5. Adversary Classes

### A0 — Passive Local Observer

The adversary can observe local metadata such as file sizes, access timing, process timing, or storage activity, but cannot modify execution or memory.

WHISPER objective:

* reduce direct structural leakage;
* enforce authenticated encryption;
* maintain local derivation separation;
* avoid plaintext persistence.

Not guaranteed:

* perfect protection against all side-channel timing observation.

---

### A1 — Passive Network Observer

The adversary can observe network traffic, including timing, packet sizes, packet frequency, routes, and bearer usage.

The adversary cannot decrypt payloads or modify packets.

WHISPER objective:

* expose only opaque encrypted packets;
* prevent transport from becoming authority;
* reduce correlation through fragmentation, scheduling, padding, and route diversity where available.

Not guaranteed:

* absolute anonymity against a global passive adversary;
* complete resistance to long-term traffic correlation.

---

### A2 — Active Network Adversary

The adversary can drop, delay, replay, reorder, inject, corrupt, or selectively block packets.

WHISPER objective:

* reject unauthenticated modifications;
* prevent corrupted packets from altering local state;
* treat external input as data, never authority;
* degrade availability rather than integrity.

Expected result:

```text
malicious packet → rejected
replayed packet → rejected or ignored
corrupted packet → authentication failure
missing bearer → degraded mode
```

---

### A3 — Compromised Bearer / Relay

The adversary controls a transport path, relay, Reticulum node, or network segment.

WHISPER objective:

* bearer compromise must not imply state compromise;
* bearer compromise must not imply cryptographic compromise;
* bearer compromise must not authorize session changes;
* bearer compromise must not unlock local secrets.

Core rule:

> External bearers carry opaque packets. They do not certify truth.

---

### A4 — Compromised Phone / Missing Phone

The adversary controls, clones, blocks, or removes the phone.

WHISPER objective:

* phone presence may be used as an optional signal;
* phone absence must not brick sovereign local boot;
* phone compromise must not provide sole authorization;
* phone must never act as a 1-of-1 validator.

Core rule:

```text
phone present     → useful signal
phone absent      → local degraded mode
phone compromised → degraded trust, never sole authority
```

---

### A5 — Malicious Fragment / Payload Injection

The adversary provides malformed fragments, corrupted payloads, replayed fragments, or adversarial metadata.

WHISPER objective:

* reject invalid AEAD tags;
* reject context mismatch;
* prevent malformed fragments from escaping sandbox boundaries;
* prevent parser-level faults from becoming global compromise.

Wasm isolation is used to reduce blast radius.

---

### A6 — Compromised Wasm Module

The adversary compromises or exploits a module running inside a Wasm sandbox.

WHISPER objective:

* contain execution within the sandbox;
* restrict filesystem access;
* restrict network access;
* restrict global authority;
* prevent direct access to host secrets;
* prevent module compromise from becoming system compromise.

Assumption:

The Wasm runtime correctly enforces memory and capability isolation.

Not guaranteed:

* protection against a fully compromised Wasm runtime;
* protection against host kernel compromise.

---

### A7 — Local User-Space Malware

The adversary executes malware in the user’s operating system after boot.

WHISPER objective:

* minimize plaintext exposure;
* zeroize sensitive buffers where practical;
* isolate sensitive logic;
* protect stored data with AEAD;
* avoid external dependency escalation.

Not guaranteed:

* full protection if the host OS can read process memory at runtime;
* full protection against keyloggers or screen capture malware.

---

### A8 — Host / Kernel Compromise

The adversary controls the host kernel, hypervisor, firmware, or physical memory during active execution.

This is outside the primary protection boundary.

WHISPER can still provide:

* encrypted-at-rest protection before compromise;
* compartmentalization;
* minimized external trust;
* reduced remote attack dependency.

Not guaranteed:

* confidentiality of live secrets against a fully compromised host;
* runtime integrity under hostile kernel control.

---

### A9 — Physical Attacker

The adversary has physical access to the device.

Variants:

* powered-off device;
* suspended device;
* powered-on unlocked device;
* hardware implant;
* evil maid attack.

WHISPER objective:

* protect powered-off data through LUKS / local boot authority;
* avoid dependence on remote unlock;
* rotate local wake/session material;
* invalidate old wake seeds after clean shutdown where implemented.

Not guaranteed:

* protection against all hardware implants;
* protection against live-memory extraction on an unlocked running system.

---

### A10 — Cryptographic Reviewer / Malicious Cryptanalyst

The adversary attempts to break WHISPER’s cryptographic claims.

WHISPER’s position:

* RotorMachine is not claimed to be a cipher;
* confidentiality relies on ChaCha20-Poly1305 or XChaCha20-Poly1305;
* authentication relies on AEAD tags;
* derivation normalization relies on HKDF-SHA-256;
* RotorMachine provides local derivation and structural diversification only.

Security claim:

> Breaking serious WHISPER ciphertext should require breaking the standard AEAD construction or compromising local secrets, not reverse-engineering the RotorMachine as a cipher.

---

## 6. Protected Assets

WHISPER protects:

* plaintext messages;
* Vault contents;
* fragments;
* fragment ordering;
* session keys;
* channel keys;
* wake seed material;
* local boot authority;
* internal routing context;
* structural transformation schedules;
* authenticated metadata;
* local state transitions.

---

## 7. Security Goals

### G1 — Confidentiality

Plaintext must not be exposed to external bearers, relays, network observers, or storage observers.

Serious data is encrypted with AEAD.

---

### G2 — Integrity

Modified ciphertext, tag, nonce, AAD, fragment, or context must fail authentication or be rejected.

---

### G3 — Local Sovereignty

No external infrastructure may define security-critical state.

---

### G4 — No External Entropy

WHISPER uses no external entropy sources.

All derivation material is local and sovereign.

---

### G5 — Context Separation

Different sessions, fragments, cycles, or states must derive different internal material and AEAD contexts.

---

### G6 — Nonce Discipline

Nonce reuse must be prevented under the tested derivation model.

---

### G7 — Sandboxed Execution

Sensitive or risky logic should run inside Wasm compartments with restricted capabilities.

---

### G8 — Degraded Mode Safety

Loss of bearer, phone, network, relay, or external connectivity must degrade availability, not integrity or sovereignty.

---

## 8. Explicit Non-Goals

WHISPER does not claim:

* perfect anonymity against a global passive adversary;
* resistance to all timing side channels;
* protection against a fully compromised host kernel;
* protection against malicious firmware;
* mathematical proof of RotorMachine pseudorandomness as a cipher;
* post-quantum confidentiality unless explicitly upgraded;
* immunity to all denial-of-service attacks;
* complete metadata elimination;
* trustless interoperability with arbitrary external protocols.

---

## 9. Failure Mode Classification

### Availability Failure

Examples:

* bearer unavailable;
* phone absent;
* relay unreachable;
* packet loss;
* route collapse.

Expected outcome:

```text
system degrades, queues, retries, or falls back
no external authority is granted
```

---

### Integrity Failure Attempt

Examples:

* tampered ciphertext;
* tampered tag;
* tampered AAD;
* replayed fragment;
* corrupted packet.

Expected outcome:

```text
authentication failure
packet rejected
state unchanged
```

---

### Confidentiality Failure Attempt

Examples:

* passive packet capture;
* stolen fragment;
* copied Vault entry;
* relay logging.

Expected outcome:

```text
opaque ciphertext only
no plaintext without local key material
```

---

### Sovereignty Failure Attempt

Examples:

* fake external signal;
* malicious phone ping;
* compromised bearer;
* fake relay state;
* bridge/RPC-style external truth injection.

Expected outcome:

```text
external input treated as data
no imported authority
no state transition without local validation
```

---

## 10. Aave / LayerZero Class Failure Exclusion

WHISPER is explicitly designed to avoid the failure class:

```text
external dependency
→ external truth accepted
→ internal state contamination
→ systemic collapse
```

Unlike cross-chain DeFi systems that may accept bridge-provided truth as protocol-valid state, WHISPER does not import external truth into its security core.

No external bridge, RPC, validator, oracle, bearer, phone, or relay can authorize state transitions alone.

Core rule:

> External input is data, never authority.

---

## 11. RotorMachine Doctrine

The RotorMachine is a local derivation and structural diversification engine.

It may produce:

* internal key material;
* rotation contexts;
* offsets;
* transformation schedules;
* fragment diversification material;
* session-specific structure.

It must not be used to:

* encrypt serious data directly;
* replace AEAD;
* replace HKDF;
* act as a custom cipher;
* authenticate data directly;
* define external truth.

Frozen doctrine:

```text
RotorMachine → HKDF-SHA-256 → ChaCha20-Poly1305 / XChaCha20-Poly1305
```

---

## 12. Validation Evidence

RotorMachine crypto doctrine v01 was validated through measured local stress tests.

Validation campaign:

```text
1K measured cycles:      passed
10K measured cycles:     passed
10K fuzz cycles:         passed
100K endurance cycles:   passed
1M soak cycles:          passed
```

Total validated cycles:

```text
1,121,000 cycles
```

Observed failures:

```text
0 failed cycles
0 material collisions
0 key collisions
0 nonce reuse
0 ciphertext collisions
0 accepted ciphertext tampering
0 accepted tag tampering
0 accepted AAD tampering
0 roundtrip failures
0 context separation failures
0 direct RotorMachine key usage
0 external dependency calls
```

1M soak performance:

```text
mean full cycle latency: 0.157191 ms
p95 full cycle latency:  0.165027 ms
p99 full cycle latency:  0.183082 ms
throughput:              6353.62 cycles/sec
```

Interpretation:

These tests do not prove cryptographic security in the mathematical sense. They validate implementation-level doctrine, context separation, nonce discipline, AEAD integrity behavior, absence of external dependency calls, and stability under large-scale local execution.

---

## 13. Residual Risks

Remaining risks include:

* host compromise;
* Wasm runtime vulnerabilities;
* implementation bugs outside the tested path;
* side-channel leakage;
* poor operational configuration;
* unsafe key storage;
* weak user secrets;
* denial-of-service;
* traffic correlation by powerful observers;
* future cryptanalytic advances against standard primitives.

---

## 14. Reviewer-Safe Security Claim

WHISPER claims the following:

> WHISPER minimizes external trust by keeping security-critical derivation, validation, boot authority, and state transitions local. External bearers transport opaque packets and never act as authorities. Serious cryptographic confidentiality and authentication rely on standard AEAD primitives and HKDF, while the RotorMachine provides local sovereign derivation and structural diversification. The current implementation doctrine has been validated over 1,121,000 measured local cycles without invariant failure.

WHISPER does not claim absolute security, perfect anonymity, or protection against fully compromised hosts.

---

## 15. Final Doctrine Statement

```text
WHISPER_SECURITY_CORE = LOCAL
EXTERNAL_INPUT = DATA_ONLY
EXTERNAL_TRUTH = REJECTED
ROTOR_MACHINE = DERIVATION_AND_DIVERSIFICATION_ONLY
AEAD = STANDARD_CRYPTOGRAPHIC_CONFIDENTIALITY_AND_AUTHENTICATION
WASM = SANDBOXED_EXECUTION_BOUNDARY
NO_EXTERNAL_ENTROPY = TRUE
NO_EXTERNAL_AUTHORITY = TRUE
```

Frozen conclusion:

```text
WHISPER_THREAT_MODEL_V2 = LOCAL_SOVEREIGN
WHISPER_THREAT_MODEL_V2 = NO_EXTERNAL_TRUTH
WHISPER_THREAT_MODEL_V2 = WASM_SANDBOXED
WHISPER_THREAT_MODEL_V2 = ROTOR_CRYPTO_DOCTRINE_V01_COMPATIBLE
```
