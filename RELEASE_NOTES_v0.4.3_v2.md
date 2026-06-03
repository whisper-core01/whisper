# RELEASE_NOTES_v0.4.3.md

## WHISPER Remote Nerve v0.4.3

**Release type:** final MVP baseline  
**Status:** tested experimental framework  
**Security status:** not a secure communication protocol  
**Review status:** grant / research review baseline  

---

## 1. Summary

WHISPER Remote Nerve v0.4.3 is the final Phase 1 MVP baseline.

This release provides a tested local Python framework for exploring whether **structural divergence** can become a measurable primitive for resilient decentralized communication research.

The release includes:

```text
end-to-end full pipeline
104 passing tests
9 regression tests
benchmark scripts
ReticulumBridge encapsulation skeleton
Vault/VaultDisk persistence
Lemonade anomaly skeleton
VoxMesh state-divergence skeleton
MCEHardened validation layer
Phase 2 documentation baseline
```

This release does **not** claim to provide security, anonymity, transport protection, or metadata confidentiality.

The correct release statement is:

```text
WHISPER Remote Nerve v0.4.3 is a tested experimental MVP framework.
```

The incorrect release statement would be:

```text
WHISPER Remote Nerve v0.4.3 is a secure or anonymous communication protocol.
```

---

## 2. Release scope

v0.4.3 closes Phase 1.

Phase 1 goal:

```text
Build a coherent, testable, local MVP pipeline.
```

Phase 1 result:

```text
Achieved.
```

Phase 1 does not include:

```text
real network deployment
real libp2p integration
real Reticulum integration
topology simulation
baseline comparison
cryptographic transport
formal security evaluation
production hardening
```

Those belong to Phase 2 and later.

---

## 3. Included components

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

---

## 4. Pipeline

Current FullPipeline flow:

```text
payload
  -> Loader
  -> fragmentation
  -> Dome filtering/envelope
  -> BAL lane distribution
  -> MCEHardened state evolution
  -> Lemonade anomaly scan
  -> ReticulumBridge encapsulation
  -> Vault metadata storage
  -> optional VaultDisk persistence
```

This validates component composition and count coherence.

It does not validate network-level path diversity.

---

## 5. Validation results

Release validation command:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

Observed result:

```text
Full test suite:        104 passed in 1.13s
Regression suite:       9 passed in 0.05s
FullPipeline smoke:     OK
FullPipeline benchmark: OK
```

---

## 6. Regression suite

v0.4.3 adds a dedicated non-regression suite.

Command:

```bash
pytest -q tests/test_regression_v043.py
```

Observed result:

```text
9 passed in 0.05s
```

Regression coverage:

```text
RotorMachine deterministic roundtrip
MCEHardened deterministic state sequence
Loader deterministic decisions
Dome envelope roundtrip
Lemonade stateless scan semantics
VoxMesh deterministic mutation
ReticulumBridge packet roundtrip
VaultDisk save/load roundtrip
FullPipeline stable summary shape
```

Purpose:

```text
prevent accidental behavioral drift across core MVP components
```

Non-purpose:

```text
prove security
```

---

## 7. FullPipeline smoke result

Command:

```bash
python3 full_pipeline_v01.py
```

Observed output:

```text
=== FullPipeline v0.1 Smoke Test ===
pipeline: Loader -> Dome -> BAL -> MCEHardened -> Lemonade -> ReticulumBridge -> Vault
input_size: 5400
fragment_size: 256
fragment_count: 22
route_count: 1
lane_count: 1
lane_loads: [22]
bridge_packets: 22
vault_entries: 22
blocked_reports: 0
max_threat_level: 0
final_mce_counter: 22
final_mce_state_hex: 1c6149d6b43d5ade
dome_rejection_rate: 0.0
persisted: True
elapsed_seconds: 0.012553
```

Count coherence:

```text
fragment_count == bridge_packets == vault_entries == final_mce_counter
22 == 22 == 22 == 22
```

---

## 8. FullPipeline benchmark

Command:

