# PHASE2_VALIDATION_CRITERIA.md

## WHISPER Remote Nerve — Phase 2 Validation Criteria

**Current baseline:** v0.4.3  
**Phase covered:** v0.6.x → v0.8.x  
**Document status:** review-grade validation criteria  
**Audience:** NLnet, Protocol Labs, external reviewers, future maintainers  

---

## 1. Purpose

This document defines the measurable criteria required to move WHISPER Remote Nerve from:

```text
tested local MVP
```

to:

```text
empirically evaluated research framework
```

The current v0.4.3 release demonstrates functional integration:

```text
104 passing tests
9 regression tests
end-to-end full pipeline
benchmark scripts
threat model
whitepaper
roadmap
security policy
```

However, v0.4.3 does **not** demonstrate network-level resilience.

Phase 2 must determine whether WHISPER’s local structural-divergence mechanisms produce measurable effects under simulated decentralized network conditions.

This document defines:

```text
what must be measured
how it must be measured
what counts as success
what counts as failure
what outputs must be reproducible
what claims are allowed
what claims remain forbidden
```

---

## 2. Core research question

The core Phase 2 question is:

```text
Does local structural divergence produce measurable network-level diversity and
resilience under adversarial decentralized topology conditions?
```

This question must be evaluated empirically.

It must not be assumed from the architecture.

---

## 3. Current claim boundary

### Allowed claim for v0.4.3

```text
WHISPER Remote Nerve v0.4.3 is a tested experimental MVP framework.
```

### Forbidden claim for v0.4.3

```text
WHISPER Remote Nerve v0.4.3 is a secure, anonymous, or metadata-protecting
communication protocol.
```

### Allowed Phase 2 goal

```text
Phase 2 will test whether WHISPER-style structural divergence produces measurable
effects compared to simplified baselines under simulated adversarial topologies.
```

### Forbidden Phase 2 goal

```text
Phase 2 will prove WHISPER is secure.
```

---

## 4. Validation philosophy

Phase 2 must be falsifiable.

A negative result is acceptable.

The project should be considered scientifically useful if it can answer one of the following:

```text
A. structural divergence improves one or more metrics under defined conditions;
B. structural divergence fails under topology constraints, and the failure mode is documented;
C. structural divergence improves diversity but introduces unacceptable overhead;
D. structural divergence is useful only under narrow topology/adversary assumptions.
```

The project must not hide negative findings.

A reproducible negative result is still a contribution.

---

## 5. Phase 2 timeline realism

The previous six-week estimate should be treated as an optimistic minimum viable simulator target.

A more realistic schedule is:

```text
6 weeks      minimum viable simulator
8–12 weeks   credible simulation and baseline comparison
12–16 weeks  review-quality evaluation with iteration and reporting
```

### Six-week milestone

The six-week milestone should include:

```text
basic topology generation
basic path sampling
at least 3 topology families
at least 2 adversary models
initial WHISPER policy mapping
JSON output
first path-overlap metrics
```

### Eight-to-twelve-week milestone

The 8–12 week milestone should include:

```text
baseline models
state-to-path mapping validation
repeated seeded runs
CSV/JSON aggregation
success/failure classification
first simulation report
```

### Twelve-to-sixteen-week milestone

The 12–16 week milestone should include:

```text
review-quality report
updated whitepaper
updated threat model
reproducible artifact bundle
clear positive/negative findings
external-review-ready documentation
```

---

## 6. Scope tiers

To avoid over-promising, Phase 2 is split into three tiers.

### Tier 1 — Minimum viable simulator

Goal:

```text
Prove that deterministic topology simulation is possible.
```

Required:

```text
3 topology families
2 adversary models
3 primary metrics
deterministic JSON output
seeded reproducibility
```

Minimum topologies:

```text
Erdős–Rényi random graph
Barabási–Albert scale-free graph
Watts–Strogatz small-world graph
```

Minimum adversaries:

```text
random node compromise
targeted high-degree node compromise
```

Minimum metrics:

```text
path_overlap
unique_path_ratio
fragment_exposure_ratio
```

### Tier 2 — Credible comparison harness

Goal:

```text
Compare WHISPER-style policy against simplified baselines.
```

Required additions:

```text
single-path baseline
random multipath baseline
fixed-circuit abstraction
persistent-tunnel abstraction
repeated seeded runs
baseline comparison JSON/CSV
```

### Tier 3 — Grant/reviewer-quality evaluation

Goal:

```text
Produce evidence suitable for NLnet, Protocol Labs, and external review.
```

Required additions:

