# SIMULATION_REPORT.md

## WHISPER Remote Nerve — Phase 2 Simulation Report

**Report status:** template / to be completed after Phase 2 experiments  
**Target release:** v0.7.x / v0.8.x  
**Current baseline:** v0.4.3  
**Security status:** not a secure communication protocol  

---

## 1. Executive summary

This report summarizes Phase 2 simulation results for WHISPER Remote Nerve.

The purpose of the simulation phase is to evaluate whether WHISPER-style local structural divergence produces measurable network-level effects under adversarial decentralized topology conditions.

The simulation does not attempt to prove that WHISPER is secure.

It evaluates whether the architecture shows measurable effects against defined baselines under controlled conditions.

### Summary result

To be completed after experiments.

```text
Primary outcome: TODO
Positive / negative / mixed: TODO
Strongest metric improvement: TODO
Largest failure mode: TODO
Recommended next step: TODO
```

### Claim boundary

Allowed claim format:

```text
Under topology T and adversary A, WHISPER policy P changed metric M by X%
relative to baseline B, with Y overhead.
```

Forbidden claim format:

```text
WHISPER is secure.
WHISPER is anonymous.
WHISPER prevents metadata leakage.
WHISPER beats Tor.
WHISPER scales to decentralized networks.
```

---

## 2. Report metadata

```text
Report version: TODO
WHISPER version: TODO
Git commit: TODO
Simulation code version: TODO
Schema version: TODO
Date: TODO
Author(s): TODO
Machine / environment: TODO
Nix flake revision: TODO
```

Reproducibility command:

```bash
nix develop
python3 simulation_runner_v01.py --config experiments/TODO.json
```

Validation command:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## 3. Research questions

Primary question:

```text
Does local structural divergence produce measurable network-level diversity and
resilience under adversarial decentralized topology conditions?
```

Secondary questions:

```text
Does state divergence map to path divergence?
Do BAL lanes collapse to overlapping paths?
Does VoxMesh fractal_count affect measurable outcomes?
Does WHISPER reduce path overlap against baselines?
Does WHISPER reduce fragment reconstruction probability?
What latency and bandwidth overhead does it introduce?
Does graceful degradation help after partial compromise?
Do results survive churn, NAT constraints, latency, and packet loss?
```

---

## 4. Experimental scope

### Included

```text
topology generation
path sampling
WHISPER policy mapping
adversary models
baseline models
state-to-path validation
lane collapse measurement
fragment reconstruction estimate
metadata exposure estimate
latency estimate
bandwidth overhead estimate
machine-readable JSON outputs
```

### Excluded

```text
real network deployment
real libp2p production integration
real Reticulum integration
full Tor implementation
full I2P implementation
full mixnet implementation
cryptographic security proof
packet-level network emulation
formal verification
```

---

## 5. Implemented simulator model

### Node model

Fields:

```text
node_id
online_probability
nat_type
bandwidth_class
region
is_relay_capable
is_compromised
```

NAT classes:

```text
public
restricted
symmetric
relay_required
```

Bandwidth classes:

```text
low
medium
high
```

### Edge model

Fields:

```text
source
target
latency_ms
jitter_ms
packet_loss
bandwidth_weight
is_compromised
```

### Churn model

```text
node_online = seeded_random(time_step, node_id) < online_probability
```

### Latency model

```text
path_latency = sum(edge.latency_ms) + jitter + relay_penalty
```

### Packet loss model

```text
path_success_probability = product(1 - edge.packet_loss)
```

### Notes

Document deviations from the planned model here.

```text
TODO
```

---

## 6. Topologies evaluated

| Topology | Node count | Edge count | Parameters | Included? |
|---|---:|---:|---|---|
| Erdős–Rényi | TODO | TODO | TODO | TODO |
| Barabási–Albert | TODO | TODO | TODO | TODO |
| Watts–Strogatz | TODO | TODO | TODO | TODO |
| Hub-and-spoke | TODO | TODO | TODO | TODO |
| Hybrid cloud-edge | TODO | TODO | TODO | TODO |
| P2P churn graph | TODO | TODO | TODO | TODO |

For each topology, record:

```text
seed
node count
edge count
degree distribution
latency distribution
packet loss distribution
NAT distribution
churn distribution
```

---

## 7. Adversary models evaluated

