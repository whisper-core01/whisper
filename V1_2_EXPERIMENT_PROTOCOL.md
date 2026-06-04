# WHISPER v1.2.0 — Local Degradation-Aware Reselection

## Status

Protocol draft frozen before implementation.

v1.2.0 is strictly behavioral, strictly local, and strictly non-oracle.

It does not detect compromised nodes.

It tests whether local next-hop degradation symptoms improve post-reset behavioral stability, and whether that stability correlates with lower adversarial exposure.

## 1. Purpose

v1.2.0 extends v1.1.0 by adding local next-hop degradation symptoms to post-reset path selection.

v1.1.0 showed that local FLV node-score-aware reselection improves path health while preserving Lemonade continuity break.

However, v1.1.0 did not reduce adversarial exposure.

The purpose of v1.2.0 is to test whether adding local behavioral degradation signals improves path stability after a Lemonade-triggered reset.

Adversarial exposure is observed, but not required for primary success.

## 2. Core Principle

WHISPER cannot know whether a node is:

- compromised
- attacked
- malicious
- under hostile control

With VoxMesh / Reticulum, each node only knows its next hop.

Therefore, v1.2.0 does not identify compromised nodes.

v1.2.0 only models local next-hop degradation symptoms.

A degradation signal is not an adversarial attribution.

It is only a local symptom.

## 3. Observable Local Symptoms

A node may locally observe symptoms such as:

- repeated timeout
- abnormal latency
- abnormal jitter
- forwarding failure
- absence of response
- detected reboot
- abrupt local score drop
- inconsistent response

The node does not know the cause.

Possible causes include:

- reboot
- attack
- congestion
- high latency
- packet loss
- transient instability
- overload
- implementation failure

WHISPER does not need to know why a node is degraded.

It only needs to know whether a next-hop relationship is currently unsuitable for stable forwarding.

## 4. Next-Hop Relationship Scope

This is the critical v1.2.0 invariant:

    v1.2.0 does not score degraded nodes.
    It scores degraded next-hop relationships.

A degradation signal is scoped to a directed next-hop relation, not to a node globally.

v1.2.0 does not model:

    node_x is degraded

It models:

    observer_node -> next_hop_node is degraded

Therefore, the degradation table is:

    next_hop_degradation_score[(observer_node, next_hop_node)] in [0.0, 1.0]

Or, in epoch-scoped form:

    next_hop_degradation_score[(observer_alias, next_hop_alias, epoch)] in [0.0, 1.0]

This preserves the next-hop-only invariant.

A node may be degraded from one observer's perspective and healthy from another.

The signal is:

- local
- relationship-scoped
- epoch-scoped
- non-oracle
- not globally shared
- not a reputation value

For a candidate path:

    [n0, n1, n2, ..., nk]

the path degradation risk is computed over directed next-hop relations:

    (n0 -> n1), (n1 -> n2), ..., (n{k-1} -> nk)

as:

    path_degradation_risk(path) =
        mean(next_hop_degradation_score[(n_i, n_{i+1})])

Missing relations default to 0.0 degradation.

This means WHISPER avoids unstable next-hop relationships, not globally bad nodes.

## 5. Hypotheses

### Primary Hypothesis

H1 — Local Degradation-Aware Reselection

After a Lemonade-triggered reset, WHISPER can preserve Lemonade continuity break and avoid candidate paths containing locally degraded next-hop relationships.

This hypothesis is behavioral.

It does not claim adversarial detection.

### Secondary Observed Hypothesis

Local degradation symptoms may correlate with lower adversarial exposure.

This is:

- observed
- measured
- not required for primary success
- not assumed
- not an attribution of compromise

Adversarial exposure reduction, if observed, is an emergent empirical result, not a direct inference.

## 6. Local Degradation Score

v1.2.0 introduces a local relationship-scoped table:

    next_hop_degradation_score[(observer_node, next_hop_node)] in [0.0, 1.0]

Interpretation:

    0.0 = no observed degradation symptom on this next-hop relation
    1.0 = strongly degraded next-hop behavior on this relation

Properties:

- local to the selector
- directed
- relationship-scoped
- epoch-scoped
- deterministic
- seedable
- reproducible
- non-oracle
- not shared globally
- not based on compromise labels

Compromise labels are used only for evaluation.

## 7. Synthetic Behavioral Signal

The synthetic behavioral signal is generated per directed next-hop relationship.

For relation:

    observer -> next_hop

the synthetic behavioral signal is:

    synthetic_behavioral_signal(observer, next_hop) =
      0.40 * timeout_risk(observer, next_hop)
    + 0.30 * latency_risk(observer, next_hop)
    + 0.30 * forwarding_failure_risk(observer, next_hop)

