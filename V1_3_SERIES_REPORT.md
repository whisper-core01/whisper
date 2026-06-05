
WHISPER v1.3 Series Report
Executive Summary

WHISPER v1.3 is a routing and reconstruction evolution for sovereign local-first communication.

Author profile:

independent developer
approximately 15 years of development experience
solo architecture and prototype work
focus: decentralized, compartmentalized, resilient communication

What v1.3 introduces:

Sol-link magnetic hop-by-hop routing
local pressure-field routing
probabilistic next-hop selection
adaptive redundancy
persistent custody
buffered and streaming receive modes
strict VoxMesh / WHISPER / Reticulum separation

Why it matters:

WHISPER is not designed as a smarter classical router.

It is designed as a compartmentalized communication organism that survives without global truth.

No layer knows everything.

No layer chooses everything.

No layer reveals everything.

Current result:

228 tests passing
98.89% reconstruction on good network profiles
100% reconstruction on normal, bad, and very bad network profiles
stable exposure
low loop rate
low dead-end rate
layer-blindness invariants preserved

The v1.3 series provides a complete experimental narrative suitable for NLnet / Protocol Labs review.

1. Core Architecture

WHISPER v1.3 separates responsibility into layers.

VoxMesh:

qualifies logical WHISPER relays
tracks admissibility
tracks local relay state
does not know Reticulum transport identities
does not know where the capsule goes

WHISPER:

fragments
encapsulates
scores logical relays
performs probabilistic hop-by-hop selection
manages custody and reconstruction strategy
does not route over the Reticulum graph

Reticulum:

transports opaque capsules
may decode transport material in real time
does not know WHISPER payload
does not participate in WHISPER logical scoring

Core rule:

VoxMesh qualifies.

WHISPER selects.

Reticulum transports.

No layer knows everything.

2. Unpredictability Invariant

WHISPER must never expose enough information for any single layer, node, endpoint, or observer to:

predict the complete route
anticipate the future hop sequence
reconstruct the fragment distribution
infer the underlying transport path
identify useful, repair, or decoy packets at the transport-observable layer

Routing decisions must remain:

local
probabilistic
epoch-scoped
context-dependent

Scores may bend probability.

They must never deterministically define the path.

Short form:

Constraints reduce the space.

Scores bend probability.

Randomness chooses.

The path emerges.

No layer knows everything.

3. Architecture Evolution
v1.3.0 — Sol-Link Magnetic Logical Routing

v1.3.0 introduced the Sol-link magnet.

A live Sol-compatible link derives an epoch-scoped Sol-link alias.

This alias acts as a magnetic attractor.

It does not define a route.

It does not expose a stable destination.

It does not expose a Reticulum address.

The routing decision remains local and probabilistic.

Core result:

Sol-link magnetic routing works mechanically
layer blindness invariants are preserved
exposure begins to improve at moderate magnet strength
raw magnet strength still requires control

Finding:

The magnet works, but it must be canalized.

v1.3.1 — Sol-Link Pressure Field

v1.3.1 added the pressure field.

It introduced:

randomness dissipation
wandering safety
routing basin safety
candidate-count tracking
dead-end detection
transport delivery ratio

The goal was to prevent the raw magnet from creating unstable corridors.

Core result:

exposure improved relative to raw magnet routing
loop behavior improved
pressure-field routing became cleaner
magnet_strength = 6.0 and wandering_strength = 0.5 became the best pilot trade-off

Finding:

v1.3.1 validates direction control.

The path remains emergent, but the flow is now canalized.

v1.3.2 — Redundancy and Custody

v1.3.2 introduced controlled redundancy and persistent custody.

The initial naive model treated a fragment as lost if the full route failed end-to-end.

That was too strict.

The corrected model introduced custody:

A fragment that reaches a WHISPER relay is not immediately lost.

It may persist locally and continue later.

This changed the reconstruction model from strict end-to-end delivery to persistent hop-by-hop progress.

Core result:

110% redundancy was insufficient
120% was near the reconstruction threshold
125% achieved 90% reconstruction in the pilot
130% approached 97.8% reconstruction
custody was essential to make redundancy meaningful

Finding:

The rain only works if intermediate basins can retain droplets.

v1.3.3 — Blind Repair and Decoy-Equivalent Flow

v1.3.3 is a defensive design layer.

Status:

design frozen
implementation pending
not yet included in the tested metrics

Purpose:

v1.3.3 prevents observers from distinguishing:

useful fragments
repair shards
decoy packets

Principle:

WHISPER never retransmits a missing fragment as-is.

Repair material is re-sliced into randomized variable-size chunks, repadded, re-encapsulated, and routed independently.

Repair packets must be transport-indistinguishable from ordinary WHISPER fragments.

Finding:

v1.3.4 solves delivery reliability.

v1.3.3 is intended to improve long-term anti-correlation defense.

v1.3.4 — Adaptive Network-Aware Redundancy

v1.3.4 replaced fixed redundancy with adaptive local control.

WHISPER now adapts:

redundancy factor
custody rounds
repair budget
receive mode

from local non-oracle symptoms:

latency risk
jitter risk
timeout risk
signal loss risk
receiver capacity risk

The first adaptive profile was too optimistic.

It used:

minimum redundancy 1.10
minimum custody 3

This failed under good and normal profiles.

The calibrated profile now uses:

minimum redundancy 1.25
maximum redundancy 1.40
minimum custody rounds 5
maximum custody rounds 7

This prevents WHISPER from saving bandwidth at the cost of reliability.

Finding:

Adaptive redundancy works, but only with a reliability floor.

4. Key Metrics Across v1.3 Series

Latest calibrated v1.3.4 n360 pilot:

GOOD network profile:

network risk: 0.1006
adaptive redundancy: 1.2651
adaptive custody: 5
streaming ratio: 0.0
reconstruction: 0.9889
delivered total: 107.47
reconstruction margin: +7.47
bandwidth overhead: 1.27
exposure: 1.0859
loop rate: 0.0378
dead-end rate: 0.0111
invariants: OK

NORMAL network profile:

network risk: 0.3604
adaptive redundancy: 1.3041
adaptive custody: 6
streaming ratio: 0.0
reconstruction: 1.0000
delivered total: 110.98
reconstruction margin: +10.98
bandwidth overhead: 1.31
exposure: 1.0898
loop rate: 0.0332
dead-end rate: 0.0106
invariants: OK

BAD network profile:

network risk: 0.6524
adaptive redundancy: 1.3479
adaptive custody: 6
streaming ratio: 0.6333
reconstruction: 1.0000
delivered total: 114.71
reconstruction margin: +14.71
bandwidth overhead: 1.3527
exposure: 1.0525
loop rate: 0.0345
dead-end rate: 0.0081
invariants: OK

VERY_BAD network profile:

network risk: 0.9005
adaptive redundancy: 1.3851
adaptive custody: 7
streaming ratio: 1.0
reconstruction: 1.0000
delivered total: 118.10
reconstruction margin: +18.10
bandwidth overhead: 1.3907
exposure: 1.0691
loop rate: 0.0376
dead-end rate: 0.0104
invariants: OK
5. Cross-Series Interpretation

v1.3.0 showed that Sol-link attraction can shape routing flow.

v1.3.1 showed that the raw magnet must be canalized by a pressure field.

v1.3.2 showed that message reconstruction requires redundancy plus persistent custody.

v1.3.4 showed that redundancy should not be fixed.

It must adapt to local network symptoms while respecting a minimum reliability floor.

v1.3.3 remains the defensive anti-correlation layer that will hide repair patterns and decoy structure.

Together, the v1.3 series demonstrates a coherent architecture:

no global route
no deterministic best path
no Reticulum graph enumeration
no Reticulum address exposure in VoxMesh
no WHISPER payload visibility in Reticulum
no single layer holds the full truth
6. Philosophical Foundation