```text
simulation report
plots or tables
updated threat model
updated whitepaper
updated benchmarks
explicit limitations
positive/negative outcomes
artifact reproducibility notes
```

---

## 7. Network realism requirements

The simulator must model enough decentralized-network behavior to make the results meaningful.

Minimum node fields:

```text
node_id
online_probability
nat_type
bandwidth_class
region
is_relay_capable
is_compromised
```

Allowed `nat_type` values:

```text
public
restricted
symmetric
relay_required
```

Allowed `bandwidth_class` values:

```text
low
medium
high
```

Minimum edge fields:

```text
source
target
latency_ms
jitter_ms
packet_loss
bandwidth_weight
is_compromised
```

Minimum realism models:

```text
churn model
NAT reachability model
latency distribution
packet loss model
bandwidth class model
relay capability model
```

### Churn model

Minimum implementation:

```text
node_online = seeded_random(time_step, node_id) < online_probability
```

Metrics:

```text
path availability
reroute count
failed fragment ratio
```

### NAT model

Minimum implementation:

```text
public nodes can connect directly
restricted nodes require compatible peers
symmetric nodes often require relay
relay_required nodes must use relay-capable path
```

This is a simplified model, not a full NAT traversal emulator.

### Latency model

Minimum implementation:

```text
path_latency = sum(edge.latency_ms) + jitter + relay_penalty
```

### Packet loss model

Minimum implementation:

```text
path_success_probability = product(1 - edge.packet_loss)
```

---

## 8. State-to-path mapping validation

The key methodological gap is:

```text
MCE/VoxMesh state divergence is local.
Network path diversity is topological.
```

Different MCE/VoxMesh states do not automatically imply different network paths.

Phase 2 must validate the mapping explicitly.

Initial mapping policy:

```text
state_material = hash(MCE_state || VoxMesh_state || fragment_id)
candidate_paths = PathSampler.sample_paths(topology, source, target, k)
selected_path = Policy.select(candidate_paths, state_material)
```

Required metrics:

```text
state_distance
path_distance
state_to_path_correlation
path_overlap
unique_path_ratio
lane_collapse_rate
```

### State distance

Initial definition:

```text
Hamming distance between per-fragment state hashes
```

### Path distance

Initial definition:

```text
1 - Jaccard similarity between edge sets or node sets
```

### Path overlap

Initial definition:

```text
shared_edges(path_a, path_b) / min(len(path_a), len(path_b))
```

### Unique path ratio

Initial definition:

```text
unique_paths / total_fragments
```

### State-to-path correlation

Initial definition:

```text
correlation(state_distance, path_distance)
```

If state distance is high but path distance remains low, then local structural divergence is not translating into topology-level diversity.

---

## 9. Lane-to-path collapse testing

BAL lanes are currently in-memory abstractions.

They do not prove real path diversity.

Phase 2 must explicitly test whether multiple BAL lanes collapse to identical or highly overlapping network paths.

Required metrics:

```text
lane_collapse_rate
mean_path_overlap
shared_edge_ratio
shared_node_ratio
unique_path_ratio
```

### Lane collapse rate

Initial definition:

```text
duplicate_or_highly_overlapping_lane_paths / total_lanes
```

A lane pair is considered collapsed if:

```text
path_overlap >= 0.85
```

### Collapse interpretation

Low collapse:

```text
lane_collapse_rate <= 0.15
```

Moderate collapse:

```text
0.15 < lane_collapse_rate <= 0.40
```

High collapse:

```text
lane_collapse_rate > 0.40
```

High lane collapse is a serious failure mode.

It means local lane diversity does not map to network path diversity.

---

## 10. VoxMesh fractal-count validation

The current MVP uses:

```text
fractal_count = 36
```

This is an MVP default, not a proven optimum.

Phase 2 must make `fractal_count` tunable.

Required test values:

```text
4
16
36
64
256
```

Optional values:

```text
8
128
512
```

Required metrics per fractal count:

```text
mutation_cost
memory_cost
state_uniqueness
state_to_path_correlation
unique_path_ratio
lane_collapse_rate
fragment_reconstruction_probability
latency_overhead
bandwidth_overhead
```

### Interpretation

If 4 or 16 performs similarly to 36:

```text
36 is likely overkill for default configuration.
```

If 36 provides a useful tradeoff:

```text
36 can remain the default.
```

If 64 or 256 improves metrics significantly within overhead limits:

```text
fractal_count should become adaptive or configurable.
```

If fractal count does not affect network metrics:

```text
VoxMesh may not contribute to network-level resilience.
```

This must be reported honestly.

---

## 11. Baseline definitions

Baselines must be simplified abstractions with explicit parameters.