| Adversary | Description | Included? |
|---|---|---|
| Random node compromise | Random compromised node subset | TODO |
| Targeted high-degree compromise | Compromise hubs / high-degree nodes | TODO |
| Bridge-node compromise | Compromise bridge/lane endpoints | TODO |
| Colluding relay group | Multiple compromised relays share observations | TODO |
| Sybil-style pseudo-diversity | Adversary creates apparent path diversity | TODO |
| Passive traffic observer | Observes timing/path metadata | TODO |
| Partial network partition | Reduces available paths | TODO |
| High-churn adversary | Induces or exploits churn | TODO |

For each adversary, define:

```text
compromise fraction
selection strategy
observation capability
active capability
collusion capability
duration
```

---

## 8. Baselines evaluated

Baselines are simplified abstractions, not full protocol implementations.

| Baseline | Parameters | Included? |
|---|---|---|
| Single-path direct transport | shortest path, whole payload | TODO |
| Random multipath | random candidate path per fragment | TODO |
| Fixed-circuit abstraction | path_length, circuit_lifetime | TODO |
| Persistent-tunnel abstraction | tunnel_length, tunnel_lifetime | TODO |
| Batch-delay abstraction | batching_window, delay_distribution | TODO |
| Static-zone abstraction | zone_count, allowed_zone_edges | TODO |

Fairness rules:

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

## 9. WHISPER policy evaluated

Document the exact WHISPER policy configuration.

```text
policy_name: TODO
route_count: TODO
fractal_count: TODO
state_material: TODO
path_sampler: TODO
candidate_paths: TODO
lane_policy: TODO
degradation_policy: TODO
```

Initial mapping policy:

```text
state_material = hash(MCE_state || VoxMesh_state || fragment_id)
candidate_paths = PathSampler.sample_paths(topology, source, target, k)
selected_path = Policy.select(candidate_paths, state_material)
```

Document any changes:

```text
TODO
```

---

## 10. Machine-readable artifacts

Every experiment batch should produce:

```text
experiment_manifest.json
topology_graph.json
simulation_run.json
metrics_report.json
baseline_comparison.csv
baseline_comparison.json
```

Schema files:

```text
schemas/simulation_run.schema.json
schemas/metrics_report.schema.json
schemas/topology_graph.schema.json
schemas/baseline_comparison.schema.json
```

Optional content-addressed publication:

```text
IPFS CID: TODO
artifact bundle hash: TODO
```

---

## 11. Metrics

### Primary metrics

```text
fragment_reconstruction_probability
mean_path_overlap
unique_path_ratio
metadata_exposure_estimate
```

### Mapping metrics

```text
state_distance
path_distance
state_to_path_correlation
lane_collapse_rate
shared_edge_ratio
shared_node_ratio
```

### Secondary metrics

```text
latency_estimate_ms
bandwidth_overhead_ratio
route_churn
degradation_frequency
false_positive_rate
blocked_fragment_rate
failed_fragment_ratio
```

---

## 12. Success thresholds

### Minimum positive outcome

```text
>= 10% relative improvement against at least one baseline
under at least two topology/adversary combinations
```

Overhead limit:

```text
latency <= 2x baseline
bandwidth <= 2x baseline
```

### Strong positive outcome

```text
>= 25% relative improvement against baseline
under at least three topology/adversary combinations
```

Overhead limit:

```text
latency <= 2x baseline
bandwidth <= 2x baseline
```

### High-impact positive outcome

```text
>= 50% relative improvement under multiple topologies and adversaries
```

Overhead limit:

```text
latency <= 3x baseline
bandwidth <= 3x baseline
```

### Weak but scientifically interesting

```text
3–9% improvement under narrow conditions
```

### Failure conditions

```text
unique_path_ratio < 0.15
mean_path_overlap > 0.85
state_to_path_correlation <= 0.05
lane_collapse_rate > 0.40
latency > 3x baseline
bandwidth > 3x baseline
```

---


## 12.1 Statistical methodology

Simulation results must be reported with variance, not only point estimates.

Phase 2 results should distinguish between:

```text
observed metric difference
statistical uncertainty
practical significance
reviewer-visible effect size
```

A single run is not sufficient to support a claim.

### Repeated runs

Minimum repeated runs per condition:

```text
n = 30 runs per topology/adversary/policy/baseline condition
```

Recommended repeated runs for reviewer-facing results:

```text
n = 100 runs per condition
```

High-confidence or noisy conditions:

```text
n = 300+ runs per condition
```

A “condition” is defined as:

```text
topology type
topology parameters
adversary model
compromise fraction
policy or baseline
payload size
fragment count
```

Each run must use a distinct reproducible seed.

Example:

```text
seed = hash(experiment_id || condition_id || run_index)
```

### Required summary statistics

For every primary metric, report:

```text
mean
median
standard deviation
minimum
maximum
95% confidence interval
number of runs
```

For skewed distributions, also report:

```text
p25
p75
p95
```

### Confidence intervals

Default reporting:

```text
95% confidence interval for the mean
```

Recommended implementation:

```text
bootstrap confidence intervals with at least 1,000 bootstrap samples
```

Acceptable simpler implementation for early v0.6 results:

```text
mean ± 1.96 * standard_error
```

Where:

```text
standard_error = standard_deviation / sqrt(n)
```

### Significance testing

For comparing WHISPER policy against a baseline:

```text
primary: bootstrap difference in means or medians
secondary: Mann-Whitney U test for non-normal distributions
optional: paired test if runs share the same topology/adversary seeds
```

A result should not be called statistically significant unless:

```text
p < 0.05
```

or the 95% confidence interval for the difference excludes zero.

### Practical significance

Statistical significance alone is not enough.

A result must also satisfy the practical thresholds defined in this report:

```text
>= 10% relative improvement for minimum positive result
>= 25% relative improvement for strong positive result
>= 50% relative improvement for high-impact result
```

with overhead constraints:

```text
latency <= 2x baseline for positive/strong result
bandwidth <= 2x baseline for positive/strong result
latency <= 3x baseline for high-divergence experimental mode
bandwidth <= 3x baseline for high-divergence experimental mode
```

### Multiple comparisons

If many topologies, adversaries, and baselines are tested, the report should avoid cherry-picking.

Minimum reporting rule:

```text
report all tested conditions, including negative and inconclusive results
```

Recommended correction for many comparisons:

```text
Benjamini-Hochberg false discovery rate control
```

Early v0.6 reports may skip formal correction, but must clearly state this limitation.

### Result classification

A result should be classified using both statistical and practical criteria.

| Statistical result | Practical threshold | Classification |
|---|---|---|
| significant | met | positive / strong / high-impact |
| significant | not met | statistically detectable but weak |
| not significant | met point estimate only | inconclusive |
| not significant | not met | negative or no evidence |
| worse than baseline | any | negative |

### Minimum reviewer-facing claim

A reviewer-facing claim should have:

```text
n >= 100 repeated runs per condition
95% confidence interval
effect size
baseline comparison
overhead measurement
all negative conditions reported
```

Without these, the claim should be described as preliminary.


## 12.2 Latency model limitations

The latency model in the first simulator is simplified.

Initial model:

```text
path_latency = sum(edge.latency_ms) + jitter + relay_penalty
```

This is a linear approximation.

It does not fully model:

```text
queueing dynamics
congestion collapse
TCP behavior
stream multiplexing effects
NAT traversal delays
relay saturation
backpressure
adaptive bitrate behavior
real libp2p stream scheduling
OS/network stack effects
```

Therefore, latency results must be interpreted as:

```text
relative simulation estimates
```

not as real-world deployment latency.

### What latency results can support

Allowed:

```text
Under the simulator’s latency model, WHISPER policy P increased estimated latency
by X relative to baseline B.
```

Forbidden:

```text
WHISPER will have X latency on real networks.
```

### Queueing limitation

Real networks often show non-linear behavior under load.

A path that appears acceptable under a linear latency model may perform poorly under queueing, congestion, or relay saturation.

Phase 2 should treat latency estimates as indicative unless a more advanced model is implemented.

### Recommended future latency extensions

Future simulator versions should consider:

```text
queue depth per node
relay saturation
bandwidth contention
burst traffic
stream multiplexing
retry behavior
backpressure
time-varying latency
```

### Reporting rule

Any table containing latency results must include this note:

```text
Latency estimates are simulator-level approximations and should not be treated
as deployment measurements.
```


## 12.3 Sample size and power planning

Phase 2 should not choose run counts arbitrarily.

The minimum number of repeated runs should be based on:

```text
target effect size
metric variance
desired statistical power
acceptable false-positive rate
```

Default planning target:

```text
alpha = 0.05
power = 0.80
minimum detectable effect = 10% relative improvement
```

### Practical default

Until real variance estimates exist, use:

```text
n = 100 runs per condition
```

This is the default reviewer-facing sample size.

### Pilot phase

Before large experiment batches, run a pilot:

```text
n = 30 runs per condition
```

Use the pilot to estimate:

```text
standard deviation
confidence interval width
metric skew
outlier frequency
runtime cost
```

Then adjust sample size.

### Detecting 10% effects

A 10% improvement should only be claimed if:

```text
the observed relative improvement is >= 10%
the 95% confidence interval excludes zero or p < 0.05
the overhead constraints are satisfied
the result appears in at least two topology/adversary combinations
```

### Detecting 25% or 50% effects

For large effects:

```text
25% improvement = strong
50% improvement = high-impact
```

These still require repeated runs and confidence intervals.

Large point estimates from small sample sizes should be reported as preliminary.

### Adaptive sample sizing

Recommended process:

```text
1. run n=30 pilot
2. estimate variance
3. calculate required n for 10% effect
4. cap initial reviewer batch at n=100 unless variance requires more
5. increase to n=300+ for noisy conditions or borderline claims
```

### Inconclusive outcomes

If confidence intervals are too wide to distinguish a 10% effect from noise:

```text
classification = inconclusive
```

Do not interpret inconclusive results as success.

### Reporting requirement

Every result table should include:

```text
n
mean
standard deviation
95% confidence interval
relative delta vs baseline
p-value or bootstrap interval
classification
```

## 13. Overall results

### Summary table

| Metric | WHISPER | Best baseline | Delta | Outcome |
|---|---:|---:|---:|---|
| Fragment reconstruction probability | TODO | TODO | TODO | TODO |
| Mean path overlap | TODO | TODO | TODO | TODO |
| Unique path ratio | TODO | TODO | TODO | TODO |
| Metadata exposure estimate | TODO | TODO | TODO | TODO |
| Latency estimate | TODO | TODO | TODO | TODO |
| Bandwidth overhead | TODO | TODO | TODO | TODO |

### Classification

```text
Positive / strong / high-impact / weak / negative / mixed: TODO
```

---

## 14. State-to-path mapping results

Report whether state divergence translated into path divergence.

| Topology | Adversary | State-to-path correlation | Unique path ratio | Mean path overlap | Mapping outcome |
|---|---|---:|---:|---:|---|
| TODO | TODO | TODO | TODO | TODO | TODO |

Interpretation:

```text
TODO
```

Key question:

```text
If MCE/VoxMesh states differ, do paths actually differ?
```

Answer:

```text
TODO
```

---

## 15. Lane collapse results

Report whether BAL lanes collapsed to identical or highly overlapping paths.

| Topology | Adversary | Route count | Lane collapse rate | Outcome |
|---|---|---:|---:|---|
| TODO | TODO | TODO | TODO | TODO |

Interpretation:

```text
TODO
```

A high collapse rate means local lane diversity did not translate into network diversity.

---

## 16. VoxMesh fractal-count results

Tested values:

```text
4
16
36
64
256
```

| Fractal count | Unique path ratio | Mean path overlap | Reconstruction probability | Latency overhead | Outcome |
|---:|---:|---:|---:|---:|---|
| 4 | TODO | TODO | TODO | TODO | TODO |
| 16 | TODO | TODO | TODO | TODO | TODO |
| 36 | TODO | TODO | TODO | TODO | TODO |
| 64 | TODO | TODO | TODO | TODO | TODO |
| 256 | TODO | TODO | TODO | TODO | TODO |

Interpretation:

```text
TODO
```

Conclusion about default fractal count:

```text
keep 36 / reduce / increase / make adaptive / remove from resilience claim: TODO
```

---

## 17. Graceful degradation results

Compromise scenarios:

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

| Scenario | Exposed fragments before degradation | Time to reconstruction | Degradation signal? | Outcome |
|---|---:|---:|---|---|
| C1 | TODO | TODO | TODO | TODO |
| C2 | TODO | TODO | TODO | TODO |
| C3 | TODO | TODO | TODO | TODO |
| C4 | TODO | TODO | TODO | TODO |
| C5 | TODO | TODO | TODO | TODO |
| C6 | TODO | TODO | TODO | TODO |
| C7 | TODO | TODO | TODO | TODO |
| C8 | TODO | TODO | TODO | TODO |

Interpretation:

```text
TODO
```

---

## 18. Baseline comparison results

### Single-path baseline

```text
TODO
```

### Random multipath baseline

```text
TODO
```

### Fixed-circuit abstraction

```text
TODO
```

### Persistent-tunnel abstraction

```text
TODO
```

### Batch-delay abstraction

```text
TODO
```

### Static-zone abstraction

```text
TODO
```

Overall baseline interpretation:

```text
TODO
```

---

## 19. Protocol Labs relevance

Report whether Phase 2 produced Protocol Labs-relevant artifacts.