Each component is generated deterministically from seed and directed relation identity.

Example:

    timeout_risk =
      H(seed || observer || next_hop || "timeout") mod 100 / 100

    latency_risk =
      H(seed || observer || next_hop || "latency") mod 100 / 100

    forwarding_failure_risk =
      H(seed || observer || next_hop || "forwarding") mod 100 / 100

The signal is generated independently from compromise labels.

## 8. Effective Degradation

v1.2.0 combines the relationship-scoped behavioral signal with v1.1.0 FLV node-score risk additively.

For relation:

    observer -> next_hop

the effective degradation is:

    effective_degradation(observer, next_hop) =
      0.70 * synthetic_behavioral_signal(observer, next_hop)
    + 0.30 * node_score_risk(next_hop)

This preserves the distinction between:

- relationship-level symptoms
- node-level FLV load/homeostasis

With additive coupling:

- the behavioral signal exists even if FLV is healthy
- FLV reinforces but does not dominate
- the degradation signal is not erased when node-score risk is low
- the signal remains non-oracle
- no compromise labels are used

## 9. Epoch and Decay Boundary

Degradation signals are epoch-scoped.

They do not represent permanent node reputation.

For v1.2.0, the synthetic degradation table is generated for the post-reset evaluation epoch.

It is not persisted as a global truth.

Future versions may introduce decay, observation windows, and revocation logic.

Those mechanisms are out of scope for v1.2.0.

## 10. Selection Score

v1.2.0 keeps the v1.1.0 continuity component:

    continuity_component =
      0.40 * pre_alarm_path_distance
    + 0.30 * state_divergence
    + 0.30 * path_divergence

It adds a behavioral path-health component:

    path_health_component =
      0.50 * node_score_safety
    + 0.50 * next_hop_degradation_safety

Where:

    next_hop_degradation_safety =
      1.0 - path_degradation_risk(path)

Final score:

    final_score =
      delta * continuity_component
    + (1 - delta) * path_health_component

## 11. Delta Grid

v1.2.0 tests:

    delta = 0.90
    delta = 0.85
    delta = 0.80

Deltas below 0.80 are intentionally excluded.

v1.1.0 showed that lower deltas improve local node-score health but degrade adversarial exposure.

## 12. Primary Metrics

v1.2.0 primary success is behavioral stability.

Primary metrics:

    continuity_retention >= 0.80
    mean_node_score_risk_per_path < lemonade_reset
    mean_degradation_risk_per_path < lemonade_reset
    lane_collapse_rate <= 0.20

These metrics do not claim adversarial detection.

They test whether v1.2.0 preserves continuity break and avoids locally degraded next-hop relationships.

## 13. Secondary Metrics

Adversarial exposure is observed through:

    mean_compromised_nodes_per_path
    clean_path_ratio
    path_compromise_rate

The result may be:

    positive adversarial exposure effect
    mixed adversarial exposure effect
    negative adversarial exposure effect

This effect is observed, not assumed.

## 14. Non-goals

v1.2.0 does not implement:

- compromise detection
- malicious-node attribution
- harassment detection
- anti-harassment damping
- reporter-side revocation
- session-hash revocation propagation
- bandwidth-fairness enforcement
- distributed FLV synchronization
- global reputation
- consensus on node health

These are deferred to later versions.

## 15. Behavioral States

v1.2.0 uses non-adversarial behavioral states:

- HEALTHY
- LOADED
- DEGRADED
- UNSTABLE
- UNFIT
- REBOOTING

REVOKED is deferred to later versions.

A degraded next-hop relationship does not mean the target node is compromised.

It only means this directed relation is currently unsuitable for stable routing.

## 16. Reviewer-Facing Summary

v1.2.0 does not detect compromise.

It tests whether local next-hop degradation symptoms improve post-reset behavioral stability, and whether that stability correlates with lower adversarial exposure.

The degradation signal is generated independently from compromise labels.

Compromise labels are used only for evaluation.

WHISPER cannot infer compromise from VoxMesh / Reticulum behavior alone.

It can only observe local next-hop degradation symptoms and avoid unstable next-hop relationships.

Adversarial exposure reduction, if observed, is an emergent empirical result, not a direct inference.

The key invariant is:

    v1.2.0 does not score degraded nodes.
    It scores degraded next-hop relationships.

## 17. Roadmap Position

    v1.1.0 = FLV path health
    v1.2.0 = next-hop behavioral stability
    v1.3.0 = anti-harassment damping
    v1.4.0 = session-hash revocation propagation
    v1.5.0 = full FLV lifecycle and revocation ladder
