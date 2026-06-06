# WHISPER Remote Nerve

## Start Here

WHISPER is not a messaging application.

WHISPER is a cryptographic organism for sovereign digital communication.

It does not only protect message content.

It protects the communication container:

- routing
- rhythm
- fragmentation
- repair
- session lifecycle
- local memory
- closure
- dormancy
- disappearance

Recommended reading order:

0. `FUNDING_BRIEF.md`  
   Short external-review brief for funders and reviewers.

1. `DOCTRINE_CONTENT_VS_CONTAINER.md`  
   Root manifesto. Explains why WHISPER protects the container, not only the content.

2. `WIKI_INDEX.md`  
   Main documentation entry point.

3. `V1_3_SERIES_REPORT.md`  
   v1.3 routing, pressure field, redundancy, custody, and adaptive reconstruction report.

4. `V1_4_0_SESSION_LIFECYCLE_REPORT.md`  
   v1.4 session lifecycle, secure shutdown, FLV dormancy, and non-reactivation report.

5. `V1_5_0_NERVE_MOBILE_REPORT.md`  
   v1.5 Nerve Mobile report: admission, Vault boot, reappearance, revocation, runtime, transport, UI, permissions, and Wasm bridge.

6. `WIKI_ROTOR.md`, `WIKI_NERVE.md`, `WIKI_NERVE_MOBILE.md`, `WIKI_FLV.md`  
   Organ-level wiki pages for lifecycle sealing, local reflexes, and dormant local memory.

Current stable milestones:

- `v1.3.4` — adaptive pressure routing and reconstruction
- `v1.4.1` — session lifecycle, FLV dormancy, and non-reactivation

Current validation snapshot:

- 297 tests passing
- 330 session reactivation cases
- 1.0000 pass rate on session reactivation prevention
- machine/LUKS-bound dormant FLV lifecycle model
- local revocation and secure shutdown validated

---


**Status:** Experimental MVP framework  
**Current baseline:** v0.4.3  
**Security status:** Not a secure communication protocol  
**Grant/review status:** NLnet-ready documentation baseline in progress  

---

## 1. What is WHISPER Remote Nerve?

WHISPER Remote Nerve is an experimental architecture for exploring resilient, assume-compromise communication pipelines.

The project investigates whether **structural divergence** can be measured and used as a building block for future resilient communication systems.

Current MVP pipeline:

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

The current release demonstrates that the architecture can be assembled, tested, benchmarked, and regression-locked.

It does **not** claim to provide anonymity, confidentiality, metadata protection, or secure transport.

---

## 2. Current validation status

As of v0.4.3:

```text
Full test suite:        104 passed
Regression suite:       9 passed
FullPipeline smoke:     OK
FullPipeline benchmark: OK
```

Reference benchmark:

```text
Payload size:       1,048,576 bytes
Fragment count:     1024
Elapsed:            ~0.77 s
Throughput:         ~1.30 MB/s
```

Run validation:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 3. Components

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

## 4. Why this architecture?

Classical approaches often rely on relatively stable abstractions:

```text
Tor-style systems       circuits and relays
I2P-style systems       tunnels
OT segmentation         static trust boundaries
classic multipath       route diversity
```

WHISPER starts from a pessimistic assumption:

```text
all nodes may eventually be compromised
metadata is always a leakage risk
static trust boundaries decay
path diversity can be simulated by an adversary
```

The project’s core hypothesis is:

```text
Structural divergence can become a measurable resilience primitive.
```

The current MVP does not prove this hypothesis. It provides the implementation foundation required to test it.

---

## 5. What this project is not

WHISPER Remote Nerve v0.4.3 is not:

```text
a secure communication protocol
an anonymous network
a Tor replacement
an I2P replacement
a Reticulum implementation
a cryptographic protocol
an IDS or SIEM
a production-ready transport
```

The current project is:

```text
a tested experimental MVP framework
a modular architecture skeleton
a foundation for topology simulation and adversarial evaluation
```

---

## 6. Repository documents

Recommended documents:

```text
README.md                 project overview
THREAT_MODEL.md           security boundaries and adversary model
WHITEPAPER.md             architecture and design rationale
ROADMAP.md                v0.5–v0.8 plan
BENCHMARKS.md             measured results
REGRESSION_TESTS.md       regression policy
SECURITY.md               vulnerability and security policy
RELEASE_NOTES_v0.4.3.md   release evidence
LICENSE                   open-source license
```

---

## 7. Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
pytest -q
python3 full_pipeline_v01.py
```

Optional benchmark:

```bash
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 8. Development status

Completed:

```text
v0.1.x core Rotor/MCE/Vault pipeline
v0.2.x MCE hardening and Loader
v0.3.x BAL, Dome, VoxMesh
v0.4.x Lemonade, ReticulumBridge, FullPipeline, regression suite
```

Next:

```text
v0.5.x documentation and reproducibility
v0.6.x topology simulator
v0.7.x baseline comparison
v0.8.x hardening and external-review candidate
```

---

## 9. Phase 2 focus

The next phase must answer:

```text
Does local structural divergence translate into network-level diversity?
Does WHISPER reduce reconstruction probability under compromise?
Does it degrade gracefully under partial node compromise?
What are the latency and bandwidth costs?
How does it compare to simplified Tor/I2P/mixnet/segmentation baselines?
```

Required Phase 2 work:

```text
topology simulator
adversarial scenarios
baseline comparisons
metrics and reports
Nix reproducibility
updated threat model and whitepaper
```

---

## 10. Security statement

The current MVP does not provide:

```text
confidentiality
integrity
authentication
anonymous routing
metadata confidentiality
traffic analysis resistance
Sybil resistance
DoS resistance
forward secrecy
secure key exchange
secure deletion
tamper-resistant persistence
```

For details, see:

```text
THREAT_MODEL.md
SECURITY.md
```

---

## 11. NLnet-facing summary

Correct project status:

```text
WHISPER Remote Nerve v0.4.3 is a tested experimental MVP framework for exploring structural-divergence-based resilient communication.
```

Incorrect project status:

```text
WHISPER Remote Nerve v0.4.3 is a secure or anonymous communication protocol.
```

Current evidence:

```text
104 passing tests
9 regression tests
full end-to-end pipeline
benchmark scripts
threat model
whitepaper
roadmap
```

Next funded work:

```text
simulation
empirical validation
baseline comparison
reproducibility
hardening
```


- `V1_6_0_CORE_ORGAN_PIPELINES_REPORT.md`  
  v1.6 Core organ pipelines report: inbound isolation, outbound isolation, upstream retention, Lemonade/Dôme immunity, and organ restart safety.
