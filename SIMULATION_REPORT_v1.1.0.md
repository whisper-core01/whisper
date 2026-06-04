# WHISPER Remote Nerve — Simulation Report v1.1.0

## Title

Node-Score-Aware Lemonade Reselection

## Status

v1.1.0 is positive on its primary hypothesis.

It improves local path health after a Lemonade-triggered reset while preserving the continuity-break effect observed in v1.0.0.

It does not yet demonstrate adversarial exposure reduction.

## Scope

v1.1.0 adds:

- local FLV node-score-aware post-reset path selection
- deterministic synthetic FLV load model
- 5-epoch pre-reset FLV warmup
- delta grid evaluation
- continuity retention metric
- node-score risk metric
- n=30 seeds under random and targeted compromise
- bootstrap confidence intervals

v1.1.0 compares:

- lemonade_reset
- node_score_aware_delta_0.90
- node_score_aware_delta_0.75
- node_score_aware_delta_0.60
- node_score_aware_delta_0.50

## Non-goals

v1.1.0 does not implement:

- next-hop degradation reports
- harassment detection
- anti-harassment damping
- reporter-side revocation
- session-hash revocation propagation
- bandwidth-fairness enforcement
- distributed FLV synchronization
- global node reputation
- consensus on node health
- oracle compromise knowledge

These mechanisms are intentionally deferred to later versions.

## Motivation

v1.0.0 showed that Lemonade-triggered reset can break continuity after an alarm.

However, v1.0.0 also showed mixed adversarial exposure results.

The key limitation was that Lemonade reset selected new paths mainly to break continuity, not to preserve local VoxMesh path health.

v1.1.0 tests whether local FLV node-score-aware reselection can preserve the continuity-break effect while reducing traversal through high-risk local node-score regions.

## Hypothesis

H1 — Node-Score-Aware Lemonade Reselection:

After a Lemonade-triggered reset, WHISPER should preserve most of the continuity-break benefit observed in v1.0.0 while reducing traversal through high-risk VoxMesh node-score regions.

The node score is interpreted as a local FLV load/homeostasis signal.

It is not:

- a trust score
- a compromise indicator
- a globally agreed reputation value
- a measure of node quality

## Deterministic Synthetic FLV Load Model

v1.1.0 uses a deterministic synthetic FLV score model to avoid both arbitrary randomness and oracle-based scoring.

All nodes start at score `0.0`.

The simulator runs exactly 5 pre-reset epochs.

In each epoch:

- Candidate paths are selected using the standard WHISPER selection policy.
- Each node appearing in a selected path receives: `score += 0.5`.
- Each node not appearing in any selected path receives: `score -= 0.1`.
- Scores are clamped to `[-1.0, 5.0]`.

After 5 epochs, the resulting local FLV score table is frozen and used by the WHISPER selector during post-reset path selection.

This model is:

- deterministic
- seedable
- topology-bound
- local to the selector
- non-oracle
- simple enough to audit

## Score Bands