```bash
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

Observed output:

```text
FullPipeline benchmark
----------------------
payload size:       1048576 bytes
fragment size:      1024 bytes
fragment count:     1024
route count:        1
bridge packets:     1024
blocked reports:    0
elapsed:            0.771 s
throughput MB/sec:  1.297
final state:        5308c0f032ff45d4
```

Interpretation:

```text
The local Python MVP can process a 1 MiB payload through the full pipeline,
produce 1024 bridge packets, update MCE state, run Lemonade scans, and store
Vault metadata.
```

Non-interpretation:

```text
This does not prove network resilience, metadata protection, anonymity,
confidentiality, or transport security.
```

---

## 9. Component benchmark summary

Observed component smoke benchmarks during v0.4.x development:

| Component | Metric | Result | Target | Status |
|---|---:|---:|---:|---|
| MCEHardened | overhead | 0.14% | < 10% | PASS |
| Loader | mean decision time | 0.001262 ms/op | < 1 ms/op | PASS |
| BAL | absolute lane cost | 0.000357 ms/fragment | < 0.01 ms/fragment | PASS |
| Dome | mean wrap/unwrap | 0.001261 ms/op | < 1 ms/op | PASS |
| VoxMesh | mean mutation cycle | 0.023414 ms/cycle | < 5 ms/cycle | PASS |
| Lemonade | mean stateless scan | 0.018292 ms/op | < 1 ms/op | PASS |
| FullPipeline | throughput | 1.297 MB/s | smoke benchmark | PASS |
| Regression | deterministic suite | 9 passed | all pass | PASS |
| Full tests | full suite | 104 passed | all pass | PASS |

These benchmarks are MVP smoke benchmarks, not security claims.

See:

```text
BENCHMARKS.md
```

---

## 10. What changed since v0.4.2

v0.4.2 introduced:

```text
ReticulumBridge skeleton
FullPipeline integration
full pipeline benchmark
release notes baseline
```

v0.4.3 adds:

```text
dedicated regression suite
regression benchmark runner
REGRESSION_TESTS.md
stable release validation checklist
final Phase 1 baseline posture
```

Main new files:

```text
tests/test_regression_v043.py
bench/bench_regression.py
REGRESSION_TESTS.md
```

---

## 11. Known limitations

v0.4.3 does not include:

```text
topology simulation
baseline comparison
real libp2p integration
real Reticulum integration
real network paths
cryptographic transport
authenticated encryption
key exchange
secure memory handling
secure deletion
tamper-resistant VaultDisk
formal verification
external audit
```

Important component limitations:

```text
RotorMachine is not encryption.
MCE is not a secure key schedule.
BAL lanes are in-memory abstractions, not real network paths.
VoxMesh measures state uniqueness in the MVP, not proven topology resilience.
Lemonade is not an IDS.
ReticulumBridge is encapsulation only, not real Reticulum.
VaultDisk is cleartext JSON metadata persistence.
```

---

## 12. Security posture

This release must not be used to protect real sensitive communications.

Do not use v0.4.3 as:

```text
secure messaging
anonymous transport
production OT security layer
encrypted tunnel
key vault
intrusion detection system
```

Acceptable use:

```text
local testing
architecture review
research prototype
simulation foundation
grant review artifact
```

See:

```text
SECURITY.md
THREAT_MODEL.md
```

---

## 13. Documentation included or expected

Recommended final Phase 1 documentation set:

```text
README.md
THREAT_MODEL.md
WHITEPAPER.md
ROADMAP.md
SIMULATION_PLAN.md
PHASE2_VALIDATION_CRITERIA.md
SIMULATION_REPORT.md               Phase 2 report template and future results structure
BENCHMARKS.md
REGRESSION_TESTS.md
SECURITY.md
PROTOCOL_LABS_ALIGNMENT.md
RESEARCH_PLAN.md
GRANT_REVIEW_POSITIONING.md
APPLY_NOTES.md
RELEASE_NOTES_v0.4.3.md
```

`SIMULATION_REPORT.md` is included as the future Phase 2 report structure and should be used to publish positive, mixed, negative, or inconclusive simulation results.


This release note should be read together with:

```text
README.md
THREAT_MODEL.md
WHITEPAPER.md
PHASE2_VALIDATION_CRITERIA.md
BENCHMARKS.md
SECURITY.md
```

---

## 14. Phase 2 direction

Phase 2 must test the architecture empirically.

Planned work:

```text
v0.5.x — documentation and reproducibility baseline
v0.6.x — topology simulator, JSON schemas, state-to-path mapping validation
v0.6.5 — minimal libp2p PoC for lane-to-stream feasibility
v0.7.x — baseline comparison and measurement reports
v0.8.x — Rust/WASM hardening evaluation and external-review candidate
```

Phase 2 must answer:

```text
Does local structural divergence map to network-level diversity?
Do BAL lanes collapse to overlapping network paths?
Does VoxMesh fractal_count affect outcomes?
Can WHISPER reduce reconstruction probability or path overlap?
What overhead does it introduce?
Does it degrade gracefully after partial compromise?
```

---

## 15. Phase 2 success thresholds

Minimum positive result:

```text
>= 10% relative improvement against at least one baseline
under at least two topology/adversary combinations
```

Strong positive result:

```text
>= 25% relative improvement against baseline
under at least three topology/adversary combinations
```

High-impact result:

```text
>= 50% relative improvement under multiple topologies and adversaries
```

Overhead constraints:

```text
positive result: <= 2x latency and bandwidth overhead
experimental high-divergence mode: <= 3x latency and bandwidth overhead
```

Negative results are acceptable and should be published.

---

## 16. NLnet relevance

v0.4.3 provides:

```text
open-source-ready MVP baseline
explicit threat model
security boundaries
reproducible test commands
regression suite
benchmark documentation
responsible non-overclaiming
Phase 2 validation plan
```

Correct NLnet-facing claim:

```text
Phase 1 produced a tested Python MVP framework with an end-to-end pipeline,
104 passing tests, 9 regression tests, benchmark scripts, release notes,
threat model, whitepaper, roadmap, and explicit security boundaries.
```

---

## 17. Protocol Labs relevance

v0.4.3 provides:

```text
tested local MVP
decentralized systems research question
simulation-ready architecture
planned machine-readable outputs
planned state-to-path validation
planned libp2p lane-to-stream PoC
baseline comparison plan
```

Correct Protocol Labs-facing claim:

```text
WHISPER Remote Nerve is a tested local MVP. Phase 2 will determine whether its
local structural-divergence mechanisms translate into measurable network-level
effects under adversarial decentralized topologies.
```

Incorrect claim:

```text
WHISPER already scales to decentralized networks.
```

---

## 18. Reproducibility

Minimum reproducibility requirements:

```text
git commit
Python version
requirements.txt or flake.nix
test command
regression command
benchmark command
machine/environment notes
```

Recommended command sequence:

```bash
nix develop
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 19. Upgrade / next steps

Immediate next repository tasks:

```text
ensure README.md is reviewer-ready
ensure SECURITY.md exists
ensure LICENSE is selected
ensure requirements.txt exists
ensure flake.nix or devshell.nix exists
apply WHITEPAPER / ROADMAP / SIMULATION_PLAN diffs
commit documentation baseline
tag v0.4.3
```

After v0.4.3:

```text
begin v0.5 reproducibility cleanup
define simulation JSON schemas
parameterize VoxMesh fractal_count
draft topology simulator interfaces
draft baseline model interfaces
```

---

## 20. Suggested release tag

```bash
git add .
git commit -m "release: finalize WHISPER MVP baseline v0.4.3"
git tag v0.4.3
```

Recommended pre-tag validation:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 21. Final note

This release closes the first engineering question:

```text
Can the architecture be assembled into a coherent, tested local MVP?
```

Answer:

```text
Yes.
```

It does not answer the research question:

```text
Does structural divergence provide measurable network-level resilience?
```

Answer:

```text
Not yet tested.
```

That is the purpose of Phase 2.
