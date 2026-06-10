# WHISPER — Security Invariants

Version: v0.1-draft
Status: architectural doctrine before implementation hardening

## 0. Principle

WHISPER does not rely on approximation.

No uncontrolled external material may cross an organic boundary.
Every boundary rejects by default.
Every promotion to the next layer must be explicit, validated, and measurable.

Core rule:

```text
No invariant without a test.
No test without a metric.
No metric without a report.
No report without explicit limits.
```

---

# 1. Fragment Model — Cryptographic Egg

A WHISPER fragment is modeled as a cryptographic egg.

```text
Shell    → visible envelope inspected by the Dome
Membrane → cryptographic protection and derivation boundary
Core     → useful fragment material processed only by the MCE
```

## WHISPER-FRAG-INV-01 — Cryptographic Egg

A sealed fragment is composed of:

1. a visible shell carrying local validation material;
2. a cryptographic membrane enforced by AEAD and local derivation context;
3. an encrypted core containing the useful text/file slice, locally encoded or compressed.

The visible shell must never expose plaintext payload material.

## WHISPER-FRAG-INV-02 — Self-Contained, Not Self-Unlocking

A fragment may be self-contained for routing, ordering, validation, provenance, and local derivation context.

A fragment must never be self-unlocking.

Forbidden visible material:

```text
master_seed
session_seed
wake_seed
secret seed material
fragment decryption key
plaintext payload
full message
global route map
pipeline map
```

Allowed visible public context:

```text
slot_id
seed_id
nonce
timestamp_bucket
chain reference
checksum / CRC
class_token
compression ratio indicator
ciphertext
```

## WHISPER-FRAG-INV-03 — seed_id Is Public Context Only

`seed_id` is a public derivation context identifier.

`seed_id` is not:

```text
a secret seed
a decryption key
a master seed
a session seed
sufficient material to decrypt a fragment
```

The fragment key is derived only from local secret material plus public fragment context.

Conceptually:

```text
K_fragment = KDF(local_secret, seed_id || nonce || slot_id || local RotorMachine context)
```

---

# 2. Dome Boundary

The Dome is the mandatory quality gate before BAL_IN, Membrane, MCE, or Wasm.

The Dome receives external material.
The Dome qualifies or rejects.
The Dome does not disclose its decision externally.

## WHISPER-DOME-INV-01 — Mandatory Qualification Boundary

All externally received fragments must pass through the Dome before reaching any active internal processing boundary.

No raw external fragment may be deposited directly into BAL_IN.

## WHISPER-DOME-INV-02 — Local Silent Rejection

The Dome may reject:

```text
decoys
clones
replays
corrupted fragments
stale fragments
invalid-chain fragments
invalid-provenance fragments
invalid CRC/checksum fragments
```

Rejection must be local and silent.

A rejection must not produce:

```text
external ACK
external error
public log
network response
observable rejection signal
distinct externally visible behavior
```

## WHISPER-DOME-INV-03 — Decoy Rejection Before MCE

Decoys are classified and rejected by the Dome at shell level.

The MCE must not receive decoys under normal operation.

## WHISPER-DOME-INV-04 — Shell Validation

The Dome validates the fragment shell before promotion.

The shell may carry:

```text
slot_id
seed_id
timestamp_bucket
checksum
CRC
local blockchain reference
class_token
cr
ciphertext
```

The Dome uses this material to evaluate provenance, non-alteration, freshness, and class eligibility.

---

# 3. Local Blockchain / Provenance

## WHISPER-CHAIN-INV-01 — Local Non-Distributed Provenance

Each fragment may carry local non-distributed blockchain material.

This material proves provenance, filiation, and continuity within the local WHISPER context.

It must not become a global tracking identifier.

## WHISPER-CHAIN-INV-02 — Invalid Provenance Rejection

Fragments with invalid chain continuity or invalid provenance must be rejected by the Dome before BAL_IN.

Such fragments must not reach the MCE or any Wasm organ.

---

# 4. Checksum / CRC / Timestamp

## WHISPER-INTEGRITY-INV-01 — Temporal Non-Alteration Context

Checksum and CRC are interpreted with timestamp/cycle context.

They provide local evidence of non-alteration and freshness before MCE processing.

## WHISPER-INTEGRITY-INV-02 — Not a Replacement for AEAD

Checksum and CRC do not replace AEAD authentication.

