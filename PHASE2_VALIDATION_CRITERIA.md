# PHASE2_VALIDATION_CRITERIA.md

## WHISPER Remote Nerve — Phase 2 Validation Criteria

**Purpose:** clarify the realism, methodology, and success thresholds for the simulation phase before implementation starts.

**Status:** pre-Phase-2 planning document  
**Applies to:** v0.6.x / v0.7.x roadmap  

---

## 1. Timeline realism

The previous six-week simulator timeline is an optimistic lower bound.

A complete topology simulator with dynamic MCE/VoxMesh-to-path mapping, adversary models, baselines, metrics, JSON outputs, and a first report is unlikely to be robust in six weeks if implemented solo.

A more realistic timeline is:

```text
Minimum viable simulator:        6 weeks
Credible evaluation harness:     8–10 weeks
Grant-quality simulation report: 10–12 weeks
```

Recommended revised timeline:

```text
Week 1–2:
  graph models
  deterministic topology generation
  seed handling
  basic path sampling

Week 3–4:
  adversary models
  compromise scenarios
  path overlap metrics
  reconstruction metrics

Week 5–6:
  WHISPER policy mapping
  Loader/MCE/VoxMesh-to-path mapping
  first JSON reports

Week 7–8:
  baseline models
  direct path
  random multipath
  fixed circuit
  persistent tunnel

Week 9–10:
  repeated experiment runs
  CSV/JSON summaries
  statistical aggregation
  reproducibility checks

Week 11–12:
  first simulation report
  updated threat model
  updated whitepaper
  funding/reviewer summary
```

### Decision

For public planning, use:

```text
8–10 weeks for Phase 2 engineering
10–12 weeks for grant-quality reporting
```

Do not promise a full simulator, baselines, metrics, and report in six weeks unless the scope is explicitly reduced.

---

## 2. Scope tiers

To avoid over-promising, Phase 2 should be split into tiers.

### Tier 1 — Minimum viable simulator

Goal:

```text
Prove that deterministic topology simulation is possible.
```

Includes:

```text
3 topology families
1 WHISPER policy
2 adversary models
3 metrics
JSON output
```

Required topologies:

```text
Erdős–Rényi
Barabási–Albert
Watts–Strogatz
```

Required adversaries:

```text
random node compromise
targeted high-degree compromise
```

Required metrics:

```text
path overlap
route diversity
fragment exposure ratio
```

### Tier 2 — Credible comparison harness

Goal:

```text
Compare WHISPER-style policy against simplified baselines.
```

Adds:

```text
direct single-path baseline
random multipath baseline
fixed circuit baseline
persistent tunnel baseline
repeated runs
CSV summary
```

### Tier 3 — Grant-quality report

Goal:

```text
Produce evidence suitable for funder/reviewer discussion.
```

Adds:

```text
simulation report
plots/tables
updated whitepaper
updated threat model
explicit positive/negative outcomes
limitations section
```

---

## 3. Methodological gap: local state divergence vs network paths

The key methodological gap is:

```text
MCE/VoxMesh state divergence is local.
Network path diversity is topological.
```

Different MCE states do not automatically imply different network paths.

Therefore, Phase 2 must validate the mapping from local state to path selection.

The simulator must implement this as an explicit policy layer:

```text
state_material = hash(MCE_state || VoxMesh_state || fragment_id)
candidate_paths = PathSampler.sample_paths(topology, source, target, k)
selected_path = Policy.select(candidate_paths, state_material)
```

The mapping is valid only if measurable path differences emerge.

---

## 4. Required mapping validation

For each experiment, the simulator must compute:

```text
state_distance
path_distance
state_to_path_correlation
path_overlap
unique_path_ratio
lane_to_path_diversity
```

### Definitions

`state_distance`:

```text
distance between per-fragment state materials
```

Can be implemented initially as Hamming distance between state hashes.

`path_distance`:

```text
1 - Jaccard similarity between node sets or edge sets of two paths
```

`path_overlap`:

```text
shared_edges(path_a, path_b) / min(len(path_a), len(path_b))
```

`unique_path_ratio`:

```text
unique_paths / total_fragments
```

`state_to_path_correlation`:

```text
correlation between state distance and path distance
```

If state distance is high but path distance remains low, then structural divergence is not translating into topology diversity.

---

## 5. Mapping success and failure criteria

### Mapping success

A mapping is considered promising if, across repeated runs:

```text
unique_path_ratio >= 0.30
mean_path_overlap <= 0.70
state_to_path_correlation > 0.20
```

This is not a security claim. It only means local state variation is influencing path choice enough to be measurable.

### Strong mapping success

```text
unique_path_ratio >= 0.50
mean_path_overlap <= 0.50
state_to_path_correlation > 0.35
```

### Mapping failure

