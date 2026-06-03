# WHISPER v1.0.0 Experiment Protocol

**FROZEN** before implementation

This protocol defines a single, well-specified hypothesis with clear success criteria.
All metric definitions, thresholds, and baseline comparisons are locked here.

## Hypothesis

**H1 — Lemonade-triggered Continuity Break**

When a Wasm module detects a critical runtime anomaly (VM inspection, cold boot, 
memory dump, debug introspection) and signals Lemonade through the membrane:

1. Lemonade triggers Dome to execute random memory rewrite and sensitive-state purge
2. Lemonade instructs Dome to reboot Nix environment
3. WHISPER recovers with new state_epoch, invalidated pre-alarm state material
4. WHISPER re-selects paths using state/path/pre-alarm-distance scoring

Expected result: post-reset WHISPER paths are more distant from pre-alarm paths 
compared to reset baselines.

This is NOT "WHISPER avoids compromised nodes."
This is "WHISPER breaks exploitable continuity after defensive system reset."

## Experiment Design

### Policies Compared

1. **random_multipath_reset**: random path selection post-reset with new seed epoch
2. **state_aware_reset**: state+path divergence scoring post-reset
3. **lemonade_reset**: state+path+pre_alarm_distance scoring post-reset

### Scoring Function (lemonade_reset only)
score(candidate) =
0.35 * state_divergence

0.35 * path_divergence
0.30 * pre_alarm_path_distance


Where:

- **state_divergence** = mean normalized Hamming distance to selected post-reset states
- **path_divergence** = mean edge-based distance to selected post-reset paths
- **pre_alarm_path_distance** = mean(path_distance(candidate, pre_alarm_path_i))

### Simulation Phases

**Phase A — Pre-alarm baseline**
- Generate state_material with epoch=0
- Select 3 paths using state_aware policy (for all policies)
- Record: pre_alarm_paths, pre_alarm_states
- Measure adversarial exposure under compromise

**Phase B — Wasm anomaly detection**
- Simulate critical runtime anomaly
- Wasm signals Lemonade through membrane
- Lemonade receives alarm signal

**Phase C — Lemonade defensive response**
- Random memory rewrite triggered (simulated as memory_epoch change)
- Sensitive state invalidated (state_material with pre_alarm epoch becomes unavailable)
- Dome receives reset instruction

**Phase D — Dome/Nix reset**
- reset_epoch += 1
- state_material regenerated with new reset_epoch
- pre_alarm_paths marked as invalid for overlap penalization
- path continuity break is the goal

**Phase E — Post-reset path re-selection**
- Generate candidate paths using reset_epoch
- All three policies select 3 new paths post-reset:
  - random_multipath_reset: random sampling with reset seed
  - state_aware_reset: state+path divergence (no pre_alarm context)
  - lemonade_reset: state+path+pre_alarm_distance scoring
- Measure: post-reset path distance from pre-alarm paths

### Route Count and State Mapping
route_count = 3 (stable across pre-alarm and post-reset)
State mapping (index-based, no post-hoc optimization):
pre_alarm_state_0  ↔  post_reset_state_0
pre_alarm_state_1  ↔  post_reset_state_1
pre_alarm_state_2  ↔  post_reset_state_2
If state count diverges, measurement stops and is reported as anomaly.

### Adversary Models

Two conditions tested across all phases:

1. **Random 20% node compromise**: 20% of nodes randomly compromised
2. **Targeted high-degree 20%**: 20% of highest-degree nodes compromised

Compromise is stable (same set) from Phase A through Phase E.

### Sample Size

n = 30 runs per condition

Total: 3 policies × 2 adversary models × 30 runs = 180 runs

## Metrics Definition

### Primary Metrics (Phase E post-reset)

**post_reset_path_distance_from_pre_alarm** (↑ better = more broken)
mean(path_distance(post_reset_path_i, nearest_pre_alarm_path))
for all i in 0..2

Range: [0, ∞) but typically [0, 1] normalized

**state_break_distance** (↑ better = more different)
mean(normalized_hamming_distance(pre_alarm_state_i, post_reset_state_i))
for all i in 0..2
normalized_hamming_distance = popcount(state_i XOR state_j) / 256

Range: [0, 1]

**state_continuity_score** (↓ better = less continuity)
state_continuity_score = 1.0 - state_break_distance

Range: [0, 1]

### Secondary Metrics (Phase A and E)

- lane_collapse_rate: fraction of path pairs below collapse threshold (≤ 0.20)
- path_overlap_internal: internal overlap among selected paths (≤ 25% worse than state_aware_reset)
- clean_path_ratio: paths untouched by any compromised node (Phase A and E)
- path_compromise_rate: fraction of paths touching ≥1 compromised node
- mean_compromised_nodes_per_path: average compromised nodes per selected path
- unique_path_ratio: must remain 1.0 (no duplicate paths)

Adversarial metrics are observed and reported, but do NOT define v1.0.0 success.

## Success Criteria

### Primary Success Threshold

v1.0.0 is **positive** if:

1. **lemonade_reset improves post_reset_path_distance_from_pre_alarm by ≥ +0.10**
   over state_aware_reset, measured as absolute mean difference over n=30 runs

