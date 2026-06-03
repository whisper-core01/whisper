# WHISPER Remote Nerve

**Status:** experimental MVP framework  
**Current baseline:** v0.4.3  
**Security status:** not a secure communication protocol  
**Review status:** grant / research review ready  

WHISPER Remote Nerve is a tested experimental framework for exploring whether **structural divergence** can improve resilience in decentralized communication pipelines under adversarial topology conditions.

The current release is a Python MVP with:

```text
104 passing tests
9 regression tests
end-to-end full pipeline
benchmark scripts
threat model
whitepaper
roadmap
security policy
Nix reproducibility baseline
```

WHISPER is not production-ready. It is not currently secure, anonymous, or metadata-protecting. It is a research and engineering baseline for Phase 2 simulation and validation.

---

## 1. What WHISPER is

WHISPER Remote Nerve is an experimental architecture for studying:

```text
assume-compromise communication
per-fragment state evolution
structural divergence
adaptive lane assignment
anomaly-aware routing decisions
network-level degradation under compromise
```

The MVP provides a local, testable pipeline:

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

The core research question is:

```text
Can local structural divergence produce measurable network-level resilience
in decentralized communication systems?
```

The current MVP does not answer that question yet. It provides the framework required to test it.

---

## 2. What WHISPER is not

WHISPER Remote Nerve v0.4.3 is not:

```text
a secure communication protocol
an anonymous network
a Tor replacement
an I2P replacement
a libp2p replacement
a Reticulum implementation
a cryptographic protocol
an IDS or SIEM
a production-ready transport
```

It does not currently provide:

```text
confidentiality
integrity
authentication
anonymous routing
metadata confidentiality
traffic-analysis resistance
Sybil resistance
DoS resistance
forward secrecy
secure key exchange
secure storage
tamper-resistant persistence
```

The correct current claim is:

```text
WHISPER Remote Nerve v0.4.3 is a tested experimental MVP framework.
```

The incorrect claim would be:

```text
WHISPER Remote Nerve v0.4.3 is a secure or anonymous communication protocol.
```

---

## 3. Why this project exists

Classical privacy and resilience systems often rely on stable abstractions:

```text
Tor-style systems       circuits and relays
I2P-style systems       tunnels
OT segmentation         static trust boundaries
classic multipath       route diversity
```

WHISPER starts from a more pessimistic assumption:

```text
all nodes may eventually be compromised
metadata is always a leakage risk
static trust boundaries decay
path diversity can be simulated by an adversary
```

The project investigates whether state evolution, lane assignment, anomaly detection, and structural divergence can become measurable inputs for future resilient communication systems.

This is still an open research question.

---

## 4. Components

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

Important component boundaries:

```text
RotorMachine is transformation, not encryption.
MCE is state evolution, not a secure key schedule.
BAL lanes are local abstractions, not proven network paths.
VoxMesh measures state uniqueness in the MVP, not proven topology resilience.
ReticulumBridge is encapsulation, not real Reticulum integration.
```

---


## 4.1 VoxMesh: structural divergence skeleton

VoxMesh is one of the core experimental components of WHISPER.

It maintains multiple deterministic fractal state machines and is used to explore whether **state diversity** can become a measurable input for future routing and degradation policies.

Current MVP behavior:

```text
36 deterministic fractal states
per-fractal mutation
state uniqueness measurement
coherence check
deterministic behavior per seed
```

Important limitation:

```text
In v0.4.3, VoxMesh divergence is maximal from initialization because each fractal is seeded with its fractal_id.
```

This means the current metric measures:

```text
state uniqueness
```

It does not yet prove:

```text
network-level path diversity
Sybil resistance
topology resilience
metadata protection
```

Phase 2 will make `fractal_count` tunable and test values such as:

```text
4
16
36
64
256
```

The goal is to measure how fractal count affects:

```text
state-to-path correlation
path diversity
lane collapse rate
fragment reconstruction probability
latency overhead
bandwidth overhead
```

Correct current claim:

```text
VoxMesh is a state-divergence skeleton for simulation.
```

Incorrect current claim:

```text
VoxMesh currently proves network resilience.
```

## 5. Repository map

Recommended repository files:

```text
README.md                         project entry point
THREAT_MODEL.md                   security boundaries and adversary model
WHITEPAPER.md                     architecture and design rationale
ROADMAP.md                        v0.5–v0.8 plan
SIMULATION_PLAN.md                Phase 2 simulator plan
PHASE2_VALIDATION_CRITERIA.md     success thresholds and mapping validation
PROTOCOL_LABS_ALIGNMENT.md        decentralized systems alignment
BENCHMARKS.md                     measured MVP benchmark results
REGRESSION_TESTS.md               non-regression policy
APPLY_NOTES.md                    patch notes and reviewer-alignment diffs
SECURITY.md                       security reporting and limitations
RELEASE_NOTES_v0.4.3.md           release evidence
requirements.txt                  Python test dependency baseline
flake.nix                         Nix development shell
```

Reviewer reading order:

```text
1. README.md
2. THREAT_MODEL.md
3. WHITEPAPER.md
4. ROADMAP.md
5. SIMULATION_PLAN.md
6. BENCHMARKS.md
7. SECURITY.md
```

---

## 6. Quick start

### Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `requirements.txt` is not yet present, the minimal dependency is:

```bash
pip install pytest
```

Run the full test suite:

```bash
pytest -q
```

Run the regression suite:

```bash
pytest -q tests/test_regression_v043.py
```

Run the full pipeline smoke test:

```bash
python3 full_pipeline_v01.py
```

Run the full pipeline benchmark:

```bash
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 7. Nix reproducibility

A minimal Nix development shell is provided for reproducible review.

Expected workflow:

```bash
nix develop
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

Optional validation script:

```bash
./scripts/validate_nix_shell.sh
```

Current Nix scope:

```text
development shell only
not a full Nix package
not a deployment profile
not a production service
```

---

## 8. Current validation status

Latest validated baseline:

```text
Version: v0.4.3
Status: final MVP baseline + regression suite
```

Observed validation:

```text
Full test suite:        104 passed in 1.13s
Regression suite:       9 passed in 0.05s
FullPipeline smoke:     OK
FullPipeline benchmark: OK
```

FullPipeline smoke coherence:

```text
fragment_count == bridge_packets == vault_entries == final_mce_counter
22 == 22 == 22 == 22
```

FullPipeline benchmark:

```text
payload size:       1,048,576 bytes
fragment size:      1,024 bytes
fragment count:     1,024
elapsed:            0.771 s
throughput:         1.297 MB/s
blocked reports:    0
```

These are functional MVP benchmarks, not security claims.

---

## 9. Benchmark commands

Full pipeline:

```bash
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

Component benchmarks:

```bash
python3 bench/bench_mce_hardened.py --fragments 1000
python3 bench/bench_loader.py --payloads 1000
python3 bench/bench_bal.py --fragments 10000 --routes 3
python3 bench/bench_dome.py --fragments 10000 --rejection-rate 0.05
python3 bench/bench_voxmesh.py --mutations 1000
python3 bench/bench_lemonade.py --fragments 10000 --bad-rate 0.05
```

Regression runner:

```bash
python3 bench/bench_regression.py
```

See:

```text
BENCHMARKS.md
REGRESSION_TESTS.md
```

---

## 10. Release validation checklist

Before tagging a release:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

A release should not be published if:

```text
tests fail
regression tests fail
FullPipeline smoke fails
VaultDisk roundtrip fails
ReticulumBridge roundtrip fails
FullPipeline count coherence breaks
```

Recommended tag for current baseline:

```bash
git tag v0.4.3
```

---

## 11. Roadmap

Current completed baseline:

```text
v0.4.3 — final MVP baseline + regression suite
```

Planned releases:

```text
v0.5.x — documentation and reproducibility baseline
v0.6.x — topology simulator, JSON schemas, state-to-path mapping validation
v0.6.5 — minimal libp2p PoC for lane-to-stream feasibility
v0.7.x — baseline comparison and measurement reports
v0.8.x — Rust/WASM hardening evaluation and external-review candidate
```

Timeline note:

```text
6 weeks     minimum viable simulator
8–12 weeks  credible simulation and baseline comparison
12–16 weeks review-quality evaluation with iteration
```

The six-week target should be treated as the first simulator milestone, not the complete Phase 2 result.

---

## 12. Phase 2: simulation and validation

Phase 2 must test whether local state divergence maps to network-level diversity.

Required simulator features:

```text
topology graph models
node churn
NAT reachability
latency distributions
packet loss
bandwidth classes
adversary models
path sampling
state-to-path mapping validation
```

Required metrics:

```text
state_distance
path_distance
state_to_path_correlation
path_overlap
unique_path_ratio
lane_collapse_rate
fragment reconstruction probability
metadata exposure estimate
latency estimate
bandwidth overhead
```

Required output artifacts:

```text
simulation_run.schema.json
metrics_report.schema.json
topology_graph.schema.json
baseline_comparison.schema.json
simulation_run.json
metrics_report.json
baseline_comparison.csv
```

Important failure condition:

```text
If state divergence is high but path diversity remains low,
then local structural divergence does not translate into network-level resilience.
```

A negative result is acceptable and should be published.

---

## 13. Success thresholds

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

Scientifically interesting but weak:

```text
3–9% improvement under narrow conditions
```

---

## 14. Baselines

Phase 2 baselines must be defined as simplified abstractions with explicit parameters.

Planned baselines:

```text
single-path direct transport
random multipath
fixed-circuit abstraction
persistent-tunnel abstraction
batch-delay abstraction
static-zone abstraction
```

They should not be described as full Tor, I2P, mixnet, or OT implementations.

Fair comparison requires:

```text
same topology
same source/target pairs
same adversary model
same payload size
same repeated run count
same latency model
same packet loss model
```

---

## 15. Protocol Labs alignment

WHISPER is not currently a libp2p, IPFS, IPLD, Filecoin, or Reticulum project.

Potential future Protocol Labs-relevant artifacts:

```text
machine-readable simulation reports
IPLD-compatible experiment metadata
IPFS-published simulation bundles
content-addressed benchmark artifacts
minimal libp2p lane-to-stream PoC
decentralized topology simulation results
```

Correct Protocol Labs-facing statement:

```text
WHISPER Remote Nerve is a tested local MVP. Phase 2 will determine whether its
local structural-divergence mechanisms translate into measurable network-level
effects under adversarial decentralized topologies.
```

Incorrect statement:

```text
WHISPER already scales to decentralized networks.
```

---

## 16. NLnet alignment

NLnet-facing strengths:

```text
open-source infrastructure research
explicit security boundaries
responsible non-overclaiming
reproducible development baseline
public-interest communication resilience research
```

Correct NLnet-facing statement:

```text
Phase 1 produced a tested Python MVP framework with an end-to-end pipeline,
104 passing tests, 9 regression tests, threat model, whitepaper, roadmap,
benchmark scripts, and explicit non-security claims.
```

Next funded work:

```text
topology simulation
adversarial evaluation
baseline comparison
Nix reproducibility
selective hardening
```

---

## 17. Security policy

This project is not safe for protecting real sensitive communications.

Do not use v0.4.3 for:

```text
secure messaging
anonymous transport
production OT security
encrypted tunnels
key storage
intrusion detection
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

## 18. Known limitations

Known limitations include:

```text
no real network integration
no libp2p integration yet
no Reticulum integration
no topology simulator yet
no baseline comparison yet
no authenticated encryption
no key exchange
no secure memory handling
no formal verification
no production hardening
```

VoxMesh limitation:

```text
current divergence score measures state uniqueness, not proven topology resilience
```

BAL limitation:

```text
current lanes are in-memory abstractions, not real network paths
```

RotorMachine limitation:

```text
deterministic transformation, not cryptography
```

---

## 19. Research posture

Correct posture:

```text
tested experimental framework
structural-divergence research
simulation-ready architecture
grant/research review baseline
```

Incorrect posture:

```text
secure protocol
anonymous network
Tor replacement
libp2p replacement
Reticulum implementation
production-ready transport
```

The project should be designed to discover the truth, not to confirm the architecture.

Positive and negative Phase 2 results are both valuable.

---

## 20. License

License decision pending.

Recommended options:

```text
Code: AGPL-3.0-or-later or Apache-2.0
Docs: CC-BY-SA-4.0 or CC-BY-4.0
```

Before public release, add:

```text
LICENSE
NOTICE, if needed
documentation license note
```

---

## 21. Contact / security reporting

Until a dedicated security contact exists, use the public issue tracker with the prefix:

```text
[security]
```

Do not include real secrets, credentials, private keys, or sensitive operational data in public reports.

See:

```text
SECURITY.md
```