```text
unique_path_ratio < 0.15
mean_path_overlap > 0.85
state_to_path_correlation <= 0.05
```

Interpretation:

```text
The local state machinery exists, but the network topology collapses path diversity.
```

This failure mode must be reported honestly.

---

## 6. Concrete success thresholds

The phrase “reduces reconstruction probability or path overlap” is too vague.

Phase 2 needs numerical thresholds.

### Minimum positive outcome

A result is minimally positive if WHISPER-style policy improves at least one primary metric by:

```text
>= 10% relative improvement
```

against at least one baseline, under at least two topology/adversary combinations, without more than:

```text
<= 2x latency estimate
<= 2x bandwidth overhead
```

### Strong positive outcome

A result is strongly positive if WHISPER-style policy improves one or more primary metrics by:

```text
>= 25% relative improvement
```

under at least three topology/adversary combinations, while keeping overhead under:

```text
<= 2x latency estimate
<= 2x bandwidth overhead
```

### Very strong outcome

A result is very strong if WHISPER-style policy improves reconstruction resistance or path diversity by:

```text
>= 50% relative improvement
```

under multiple topologies and adversaries, while keeping overhead under:

```text
<= 3x latency estimate
<= 3x bandwidth overhead
```

This would be funder-visible.

---

## 7. Primary metrics and thresholds

Primary metrics:

```text
fragment reconstruction probability
mean path overlap
unique path ratio
metadata exposure estimate
```

Secondary metrics:

```text
latency estimate
bandwidth overhead
route churn
degradation frequency
false-positive rate
```

### Path overlap

Positive:

```text
>= 10% reduction vs baseline
```

Strong:

```text
>= 25% reduction vs baseline
```

Very strong:

```text
>= 50% reduction vs baseline
```

### Reconstruction probability

Positive:

```text
>= 10% reduction vs baseline
```

Strong:

```text
>= 25% reduction vs baseline
```

Very strong:

```text
>= 50% reduction vs baseline
```

### Unique path ratio

Positive:

```text
>= 10% relative increase vs baseline
```

Strong:

```text
>= 25% relative increase vs baseline
```

Very strong:

```text
>= 50% relative increase vs baseline
```

### Overhead limits

A result should be considered questionable if it only improves diversity by adding unrealistic overhead.

Acceptable initial limits:

```text
latency estimate <= 2x baseline for positive outcome
bandwidth overhead <= 2x baseline for positive outcome
latency estimate <= 3x baseline for experimental high-divergence mode
bandwidth overhead <= 3x baseline for experimental high-divergence mode
```

---

## 8. Funder-facing interpretation

### Scientifically interesting but weak

```text
3–9% improvement under narrow topology/adversary combinations
```

This is useful for research, but not enough to sell as a strong Phase 2 success.

### Minimum funder-visible positive

```text
>= 10% improvement under at least two topology/adversary combinations
```

This is enough to justify continued investigation.

### Strong funder-visible positive

```text
>= 25% improvement under at least three topology/adversary combinations
```

This is a credible positive result.

### High-impact positive

```text
>= 50% improvement under multiple topologies and adversaries
```

This is the kind of result that can anchor a strong Protocol Labs or NLnet follow-up.

---

## 9. Graceful degradation thresholds

Graceful degradation should be measured under compromise.

Minimum claim:

```text
Under partial compromise, WHISPER should degrade route diversity, latency, or
reachability before allowing full reconstruction.
```

Metrics:

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

Failure:

```text
single compromised node with current state predicts future paths or reconstructs
fragment flow with no meaningful degradation signal
```

---

## 10. What to tell funders

Correct:

```text
The six-week target is a minimum viable simulator. A credible adversarial
evaluation and report is more realistically 8–12 weeks.
```

Correct:

```text
Phase 2 will explicitly test whether local structural divergence maps to
network-level diversity.
```

Correct:

```text
Positive results will require numerical improvements against baselines, not just
qualitative architectural arguments.
```

Avoid:

```text
The simulator will prove WHISPER is resilient in six weeks.
```

Avoid:

```text
Different MCE states automatically imply different network paths.
```

Avoid:

```text
Any improvement counts as success.
```

---

## 11. Updated Phase 2 statement

Recommended statement:

```text
Phase 2 will implement a reproducible topology simulator and baseline comparison
framework. The first milestone is a minimum viable simulator in approximately
six weeks. A credible grant-quality adversarial evaluation is expected to take
eight to twelve weeks. Success will be measured through explicit thresholds:
at least 10% relative improvement for a minimum positive result, 25% for a
strong result, and 50% for a high-impact result, subject to latency and bandwidth
overhead limits.
```

---

## 12. Final note

A negative result is acceptable.

If Phase 2 shows that local structural divergence does not translate into network-level diversity, that is still a useful research outcome.

The project should be designed to discover the truth, not to confirm the architecture.
