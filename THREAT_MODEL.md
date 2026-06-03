# THREAT_MODEL.md — Whisper Remote Nerve MVP v0.4.3

## 1. Status

Whisper Remote Nerve v0.4.3 is an experimental MVP architecture skeleton.

It is not a validated secure communication protocol.

The current implementation demonstrates a tested end-to-end pipeline composed of deterministic fragment transformation, state evolution, basic filtering, anomaly detection, metadata persistence, bridge encapsulation, and integration tests.

Current validation status:

```text
Full test suite:       104 passed
Regression suite:      9 passed
FullPipeline smoke:    OK
FullPipeline benchmark OK
```

Reference MVP benchmark:

```text
Payload size:       1,048,576 bytes
Fragment count:     1024
Elapsed:            ~0.77 s
Throughput:         ~1.30 MB/s
Blocked reports:    0 for clean benchmark payload
```

These tests validate functional coherence, determinism, roundtrip behavior, and regression stability. They do not validate anonymity, metadata confidentiality, adversarial routing resilience, or transport security.

---

## 2. Security posture

The current MVP must be described as:

```text
tested architecture skeleton
experimental defensive pipeline
pre-specification implementation
```

It must not be described as:

```text
secure communication protocol
anonymous network
validated metadata-protection system
production-ready transport
cryptographic protocol
Reticulum implementation
```

The project currently provides implementation evidence that the proposed architecture can be assembled and tested. It does not yet provide empirical evidence that the architecture resists realistic network adversaries.

---

## 3. System components

Current MVP components:

```text
RotorMachine      deterministic reversible fragment transformation
MCE               state evolution
MCEHardened       state validation and coherence checks
Loader            fragmentation / route / retry decisions
BAL               in-memory parallel lanes
Dome              filtering and reversible envelope
VoxMesh           36-fractal state-divergence skeleton
Lemonade          anomaly / immune-system skeleton
Vault             in-memory metadata store
VaultDisk         JSON metadata persistence
ReticulumBridge   simple bridge encapsulation skeleton
FullPipeline      end-to-end MVP integration
```

Current pipeline:

```text
payload
  -> Loader
  -> fragment_payload()
  -> Dome wrap/filter
  -> BAL distribute/collect
  -> MCEHardened digest checked
  -> Lemonade stateless scan
  -> ReticulumBridge encapsulation
  -> Vault metadata storage
  -> optional VaultDisk persistence
```

---

## 4. Assets

The intended long-term system may aim to protect:

```text
message content
fragment structure
fragment ordering
routing metadata
state evolution metadata
node health metadata
transport metadata
operator configuration
deployment profile assumptions
```

The current MVP does not protect all of these assets.

Current MVP asset handling:

| Asset | Current status |
|---|---|
| Message content | Not encrypted by MVP |
| Fragment content | Transformed, not cryptographically protected |
| Fragment order | Preserved internally for testing |
| Routing metadata | Not protected |
| Transport metadata | Not protected |
| MCE state | Stored in memory; truncated snapshots may be persisted |
| Vault metadata | Stored in cleartext JSON if VaultDisk is used |
| Operator config | Not hardened |
| Deployment profile | Not validated |

---

## 5. Explicit non-goals for v0.4.3

Whisper Remote Nerve v0.4.3 does not provide:

```text
confidentiality
integrity
authentication
anonymous routing
metadata confidentiality
traffic analysis resistance
replay protection at protocol level
Sybil resistance
DoS resistance
secure key exchange
forward secrecy
post-compromise recovery
secure deletion
tamper-resistant persistence
Reticulum network integration
NixOS reproducibility
Rust/WASM hardening
formal verification
```

These are future work items or external dependencies, not claims of the current MVP.

---

## 6. Trust assumptions

The current MVP assumes:

```text
local execution is trusted
Python runtime is trusted
the seed is provided securely
the process memory is not actively compromised
the filesystem is not hostile
VaultDisk files are not tampered with
test inputs are controlled
no real adversarial network is present
```

These assumptions are intentionally strong because the current release is a local MVP, not a deployed system.

If these assumptions do not hold, the current MVP should be considered unsafe.

---

## 7. Adversary model

### A0 — Non-adversarial environment

The system is executed locally for development and testing.

Current tests operate mostly under A0.

### A1 — Passive local observer

The adversary can observe files, logs, persisted VaultDisk JSON, runtime outputs, and benchmark output.

Expected exposure in v0.4.3:

```text
fragment counts
input/output sizes
timestamps
MCE state previews
pipeline summary
metadata stored in Vault/VaultDisk
```