```text
watch zone:   -1.0 <= score < 0.0
healthy:       0.0 <= score <= 1.0
loaded:        1.0 < score <= 3.0
overloaded:    3.0 < score <= 5.0

Because scores are clamped to [-1.0, 5.0], the simulation does not observe values outside this range.

Node Score Risk

The node score risk function is:

if -1.0 <= score < 0.0:
    risk = abs(score)

if 0.0 <= score <= 1.0:
    risk = 0.0

if 1.0 < score <= 5.0:
    risk = (score - 1.0) / 4.0

For a path:

node_score_risk(path) =
    mean(node_score_risk(node) for node in path)

And:

node_score_safety(path) =
    1.0 - node_score_risk(path)
Selection Score

v1.1.0 uses:

final_score =
  delta * continuity_component
+ (1 - delta) * node_score_safety

Where:

continuity_component =
  0.40 * pre_alarm_path_distance
+ 0.30 * state_divergence
+ 0.30 * path_divergence

The tested delta grid is:

delta = 0.90
delta = 0.75
delta = 0.60
delta = 0.50

The grid is predefined before evaluation.

Primary Metrics

v1.1.0 uses two primary metrics:

1. continuity_retention
continuity_retention =
  node_score_aware_path_break / lemonade_reset_path_break

Success threshold:

continuity_retention >= 0.80
2. mean_node_score_risk_per_path

Success condition:

node_score_aware < lemonade_reset
Secondary Metrics

The following metrics are reported but do not define primary success:

clean_path_ratio
path_compromise_rate
mean_compromised_nodes_per_path
path_overlap
lane_collapse_rate
healthy_node_ratio
mean_raw_node_score_per_path
Experiment Design

The n60 evaluation uses:

30 seeds
2 adversary conditions
4 node-score-aware deltas
1 Lemonade baseline

Adversary conditions:

random compromise 20%
targeted high-degree compromise 20%

Total:

30 seeds × 2 adversaries = 60 experiment conditions
60 × 5 policies = 300 CSV rows

Outputs:

outputs/compare_node_score_reset_n60.csv
outputs/compare_node_score_reset_n60.json
Aggregate Results
Lemonade baseline
mean node risk:                 0.2010
mean compromised nodes/path:    4.0056
mean clean path ratio:          0.0333
Delta 0.50
mean continuity retention:      0.8819
mean node risk:                 0.1593
mean compromised nodes/path:    5.2167
mean clean path ratio:          0.0389
success candidates:             12 / 60
Delta 0.60
mean continuity retention:      0.8905
mean node risk:                 0.1609
mean compromised nodes/path:    5.0333
mean clean path ratio:          0.0333
success candidates:             12 / 60
Delta 0.75
mean continuity retention:      0.8942
mean node risk:                 0.1663
mean compromised nodes/path:    4.8167
mean clean path ratio:          0.0389
success candidates:             16 / 60
Delta 0.90
mean continuity retention:      0.9046
mean node risk:                 0.1854
mean compromised nodes/path:    4.1056
mean clean path ratio:          0.0333
success candidates:             20 / 60
Bootstrap Confidence Intervals
Delta 0.90
continuity retention mean:      0.9046
continuity 95% CI:              [0.8218, 0.9732]
continuity passes 0.80:         true

node risk reduction mean:       0.0156
node risk reduction 95% CI:     [0.0104, 0.0208]
node risk reduction positive:   true

exposure improvement mean:      -0.1000
exposure improvement 95% CI:    [-0.4500, 0.2778]
exposure improvement positive:  false
Delta 0.75
continuity retention mean:      0.8942
continuity 95% CI:              [0.8128, 0.9625]
continuity passes 0.80:         true

node risk reduction mean:       0.0348
node risk reduction 95% CI:     [0.0290, 0.0405]
node risk reduction positive:   true

exposure improvement mean:      -0.8111
exposure improvement 95% CI:    [-1.2444, -0.3833]
exposure improvement positive:  false
Delta 0.60
continuity retention mean:      0.8905
continuity 95% CI:              [0.8089, 0.9587]
continuity passes 0.80:         true

node risk reduction mean:       0.0402
node risk reduction 95% CI:     [0.0343, 0.0458]
node risk reduction positive:   true

exposure improvement mean:      -1.0278
exposure improvement 95% CI:    [-1.5000, -0.5833]
exposure improvement positive:  false
Delta 0.50
continuity retention mean:      0.8819
continuity 95% CI:              [0.8014, 0.9494]
continuity passes 0.80:         true

node risk reduction mean:       0.0417
node risk reduction 95% CI:     [0.0356, 0.0476]
node risk reduction positive:   true

exposure improvement mean:      -1.2111
exposure improvement 95% CI:    [-1.8111, -0.6278]
exposure improvement positive:  false
Interpretation

v1.1.0 is positive on its primary hypothesis.

Across the tested delta grid, node-score-aware Lemonade reselection preserves at least 80% of the Lemonade continuity-break effect and significantly reduces local FLV node-score risk.

However, v1.1.0 does not demonstrate adversarial exposure reduction.

Lower deltas reduce node-score risk more strongly, but they significantly worsen adversarial exposure.

Delta 0.90 is the best observed trade-off:

continuity retention remains above threshold
local node-score risk is reduced
adversarial exposure is not significantly improved
adversarial exposure is also not significantly worse under the bootstrap CI
Key Finding

The key v1.1.0 finding is:

Path health is not adversarial safety.

v1.1.0 validates FLV node-score as a path-health signal.

It does not validate FLV node-score as an adversarial-safety signal.

This is expected because v1.1.0 uses only local FLV load/homeostasis signals and does not incorporate behavioral degradation reports, harassment detection, revocation, or adversarial indicators.

Limitations

v1.1.0 is limited because:

the FLV model is synthetic
only 5 pre-reset epochs are used
no live traffic model is simulated
no latency model is simulated
no packet loss model is simulated
no next-hop degradation signals are used
no harassment detection is used
no revocation mechanism is used
no adversarial indicator is used during selection
no distributed FLV synchronization is implemented
no global reputation or consensus is used
Conclusion

v1.1.0 confirms that local FLV node-score-aware reselection can improve post-reset path health while preserving Lemonade’s continuity-break effect.

It does not yet solve adversarial exposure.

The result is positive on path-health correction and negative/inconclusive on adversarial exposure reduction.

This clarifies the modular architecture:

v1.0.0 = continuity break
v1.1.0 = path-health correction
v1.2.0 = next-hop behavioral degradation
v1.3.0 = anti-harassment damping
v1.4.0 = session-hash revocation propagation
v1.5.0 = full FLV lifecycle and revocation ladder
Next Step

v1.2.0 should add local next-hop degradation reports.

The next hypothesis should test whether behavioral next-hop signals can reduce adversarial exposure while preserving:

Lemonade continuity break
FLV path-health correction
next-hop-only knowledge invariant


```
