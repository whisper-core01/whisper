# RESEARCH_PLAN.md

## WHISPER Remote Nerve — Research Plan

**Current status:** v0.4.3 tested MVP  
**Research objective:** evaluate structural divergence as a resilience primitive  

---

## 1. Research question

Primary question:

```text
Can structural divergence improve resilience in decentralized communication
pipelines under adversarial network conditions?
```

Sub-questions:

```text
Does local state divergence produce network path diversity?
Can adversaries reconstruct fragmented flows under partial compromise?
Can graceful degradation reduce exposure after anomaly signals?
How does the model compare to simplified existing baselines?
What latency and bandwidth overhead does it introduce?
```

---

## 2. Hypothesis

The working hypothesis is:

```text
A pipeline combining per-fragment state evolution, lane distribution, anomaly
scoring, and topology-aware path selection may reduce reconstruction probability
under some adversarial conditions.
```

This is not yet proven.

The project is explicitly open to negative results.

---

## 3. Methodology

Phase 1 produced:

```text
tested local MVP
component boundaries
full pipeline
regression suite
threat model
whitepaper
```

Phase 2 will produce:

```text
topology simulator
adversarial scenarios
baseline comparisons
metrics reports
reproducible outputs
```

Phase 3 may produce:

```text
Rust/WASM hardening
real transport bridge experiments
libp2p/Reticulum compatibility experiments
external review candidate
```

---

## 4. Experimental variables

Independent variables:

```text
topology type
node count
edge density
adversary type
compromise fraction
fragment count
route count
lane policy
degradation policy
```

Dependent variables:

```text
reachability
latency estimate
path overlap
fragment exposure
reconstruction probability
bandwidth overhead
blocked fragment rate
degradation frequency
```

---

## 5. Baselines

Baselines should include:

```text
single-path direct transport
random multipath
fixed circuit model
persistent tunnel model
mixnet batching/delay model
static segmentation model
```

The goal is comparison, not replacement claims.

---

## 6. Evaluation principle

Every claim should be tied to:

```text
a topology
an adversary model
a metric
a seed
a reproducible run
```

Avoid claims such as:

```text
WHISPER is secure
WHISPER is anonymous
WHISPER beats Tor
WHISPER prevents metadata leakage
```

Prefer claims such as:

```text
Under topology T and adversary A, policy P reduced metric M by X compared to baseline B.
```

---

## 7. Expected outputs

Research outputs:

```text
simulation framework
experiment JSON files
metrics reports
baseline comparisons
updated threat model
updated whitepaper
simulation report
```

Potential publication outputs:

```text
technical report
workshop paper
grant report
open dataset
reproducible benchmark bundle
```

---

## 8. Protocol Labs alignment

Protocol Labs-facing value:

```text
decentralized topology simulation
adversarial network models
machine-readable experiment outputs
resilience metrics
insights for libp2p-style systems
```

Potential future integrations:

```text
libp2p stream experiments
IPLD-compatible experiment metadata
IPFS storage of simulation artifacts
content-addressed benchmark bundles
```

These are future directions, not current claims.

---

## 9. NLnet alignment

NLnet-facing value:

```text
open-source infrastructure research
security-boundary transparency
public-interest resilient communication research
reproducible development environment
responsible non-overclaiming
```

---

## 10. Research risks

Key risks:

```text
structural divergence may not map to network diversity
Sybil-style adversaries may collapse diversity
latency or bandwidth overhead may be too high
metrics may be hard to interpret
simulation may not generalize to real networks
```

These risks should be documented, not hidden.

---

## 11. Decision points

After v0.6:

```text
Does simulation infrastructure work?
Are metrics meaningful?
```

After v0.7:

```text
Do baselines reveal useful tradeoffs?
Does WHISPER outperform any baseline under any condition?
Does it fail clearly under specific adversaries?
```

After v0.8:

```text
Is the architecture worth hardening?
Should work continue toward Rust/WASM or transport integration?
Should the project pivot toward simulation tooling only?
```

---

## 12. Correct research posture

Correct:

```text
WHISPER is an experimental framework for studying structural divergence in
decentralized communication pipelines.
```

Incorrect:

```text
WHISPER is already a secure decentralized communication protocol.
```