The MVP does not protect against this adversary.

### A2 — Malformed input adversary

The adversary can provide malformed, oversized, repetitive, or suspicious fragments.

Current partial mitigations:

```text
Dome rejects oversized fragments above 10 MiB
Dome rejects long null-byte runs
Lemonade detects poison patterns
Lemonade detects oversize
Lemonade detects low entropy
Lemonade detects replayed fragment IDs
MCEHardened detects corrupted runtime state shape
ReticulumBridge rejects malformed bridge packets
VaultDisk rejects malformed JSON format/version
```

These are sanity checks, not comprehensive security controls.

### A3 — Active local tampering adversary

The adversary can modify Python objects, source files, VaultDisk JSON, or runtime state.

Current status:

```text
not protected
```

MCEHardened may detect some obvious state corruption, such as incorrect state length or negative counters, but it does not prevent or recover from malicious tampering.

### A4 — Network adversary

The adversary can observe, delay, reorder, inject, replay, or drop network traffic.

Current status:

```text
not modeled in implementation
not simulated
not defended against
```

ReticulumBridge is only an encapsulation skeleton. It does not perform real Reticulum transport, authentication, peer validation, routing, retransmission, or encryption.

### A5 — Global passive adversary

The adversary can observe timing, size, routing, and traffic metadata across the network.

Current status:

```text
not evaluated
not defended against
```

No claim is made regarding anonymity, unlinkability, correlation resistance, or metadata confidentiality.

### A6 — Sybil / colluding node adversary

The adversary controls multiple apparent nodes or lanes and attempts to simulate diversity.

Current status:

```text
not evaluated
not defended against
```

BAL lanes are in-memory structures, not real independent network paths. VoxMesh divergence is a state skeleton, not a Sybil-resistance mechanism.

### A7 — Compromised host adversary

The adversary controls the host OS, Python interpreter, process memory, or filesystem.

Current status:

```text
out of scope for MVP
```

Python does not guarantee secure zeroization of seed material or state. Future hardening would require Rust/WASM/native components, memory locking where appropriate, and explicit zeroization.

---

## 8. In-scope threats for current MVP

The current MVP partially addresses:

```text
accidental state corruption
invalid fragment sizes
simple malformed envelopes
simple poison byte patterns
long null-byte sequences
fragment replay indicators
low-entropy fragment indicators
malformed VaultDisk files
pipeline regression drift
```

These are development-level defensive checks.

---

## 9. Out-of-scope threats for current MVP

The current MVP does not address:

```text
cryptographic confidentiality
cryptographic integrity
transport authentication
network anonymity
traffic correlation
global passive adversaries
adaptive active network attackers
Sybil attacks
colluding relays
bridge-node compromise
side-channel attacks
host compromise
malicious Python runtime
secure deletion
rollback attacks against VaultDisk
supply-chain attacks
NixOS/reproducible build attacks
```

These must be handled in later phases or by external security layers.

---

## 10. Security boundaries

The current security boundaries are intentionally narrow.

### RotorMachine

Provides:

```text
deterministic reversible transformation per (seed, fragment_id)
```

Does not provide:

```text
encryption
PRP security
collision resistance
diffusion guarantees
indistinguishability
metadata protection
```

### MCE / MCEHardened

Provides:

```text
deterministic state evolution
basic state shape validation
coherence checks
```

Does not provide:

```text
secure key schedule
forward secrecy
state compromise recovery
formal verification
```

### Loader

Provides:

```text
deterministic fragmentation / route / retry decisions
```

Does not provide:

```text
secure routing
adaptive network protection
Reticulum integration
```

### BAL

Provides:

```text
in-memory lane distribution
round-robin scheduling
ordered collection
```

Does not provide:

```text
real multipath routing
lane independence
traffic analysis resistance
```

### Dome

Provides:

```text
size filtering
long null-run rejection
minimal envelope roundtrip
```

Does not provide:

```text
authenticated envelopes
malware scanning
semantic content filtering
```

### Lemonade

Provides:

```text
7 deterministic anomaly detectors
per-fragment stateless scan
cumulative threat scan
```

Does not provide:

```text
IDS-grade detection
ML-based detection
adaptive adversary detection
formal threat scoring
```

### VoxMesh

Provides:

```text
36 deterministic fractal states
mutation and divergence scoring
coherence check
```

Does not provide:

```text
consensus
randomness beacon
entropy extraction
Sybil resistance
```

### Vault / VaultDisk

Provides:

```text
in-memory metadata store
JSON persistence
deterministic save/load roundtrip
```

