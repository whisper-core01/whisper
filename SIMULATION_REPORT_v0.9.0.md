# WHISPER Remote Nerve — Simulation Report v0.9.0

## Status

Preliminary state-aware path selection report.

This report extends v0.8.0 by adding a simulated state-aware path selection policy.

These results are preliminary and do not support security, anonymity, metadata-protection, or resilience claims yet.

## Objective

v0.9.0 answers one narrow question:

Does a hybrid state-aware path selection policy change path diversity and adversarial exposure outcomes compared to current WHISPER candidate-path sampling and naive random multipath?

## Scope

v0.9.0 includes:

- path_state_material
- hybrid state/path scoring
- greedy state-aware path selection
- comparison against current WHISPER candidate paths
- comparison against naive random multipath
- random 20% node compromise model
- state_aware_comparison.csv
- state_aware_comparison.json

## Non-goals

v0.9.0 does not include:

- production routing
- cryptographic key material
- real MCE/VoxMesh feedback
- targeted adversary
- active adversary behavior
- latency model
- packet loss model
- libp2p PoC
- security claim

## Policy definition

The state-aware policy derives deterministic diagnostic state material from each candidate path.

The candidate score is:

    score(candidate) =
      0.5 * mean_state_distance(candidate_state, selected_states)
    + 0.5 * mean_path_distance(candidate_path, selected_paths)

The selector uses greedy maximization until route_count paths are selected.

This is a simulated policy.

The state material is not cryptographic key material.

## Compared policies

v0.9.0 compares:

- whisper_candidate_paths
- random_multipath
- state_aware_whisper

All policies are evaluated under:

- same seeds
- same topology configuration
- same random 20% node compromise model
- same route_count

## Metrics

v0.9.0 reports:

- unique_path_ratio
- path_overlap
- clean_path_ratio
- path_compromise_rate
- mean_compromised_nodes_per_path
- state_to_path_correlation
- lane_collapse_rate

## Results

Detailed results in:

- outputs/state_aware_comparison.csv
- outputs/state_aware_comparison.json

## Summary table

| Seed | Policy | Path Overlap | Clean Path Ratio | Mean Compromised Nodes/Path | State-to-Path Correlation | Lane Collapse |
|---|---|---:|---:|---:|---:|---:|
| run-001 | whisper_candidate_paths | 0.1667 | 0.00 | 3.67 | -0.7061 | 0.00 |
| run-001 | random_multipath | 0.0833 | 0.00 | 2.33 | -0.8660 | 0.00 |
| run-001 | state_aware_whisper | 0.1111 | 0.33 | 2.67 | -0.8386 | 0.00 |
| run-002 | whisper_candidate_paths | 0.4615 | 0.33 | 2.33 | -0.9754 | 0.00 |
| run-002 | random_multipath | 0.3333 | 0.00 | 2.33 | 0.2402 | 0.00 |
| run-002 | state_aware_whisper | 0.0000 | 0.00 | 4.67 | 0.0000 | 0.00 |
| run-003 | whisper_candidate_paths | 0.1256 | 0.00 | 3.33 | 0.9683 | 0.00 |
| run-003 | random_multipath | 0.0952 | 0.33 | 1.00 | 0.9924 | 0.00 |
| run-003 | state_aware_whisper | 0.0000 | 0.33 | 1.67 | 0.0000 | 0.00 |

## Observed results

The state-aware policy changed path selection behavior.

In run-001:

- state_aware_whisper improved clean_path_ratio compared to both current WHISPER and random_multipath.
- random_multipath had lower mean compromised nodes per path than state_aware_whisper.
- state_aware_whisper reduced path_overlap relative to current WHISPER, but not relative to random_multipath.

In run-002:

- state_aware_whisper produced path_overlap = 0.0.
- state_aware_whisper did not improve clean_path_ratio.
- state_aware_whisper had higher mean compromised nodes per path than both baselines.
- This is a negative result for adversarial exposure.

In run-003:

- state_aware_whisper produced path_overlap = 0.0.
- state_aware_whisper improved clean_path_ratio compared to current WHISPER.
- random_multipath remained better on mean compromised nodes per path.

## Preliminary interpretation

v0.9.0 shows that hybrid state/path scoring can change path selection behavior.

It can reduce path_overlap and sometimes improve clean_path_ratio.

However, it does not consistently outperform random_multipath under random node compromise.

The result is mixed.

This means that state-aware divergence alone is not sufficient to claim adversarial robustness.

The next required mechanism is adversary-aware or exposure-aware scoring.

## Key finding

The key v0.9.0 finding is:

    State-aware path selection changes behavior, but does not yet guarantee lower adversarial exposure.

This is an important negative/mixed result.

It shows that maximizing state/path divergence can still route through compromised regions of the graph.

## Limitations

The current comparison is limited because:

- only three seeds are reported
- only one topology configuration is reported
- only random compromise is modeled
- no targeted compromise is modeled
- no active adversary behavior is modeled
- no statistical significance is claimed
- state material is diagnostic, not cryptographic
- no real network behavior is modeled

## Next step

v0.9.1 or v1.0.0 should add:

- exposure-aware scoring
- targeted high-degree compromise
- n=30 pilot runs per condition
- repeated comparison against random_multipath
- topology variation beyond Erdős-Rényi
- confidence intervals for key metrics

## Conclusion

v0.9.0 adds the first simulated state-aware path selection policy.

The result is mixed and does not demonstrate WHISPER superiority.

It establishes that state-aware selection changes behavior, but that adversarial robustness requires exposure-aware scoring and broader repeated experiments.