2. **lemonade_reset also exceeds random_multipath_reset** on the same metric
   (sanity baseline: not worse than naive reset)

3. **lane_collapse_rate ≤ 0.20** for lemonade_reset

4. **internal path_overlap not worse than state_aware_reset by >25%**

5. **No oracle knowledge of compromised nodes is used**

### Strong Positive Threshold

v1.0.0 is **strong positive** if conditions above are met AND:

6. **Bootstrap 95% confidence interval for the delta (lemonade_reset - state_aware_reset)**
   has lower bound > 0

### Weak/Suggestive Signal

A delta of +0.05 to +0.10 is reported as **suggestive but not sufficient** for positive claim.

### Negative Result

v1.0.0 is **negative** if:

- post_reset_path_distance_from_pre_alarm delta < +0.05
- or lane_collapse_rate > 0.20
- or internal path_overlap degrades >25%
- or unique_path_ratio < 1.0

## Adversarial Metrics Trade-off Disclosure

If lemonade_reset improves continuity break but worsens clean_path_ratio 
or mean_compromised_nodes_per_path, the report states:
"v1.0.0 shows positive continuity break signal (+X.XX) but does not improve
adversarial exposure metrics. This suggests Lemonade-triggered reset breaks
exploitable continuity but does not guarantee safer routing under compromise.
Future work: approximate exposure signals post-reset without oracle access."

This is an acceptable result because H1 targets continuity break, not adversarial robustness.

## Statistical Analysis

For each policy-adversary pair:

- Report: mean, std, min, max for all primary metrics
- Compute: 95% confidence intervals via bootstrap (1000 samples)
- Test: does CI for (lemonade_reset - state_aware_reset) exclude zero?

A result is statistically significant if 95% CI lower bound > 0.

## Important Caveats

### What v1.0.0 Does NOT Claim

- Physical resistance to cold boot or memory forensic attacks
- Guaranteed memory sanitization (memory_epoch change is simulation-level only)
- Cryptographic security or integrity
- Anonymity or metadata protection
- Global adversary resilience
- Oracle knowledge of compromised nodes

### What v1.0.0 Tests

- Architectural response to local anomaly detection
- Path/state continuity break via deterministic epoch reset
- Reduced path reuse overlap post-reset vs pre-reset baseline
- Scoring function effectiveness post-reset

### Simulation Modeling Notes

Memory rewrite and purge are modeled as:
- epoch increment (deterministic reset, not random)
- state_material invalidation (pre_alarm states unavailable)
- Lane/path context loss (not reusable by greedy scorer)

NOT as:
- Physical RAM sanitization
- Cold boot attack resistance
- Forensic memory recovery prevention

Real memory forensics, DMA attacks, swap/cache residue are out of scope.

## Oracle Policy

**v1.0.0 contains NO oracle exposure-aware scoring.**

Oracle experiment deferred to v1.0.1 / v1.1.0.

If future work requires oracle upper-bound, it is labeled explicitly as "diagnostic upper bound"
and presented as separate from H1 testing.

## Implementation Freeze

Once this protocol is committed, NO changes to:

- Hypothesis H1 (continuity break)
- Scoring weights (0.35/0.35/0.30)
- Primary metric (post_reset_path_distance_from_pre_alarm)
- Success threshold (+0.10 absolute mean)
- Sample size (n=30)
- Adversary models (random 20%, targeted 20%)
- Route count (3 pre, 3 post)
- State mapping (index-based, no post-hoc)

Amendments require new protocol document and re-frozen release.

## Posture and Allowed Claims

### ✅ Allowed

"v1.0.0 testing shows that Lemonade-triggered Dome reset with memory purge reduces 
post-alarm path continuity overlap by X% compared to baseline reset policies."

"This suggests that breaking exploitable state continuity post-alarm can reduce 
exposure correlation over time."

"Future work: approximate Lemonade-style continuity break in real networks."

### ❌ Forbidden

"WHISPER is secure."
"WHISPER detects or identifies compromised nodes."
"WHISPER is resistant to cold boot attacks."
"WHISPER guarantees memory erasure."
"WHISPER provides anonymity or metadata protection."
"v1.0.0 proves WHISPER superiority."

## Expected Timeline

- Day 0: Commit V1_EXPERIMENT_PROTOCOL.md
- Day 1: lemonade_reset_policy_v01.py + unit tests
- Day 2: compare_reset_v01.py + phase model
- Day 3: Benchmark 30 runs to check runtime
- Day 3-4: Full 180 runs (if runtime acceptable; else n=10 pilot)
- Day 4-5: Bootstrap CI, CSV outputs, analysis
- Day 5: SIMULATION_REPORT_v1.0.0.md
- Day 6: Commit, tag v1.0.0, push

## Final Hypothesis Statement

**WHISPER v1.0.0 tests whether Lemonade-triggered memory purge and Nix reset 
can reduce post-alarm path/state continuity below reset baseline policies.**

If positive: continuity break is an achievable architectural response.

If negative: state epoch alone does not sufficiently break exploitable continuity.

Either result is scientifically valid and informs next architectural steps.

---

**This protocol is the contract.**
Results will be reported exactly as observed.
No cherry-picking metrics. No post-hoc criterion changes.
