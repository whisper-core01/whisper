# PROTOCOL_LABS_ALIGNMENT.md

## WHISPER Remote Nerve — Protocol Labs Alignment

**Current baseline:** v0.4.3  
**Status:** tested experimental MVP framework  
**Security status:** not a secure communication protocol  
**Primary research axis:** structural divergence for resilient decentralized communication  

---

## 1. Summary

WHISPER Remote Nerve is an experimental open research framework for evaluating whether **structural divergence** can become a measurable primitive for resilient decentralized communication.

The project is currently a Python MVP with:

```text
104 passing tests
9 regression tests
end-to-end full pipeline
benchmark scripts
threat model
whitepaper
roadmap
Nix reproducibility baseline
```

The current MVP does not claim to provide security, anonymity, or transport protection.

Its purpose is to provide a tested foundation for the next phase:

```text
reproducible topology simulation
adversarial network evaluation
baseline comparison
machine-readable metrics
selective implementation hardening
```

---

## 2. Why this may matter to Protocol Labs

Protocol Labs focuses on decentralized networks, open protocols, verifiable systems, resilient infrastructure, and research artifacts that can be reused by broader ecosystems.

WHISPER is relevant to this space because it explores:

```text
resilience under compromise
fragment-level routing behavior
adaptive path selection
metadata exposure measurement
adversarial topology simulation
decentralized communication failure modes
machine-readable network experiments
```

The key research question is:

```text
Can local structural divergence produce measurable network-level resilience
in decentralized communication systems?
```

---

## 3. Relationship to libp2p / IPFS / Filecoin ecosystems

WHISPER is not currently integrated with libp2p, IPFS, IPLD, or Filecoin.

It should not be presented as a replacement for these systems.

A correct positioning is:

```text
WHISPER can be evaluated as an experimental layer above, beside, or in simulation
against libp2p-style transports.
```

Potential future integration surfaces:

```text
libp2p stream abstraction
libp2p peer routing experiments
IPLD-compatible simulation reports
content-addressed benchmark artifacts
Filecoin/IPFS storage of simulation outputs
Bitswap-like or Graphsync-like transfer pattern baselines
```

These are future compatibility targets, not current claims.

---

## 4. What WHISPER is not

WHISPER Remote Nerve v0.4.3 is not:

```text
a libp2p protocol
an IPFS protocol
a Filecoin protocol
a Reticulum implementation
a secure messaging protocol
an anonymous network
a consensus protocol
a cryptographic protocol
a production transport
```

It is currently:

```text
a tested local MVP framework
a modular simulation foundation
an architecture for studying structural divergence
```

---

## 5. Current implementation evidence

Current components:

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

Current validation:

```text
Full test suite:        104 passed
Regression suite:       9 passed
FullPipeline smoke:     OK
FullPipeline benchmark: OK
```

Reference benchmark:

```text
Payload size:       1 MiB
Fragment count:     1024
Elapsed:            ~0.77 s
Throughput:         ~1.30 MB/s
```

---

## 6. Research contribution hypothesis

The research hypothesis is not:

```text
WHISPER is already more secure than existing decentralized transports.
```

The research hypothesis is:

```text
Structural divergence can be measured, simulated, and evaluated as a resilience
primitive under adversarial decentralized network conditions.
```

The project aims to test whether a pipeline that combines:

```text
state evolution
per-fragment decisions
parallel lane abstraction
fractal state diversity
anomaly detection
bridge encapsulation
regression-locked execution
```

can produce measurable differences in:

```text
path overlap
fragment reconstruction probability
metadata exposure
degradation behavior
route diversity
latency / overhead tradeoffs
```

---

## 7. Phase 2 alignment with Protocol Labs-style research

Phase 2 should generate reusable research artifacts:

```text
topology simulator
adversary models
baseline models
JSON experiment outputs
CSV summaries
reproducible seeds
benchmark harness
Nix reproducibility
plots/tables
updated whitepaper
updated threat model
```

These are stronger Protocol Labs signals than the current Python MVP alone.

The desired evolution:

```text
v0.4.3 — tested local MVP
v0.5.x — reproducible research environment
v0.6.x — topology simulator
v0.7.x — baseline comparison
v0.8.x — hardening and external-review candidate
```

---

## 8. Simulation focus

Protocol Labs reviewers are likely to care about whether the idea can be tested under realistic decentralized network assumptions.

Minimum topology families:

```text
Erdős–Rényi random graphs
Barabási–Albert scale-free graphs
Watts–Strogatz small-world graphs
hub-and-spoke industrial graphs
hybrid cloud-edge graphs
peer-to-peer churn graphs
```

Minimum adversarial scenarios:

```text
random node compromise
targeted hub compromise
bridge-node compromise
Sybil-style pseudo-diversity
colluding relay groups
traffic observer
partial partition
high-churn network
```

Minimum metrics:

```text
path overlap
route diversity
reachability
latency estimate
fragment reconstruction probability
metadata exposure estimate
bandwidth overhead
degradation frequency
false-positive rate
```

---

## 9. Machine-readable artifacts

To align with decentralized research norms, future outputs should be machine-readable.

Recommended output formats:

```text
simulation_run.json
metrics_report.json
topology_graph.json
baseline_comparison.csv
benchmark_results.json
regression_report.json
```

Optional future content addressing:

```text
store simulation artifacts via IPFS
represent experiment metadata as IPLD-compatible JSON
hash benchmark artifacts for reproducibility
```

These are future directions, not current implementation claims.

---

## 10. Potential Protocol Labs value

WHISPER may be valuable if Phase 2 can produce:

```text
a reusable adversarial topology simulator
a methodology for measuring structural divergence
baseline comparison data
open datasets of simulation outputs
new failure-mode insights for decentralized transports
clear evidence for or against the architecture
```

A negative result is still useful if it shows that local divergence does not translate into network-level resilience.

---

## 11. Correct Protocol Labs-facing statement

Correct:

```text
WHISPER Remote Nerve is a tested experimental MVP framework for studying
structural divergence and graceful degradation in decentralized communication
pipelines. The next phase focuses on reproducible adversarial topology simulation
and baseline comparison.
```

Incorrect:

```text
WHISPER Remote Nerve is a secure decentralized transport protocol.
```

---

## 12. Open questions

The project should be evaluated through open research questions:

```text
Does local structural divergence survive topology constraints?
Can Sybil-style pseudo-diversity collapse the model?
Does state evolution reduce reconstruction probability?
Can graceful degradation be measured after partial compromise?
What is the latency/bandwidth cost of structural divergence?
Can the model produce reusable insights for libp2p-style transports?
```

These questions define the next phase.