WHISPER is not a smarter router.

WHISPER is a compartmentalized communication organism.

It does not survive by knowing everything.

It survives by ensuring that no layer knows everything.

Classical routing tries to compute a route.

WHISPER creates conditions for a route to emerge.

Classical systems concentrate knowledge.

WHISPER distributes ignorance.

Classical reliability often depends on deterministic paths.

WHISPER uses pressure, custody, redundancy, and adaptation.

Core idea:

The system is strong because it is incompletely known.

7. Production-Readiness Status

WHISPER v1.3 is not yet production-ready.

However, the v1.3 series establishes several production-readiness signals:

228 tests passing
deterministic reproducible simulations
no oracle dependency
no manual routing decisions
local-only network symptoms
adaptive parameters
layer-blindness invariants validated
reconstruction reliability reaches 98.89% to 100% in the n360 pilot
Reticulum / VoxMesh / payload separation preserved

Remaining work before production:

implement real erasure coding
implement real cryptographic repair shards
implement v1.3.3 blind repair and decoy-equivalent flow
integrate with real Reticulum primitives
test under real network conditions
expand adversarial simulations
benchmark bandwidth, memory, and CPU costs
formalize threat model updates
harden state persistence and custody management
8. Why This Matters for NLnet / Protocol Labs

WHISPER aligns with funding goals around:

sovereign communication
decentralized infrastructure
privacy-preserving transport
local-first design
compartmentalized security
censorship resistance
resilient communication under degraded conditions
verifiable open-source experimentation

The key contribution is not another overlay router.

The key contribution is a compartmentalized routing and reconstruction model where:

VoxMesh does not know where capsules go
Reticulum does not know what it transports
WHISPER does not expose full routing truth
message reconstruction survives partial transport failure
routing remains probabilistic and local
adaptation is based on non-oracle symptoms

This is a practical privacy architecture, not only a theoretical abstraction.

9. Current Calibrated Pilot Parameters

Recommended v1.3.4 pilot parameters:

magnet_strength:
6.0

wandering_strength:
0.5

minimum redundancy:
1.25

maximum redundancy:
1.40

minimum custody rounds:
5

maximum custody rounds:
7

streaming threshold:
receiver_capacity_risk >= 0.65

receive modes:
BUFFERED
STREAMING

Initial operational interpretation:

good network: around 1.27 overhead
normal network: around 1.31 overhead
bad network: around 1.35 overhead
very bad network: around 1.39 overhead

The target is not minimum overhead.

The target is reliable reconstruction without violating the invariants.

10. Roadmap
v1.3.3 — Blind Repair and Decoy-Equivalent Flow

Status:
design frozen, implementation pending

Goal:
prevent observers from identifying repair patterns or missing fragment structure

Expected additions:
randomized repair slicing
variable-size repair chunks
decoy-equivalent packets
repair packets indistinguishable from normal fragments
no retransmission of missing fragments as-is

v1.4.0 — Session-Hash Revocation

Goal:
introduce local revocation propagation without exposing stable identities

Expected additions:
session-scoped revocation
hash-bound relay rejection
local revocation memory
no global blacklist requirement

v1.5.0 — Distributed Temporal Immunity

Goal:
model long-term immune behavior across time

Expected additions:
temporal degradation memory
adaptive trust decay
recovery of previously degraded relays
local immune response
no global oracle

11. Final Statement

The v1.3 series changes WHISPER from a path-selection prototype into a compartmentalized adaptive communication organism.

The route is not chosen globally.

The path emerges locally.

The message is reconstructed through custody and adaptive redundancy.

The transport remains opaque.

The logical tissue remains blind to transport identity.

No layer knows everything.

Final rule:

VoxMesh qualifies.

WHISPER selects.

Reticulum transports.

The Sol-link attracts.

The pressure field canalizes.

Custody persists.

Adaptive redundancy reconstructs.

The path emerges.