They must not be described as full Tor, I2P, mixnet, or OT implementations.

### Baseline A — single-path direct transport

```text
all fragments use one shortest path
path lifetime = entire payload
```

Expected:

```text
low overhead
high correlation
poor diversity
```

### Baseline B — random multipath

```text
each fragment selects one random candidate path
no state evolution
```

Expected:

```text
better diversity than single path
no adaptive state evolution
```

### Baseline C — fixed-circuit abstraction

Tor-style abstraction, not Tor.

Parameters:

```text
path_length
circuit_lifetime
relay_selection_policy
```

Behavior:

```text
select path of length N
reuse for circuit_lifetime fragments
```

### Baseline D — persistent-tunnel abstraction

I2P-style abstraction, not I2P.

Parameters:

```text
inbound_tunnel_length
outbound_tunnel_length
tunnel_lifetime
```

Behavior:

```text
select inbound/outbound tunnel pair
reuse for tunnel_lifetime fragments
```

### Baseline E — batch-delay abstraction

Mixnet-style abstraction, not a real mixnet.

Parameters:

```text
batching_window
delay_distribution
batch_size
```

Behavior:

```text
batch fragments
apply delay distribution
forward after batching window
```

### Baseline F — static-zone abstraction

OT segmentation abstraction.

Parameters:

```text
zone_count
allowed_zone_edges
boundary_compromise_rate
```

Behavior:

```text
routes constrained by fixed allowed zones
```

### Fairness rules

Every baseline must use:

```text
same topology
same source/target pairs
same adversary model
same payload size
same fragment count
same repeated run count
same latency model
same packet loss model
```

---

## 12. Primary metrics

Primary metrics determine whether Phase 2 produced meaningful evidence.

### Fragment reconstruction probability

Definition:

```text
probability that an adversary can reconstruct enough fragments or metadata
to link or rebuild a communication flow under a defined scenario
```

### Mean path overlap

Definition:

```text
average shared path fraction across fragment paths
```

### Unique path ratio

Definition:

```text
unique paths / total fragment paths
```

### Metadata exposure estimate

Definition:

```text
fraction of routing or fragment metadata visible to adversary-controlled nodes
```

---

## 13. Secondary metrics

Secondary metrics constrain whether a result is practical.

```text
latency_estimate_ms
bandwidth_overhead_ratio
route_churn
degradation_frequency
false_positive_rate
blocked_fragment_rate
failed_fragment_ratio
```

A policy that improves diversity but introduces unrealistic overhead should not be treated as a strong result.

---

## 14. Success thresholds

The phrase “improves resilience” is too vague.

Phase 2 uses numerical thresholds.

### Minimum positive outcome

A result is minimally positive if WHISPER-style policy improves at least one primary metric by:

```text
>= 10% relative improvement
```

against at least one baseline, under at least two topology/adversary combinations, while keeping overhead within:

```text
latency <= 2x baseline
bandwidth <= 2x baseline
```

### Strong positive outcome

A result is strong if WHISPER-style policy improves at least one primary metric by:

```text
>= 25% relative improvement
```

against baseline, under at least three topology/adversary combinations, while keeping overhead within:

```text
latency <= 2x baseline
bandwidth <= 2x baseline
```

### High-impact positive outcome

A result is high-impact if WHISPER-style policy improves one or more primary metrics by:

```text
>= 50% relative improvement
```

under multiple topologies and adversaries, while keeping overhead within:

```text
latency <= 3x baseline
bandwidth <= 3x baseline
```

### Scientifically interesting but weak outcome

```text
3–9% improvement under narrow conditions
```

This is worth documenting, but should not be sold as a strong funder-visible success.

---

## 15. Failure thresholds

Phase 2 should explicitly identify failure.

### Mapping failure

```text
unique_path_ratio < 0.15
mean_path_overlap > 0.85
state_to_path_correlation <= 0.05
```

Interpretation:

```text
local state divergence does not map to network diversity.
```

### Lane collapse failure

```text
lane_collapse_rate > 0.40
```

Interpretation:

```text
BAL lanes collapse to overlapping paths under topology constraints.
```

### Overhead failure

```text
latency > 3x baseline
bandwidth > 3x baseline
```

Interpretation:

```text
divergence is too expensive for practical use.
```

### Compromise failure

```text
single compromised node with current state predicts future routing or reconstructs
fragment flow with no meaningful degradation signal
```

Interpretation:

```text
assume-compromise posture is not producing graceful degradation.
```

---

## 16. Graceful degradation validation

The intended graceful-degradation property is not:

```text
a compromised node learns nothing
```

