WHISPER Remote Nerve — Release Notes v0.8.0
Release type: diagnostic experimental release
Status: reproducible research artifact
Security status: no security or anonymity guarantees
Review status: Phase 2 early‑stage empirical baseline

1. Summary
WHISPER Remote Nerve v0.8.0 introduces the first state‑to‑path diagnostics and lane‑collapse metrics.

This release does not implement state‑aware routing.
It provides diagnostic tools only, enabling reviewers to measure whether simulated state diversity correlates with path diversity in the current simulator.

Results are inconclusive, as expected.

2. Scope
v0.8.0 includes:

deterministic state_material generation

normalized state distance

edge‑based path distance

state_to_path_correlation (Pearson)

lane_collapse_rate

doubled route_count for diagnostics (3 → 6)

state_mapping_report.csv

state_mapping_report.json

These components allow WHISPER to measure whether state divergence maps to path divergence, without yet influencing routing.

3. Non‑goals
v0.8.0 does not include:

state‑driven path selection

MCE/VoxMesh‑driven routing

targeted adversary

active adversary behavior

latency or packet‑loss model

libp2p PoC

any security, anonymity, or resilience claim

These belong to v0.9.0 state‑aware routing and later.

4. Diagnostic Method
Default experiment route_count = 3.

For v0.8.0 diagnostics, route_count is doubled to 6, increasing pairwise comparisons:

Code
3 paths  ->  3 pairwise comparisons
6 paths  -> 15 pairwise comparisons
This reduces correlation instability but does not eliminate it.

Metrics reported:

pairwise state_distance

pairwise path_distance

state_to_path_correlation

lane_collapse_rate

Definitions:

state_distance — normalized Hamming distance between deterministic state hex strings

path_distance — edge‑based path distance

state_to_path_correlation — Pearson correlation between state and path distances

lane_collapse_rate — fraction of path pairs below the collapse threshold

5. Results
Detailed outputs:

outputs/state_mapping_report.csv

outputs/state_mapping_report.json

Summary
Seed	Original RC	Analysis RC	Path Count	Pairwise	Correlation	Collapse
run‑001	3	6	6	15	0.3198	0.00
run‑002	3	6	6	15	0.0270	0.00
run‑003	3	6	6	15	−0.1400	0.00


Observed behavior
run‑001 → weak‑to‑moderate positive signal

run‑002 → near‑zero signal

run‑003 → weak negative signal

lane_collapse_rate = 0.0 in all runs

6. Interpretation
v0.8.0 does not show stable state‑to‑path correlation.

This is expected because state_material does not yet influence path selection.

The results should be interpreted as diagnostic only:

the simulator can now measure state/path relationships

WHISPER’s current routing does not use state

no resilience or anonymity claim is supported

no superiority over baselines is implied

Lane collapse was not observed under the current threshold.
This does not imply resilience — only that sampled paths were not near‑identical.

7. Key Finding
State material exists and can be measured,
but current path selection is not state‑driven.

The next required mechanism is state‑aware path selection.

8. Limitations
The v0.8.0 diagnostic is limited because:

only three seeds

only one topology (Erdős–Rényi)

doubled route_count only for diagnostics

state does not influence routing

no targeted compromise

no active adversary

no statistical significance

no real network behavior

These limitations are intentional for early Phase 2.

9. Next Steps
v0.8.1 / v0.9.0 should add:

state‑aware path scoring

state‑influenced path selection

comparison against random_multipath under identical adversary models

lane‑collapse analysis across multiple route counts

targeted high‑degree compromise

n=30 pilot runs per condition

full JSON/CSV publication

See v0.9.0 plan.

10. Final Note
v0.8.0 introduces WHISPER’s first state‑to‑path and lane‑collapse diagnostics.

The results are inconclusive, as expected.
They do not demonstrate WHISPER superiority.
They establish the next required mechanism: state‑aware routing.

This release is suitable for funding review, not for production use.
