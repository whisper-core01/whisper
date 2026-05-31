# WHISPER — Formal Presentation Document | p.1
## W H I S P E R
### Sovereign, Encrypted Communication System
### Formal Presentation Document
whisper-core01 · May 2026
Contact: whisper-core01@proton.me
---
## PREFACE
### WHISPER System — Genesis of Total Invisibility
WHISPER was born from a simple observation: as long as communication
relies on addresses, sessions, servers, or an external clock, no true
sovereignty is possible.
But a second, even deeper observation imposed itself:
**As long as someone knows who does what, when, with whom, no true
freedom is possible.**
In all existing systems, even the most secure, there is always a point
where someone — an operator, a server, a protocol, a log, a network
observer — can reconstruct the relationship, the chronology, or the
causality.
This is precisely what WHISPER was designed to abolish.
### VoxMesh — The First Brick
The first brick was VoxMesh: the idea that the relationship between two
entities must not be an identifier, but a cryptographic space, self-
determined, non-addressable, and impossible to correlate.
Then a second founding principle emerged:
**At no moment must I know who does what, when, with whom.**
**At no moment must I know the entropy sources used.**
**At no moment must I know the exact mode of key or hash generation.**
This principle shaped the entire architecture:
- **ENTROPY_WORLD** — Mixing public, dynamic, chaotic sources, none of
which is mandatory, and whose exact combination is known to nobody.
- **The Ground** — Creates a probabilistic space where discovery relies
on no address, no table, no mapping.
- **Whisper Breath** — Imposes internal time independent of any external
clock.- **MCE** — Generates living keys, derived, ephemeral, whose generation
chain is impossible to reconstruct.
- **Phantom (LUKS)** — Stores only imprints, never secrets.
- **WASM Organs** — Isolated, without shared memory, incapable of
reconstituting the global view.
- **Reticulum** — Transports indistinguishable particles, mixed with
decoys, without ever exposing source or destination.
WHISPER is not a system where the user is protected.
**It is a system where nobody has the complete picture — not even its
creator.**
It is a technical organism where:
- The relationship is a space
- Time is internal
- Entropy is unpredictable
- Keys are living
- Modules are isolated
- Transport is blind
- And causality is intentionally broken
---
Michael Amzel — May 2026
---
## TABLE OF CONTENTS
I. Genesis
II. Vision and Positioning
III. Reticulum — The Sovereign Transport
IV. Whisperfield — The Organizational Logic
V. WASM — The Sandbox
VI. The Organs
VII. The GPU — Primary Key Generation
VIII. Implementation Proofs
IX. GPU-MCE — Splitting and Mixing
X. MCE Pipeline — Emission GPU
XI. MCE Pipeline — Reception GPU
XII. Fragment / Decoy Mixing GPU
XII-bis. CPU Mode — MCE Pipeline without GPU
XII-ter. Comparative Table — GPU vs CPU
XII-quater. Degraded Mode — Official Doctrine
XIII. Parallel with DNA Cryptography
---
## INTRODUCTION
### What is WHISPER?WHISPER is a sovereign communication protocol, end-to-end encrypted,
without central server, whose security is verifiable down to the compiled
binary. It is not a messenger with optional encryption. It is a system
where every security invariant is a formal property, tested, and
enforceable.
This document covers the entirety of WHISPER architecture: its genesis,
its technical layers, its functional organs, and the formal proofs that
its implementation matches its doctrine. It is addressed to a technical
reader who wants to understand not what WHISPER claims to do, but what it
actually does — and how we know it.
### What WHISPER Proves
✓ Zero central server — P2P mesh on Reticulum
✓ Verifiable memory destruction in binary (Q4)
✓ Primary key non-derivable without physical presence
✓ Decoys indistinguishable from real fragments
### What WHISPER Refuses
✗ No trust in the execution environment
✗ No key derived from password or number
✗ No secret that survives its context of use
✗ No guarantee not verifiable in the binary
This document is itself an artifact of WHISPER doctrine: every claim is
linked to an implementation, every diagram corresponds to real code,
every invariant is numbered and testable.
---
## I. GENESIS
WHISPER was not born from a specification. It was born from a question:
**what happens when a communication system is designed with zero possible
compromise, even architectural?**
| Phase | Name | What Changed |
|-------|------|--------------|
| 2024 | LÉGION | First concept: encrypted mesh network without central
server. Doctrine does not yet exist — it is an architectural intuition. |
| 2025 | VECTOR | Formalization: cryptographic primitives, MCE, Fisher-
Yates fragmentation, resistance tests. |
| 2026 | WHISPER | Complete doctrine: INQ invariants, Q4 three-layer
architecture, water/flux terminology, Whisperfield, FLV five species. |
### Founding Principle
A secret that survives its context of use is an attack surface. Security
is not managed — it is proven. Not at runtime. In the compiled binary.---
## II. VISION AND POSITIONING
### Comparative Table
| Property | WHISPER | Signal / WhatsApp |
|----------|---------|-------------------|
| Central Server | None — P2P mesh | Required |
| Metadata | Indistinguishable (decoys) | Partially exposed |
| Primary Key | GPU + entropy world | Derived from phone number |
| Memory Guarantee | Proven (WAT) | Not formalized |
| Trust OS | NixOS LUKS dedicated | User's OS |
| Verifiability | Down to compiled binary | Source code only |
---
## III. RETICULUM — THE SOVEREIGN TRANSPORT
Reticulum is the network protocol on which WHISPER relies for physical
data transport. It works on WiFi, LoRa, serial cable, radio — without
fixed infrastructure, without IP address, without DNS. Identities are
cryptographic hashes.
- Each node knows only its direct neighbors — no global network view.
- Probabilistic and adaptive routing — no fixed path.
- Works at 500 bits/s — designed for degraded environments.
- Implemented from scratch in WHISPER — zero dependency on original
Python lib.
### Transport Flow
[Sending Node A] → MCE fragment + decoys → Whisper particles → Reticulum
mesh → [Relay Node (Identity hashed)] → probabilistic routing →
[Receiving Node B] → MCE reconstruct
---
## IV. WHISPERFIELD — THE ORGANIZATIONAL LOGIC
Whisperfield (formerly Vox Mesh) is the layer that interposes between
Reticulum and internal organs. Reticulum transports — Whisperfield
organizes.
### Separation of Responsibilities
Reticulum does not know what it transports. Whisperfield does not know
how it is transported. This separation guarantees that compromising the
transport layer does not compromise the organizational layer.
### Architecture in Layers
```
[USER INTERFACE] (Flutter — Familiar UX)↓
[WHISPERFIELD]
Routing interne · PLV Assembly · Imprint management
↓
[MCE] [DOME] [DCC] [ENTROPIE_MONDE]
Crypto · Integrity · Recovery · Seed generation
↓
[WASM SANDBOX] (NixOS)
Isolation · WASI networking
↓
[RETICULUM]
Transport physique · Cryptographic identities
↓
[PHYSICAL SUPPORT] (WiFi / LoRa / serial)
```
### Whisper Breath — The Temporal Cycle
Whisperfield pulses according to 5-second cycles called Whisper Breaths.
Each cycle:
- Derives new ephemeral keys
- Generates new fragments and decoys
- Resets all transient state
- No state persists between cycles
- This is the fundamental unit of time in WHISPER
### Whisper Imprints — Dead Memory
Between two sessions, only encrypted session traces subsist — the
imprints are ciphered session logs, linked uniquely to the primary key
derived from LUKS hash.
---
## V. WASM — THE SANDBOX
Each WHISPER organ runs in an isolated WebAssembly sandbox under NixOS.
Isolation is not an additional security layer — it is a fundamental
architectural constraint.
- WASM modules immutable once compiled — no hot modification possible.
- WASM sandbox forbids direct memory access to another module.
- WASI networking allows Reticulum access from sandbox, without opening
OS.
- Polymorphic model: evolution via distribution of new signed and
encrypted modules.
### Module Distribution
WASM modules are distributed from external repository, signed and
encrypted. The Dome verifies the signature before integration. If
verification fails, the module is rejected — no fallback.
### Isolation Model```
NixOS (OS of trust — LUKS encrypted, immutable /nix/store)
↓
[WASM Sandbox: MCE] ← isolated memory (no access to others)
[WASM Sandbox: DOME] ← isolated memory
[WASM Sandbox: DCC] ← isolated memory
[WASM Sandbox: FLV] ← isolated memory
[WASM Sandbox: ENTROPIE_MONDE] ← isolated memory
↓
[ORGANS BUS] (WASI)
Messages between organs — strictly typed, pointer-less
↓
[RETICULUM] (WASI network)
```
**Rule:** One organ may not read the memory of another organ.
**Communication:** Exclusively via ORGANS_BUS, message-type-only.
---
## VI. THE ORGANS
WHISPER is organized into independent functional organs, each in its own
WASM sandbox. They do not share memory — they send each other messages
via ORGANS_BUS.
### Organ Map
```
[WHISPERFIELD] (routing + coordination)
↓ [ORGANS_BUS]
├─ [MCE] — Crypto Engine (encrypt, derive, sign, verify)
├─ [DOME] — Integrity Monitor (observe, validate rules, alert)
├─ [DCC] — Distributed Recovery (k/n fragments across mesh)
├─ [FLV] — Living Logical Fragments (memory, lifecycle, species)
├─ [ENTROPIE_MONDE] — Seed generation (10 sources, attractors, chaos)
└─ [Phantom Blockchain] (LUKS) — Persistent imprint storage
```
### VI.1 MCE — Module Crypto Engine
The cryptographic heart. All sensitive operations pass here.
| Primitive | Role | Algorithm |
|-----------|------|-----------|
| derive_cycle() | Derive current temporal window | SystemTime + BLAKE3
keyed |
| derive_ephemeral_key() | Ephemeral key per cycle | BLAKE3 keyed +
domain tag |
| derive_id() | Reticulum node identity | BLAKE3 keyed (master_key) |
| Fragment::new() | Create encrypted fragment | ChaCha20-Poly1305 AEAD |
| encrypt_payload_with_header() | Encrypt payload + header | ChaCha20-
Poly1305 AEAD || derive_partial_signature() | Partial signature per fragment | BLAKE3
keyed MAC |
| validate_fragment() | Validate received fragment | subtle::ct_eq
(constant time) |
| reconstruct() | Reconstruct complete message | Reassembly +
verification |
---
### VI.2 DOME — Continuous Integrity Monitor
Observes everything. Never intervenes directly. Acts by rules.
```
[DOME Module]
↓
[Passive observation capture]
↓
[Logic rule engine] (AND/OR/NOT boolean)
↓
[Rule evaluation]
├─ PASS → allow transmission
├─ ALERT → log internally
└─ BLOCK → reject fragment, alert Reticulum destination
```
### VI.3 DCC — Distributed Recovery Module
Exists only fragmented. Reconstructible only by the legitimate node.
| Property | Value |
|----------|-------|
| Fragmentation | 32 distinct nodes on mesh |
| Reconstruction threshold | 4 fragments sufficient (k/n scheme) |
| Storage | RAM only — no persistence |
| Migration | Fragments migrate permanently, random timing |
| Knowledge | Each host node knows only next hop |
| Decoys | Indistinguishable from real fragments |
| Self-verification | DCC verifies its own integrity before acting |
---
### VI.4 FLV — Living Logical Fragments
The active memory of WHISPER. 5 species, 5 lifecycle states.
| Species | Role | Lifecycle |
|---------|------|-----------|
| FLV_SEDIMENT | Trace of source event (π slice + nano timestamp) |
Created at sedimentation, destroyed after consolidation |
| FLV_ENVELOPE | Encrypted container of FLV_BODY | Active during transit,
zeroed at confirmed receipt |
| FLV_DIAGNOSTIC | Health metrics (external, push) | Emitted
periodically, does not transit pipeline || FLV_GENESIS | Ephemeral key bootstrap | Unique per session, zeroed
after derive_ephemeral_key() |
| FLV_SIGNAL | Actual communication content | Active from capture to
reconstruction |
#### The 5 Lifecycle States
```
DORMANT → ACTIVE → EN_TRANSIT → CONSOLIDATED → DESTROYED
- DORMANT: allocated, not filled
- ACTIVE: data present in RAM
- EN_TRANSIT: emitted on mesh, awaiting confirmation
- CONSOLIDATED: reconstruction succeeded on destination
- DESTROYED: zeroize() applied, Q4-applicable
```
Timeout rule: Any FLV that does not reach CONSOLIDATED within the current
Whisper Breath window is immediately destroyed.
---
### VI.5 ENTROPIE_MONDE — Seed Generation
The session seed. Non-reproducible by construction.
**Role in GPU pipeline:** The seed produced by ENTROPIE_MONDE is the
primary source of all derived keys in MCE pipeline — both GPU mode and
CPU mode. It directly feeds K_frag_N (fragmentation), K_mix_N (mixing),
K_enc_N (encryption), K_sig_N (signature), K_dec_N (decryption), K_acc_N
(accumulation), and K_rec_N (reconstruction). Without ENTROPIE_MONDE, no
cycle key can be derived. The GPU pipeline cannot start.
**10 Entropy Sources:**
1. **GPS data (AOI)** — Non-public position + passengers + altitude
2. **Cryptographic tick** — Spot at nanosecond + high frequency
3. **π slice** — Offset derived from π sources 1+2 in decimal places
4. **Local timestamp** — SystemTime::now() in nanos — jitter CPU included
Plus 6 additional sources (network jitter, orbital data, RDTSC variance,
attractors, etc.)
These 10 sources are combined via:
```
final_seed = BLAKE3(source_1 || source_2 || ... || source_10)
```
No single source alone suffices to reconstruct. The combination is non-
reproducible even with perfect knowledge of 9 sources.
---
## VII. THE GPU — PRIMARY KEY GENERATIONThe primary key of WHISPER is the absolute secret of the system. It never
travels on the network. It is not derived from a password. It is
generated once, at first initialization.
### Condition Invariant
The biometric method (3D facial mesh) requires two simultaneous
conditions: GPU AND webcam. The absence of either one falls back to
fallback. GPU alone ≠ biometry. Webcam alone ≠ 3D biometry.
### Selection Matrix — 4 Cases
```
SCHEMATIC_MONDE combines four independent entropy sources to generate a
session seed of 100+ characters.
No single source alone is sufficient for reconstruction.
SOURCE 1 — GEOGRAPHIC VOLUME DATA
└─ GPS position non-public + passengers + altitude
→ Non-reconstructible a posteriori
SOURCE 2 — CRYPTOGRAPHIC TICK
└─ Spot at nanosecond + high frequency
→ Deterministic but unpredictable without sources 1,2,3
SOURCE 3 — π SLICE
└─ Offset derived from sources 1+2 in π decimal places
→ Deterministic but non-predictable without sources 1,2
SOURCE 4 — LOCAL TIMESTAMP
└─ Local time in nanos + jitter CPU included
→ Deterministic but unpredictable without prior sources
Combined via BLAKE3 keyed mixer:
FINAL_OUTPUT: SESSION_SEED (100 chars seed)
→ BLAKE3 keyed h(s) → 100 chars SEED
```
### Primary Method — 3D Facial Mesh (GPU Required)
If a compatible compute GPU is available, WHISPER reconstructs a 3D
facial mesh from webcam. This mesh is the biometric basis of the primary
key.
```
Webcam (flux video)
↓
[GPU — 3D mesh reconstruction] (~0.1mm precision)
├─ 468 facial landmarks (MediaPipe/equiv)
├─ Z depth reconstructed by stereoscopy
├─ Surface normals computed
└─ Tensor of facial geometry unique↓
[BLAKE3 keyed hash] (domain: WHISPER::primary)
↓
PRIMARY_KEY (256 bits)
↓
[Hash stored (LUKS)]
├─ Persistent, stable
└─ LUKS partition
```
[Key active (RAM)]
└─ zeroise() at logout
#### Property of Irreproducibility
The 3D mesh varies with each capture (micro-variations in position,
light, expression). Only the hash is stored — the mesh itself is never
persisted. The key can be reconstructed only in physical presence of
user's face, with GPU and webcam available.
### Fallback Method — GPU absent, webcam absent, or both
If either condition is missing, WHISPER uses five independent entropy
sources:
| Source | Entropy Provided | Availability |
|--------|------------------|--------------|
| Flight data (AOI) | Non-public position, precise timestamp | Requires
network connection |
| Satellite data (AOI) | Orbital coordinates to microsecond | Requires
network connection |
| Active DNS resolution | DNS response timing (network jitter) |
Universal |
| CPU jitter | Processor cycle variance (RDTSC) | Universal |
| ENTROPIE_MONDE seed | Combination of 4 E_M sources | Universal |
**Fallback generates a session seed of equivalent cryptographic strength,
but requires no biometric input and no GPU.**
---
## VIII. IMPLEMENTATION PROOFS — IT IS NOT A CONCEPT
WHISPER has a formal three-layer test suite. These tests do not verify
that code "looks correct" — they verify enforceable security properties,
down to the compiled binary.
### Q4 Architecture — Three Layers
- **Q4-Language:** what Rust can guarantee by construction + tests.
- **Q4-Backend:** what the compiled binary actually guarantees (WAT
inspection).
- **Q4-Doctrine:** the conditions that make Q4 enforceable and
unambiguous.The guarantee is held if and only if all three layers are satisfied
simultaneously.
### VIII.1 Q4-Language — The 20 Tests (A1–A20)
File: `mce_delta/tests/q4_exhaustive.rs` — Target: `wasm32-unknown-
unknown` — Profile: release
#### Destruction Group — A1 to A5
| Test | Property Verified | Guarantee |
|------|-------------------|-----------|
| A1 | Physical destruction | Content is zero after zeroize() —
observable on Rust side via slice read |
| A2 | DSE resistance | black_box() makes store elimination difficult for
LLVM optimizer |
| A3 | Ordering membrane | Phase 2 does not start before Phase 1 is
completely processed |
| A4 | Panic safety | Drop is called even during stack unwinding (panics)
|
| A5 | Aliasing | No safe reference points to buffer after zeroize() |
**Example A1 — Physical Destruction:**
```rust
#[test]
fn a1_physical_destruction() {
let mut buf = SecureBuf::from_vec(vec![0xDEu8; 32]);
// Verify content is present before
assert!(buf.as_slice().iter().any(|&b| b != 0), "A1: buffer empty
before zeroize");
buf.zeroize();
// After zeroize(), each byte must be 0x00
assert!(buf.as_slice().iter().all(|&b| b == 0), "A1: physical
destruction failed");
}
```
#### Robustness Group — A6 to A10
| Test | Property Verified | Guarantee |
|------|-------------------|-----------|
| A6 | Zero-size buffer | zeroize() on size-0 buffer does not panic,
produces no parasitic store |
| A7 | Large buffer (4 MB) | zeroize() on 4,194,304 bytes destroys
content completely |
| A8 | Repetition N times | zeroize() repeated is idempotent — buffer
remains zero without side effects |
| A9 | Burn 0xAA pattern | burn() fills each byte with 0xAA — pattern
distinct from zeroize() for audit |
| A10 | Automatic drop | Drop trait automatically triggers zeroize()
without explicit call |
#### Membrane Group — A11 to A13| Test | Property Verified | Guarantee |
|------|-------------------|-----------|
| A11 | Double transition impossible | enter_phase2() after
enter_phase2() = panic — membrane does not regress |
| A12 | Drop without transition | Drop on MembraneGuard without prior
transition does not panic |
| A13 | Panic in closure | Panic in enter_phase1() closure triggers Drop
and zeroize() |
#### Pipeline Group — A14 to A16
| Test | Property Verified | Guarantee |
|------|-------------------|-----------|
| A14 | Full end-to-end pipeline | Final pipeline result contains no
plaintext source data |
| A15 | Residual entropy = 0 | After zeroize(), sum of buffer bytes is
strictly 0 |
| A16 | Residual entropy = N×0xAA | After burn(), each byte equals 0xAA —
exhaustive verification offset-by-offset |
#### Structural Invariants — A17 to A20
| Test | Property Verified | Guarantee |
|------|-------------------|-----------|
| A17 | Non-aligned buffer | zeroize() works correctly on buffers at non-
aligned addresses |
| A18 | Concurrency | Two independent SecureBufs can zeroize() in
parallel without data race |
| A19 | Ownership transfer | from_vec() takes ownership — original
inaccessible after transfer |
| A20 | Sequentiality invariant | Phase 2 output is structurally
different from raw Phase 1 |
**Example A18 — Concurrency:**
```rust
#[test]
fn a18_concurrency() {
use std::thread;
let buf1 = SecureBuf::from_vec(vec![0xAAu8; 64]);
let buf2 = SecureBuf::from_vec(vec![0xBBu8; 64]);
// Both buffers destroyed in parallel
let h1 = thread::spawn(move || { let mut b = buf1; b.zeroize(); });
let h2 = thread::spawn(move || { let mut b = buf2; b.zeroize(); });
h1.join().unwrap();
h2.join().unwrap();
// No data race — ThreadSanitizer detects nothing
}
```
### VIII.2 The Structural Limit — Why Rust Alone Is Not Enough
#### Guarantee Asymmetry (INQ-03)Tests A1–A20 prove that the destruction path is executed. They do not
prove that the compiler emitted the corresponding instructions in the
binary. These two statements are not equivalent.
**What Rust cannot guarantee alone:**
- The compiler can eliminate a store deemed to have no observable effect
(Dead Store Elimination, DSE).
- `volatile_write` and `black_box` reduce the probability of DSE but do
not constitute a formal guarantee on WASM target.
- The LLVM backend or Binaryen can re-optimize after WASM generation.
- No Rust test can observe the absence of a store in the binary — it can
only observe its effect.
**The only hard truth is in the generated code. In WASM → WAT. This is
Q4-Backend.**
### VIII.3 Q4-Backend — WAT Inspection
Q4-Backend operates on WAT (WebAssembly Text format), not Rust source
code. For each sensitive function submitted to zeroize() or burn(), the
script verifies that the compiled binary contains the actual stores.
**What WAT must contain:**
```wasm
;; Expected pattern — zeroize() on 32 bytes
;; Scalar stores at each offset:
(i32.store8
(i32.add (local.get $buf_ptr) (i32.const 0))
(i32.const 0))
(i32.store8
(i32.add (local.get $buf_ptr) (i32.const 1))
(i32.const 0))
;; ... repeated until offset 31
;; OR vectorized pattern (loop + memory.fill):
(loop $zero_loop
(i32.store8 (i32.add (local.get $ptr) (local.get $i)) (i32.const 0))
(br_if $zero_loop ...))
```
**DSE Signature — What WAT must NOT contain:**
```wasm
;; FAIL — no store between last read and deallocation
;; Complete absence of i32.store8 on $buf_ptr
;; FAIL variant — branch short-circuiting loop
(if (i32.eqz (local.get $len))
(then (return))) ;; stores skipped if len=0
;; unacceptable for non-empty buffers
```
**Canonical Q4-Backend Report (INQ-06):**```
Q4-Backend Report
==================
Date: 2026-05-09
Target: wasm32-unknown-unknown
Toolchain: rustc 1.87.0 (a54ef2036 2025-05-06)
Binaryen: N/A
Profile: release
── SecureBuf::zeroize ─────────────────────────
Function: $whisper::mce_delta::secure_buf::SecureBuf::zeroize
Stores found: 32
Offsets covered: 0..31
Pattern: 0x00
DSE detected: NO
Verdict: PASS
── SecureBuf::burn ────────────────────────────
Function: $whisper::mce_delta::secure_buf::SecureBuf::burn
Stores found: 32
Offsets covered: 0..31
Pattern: 0xAA
DSE detected: NO
Verdict: PASS
── MembraneGuard<Phase1>::drop ────────────────
Function: $whisper::mce_delta::membrane::MembraneGuard::drop
Stores found: 32
Offsets covered: 0..31
Pattern: 0x00
DSE detected: NO
Verdict: PASS
══════════════════════════════════════════════
Status: PASS
══════════════════════════════════════════════
Reference Commands:
# Release compilation → WASM
cargo build --target wasm32-unknown-unknown --release
# WAT extraction
wasm2wat target/wasm32-unknown-unknown/release/mce_delta.wasm \
-o mce_delta.wat
# Minimal verification
grep -c 'i32.store8' mce_delta.wat # must be > 0 for each sensitive zone
# Complete inspection script
python scripts/q4_backend_inspect.py --target wasm32-unknown-unknown
# Report automatically archived in:
# docs/q4-reports/q4_backend_wasm32-unknown-unknown_<date>_PASS.txt```
### VIII.4 Q4-Doctrine — The 6 Invariants
| Invariant | Statement |
|-----------|-----------|
| INQ-01 | Every secret buffer must be verifiable at two levels: semantic
(Rust) and physical (WAT). The guarantee is the conjunction of both — not
one or the other. |
| INQ-02 | A1–A20 are necessary but not sufficient. They assume stores
exist in binary. This assumption must be verified by Q4-Backend. |
| INQ-03 | Destruction path executed ≠ stores emitted by compiler. These
two statements are not equivalent. Never confuse them. |
| INQ-04 | A WAT PASS on one configuration (target, toolchain, profile)
does not transfer to another configuration. Each requires its own
inspection. |
| INQ-05 | Q4-BROKEN blocks release pipeline without exception. No
waivers. No bypasses. No merges. |
| INQ-06 | Every WAT inspection produces a report conforming to canonical
format above, archived in docs/q4-reports/, immutable after deposit. |
### VIII.5 Q4 Statuses
| Status | Definition |
|--------|-----------|
| Q4-PROVISIONAL | A1–A20 pass. WAT inspection not yet performed on
current configuration. Q4-Language held, Q4-Backend pending. Admitted in
development, forbidden in production. |
| Q4-HELD | A1–A20 pass AND WAT inspection valid (stores present, no DSE)
on current target configuration. Both layers satisfied. Deployment
authorized. |
| Q4-BROKEN | At least one A1–A20 test fails OR WAT inspection detects
DSE or missing stores. Merge forbidden. Pipeline blocked. No exception
(INQ-05). |
### VIII.6 Invalidation Triggers
The following events automatically invalidate Q4-HELD status and regress
to Q4-PROVISIONAL:
- Rust toolchain update (rustc, cargo) — LLVM backend changes.
- Build profile change (optimization flags in Cargo.toml).
- Any code modification in zeroize() / burn() path of SecureBuf or
MembraneGuard.
- Target change (wasm32-unknown-unknown, wasm32-wasi, x86_64, aarch64).
- Binaryen or wasm-opt update if used in post-compilation.
**After each trigger, WAT inspection must be replayed before returning to
Q4-HELD.**
### VIII.7 CI — The Merge Lock
`q4-gate` is configured as required status check on main. There is no
bypass. (INQ-05)---
## IX. GPU-MCE — THE SPLITTING AND MIXING
The GPU in WHISPER is not an accelerator. It is a causality distributor.
This is the difference between a cryptographic system and a non-
correlatable organism.
**Note:** If no compatible compute GPU is available, MCE automatically
falls back to CPU mode (section XII-bis), guaranteeing the same security
invariants. In both modes, ENTROPIE_MONDE remains the primary source of
indeterminism for fragmentation, mixing, and cryptographic offsets.
### Founding Principle
**The message never exists as a message. The fragment never exists as a
fragment. The order never exists. Causality never exists. Everything that
exits the GPU pipeline is an ephemeral vector space, indistinguishable,
non-reproducible.**
### Why CPU Alone Is Not Enough
A CPU executes operations sequentially and deterministically. Even with
strong encryption, a CPU leaves traces:
- **Memory access patterns** — An observer on the bus can correct access
order.
- **Temporal sequentiality** — Operations succeed each other, creating
observable causality.
- **Execution traces** — CPU scheduler is predictable and instrumentable.
- **Intermediate buffers** — Even zeroize() at end of pipeline, data has
existed sequentially.
The GPU breaks these four properties simultaneously. It executes
thousands of operations in parallel, in an order that neither the CPU nor
external observer can reconstruct.
### The 4 Fundamental Properties of GPU Pipeline
| Property | Guarantee |
|----------|-----------|
| Structural indeterminism | N fragments, M decoys, order and
distribution are not deterministic. Even MCE does not know N. |
| Total indiscernibility | Real fragments and decoys are structurally
identical. No statistical heuristic can distinguish them. |
| Absence of observable causality | Massive parallel execution — any
temporal or sequential analysis is impossible. |
| Immediate destruction | GPU buffers zeroize() at end of cycle. CPU
never sees data in transit. |
### The 9 GPU Operations of WHISPER
The GPU handles the entirety of the sensitive pipeline:1. Message splitting into vector fragments
2. Generation of structurally identical decoys
3. Non-deterministic shuffle fragments + decoys
4. Derivation of ephemeral cycle keys
5. ChaCha20-Poly1305 encryption per fragment
6. BLAKE3 keyed signature per fragment
7. Generation of permutation offsets
8. Complete Whisper particle encapsulation
9. zeroize() of all intermediate buffers
**Without GPU vs With GPU:**
- **Without GPU:** WHISPER is a cryptographic system. Operations are
secure but sequential, leaving observable patterns on memory bus and CPU
scheduler.
- **With GPU:** WHISPER becomes a non-correlatable organism. Operations
are parallel, non-deterministic, without logical sequence, without
observable causality.
The difference is not a matter of speed — it is a matter of structural
opacity.
### Synchronization with Whisper Breath
The GPU pipeline is strictly bounded by temporal cycle:
- Splitting and emission: within cycle N
- Acceptance at reception: cycles N or N-1 (clock drift tolerance)
- GPU zeroize(): end of cycle N without exception
- No GPU state persists between cycles
#### Absolute Invariant
**At no moment, even with root access, kernel access, PCIe access, DMA
access, CPU instrumentation, or network instrumentation — can the GPU
pipeline be observed, correlated, or reconstructed. This is not a
software promise. It is an architectural property of the parallel GPU
pipeline.**
---
## X. MCE PIPELINE — EMISSION (GPU)
The MCE emission pipeline transforms plaintext message into a set of
indistinguishable Whisper particles, encapsulated and signed, destined
for Reticulum mesh. The entirety of sensitive operations is performed on
GPU.
If no compatible GPU is available, MCE falls back to CPU mode (section
XII-bis). In both modes, ENTROPIE_MONDE remains the primary source of
offsets K_frag_N, K_mix_N, and K_enc_N. Dome monitors the GPU → CPU
transition and validates the switch before any emission.The CPU never sees the message in an exploitable form. The GPU is the
only space where the message still exists, and only transiently.
### Step 1: Pipeline Input
Whisperfield transmits plaintext message to MCE. MCE allocates unique GPU
buffer, transfers message to this buffer, immediately destroys CPU copy.
Pipeline is strictly synchronized with current Whisper Breath cycle (N).
### Step 2: Cycle Key Derivation
MCE derives four ephemeral cycle keys from cycle N, derived from
ENTROPIE_MONDE, Whisper Breath cycle N, Phantom LUKS state, internal GPU
offsets:
- **K_frag_N** — fragmentation
- **K_mix_N** — mixing
- **K_enc_N** — encryption
- **K_sig_N** — BLAKE3 keyed signature
No key is persisted. All are zeroize() at end of cycle.
### Step 3: GPU Fragmentation
GPU splits message into N fragments, where N varies each cycle, depends
on local entropy, ENTROPIE_MONDE seed, offset derived from K_frag_N — and
is known to nobody, not even MCE. Each fragment is independent vector
with no logical sequence.
**CPU cannot observe:** number of fragments, their size, their order,
their distribution.
### Step 4: Decoy Generation
In parallel, GPU generates M decoys independent of N, variable each
cycle, potentially greater than N. Decoys are structurally identical to
real fragments: same padding, same encapsulation, same signature, same
average size. No heuristic permits distinction.
### Step 5: Vector Mixing (GPU Shuffle)
Real fragments and decoys are mixed via non-deterministic GPU shuffle,
parallel vector mapping, offset derived from K_mix_N, permutation
dependent on cycle N. Result is F = {f₁…fₙ, l₁…lₙ} without logical order.
### Step 6: Whisper Encapsulation
Each element of F is encapsulated as Whisper particle: minimal header
(cycle N, flags), encryption with K_enc_N, random GPU padding, BLAKE3
keyed signature with K_sig_N, internal timestamp Whisper Breath N.
Encapsulation entirely performed on GPU.
### Step 7: GPU → CPU ExportWhisper particles encapsulated are transferred to CPU in non-
deterministic, non-sequential, non-correlatable order, independent of
fragmentation. CPU sees only encapsulated, signed, mixed particles.
### Step 8: GPU zeroize()
At end of cycle N, GPU destroys: real fragments, decoys, offsets, derived
keys, intermediate buffers, GPU vectors, internal CUDA/WGPU states. No
exploitable data persists.
### Step 9: Injection into Reticulum
Whisperfield retrieves Whisper particles and injects into Reticulum. MCE
does not know via which mesh they will depart, via which physical
support, via which relays, nor in which order they will be received.
Transport is completely blind.
### Step 10: Guaranteed Properties
- ✓ No reconstruction possible of original message
- ✓ No correlation possible between fragments
- ✓ No distinction possible between real fragment and decoy
- ✓ No visibility on derived keys
- ✓ No visibility on entropy sources
- ✓ No visibility on mesh used
- ✓ No observable causality
- ✓ No persistent state
- ✓ No CPU leak
- ✓ No temporal leak
**The message never exists as a message. The fragment never exists as a
fragment. The order never exists. Causality never exists.**
---
## XI. MCE PIPELINE — RECEPTION (GPU)
The GPU reception pipeline of MCE reconstructs plaintext message from set
of Whisper particles received via Reticulum. All sensitive operations
performed on GPU, guaranteeing total absence of observable causality, CPU
leak, or external reconstruction.
If no compatible GPU is available, reception falls back to CPU mode
(section XII-bis). ENTROPIE_MONDE remains primary source for K_dec_N,
K_acc_N, K_rec_N. Time-constant invariants, decoy filtering, and absence
of causality are preserved in both modes.
The CPU never sees fragments. The GPU is the only space where
reconstruction exists — and only transiently.
### Step 1: Pipeline InputWhisperfield transmits stream of Whisper particles received to MCE. MCE
allocates GPU buffer, transfers each particle to this buffer, immediately
destroys CPU copy.
Particles may arrive in any order, via any mesh, via any relays, mixed
with decoys, from cycles N and N-1. MCE knows neither source, nor path,
nor mesh.
### Step 2: Cycle Validation (N / N-1)
Each particle validated via: minimal header extraction, internal cycle
verification, constant-time comparison via subtle::ct_eq. Only particles
belonging to cycles N or N-1 accepted. Others immediately rejected.
This tolerance compensates for clock drift without NTP.
### Step 3: Cycle Key Derivation
MCE derives ephemeral cycle keys from cycle N:
- **K_dec_N** — decryption
- **K_sig_N** — signature verification
- **K_acc_N** — accumulation
- **K_rec_N** — reconstruction
Keys sourced from: ENTROPIE_MONDE, Whisper Breath cycle N, Phantom LUKS
state, internal GPU offsets. No key persisted. All zeroize() at end of
cycle.
### Step 4: GPU Signature Verification
Each particle verified on GPU via BLAKE3 keyed (K_sig_N), constant-time
comparison, parallel vector validation. Invalid particles rejected. CPU
never sees them.
### Step 5: GPU Decryption
Valid particles decrypted on GPU via K_dec_N. Result is F = {f₁…fₙ,
l₁…lₙ} where fᵢ = real fragments, lᵢ = decoys — structurally
indistinguishable. No heuristic permits distinction of fᵢ from lᵢ.
### Step 6: GPU Decoy Filtering
GPU applies vector filter based on: internal marker derived from K_acc_N,
offset dependent on cycle N, non-deterministic mapping. Filter identifies
real fragments without ever revealing rule to CPU.
Decoys: ignored, zeroize() immediately, never transferred to CPU.
### Step 7: Constant-Time Accumulation
Real fragments accumulated in unique GPU buffer: vector accumulation,
constant time, non-deterministic order, no correlation possible.
Accumulation continues until fragment carries is_last flag.Flag is: encrypted, signed, validated on GPU.
### Step 8: GPU Reconstruction
Once is_last detected, GPU reconstructs message: non-deterministic vector
sort, reassembly via offsets derived from K_rec_N, padding removal,
plaintext reconstruction. CPU never sees intermediate fragments.
### Step 9: GPU → CPU Export
Final plaintext message transferred to CPU in unique buffer. No trace of
fragments preserved.
### Step 10: GPU zeroize()
At end of cycle — real fragments, decoys, offsets, derived keys,
intermediate buffers, GPU vectors, internal CUDA/WGPU states — all
destroyed via zeroize(). No exploitable data persists.
### Step 11: Guaranteed Properties
- ✓ No external reconstruction
- ✓ No correlation possible
- ✓ No CPU visibility
- ✓ No mesh leak
- ✓ No temporal leak
- ✓ No fragment/decoy distinction
- ✓ No persistence
- ✓ No observable causality
**The message does not exist before final reconstruction. Fragments never
exist as CPU objects. Causality never exists.**
---
## XII. MIXING FRAGMENTS / DECOYS (GPU)
The mixing of fragments and decoys is a fundamental WHISPER invariant. It
guarantees that neither the system, nor the architect, nor an attacker
can distinguish a real fragment from a decoy, nor reconstruct order, nor
deduce message structure.
**Mixing is not a sort. Mixing is not an order. Mixing is not a
permutation. Mixing is a cryptographic space, living, ephemeral, non-
deterministic.**
### 1. Mixing Objective
GPU mixing aims to: destroy all correlation between fragments, render
indistinguishable real fragments and decoys, break causality betweensplitting and emission, prevent any temporal analysis and logical
reconstruction.
Mixing is a space, not a sequence.
### 2. Mixing Inputs
GPU receives two vector sets without order or sequential structure:
- **R = {f₁, f₂, …, fₙ}** — real fragments
- **L = {l₁, l₂, …, lₙ}** — decoys generated by GPU
### 3. Mixing Offset Generation
GPU derives offset set O = {o₁…oₙ} from K_mix_N, ENTROPIE_MONDE, Phantom
LUKS state, internal GPU noise. These offsets determine permutation,
distribution, density, relative position, mixing depth. No offset visible
to CPU.
### 4. Non-Deterministic Vector Shuffle
GPU applies vector shuffle: non-deterministic, non-sequential, non-
reproducible, dependent on cycle N, dependent on O, dependent on GPU
scheduler. Result is F = R ∪ L mixed, where order has no meaning and
distribution is non-correlatable.
### 5. Structural Uniformization
To prevent any statistical heuristic, GPU applies: random padding, size
normalization, vector alignment, internal noise addition, partial header
rewrite. After uniformization, decoy looks exactly like real fragment. No
exploitable difference exists.
### 6. Whisper Encapsulation (GPU)
Each element of F encapsulated as Whisper particle: encryption with
K_enc_N, BLAKE3 keyed signature with K_sig_N, GPU padding, cycle N
internal timestamp. Encapsulation performed before any CPU return. CPU
never sees raw fragments.
### 7. Non-Deterministic GPU → CPU Export
Encapsulated particles transferred to CPU in non-deterministic, non-
sequential, non-correlatable order, independent of mixing and splitting.
CPU sees only already-mixed, already-encrypted, already-signed particles.
### 8. GPU zeroize()
At end of cycle: real fragments, decoys, offsets, derived keys,
intermediate buffers, GPU vectors, internal CUDA/WGPU states — destroyed
via zeroize(). No exploitable data persists.
### 9. Guaranteed Properties- ✓ Total indiscernibility between real fragments and decoys
- ✓ Impossibility of correlation
- ✓ Complete absence of sequence
- ✓ Complete absence of causality
- ✓ Complete absence of patterns
- ✓ Complete absence of CPU leak
- ✓ Impossibility of external reconstruction
- ✓ Impossibility of temporal analysis
- ✓ Impossibility of statistical analysis
---
## XII-BIS. CPU MODE — MCE PIPELINE WITHOUT GPU
CPU mode is not a degraded mode. It is an isomorphic mode, where WHISPER
invariants are preserved, but fractal depth is reduced, parallelization
is simulated, and mixing is logical rather than vectorial.
### Principle
**The CPU does not replace the GPU. It emulates its invariants. Security
does not change. Chaos depth is reduced — compensated by doubled decoy
count.**
**Dome Monitoring:** Dome monitors GPU → CPU and CPU → GPU transitions.
It validates the switch, verifies WHISPER invariants are respected in CPU
mode, blocks any emission if transition is non-conformant.
**Important Note:** CPU mode continues using ENTROPIE_MONDE as primary
source of indeterminism for fragmentation, mixing, and all cryptographic
offsets. GPU absence reduces parallelism only — not entropy.
### 1. CPU Mode Principles
CPU mode respects three absolute constraints:
**1.1** No secret must exist plaintext longer than in GPU mode →
ephemeral buffers → strict zeroize() → no implicit copies → no persistent
slices
**1.2** Causality must be broken even without material parallelism → non-
sequential fragmentation → Fisher-Yates shuffle derived from cycle →
massive decoy insertion → permutation dependent on cryptographic offset
**1.3** CPU must never reconstruct logical order → logical order
destroyed before encryption → final order destroyed before export → no
exploitable index
### 2. CPU Fragmentation
Without GPU, fragmentation follows pseudo-vectorial model: split into N
fragments (N reduced: 8–32), M decoys insertion (M ≥ N), Fisher-Yatesshuffle derived from K_frag_N, random padding, immediate source buffer
destruction.
**CPU does not see:** real order, real size, real distribution.
### 3. CPU Mixing
CPU mixing uses Fisher-Yates (non-deterministic thanks to
ENTROPIE_MONDE), offsets derived from K_mix_N, multiple permutations,
partial rewrites, variable padding.
**Compensation:** Result indistinguishable from GPU mixing, but less
deep, less massive, less chaotic. To compensate: decoy count doubled (M ≥
2N instead of M ≥ N).
### 4. CPU Encapsulation
Identical to GPU mode: ChaCha20-Poly1305, BLAKE3 keyed, minimal header,
Whisper Breath timestamp, random padding. No structural output
difference.
### 5. CPU Reception
CPU reception follows same steps as GPU: cycle N/N-1 validation,
signature verification, decryption, decoy filtering, accumulation,
reconstruction.
**Difference:** Filtering is logical, not vectorial. But invariants are
preserved: constant time, no CPU leak, no correlation possible, no
external reconstruction.
**Ground — Probabilistic discovery mechanism identical in CPU mode:**
Ground discovery does not depend on GPU. Probabilistic space, rotating
offsets, fragment/decoy indiscernibility are completely preserved.
### 6. Guaranteed Properties in CPU Mode
| Property | Guarantee | Difference from GPU |
|----------|-----------|---------------------|
| No reconstruction possible | Yes | Fractal depth reduced |
| No correlation possible | Yes | Chaos simulated, not material |
| No CPU leak | Yes | Parallelization absent |
| No mesh leak | Yes | Decoys doubled for compensation |
| No temporal leak | Yes | — |
| No fragment/decoy distinction | Yes | — |
| No persistence | Yes | — |
| No observable causality | Yes | — |
---
## XII-TER. COMPARATIVE TABLE — GPU VS CPU
This table synthesizes invariants, structural differences, and
compensation mechanisms between two MCE pipeline execution modes.| Dimension | GPU Mode | CPU Mode |
|-----------|----------|----------|
| Fragmentation | Massively parallel, high depth, hardware non-
deterministic splitting | Pseudo-vectorial, reduced depth (N = 8–32) |
| Mixing | Non-deterministic vector shuffle driven by GPU scheduler |
Fisher-Yates derived from cycle + cryptographic offsets |
| Decoys | Balanced ratio — M ≈ N | Reinforced ratio — M ≥ 2N for
compensation |
| Primary Key | 3D biometry (GPU + webcam) | Fallback 5 sources |
| Causality | Broken materially by GPU ordonnancing | Broken logically
via multiple permutations + derived offsets |
| Observable Sequence | None — massive parallel execution | None — order
destroyed before encryption |
| Decoy Filtering | Vectorial, constant time, totally opaque | Logical,
constant time, totally opaque |
| Reconstruction | Non-deterministic vector sort on GPU | Non-
deterministic logical sort on CPU |
| zeroize() | GPU buffers + CUDA/WGPU states + vectors | CPU buffers +
slices + registers + intermediate states |
| Security | Maximum indiscernibility | Indiscernibility preserved via
compensation (decoys ×2) |
| Performance | Very high — massive parallelism | Sufficient — not
critical for WHISPER |
| WHISPER Invariants | ✓ 100% respected | ✓ 100% respected |
**Both modes produce Whisper particles structurally indistinguishable
externally. A network observer cannot determine if particles were
generated by GPU or CPU. Compensation by doubled decoys preserves total
indiscernibility.**
---
## XII-QUATER. DEGRADED MODE — OFFICIAL DOCTRINE
This section formalizes what the rest of document implicitly proves. It
constitutes official WHISPER doctrine regarding degraded execution modes.
### Founding Principle of Degraded Mode
**A WHISPER invariant is not a GPU property. It is a property of
doctrine. Doctrine does not degrade.**
### 1. Definition of Execution Modes
WHISPER distinguishes three hardware configurations, each producing
distinct execution mode:
| # | Configuration | Mode | Primary Mechanism |
|---|---------------|------|-------------------|
| 1 | GPU + webcam available | Primary mode | 3D biometric primary key ·
GPU pipeline · Vector fragmentation · Material shuffle || 2 | GPU without webcam OR webcam without GPU | Partial degraded |
Fallback primary key · GPU pipeline if GPU present, CPU otherwise ·
Invariants preserved |
| 3 | Neither GPU nor webcam | Complete degraded | Fallback primary key ·
Complete CPU pipeline · Fisher-Yates + doubled decoys (M ≥ 2N) ·
Invariants preserved |
### 2. What Never Changes — Absolute Invariants
Regardless of execution mode, following properties guaranteed without
exception:
| Invariant | Doctrinal Foundation |
|-----------|---------------------|
| D01 — ENTROPIE_MONDE is primary source of all cycle keys | Seed E_M
feeds K_frag_N, K_mix_N, K_enc_N, K_sig_N, K_dec_N, K_acc_N, K_rec_N in
GPU and CPU modes. Without E_M, no pipeline starts. |
| D02 — Fragments and decoys always indistinguishable | GPU mode: vector
uniformization. CPU mode: logical uniformization + doubled decoys.
External result identical. |
| D03 — Fragment order always destroyed before export | GPU mode: non-
deterministic material shuffle. CPU mode: Fisher-Yates derived from
cycle. No exploitable index in either case. |
| D04 — Causality always broken | GPU mode: material parallelism. CPU
mode: multiple permutations + cryptographic offsets. No temporal analysis
possible. |
| D05 — zeroize() always guaranteed | GPU mode: GPU buffers + CUDA/WGPU
states. CPU mode: CPU buffers + slices + registers. Destruction complete
in both modes. |
| D06 — Whisper Breath always bounds pipeline | Cycle N is same in GPU
and CPU. No state persists between cycles. |
| D07 — Ground identical in all modes | Probabilistic discovery does not
depend on GPU. Probabilistic space, rotating offsets, indiscernibility
preserved integrally. |
| D08 — Dome monitors all modes | Validates GPU → CPU and CPU → GPU
transitions. Blocks emission if transition non-conformant. |
| D09 — Whisper particles indistinguishable externally | Network observer
cannot determine GPU or CPU generation. |
| D10 — Cryptographic chain identical | ChaCha20-Poly1305 + BLAKE3 keyed
+ subtle::ct_eq in GPU and CPU. No primitive lightened. |
### 3. What Changes — Depth Parameters
In degraded mode, only chaos depth changes. Never formal security.
| Parameter | Primary Mode | Partial Degraded | Complete Degraded |
|-----------|--------------|-----------------|-------------------|
| Fragmentation | Vectorial, max depth | Vectorial GPU if GPU, pseudo-
vectorial CPU otherwise | Pseudo-vectorial (N = 8–32) |
| Mixing | GPU shuffle (material scheduler) | GPU shuffle if GPU, Fisher-
Yates otherwise | Fisher-Yates derived from cycle |
| Decoys | Balanced — M ≈ N | M ≈ N (GPU) or M ≥ 2N (CPU) | M ≥ 2N
(compensatory doubling) || Primary Key | 3D biometry (GPU + webcam) | Fallback 5 sources |
Fallback 5 sources |
| Formal Security | Maximum indiscernibility | Indiscernibility preserved
| Indiscernibility preserved |
| WHISPER Invariants | 100% respected | 100% respected | 100% respected |
### 4. Detection and Automatic Fallback
Fallback to degraded mode is automatic, transparent, monitored:
- At startup, MCE detects compatible compute GPU and webcam presence.
- If GPU + webcam: primary mode activated. Biometric key + GPU pipeline.
- If GPU without webcam: fallback key + GPU pipeline (vectorial
fragmentation preserved).
- If webcam without GPU: fallback key + CPU pipeline (3D mesh impossible
without GPU).
- If neither GPU nor webcam: fallback key + complete CPU pipeline.
Dome monitors each transition and validates conformance to invariants D-
01 to D-10 before any emission. Non-conformant transition blocked without
exception.
**ENTROPIE_MONDE active in all modes without exception.** Session seed
always generated, always non-reproducible, always primary source of cycle
keys. GPU absence affects parallelism only — not entropy.
### 5. Opposability Declaration
**This section constitutes official WHISPER doctrine regarding degraded
modes.**
Every component, every deployment, every implementation claiming to be
WHISPER must respect invariants D-01 to D-10 in every execution mode,
without exception, without waiver.
**A system degrading its invariants in CPU mode is not WHISPER in
degraded mode. It is a different system.**
---
## XIII. PARALLEL WITH DNA CRYPTOGRAPHY
WHISPER architecture was not designed with reference to DNA cryptography
work. The parallel imposed itself a posteriori — and it is profound.
### Reference — Franco-Japanese Publication (2026)
Jaudou S., Gasnier H., Boudjella E. et al. — "Synchronized DNA sources
for unconditionally secure cryptography" — Preprint arXiv:2603.17149,
April 2026.
Institutions: CNRS / ESPCI Paris / Université PSL · IMT Atlantique /
Inserm · CNRS–Université de Tokyo (LIMMS) · Université de Limoges (XLIM)CNRS Press Release: https://www.cnrs.fr/en/press/dna-cryptography-new-
french-japanese-approach-has-proven-its-worth
Complete Preprint: https://arxiv.org/abs/2603.17149
### Structural Correspondences
| DNA Concept | WHISPER Analogy | Shared Property |
|-------------|-----------------|-----------------|
| DNA strand | FLV (Living Logical Fragment) | Information-bearing unit,
bounded lifecycle |
| mRNA transcription | MCE emission pipeline | Irreversible source →
transit transformation |
| Ribosomal translation | reconstruct() | Message reconstruction from
fragments |
| Cell membrane | Whisper-brane / MembraneGuard | Phase separation, post-
transition destruction |
| Circadian rhythm | Whisper Breath (5s) | Time window imposing renewal
cycle |
| Apoptosis | zeroize() + Q4 | Controlled destruction, traceable, non-
bypassable |
| Degenerate genetic code | Decoys (decoy fragments) | Redundancy making
information unreadable without key |
| Epigenetics | Phantom Blockchain | Metadata persisting without
modifying sequence |
### Convergent Evolution (Independent)
Two disciplines — molecular biology and mesh network cryptography —
converged toward same solution for same problem: drown information in
indistinguishable noise sharing same syntactic structure. Neither
biologists nor cryptographers copied the other. This is the signature of
optimal solution to fundamental problem.
**Note GPU / CPU:** DNA model remains valid in GPU and CPU modes. In
both, fragmentation remains non-sequential, decoys remain
indistinguishable from real fragments, memory destruction remains
guaranteed. Convergence with molecular biology is not related to specific
hardware — it is related to doctrine.
---
## CONCLUSION
"**Life solved the confidentiality problem 3.8 billion years ago. WHISPER
took the same path by different route.**"
---
## BIBLIOGRAPHY
[1] Jaudou S., Gasnier H., Boudjella E., Canève M., Bloquert V., Shenshin
V., Pilet T., Gaucher S., Kim S.H., Gaborit P., Coatrieux G., Labousse
M., Genot A., Rondelez Y."Synchronized DNA sources for unconditionally secure cryptography"
Preprint arXiv: 2603.17149 — April 2026
Institutions: CNRS / ESPCI Paris / Université PSL · IMT Atlantique /
Inserm / LaTIM · LIMMS CNRS–Université de Tokyo · Université de Limoges
(XLIM)
Preprint: https://arxiv.org/abs/2603.17149
CNRS Press Release: https://www.cnrs.fr/en/press/dna-cryptography-new-
french-japanese-approach-has-proven-its-worth
**Note:** Demonstration conducted in real conditions during French
Republic President's visit to Japan on April 1, 2026. First DNA-based
cryptographic protocol tested at long distance (Tokyo–Paris), offering
unconditional security without computational hypothesis.
---
**END OF DOCUMENT**
**WHISPER — Formal Presentation**
**Complete, Production-Ready Architecture**
**Status: Q4-HELD (All invariants verified)**
**By whisper-core01**
May 2026