| Artifact | Produced? | Notes |
|---|---|---|
| JSON simulation outputs | TODO | TODO |
| Baseline comparison | TODO | TODO |
| State-to-path mapping metrics | TODO | TODO |
| Churn/NAT/latency model | TODO | TODO |
| libp2p lane-to-stream PoC | TODO | TODO |
| IPFS/IPLD-compatible artifact bundle | TODO | TODO |

Interpretation:

```text
TODO
```

---

## 20. NLnet relevance

Report whether Phase 2 produced NLnet-relevant artifacts.

| Artifact | Produced? | Notes |
|---|---|---|
| Reproducible simulator | TODO | TODO |
| Updated threat model | TODO | TODO |
| Updated whitepaper | TODO | TODO |
| Baseline comparisons | TODO | TODO |
| Security-boundary updates | TODO | TODO |
| Public-interest research output | TODO | TODO |

Interpretation:

```text
TODO
```

---

## 21. Negative results

Negative results must be documented.

### Negative result summary

```text
TODO
```

### What failed?

```text
TODO
```

### Why did it fail?

```text
TODO
```

### Is the failure useful?

```text
TODO
```

### Recommended response

```text
continue / narrow scope / pivot to simulator tooling / abandon claim: TODO
```

---

## 22. Limitations

Known limitations of this simulation report:

```text
TODO
```

Possible limitations:

```text
simplified topology model
simplified NAT model
simplified latency model
simplified baseline abstractions
no real deployment
no real libp2p production integration
no real Reticulum integration
no cryptographic evaluation
limited repeated runs
limited topology diversity
```

---

## 23. Threat model updates

Summarize required updates to `THREAT_MODEL.md`.

```text
TODO
```

Potential updates:

```text
state-to-path mapping validated / not validated
lane collapse observed / not observed
new adversary failure mode
new graceful degradation behavior
new out-of-scope condition
```

---

## 24. Whitepaper updates

Summarize required updates to `WHITEPAPER.md`.

```text
TODO
```

Potential updates:

```text
VoxMesh fractal_count result
baseline comparison result
simulation methodology
structural divergence interpretation
limitations
future work
```

---

## 25. Reproducibility package

The report should point to a reproducibility bundle.

Required files:

```text
README.md
SIMULATION_REPORT.md
simulation_run.json
metrics_report.json
baseline_comparison.csv
topology_graph.json
experiment_manifest.json
schemas/*.schema.json
requirements.txt or flake.nix
```

Optional:

```text
IPFS CID
artifact hash
plots
CSV summaries
```

---

## 26. Final conclusion

Choose one:

### Positive

```text
The simulation provides evidence that WHISPER-style structural divergence
improves specific metrics under defined topology/adversary conditions, within
documented overhead bounds.
```

### Mixed

```text
The simulation shows measurable benefits under some conditions, but also shows
collapse or unacceptable overhead under others.
```

### Negative

```text
The simulation does not show that WHISPER-style structural divergence translates
into meaningful network-level resilience under the tested conditions.
```

### Inconclusive

```text
The simulation framework works, but the current experiments are insufficient to
support positive or negative conclusions.
```

Final statement:

```text
TODO
```

---

## 27. Next steps

Depending on outcome:

### If positive

```text
expand topology/adversary coverage
implement libp2p PoC
begin Rust/WASM hardening
prepare external review
```

### If mixed

```text
narrow claims
identify conditions where it works
document failure modes
adjust architecture
```

### If negative

```text
publish negative result
preserve simulator as research artifact
reconsider architecture assumptions
pivot if necessary
```

### If inconclusive

```text
increase repeated runs
refine metrics
tighten baselines
reduce simulator ambiguity
```

---

## 28. Appendix A — Commands

Example commands:

```bash
nix develop
pytest -q
pytest -q tests/test_regression_v043.py
python3 simulation_runner_v01.py --config experiments/example.json
python3 tools/summarize_metrics.py outputs/*.json
```

---

## 29. Appendix B — JSON artifact checklist

```text
[ ] simulation_run.json
[ ] metrics_report.json
[ ] topology_graph.json
[ ] baseline_comparison.json
[ ] baseline_comparison.csv
[ ] experiment_manifest.json
[ ] schema validation logs
```

---

## 30. Appendix C — Reviewer notes

This report should be read together with:

```text
README.md
THREAT_MODEL.md
WHITEPAPER.md
ROADMAP.md
PHASE2_VALIDATION_CRITERIA.md
SIMULATION_PLAN.md
BENCHMARKS.md
SECURITY.md
```

Core posture:

```text
The purpose of Phase 2 is not to confirm WHISPER.

The purpose of Phase 2 is to test WHISPER.
```