That is unrealistic.

The intended property is:

```text
a compromised local observation should not automatically provide global
reconstruction ability.
```

Minimum compromise cases:

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

Required metrics:

```text
time_to_reconstruction
fragments_exposed_before_degradation
latency_increase_after_degradation
path_overlap_after_degradation
blocked_or_rerouted_fragment_ratio
```

Minimum positive degradation behavior:

```text
>= 10% reduction in exposed fragments before reconstruction
```

Strong degradation behavior:

```text
>= 25% reduction in exposed fragments before reconstruction
```

---

## 17. Machine-readable outputs

Phase 2 must publish stable machine-readable outputs.

Minimum schemas:

```text
simulation_run.schema.json
metrics_report.schema.json
topology_graph.schema.json
baseline_comparison.schema.json
```

Minimum output files per experiment batch:

```text
simulation_run.json
metrics_report.json
topology_graph.json
baseline_comparison.csv
experiment_manifest.json
```

Required metadata:

```text
schema_version
experiment_id
seed
topology type
topology parameters
adversary model
policy name
baseline name
payload size
fragment count
metrics
timestamp
software version
git commit
```

Optional future publication:

```text
IPFS-published simulation bundles
IPLD-compatible experiment manifests
content-addressed benchmark artifacts
```

---

## 18. Reproducibility requirements

A result is not acceptable unless it can be reproduced from:

```text
git commit
seed
topology config
adversary config
policy config
baseline config
payload config
software version
```

Minimum reproducibility command:

```bash
nix develop
python3 simulation_runner_v01.py --config experiments/example.json
```

Minimum validation command:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 19. Reporting rules

Every reported result must include:

```text
topology
adversary
baseline
policy
seed or seed range
number of repeated runs
mean
median
min/max or confidence interval
overhead
limitations
```

Claims should be phrased like:

```text
Under topology T and adversary A, WHISPER policy P reduced metric M by X%
relative to baseline B, with Y overhead.
```

Avoid:

```text
WHISPER is secure.
WHISPER beats Tor.
WHISPER prevents metadata leakage.
```

---

## 20. Protocol Labs-facing interpretation

Protocol Labs reviewers are likely to value:

```text
machine-readable artifacts
decentralized topology realism
state-to-path validation
libp2p feasibility PoC
negative-result honesty
baseline fairness
```

Minimum Protocol Labs-visible outcome:

```text
JSON simulation outputs
baseline comparison
state-to-path mapping metrics
churn/NAT/latency model
libp2p lane-to-stream PoC plan or prototype
```

Strong Protocol Labs-visible outcome:

```text
published positive or negative results
content-addressed simulation artifacts
clear topology/adversary limits
reusable simulator code
```

---

## 21. NLnet-facing interpretation

NLnet reviewers are likely to value:

```text
open-source infrastructure
security-boundary clarity
public-interest research
reproducibility
responsible non-overclaiming
```

Minimum NLnet-visible outcome:

```text
threat model
whitepaper
roadmap
reproducible test environment
simulation plan
baseline comparison plan
```

Strong NLnet-visible outcome:

```text
published simulator
documented experiments
updated threat model
clear security boundaries
negative results accepted
```

---

## 22. Decision points

### After Tier 1

Question:

```text
Can deterministic topology simulation run and produce meaningful path metrics?
```

If no:

```text
reduce scope or pivot to simulation tooling.
```

### After Tier 2

Question:

```text
Does WHISPER-style policy improve any metric against baselines?
```

If no:

```text
publish negative result and document failure mode.
```

### After Tier 3

Question:

```text
Is the architecture worth hardening or integrating with decentralized runtimes?
```

If yes:

```text
begin Rust/WASM and libp2p/Reticulum bridge track.
```

If no:

```text
archive as research prototype or pivot to reusable simulator.
```

---

## 23. Final Phase 2 statement

Recommended statement:

```text
Phase 2 will implement a reproducible topology simulator and baseline comparison
framework. The first milestone is a minimum viable simulator in approximately
six weeks. A credible adversarial evaluation is expected to take eight to twelve
weeks, and a review-quality evaluation with iteration may require twelve to
sixteen weeks. Success will be measured through explicit thresholds: at least
10% relative improvement for a minimum positive result, 25% for a strong result,
and 50% for a high-impact result, subject to latency and bandwidth overhead
limits. Negative results will be published and treated as valid research outcomes.
```

---

## 24. Final note

The purpose of Phase 2 is not to confirm WHISPER.

The purpose of Phase 2 is to test WHISPER.

The project should be designed to discover the truth, not to defend the architecture.
