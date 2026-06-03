# ROADMAP.md — WHISPER Remote Nerve

**Current baseline:** v0.4.3  
**Current status:** tested experimental MVP framework  
**Next target:** v0.5–v0.8 validation and reproducibility track  

---

## 1. Current baseline: v0.4.3

WHISPER Remote Nerve v0.4.3 is a tested Python MVP architecture skeleton.

It includes:

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

Validation status:

```text
Full test suite:       104 passed
Regression suite:      9 passed
FullPipeline smoke:    OK
FullPipeline benchmark OK
```

Reference benchmark:

```text
Payload size:       1 MiB
Fragment count:     1024
Elapsed:            ~0.77 s
Throughput:         ~1.30 MB/s
```

Important status statement:

```text
v0.4.3 is not a secure communication protocol.
v0.4.3 is a tested experimental MVP framework.
```

---

## 2. Roadmap overview

The next releases focus on validation, reproducibility, simulation, and selective hardening.

```text
v0.5.x — Documentation and reproducibility baseline
v0.6.x — Topology simulator and adversarial scenarios
v0.7.x — Baseline comparison and measurement reports
v0.8.x — Hardening track and release candidate for external review
```

The objective is to move from:

```text
tested local MVP
```

to:

```text
empirically evaluated experimental architecture
```

No security, anonymity, or resilience claim should be made before v0.7/v0.8 evidence exists.

---

## 3. v0.5.x — Documentation and reproducibility baseline

### Goal

Make the repository reviewable, reproducible, and grant-ready.

### Deliverables

```text
README.md
THREAT_MODEL.md
WHITEPAPER.md
ROADMAP.md
BENCHMARKS.md
REGRESSION_TESTS.md
SECURITY.md
RELEASE_NOTES_v0.4.3.md
LICENSE
requirements.txt
flake.nix or devshell.nix
```

### Technical tasks

```text
Add reproducible Python environment
Add Nix development shell
Document test commands
Document benchmark commands
Document non-goals
Document security boundaries
Document Phase 2 simulation plan
```

### Validation commands

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

### Exit criteria

```text
Repository can be cloned and tested by a third party.
All current tests pass.
Regression tests pass.
README clearly states what the MVP is and is not.
Threat model and whitepaper are present.
```

### Non-goals

```text
No real Reticulum integration
No Rust port
No security claims
No topology simulation yet
```

---

## 4. v0.6.x — Topology simulator

### Goal

Implement a repeatable topology simulation harness to evaluate whether local structural divergence can map to network-level diversity.

### Required topology classes

```text
Erdős–Rényi random graph
Barabási–Albert scale-free graph
Watts–Strogatz small-world graph
hub-and-spoke industrial topology
hierarchical OT-style topology
hybrid cloud-edge topology
```

### Required simulator components

```text
TopologyGraph
Node
Edge
PathSampler
AdversaryModel
SimulationRun
MetricsReport
```

### Initial adversary scenarios

```text
random node compromise
bridge-node compromise
colluding relay set
Sybil-style pseudo-diversity
partial network partition
low-noise traffic observer
false-positive-heavy environment
```

### Required metrics

```text
reachability
latency estimate
route diversity
path overlap
fragment reconstruction probability
metadata exposure estimate
degradation frequency
false-positive rate
bandwidth overhead
```

### Exit criteria

```text
At least 3 graph families implemented.
At least 3 adversary scenarios implemented.
Simulation outputs deterministic JSON reports.
Basic plots or tables can be generated.
Results are reproducible from a seed.
```

### Non-goals

```text
No claim of real-world anonymity
No production routing
No live network deployment
```

---

## 5. v0.7.x — Baseline comparison

### Goal

Compare WHISPER-style structural divergence against simplified baselines.

### Baselines

```text
direct single-path transport
basic multipath routing
Tor-style circuit abstraction
I2P-style tunnel abstraction
mixnet-style batching/delay abstraction
classic OT segmentation
```

### Comparison questions

```text
Does structural divergence reduce path overlap?
Does it reduce fragment reconstruction probability?
Does it increase latency or bandwidth overhead?
Does it degrade gracefully under partial compromise?
Does it collapse under Sybil-style pseudo-diversity?
```

### Required outputs

```text
baseline simulation scripts
metrics tables
benchmark JSON outputs
plots or CSV summaries
updated WHITEPAPER.md
updated THREAT_MODEL.md
```

### Exit criteria

```text
At least 3 baselines implemented.
At least 3 topologies evaluated.
At least 3 adversary models evaluated.
Results documented without overstated security claims.
```

### Non-goals

```text
No definitive anonymity claim
No formal proof
No replacement claim against Tor/I2P
```

---

## 6. v0.8.x — Hardening and review candidate

### Goal

Prepare a technically credible external-review candidate.

### Candidate hardening tasks

```text
Nix flake or devshell finalized
CI pipeline
structured benchmark output
JSON simulation reports
type hints cleanup
API documentation
component boundaries reviewed
failure modes documented
```

### Optional implementation hardening

```text
Rust/WASM hot path for RotorMachine
Rust/WASM hot path for MCE
explicit zeroization experiments
memory handling review
ReticulumBridge protocol draft
```

### Required documents

```text
SECURITY.md updated
THREAT_MODEL.md updated
WHITEPAPER.md updated
BENCHMARKS.md updated
SIMULATION_REPORT.md
RELEASE_NOTES_v0.8.md
```

### Exit criteria

```text
Repository is reproducible.
Simulation can be rerun.
Baseline comparison is documented.
Security boundaries are explicit.
Open questions are listed.
External reviewers can inspect the project without private context.
```

---

## 7. Phase 2 research questions

The core Phase 2 questions are:

```text
Does local state divergence map to network-level path diversity?
Does structural divergence reduce adversarial reconstruction probability?
Can graceful degradation be measured under partial compromise?
Can Sybil-style pseudo-diversity collapse the architecture?
What latency and bandwidth costs are introduced?
```

These questions must be answered empirically before WHISPER can make resilience claims.

---

## 8. Graceful degradation plan

Future work must define what happens after compromise.

Compromise cases:

```text
C1 — node sees one fragment
C2 — node sees one fragment plus metadata
C3 — node sees current MCE state
C4 — node sees VoxMesh state
C5 — node sees Loader route decision
C6 — node sees Vault metadata
C7 — node controls bridge/lane endpoint
C8 — multiple compromised nodes collude
```

Candidate degradation loop:

```text
anomaly or compromise signal
  -> Lemonade threat escalation
  -> Loader policy change
  -> BAL lane redistribution
  -> MCE/VoxMesh perturbation
  -> Vault records degradation event
  -> simulator measures reachability/latency/leakage impact
```

Success criterion:

```text
A compromised local observation should not automatically provide global reconstruction ability.
```

Failure criterion:

```text
A single compromised node with current state can predict future routing or reconstruct enough metadata to defeat structural divergence.
```

---

## 9. NLnet-facing milestone summary

### Completed

```text
v0.4.3 tested MVP framework
104 passing tests
9 regression tests
full integration pipeline
benchmark scripts
threat model
whitepaper
```

### Next

```text
v0.5 reproducibility and documentation
v0.6 topology simulation
v0.7 baseline comparison
v0.8 hardening and review candidate
```

### Correct claim

```text
WHISPER Remote Nerve is a tested experimental MVP framework exploring structural-divergence-based resilient communication.
```

### Incorrect claim

```text
WHISPER Remote Nerve is currently a secure or anonymous communication protocol.
```