They are Dome-level rejection filters.

AEAD remains the cryptographic authenticity and integrity mechanism for the encrypted core.

---

# 5. AEAD / Membrane

## WHISPER-AEAD-INV-01 — Cryptographic Authenticity

The AEAD tag proves cryptographic authenticity and integrity of the encrypted fragment core.

The MCE verifies AEAD during decryption.

If AEAD verification fails, the fragment is rejected.

## WHISPER-AEAD-INV-02 — MCE-Only Decryption

Only the MCE may derive the fragment key and decrypt the encrypted core.

Daemon, Dome, Coursier, BAL_IN, and Membrane must not decrypt fragment cores.

---

# 6. MCE Boundary

The MCE is not a trash sorter.
The MCE is the clean processing room.

## WHISPER-MCE-INV-01 — First-Grade Material Only

The MCE only processes first-grade material promoted by the Dome.

The following must not cross the MCE boundary:

```text
decoys
clones
replays
corrupted fragments
stale fragments
invalid-chain fragments
invalid-provenance fragments
raw external fragments
```

## WHISPER-MCE-INV-02 — No Unqualified Material in BAL_IN

The active BAL_IN may contain only Dome-promoted material.

No raw network material may be deposited into active BAL_IN.

## WHISPER-MCE-INV-03 — Late Failure Is Exceptional

The MCE may still reject a fragment due to AEAD failure, decoding failure, or internal checksum failure.

Such failure is treated as exceptional or late corruption, not as normal decoy sorting.

---

# 7. Wasm Boundary

Wasm is not a garbage disposal.

The Wasm sandbox limits execution, but it must not be the first filter for uncontrolled external material.

## WHISPER-WASM-INV-01 — No Raw External Material Enters Wasm

No raw external fragment may enter a Wasm organ.

All externally received fragments must first pass Dome-level qualification.

## WHISPER-WASM-INV-02 — Qualified Material Only

A Wasm organ may receive only material promoted by the proper upstream boundary.

For MCE-related organs, that means Dome-promoted, BAL_IN-qualified, Membrane-signaled fragments.

## WHISPER-WASM-INV-03 — Sandbox Is Defense-in-Depth

Wasm sandboxing is a defense-in-depth execution boundary.

It does not replace Dome qualification, BAL_IN hygiene, MCE first-grade material policy, or AEAD authentication.

---

# 8. Decoys

## WHISPER-DECOY-INV-01 — Dome-Level Classification

Real/decoy classification occurs before the MCE boundary.

The MCE must not intentionally process decoys.

## WHISPER-DECOY-INV-02 — No External Signal

Decoy rejection must not be externally signaled.

The external observer must not be able to infer Dome rejection through explicit output, error, ACK, or public log.

## WHISPER-DECOY-INV-03 — Same Transport Shape

Decoys and real fragments must share the same external transport shape unless the distinction is interpretable only by the Dome.

No field may be named:

```text
is_decoy
real
fake
decoy
```

in externally visible transport structures.

---

# 9. Compression

## WHISPER-COMP-INV-01 — Per-Fragment Compression

Compression is applied independently per fragment.

WHISPER does not compress the full payload globally before fragmentation in the sensitive MCE path.

## WHISPER-COMP-INV-02 — Self-Contained Encoded Fragment

Each fragment carries an encoded/compressed body that can be decoded independently after decryption.

No fragment may require a global compression dictionary or global payload context.

## WHISPER-COMP-INV-03 — Codec Selection Policy

The codec is selected by `turbo_quant`, not directly by the MCE.

The MCE invokes the fragment encoding pipeline and then seals the result.

Allowed v1 modes:

```text
Raw
LZH
```

A codec may be selected only if:

```text
roundtrip succeeds
forbidden metadata count is zero
encoded size including header beats Raw according to policy
```

## WHISPER-COMP-INV-04 — No Archive Metadata

No compression mode may introduce:

```text
filename
filesystem path
timestamp
user identifier
system metadata
archive metadata
```

---

# 10. Current Validation Status

Current confirmed tests:

```text
Rust lib tests: 47 passed
Sandbox tests: 4 passed
Verification metrics tests: 6 passed
SUP-INV-01: validated
SUP-INV-02: validated
SUP-INV-03a: MCE sealed output baseline validated
```

Current limitations:

```text
FragmentScelle still needs to be upgraded to the full cryptographic egg model.
Dome quality gate is not fully implemented as described here.
SUP-INV-03 complete is not yet validated.
SUP-INV-05 serialized transition isolation is not yet validated.
1k / 10k / 100k / 1M stress must wait until Tier-1 invariants are fully implemented.
```

---

# 11. Controlled Polymorphism

WHISPER is a controlled polymorphic architecture.

WHISPER may change observable appearance, but it must never change its architectural identity.

Canonical phrase:

```text
WHISPER peut se déguiser pour Halloween,
mais il n’en reste pas moins WHISPER.
```

## WHISPER-POLYMORPHISM-INV-01 — Controlled Polymorphism

WHISPER may alter its observable form through:

```text
carrier rotation
video-like traffic
audio-like traffic
game-like traffic
social-like traffic
timing variation
dynamic timeout policy
randomized tunnel selection
codec policy
permanent decoy flow
transport camouflage
```

However, polymorphism must remain controlled.

No polymorphic variation may bypass:

```text
Dome qualification
Wasm foundational execution boundary
MCE first-grade material policy
AEAD authentication
local derivation rules
seed secrecy rules
decoy behavioral equivalence
fragment size policy
reporting requirements
verification requirements
```

## WHISPER-POLYMORPHISM-INV-02 — Stable Identity Under Disguise

A disguised WHISPER instance remains WHISPER only if it preserves the core architectural identity.

Core identity:

```text
Dome is mandatory.
Wasm is foundational.
MCE only processes first-grade material.
Fragments are cryptographic eggs.
Decoys are unfertilized cryptographic eggs.
Decoy traffic is permanent.
Real fragments and decoys are structurally indistinguishable.
AEAD protects the encrypted core.
Local derivation protects fragment keys.
No secret seed is exposed.
Every security claim is explicit, tested, measured, and reported.
```

If a disguise violates one of these properties, it is not a valid WHISPER mode.

## WHISPER-POLYMORPHISM-INV-03 — Costume Is Not Identity

Carrier profiles, timing profiles, tunnel choices, codecs, and camouflage strategies are costumes.

They may change.

They do not define WHISPER’s security identity.

WHISPER security must not depend on a single costume.

Canonical phrase:

```text
Le costume change.
La colonne vertébrale ne change pas.
```

## WHISPER-POLYMORPHISM-INV-04 — No Unbounded Morphing

WHISPER polymorphism must be bounded by explicit policy.

A component may not arbitrarily mutate behavior outside declared limits.

Every polymorphic behavior must declare:

```text
allowed range
activation condition
inhibited state
observable surface
security impact
test coverage
metric output
fallback or replacement rule
```

No uncontrolled mutation is allowed.

## WHISPER-POLYMORPHISM-INV-05 — Revalidation After Morphing

Any change in carrier, timing, tunnel, codec, decoy policy, or transport profile must trigger revalidation of the affected invariants.

At minimum, the following must be rechecked:

```text
real/decoy structural indistinguishability
decoy permanent flow
fragment size bounds
timer policy equivalence
timeout policy equivalence
tunnel policy equivalence
no visible decoy marker
no plaintext exposure
no secret seed exposure
Dome rejection behavior
BAL_IN promotion hygiene
MCE first-grade material policy
```

# 12. Modular Lego Doctrine

WHISPER is built like a controlled Lego construction.

Each component has:

```text
a clear boundary
a narrow responsibility
explicit invariants
testable behavior
measurable output
replaceability rules
activation/inhibition logic
```

A WHISPER component may be replaceable, but not all components are optional.

WHISPER distinguishes:

```text
foundational components
functional components
carrier/camouflage components
policy components
```

## WHISPER-MODULARITY-INV-01 — Lego Construction

WHISPER is a modular architecture.

Each component must expose:

```text
input boundary
output boundary
responsibility
security claims
failure modes
replacement conditions
tests
metrics
```

No component may become an undocumented single point of architectural failure.

Canonical phrase:

```text
Une brique WHISPER peut mourir.
WHISPER ne doit pas mourir avec elle.
```

## WHISPER-MODULARITY-INV-02 — Capability Activation

Each functional component activates an explicit capability when present.

If the component is absent, disabled, removed, or replaced by a neutral version, the associated capability must be explicitly inhibited.

No capability may be assumed active implicitly.

Canonical rule:

```text
Brique présente  → capacité active → invariants testables
Brique absente   → capacité inhibée → claims désactivés
Brique remplacée → capacité réévaluée → tests relancés
```

## WHISPER-MODULARITY-INV-03 — No Ghost Capability

A WHISPER capability must not exist as a ghost assumption.

If the component that provides a capability is absent, disabled, failed, or removed, then:

```text
the capability is unavailable
dependent claims are disabled
reports must show degraded capability
tests must reflect the missing component
```

A missing component must never leave a false impression of security.

## WHISPER-MODULARITY-INV-04 — Replaceability Without Identity Loss

Functional and policy components may be replaced if the replacement preserves the required interface and passes the required invariant tests.

Replaceable components may include:

```text
carrier profile
timing policy
timeout policy
tunnel selection policy
compression codec
threat scoring module
transport adapter
reporting backend
```

Replacement must not bypass foundational invariants.

## WHISPER-MODULARITY-INV-05 — Explicit Degraded Mode

If WHISPER enters degraded mode due to a missing functional component, the degraded mode must be explicit.

A degraded report must state:

```text
missing component
disabled capability
security claims removed
remaining active claims
additional risk
tests not run
tests failed
tests still valid
```

No silent degraded mode is allowed.


# 13. Foundational Components

Not every WHISPER component is optional.

Some components are foundational.

A foundational component is part of WHISPER’s architectural security model.
If such a component is absent, the dependent subsystem must not run.

## WHISPER-FOUNDATION-INV-01 — Foundational Components

A foundational component is required to preserve WHISPER’s security identity.

If a foundational component is absent, WHISPER must disable the dependent subsystem rather than silently falling back to a weaker mode.

A foundational component is not a decorative feature.

## WHISPER-FOUNDATION-INV-02 — Wasm Is Foundational

Wasm sandboxing is a foundational execution boundary for WHISPER organs.

It is not an optional capability.

If the Wasm execution boundary is unavailable, WHISPER must not execute organ logic that requires sandbox isolation.

Correct rule:

```text
Wasm present → WHISPER organ execution authorized
Wasm absent  → WHISPER organ execution forbidden
```

Incorrect rule:

```text
Wasm absent → fallback local execution with same claims
```

Such a fallback is forbidden unless it is explicitly defined as a different, reduced, non-equivalent mode with reduced claims.

## WHISPER-FOUNDATION-INV-03 — Foundation Absence Disables Dependent Rooms

A functional room may be disabled if its foundation is missing.

Example:

```text
Wasm unavailable
→ organ execution disabled
→ dependent claims disabled
→ no silent fallback
```

Canonical phrase:

```text
Une brique fonctionnelle peut être retirée.
Une fondation absente condamne la pièce qui repose dessus.
```

## WHISPER-FOUNDATION-INV-04 — Foundation Replacement Requires Full Revalidation

A foundational component may be replaced only through full revalidation.

Replacing the Wasm runtime, execution boundary, sandbox policy, memory isolation model, or host capability model requires rerunning all affected Tier-1 invariants.

At minimum:

```text
sandbox execution test
memory isolation test
host capability restriction test
no raw external material enters Wasm test
serialized transition test
organ boundary test
report generation test
```


A new disguise without revalidation is not trusted.



# 14. Target Test Matrix

Required next tests:

```text
test_fragment_shell_rejects_invalid_crc
test_fragment_shell_rejects_invalid_checksum
test_fragment_shell_rejects_invalid_timestamp
test_fragment_shell_rejects_invalid_chain
test_dome_rejects_decoy_before_mce
test_bal_in_accepts_only_dome_promoted_material
test_wasm_never_receives_raw_external_fragment
test_mce_receives_first_grade_material_only
test_fragment_body_roundtrip_after_aead_and_turbo_quant
test_real_and_decoy_transport_shape_is_not_explicitly_labeled
test_transition_is_serialized_not_shared_mutable_state
```

Stress targets after baseline:

```text
1k
10k
100k
1M
```
Metrics to report:

```text
raw_external_fragments_entered_wasm = 0
decoys_entered_mce = 0
clones_accepted = 0
replays_accepted = 0
invalid_crc_accepted = 0
invalid_checksum_accepted = 0
invalid_chain_accepted = 0
invalid_timestamp_accepted = 0
plaintext_exposure_count = 0
secret_seed_exposure_count = 0
shared_wasm_memory_detected = 0
```