Does not provide:

```text
encrypted storage
tamper resistance
access control
rollback protection
secure deletion
```

### ReticulumBridge

Provides:

```text
simple packet encapsulation
lane_id and sequence_id fields
metadata preservation
roundtrip decode
```

Does not provide:

```text
real Reticulum transport
network I/O
peer authentication
transport security
routing
```

---

## 11. Current guarantees

The current implementation supports the following limited guarantees under local trusted execution:

```text
RotorMachine byte transformations roundtrip for same (seed, fragment_id)
MCE state evolution is deterministic for same seed and fragment sequence
MCEHardened detects basic state-shape corruption
Loader decisions are deterministic
BAL reassembles in original order after round-robin distribution
Dome wraps and unwraps valid fragments
Lemonade detects configured simple anomalies
VoxMesh mutation is deterministic per seed and entropy sequence
VaultDisk persists and reloads metadata deterministically
ReticulumBridge encapsulates and decapsulates payloads
FullPipeline maintains count coherence across fragments, packets, and Vault entries
Regression tests lock key deterministic behavior
```

These are functional guarantees, not security guarantees.

---

## 12. Current validation evidence

As of v0.4.3:

```text
Full test suite:     104 passed
Regression suite:    9 passed
FullPipeline smoke:  OK
FullPipeline bench:  OK
```

Known benchmark:

```text
Payload size:       1 MiB
Fragment size:      1024 bytes
Fragment count:     1024
Elapsed:            ~0.77 s
Throughput:         ~1.30 MB/s
Blocked reports:    0 for clean benchmark
```

This demonstrates functional integration and regression stability.

It does not demonstrate adversarial resilience.

---

## 13. Known failure modes

Known failure modes include:

```text
incorrect operator assumptions
seed exposure
Python memory exposure
VaultDisk tampering
VaultDisk rollback
metadata leakage through persisted JSON
metadata leakage through logs
route_count collapse to 1
no real path diversity
no real Reticulum integration
no cryptographic authentication
no encrypted transport
no simulation-backed resilience claims
```

The current MVP should fail closed only in narrow cases such as malformed envelopes, invalid VaultDisk format, or basic MCE state-shape corruption. It does not provide systemic fail-safe behavior.

---

## 14. Required Phase 2 validation

Before any security claim, the following work is required:

```text
topology simulator
adversarial network model
baseline comparison
metric definitions
repeatable experiments
Nix reproducibility
threat-model refinement
```

Minimum topology classes:

```text
Erdős–Rényi random graph
Barabási–Albert scale-free graph
Watts–Strogatz small-world graph
hierarchical OT topology
hub-and-spoke industrial topology
hybrid cloud-edge topology
```

Minimum adversarial scenarios:

```text
random node compromise
bridge-node compromise
Sybil-style pseudo-diversity
colluding relay groups
low-noise patient adversary
partial network partition
false-positive-heavy environment
traffic correlation observer
```

Minimum metrics:

```text
reachability
latency
fragment reconstruction probability
metadata exposure estimate
route diversity
degradation frequency
false-positive rate
bandwidth overhead
pipeline throughput
```

---

## 15. Baseline comparison still required

Future evaluation should compare Whisper against:

```text
direct single-path transport
Tor-style onion routing model
I2P-style routing model
mixnet-style batching/delay model
classic OT segmentation
basic multipath routing
```

The current MVP does not implement these comparisons.

---

## 16. NLnet-facing summary

The current project status can be summarized as:

```text
Phase 1 is complete:
A tested Python MVP architecture skeleton exists.
It includes an end-to-end pipeline, 104 passing tests, 9 regression tests,
smoke tests, benchmark scripts, release notes, and explicit non-security claims.

Phase 2 is required:
Topology simulation, adversarial evaluation, baseline comparison,
Nix reproducibility, and selective hardening are still required before any
security or resilience claims can be made.
```

The correct claim is:

```text
Whisper Remote Nerve v0.4.3 is a tested experimental MVP framework.
```

The incorrect claim would be:

```text
Whisper Remote Nerve v0.4.3 is a secure communication protocol.
```

---

## 17. Release checklist before public grant review

Before public NLnet review, ensure the repository contains:

```text
README.md
THREAT_MODEL.md
WHITEPAPER.md
ROADMAP.md
BENCHMARKS.md
REGRESSION_TESTS.md
RELEASE_NOTES_v0.4.3.md
LICENSE
SECURITY.md
requirements.txt or flake.nix
```

Recommended release validation command:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```
