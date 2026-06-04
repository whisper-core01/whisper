# WHISPER Remote Nerve — v1.1.0 Experiment Protocol

## Hypothesis

**H1 — Node-Score-Aware Lemonade Reselection**

After a Lemonade-triggered reset, WHISPER should preserve most of the continuity-break benefit observed in v1.0.0 while reducing traversal through high-risk VoxMesh node-score regions.

The node score is a local FLV load/homeostasis signal, not a trust score, not a compromise indicator, and not a globally agreed reputation value.

## Deterministic Synthetic FLV Load Model

v1.1.0 uses a deterministic synthetic FLV score model to avoid both arbitrary randomness and oracle-based scoring.

### Score Generation

All nodes start at score `0.0`.

The simulator runs exactly 5 pre-reset epochs.

In each epoch:

- Candidate paths are selected using the standard WHISPER selection policy.
- Each node appearing in a selected path receives: `score += 0.5`.
- Each node not appearing in any selected path receives: `score -= 0.1`.
- Scores are clamped to `[-1.0, 5.0]`.

After 5 epochs, the resulting local FLV score table is frozen and used by the WHISPER selector during post-reset path selection.

### Why This Model

- **Deterministic**: same seed → same scores.
- **Topology-bound**: scores reflect actual path usage, not oracle knowledge.
- **Local**: no distributed consensus, no gossip.
- **Simple**: 5 epochs, two operations (`+0.5`, `-0.1`), no complex traffic simulation.
- **Falsifiable**: reviewers can audit the score generation directly.

### Score Interpretation

Node score is a synthetic **load/homeostasis signal** generated from pre-reset path selection patterns.

It is not:

- a trust score
- a compromise indicator
- a globally agreed reputation value
- a measure of node quality

It reflects only:

> how frequently this node was selected during the pre-reset FLV warmup window.

### Bands
watch zone:   -1.0 ≤ score < 0.0
healthy:       0.0 ≤ score ≤ 1.0
loaded:        1.0 < score ≤ 3.0
overloaded:    3.0 < score ≤ 5.0

Because scores are clamped to `[-1.0, 5.0]`, the simulation never observes values outside this range.

### Node Score Risk

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

## Scoring Policy

### Continuity Component
continuity_component =
0.40 * pre_alarm_path_distance

0.30 * state_divergence
0.30 * path_divergence


(Same as v1.0.0)

### Final Score
final_score(candidate) =
delta * continuity_component

(1 - delta) * node_score_safety


### Delta Sweep

Four values tested, fixed before experiment start:
delta ∈ {0.90, 0.75, 0.60, 0.50}

Success requires at least one delta to satisfy the primary metrics.

## Primary Metrics

### continuity_retention
continuity_retention =
post_reset_path_distance_from_pre_alarm(node_score_aware)
/ post_reset_path_distance_from_pre_alarm(lemonade_reset)

**Success threshold**: `continuity_retention >= 0.80`

Meaning: node-score-aware reselection preserves at least 80% of Lemonade's continuity-break effect.

### mean_node_score_risk_per_path
mean_node_score_risk_per_path =
mean(node_score_risk(path) for all selected paths)

**Success threshold**: `node_score_aware < lemonade_reset`

Meaning: on average, selected paths traverse nodes with lower risk scores than baseline Lemonade reselection.

## Constraints
lane_collapse_rate ≤ 0.20
unique_path_ratio == 1.0
path_overlap degradation ≤ 25% vs lemonade_reset

## Experiment Design

- **n_seeds**: 30
- **compromise_fraction**: 0.20
- **compromise_types**: ["random", "targeted"]
- **route_count**: 3 (stable pre/post)
- **pre_reset_warmup_epochs**: 5
- **phase_structure**: 5-phase (same as v1.0.0)

Total runs: 30 seeds × 2 adversaries × 4 deltas = 240 rows

### Statistics

Bootstrap 95% CI for:
- continuity_retention (must not cross 0.80 downward)
- mean_node_score_risk_per_path (must be < lemonade_reset)

## Secondary Metrics

Reported but non-defining:

- clean_path_ratio
- path_compromise_rate
- mean_compromised_nodes_per_path
- max_node_score_in_path
- healthy_node_ratio_in_path
- overloaded_node_ratio_in_path

## Scope Boundary

v1.1.0 does not implement:

- harassment detection
- reporter-side revocation
- bandwidth fairness enforcement
- distributed FLV synchronization
- next-hop degradation reporting
- global node reputation
- consensus on node health

Those mechanisms are intentionally deferred to later versions.

v1.1.0 tests only whether local FLV node-score-aware reselection can preserve Lemonade's continuity-break effect while reducing traversal through nodes outside the healthy score band.

## Success Criteria

**All must be true for v1.1.0 to be POSITIVE:**

1. At least one delta satisfies: `continuity_retention >= 0.80`
2. At least one delta satisfies: `mean_node_score_risk_per_path < lemonade_reset`
3. All constraints satisfied
4. Bootstrap 95% CI for primary metrics does not cross failure thresholds

**If primary metrics positive but secondary metrics show worse adversarial exposure:**
- Document as "continuity preserved, exposure trade-off remains" (same as v1.0.0 finding)
- This is acceptable per protocol

## Next Steps

If v1.1.0 is positive:

- v1.2.0: next-hop degradation signals
- v1.3.0: local harassment detection
- v1.4.0: revocation ladder integration
