# WHISPER RotorCode Unlock — Three-Level Architecture

## Principle

WHISPER does not persist operational state. Instead, at each critical event, 
temporary unlock mechanisms create ephemeral access paths without static secrets.

## Three Levels

### Level 1: Master Recovery Passphrase
- Secret root, offline, rare use only
- Ultimate fallback

### Level 2: RotorCode Temporaire
- 30 characters (6 × 5), one-time use
- Delivery: local text + QR (primary), email (fallback)
- TTL configurable at shutdown (except emergency mode)

### Level 3: Unlock Capsule
- Temporary secret tied to RotorCode
- Opens Vault without exposing passphrase
- Consumed and invalidated post-unlock

## Event Modes

### Emergency Defensive Reboot
Fixed duration: 10 minutes post-boot
Display window: 120 seconds pre-boot
No user choice (policy enforced)
One-time use
Fallback: master passphrase

### Clean Shutdown (User Configurable)
User selects Resume RotorCode TTL at shutdown:
( ) No RotorCode
Reopen with master passphrase only.
( ) Short Resume — 15 minutes
For quick restart.
( ) Standard Resume — 1 hour
For short interruption.
( ) Travel Resume — 12 hours
For travel / long break.
( ) Long Resume — 24 hours
⚠️ Higher exposure if code is copied.

Each option includes warning:
RotorCode is one-time use, event-bound.
It will be deleted after unlock or expiration.
Longer validity increases risk if the code is copied.
Choose based on expected resume time and environment.

## Invariants (All Modes)

- RotorCode never stored in clear
- RotorCode never reused
- RotorCode one-time use
- RotorCode deleted/expired post-unlock
- Capsule contains zero operational state
- Master passphrase recovery-only

## Why This Design

**Clean shutdown = flexible**
- User chooses based on actual need
- Travel mode enables real use cases (8h flights)
- No artificial constraints

**Emergency reboot = strict**
- Fixed, short TTL
- No UX decisions under attack
- Security by policy

**Both share capsule model**
- Smaller critical window than direct keyslot
- Extensible (multi-factor, smartphone future)
- Aligns with WHISPER principle: zero state persistence

## Implementation

Deferred to v1.1.0.
v1.0.0 documents design only.

## Addressing the Passphrase SPOF

### Question NLnet/Protocol Labs Will Ask
"Your Vault LUKS depends on user passphrase. Isn't that a single point of failure?"

### Answer

Yes, a static user passphrase would be a SPOF if it were the only operational unlock mechanism.

WHISPER addresses this by separating **recovery identity** from **operational resume**.

The master passphrase remains the recovery root, but routine post-shutdown or post-defensive-reboot unlock uses event-bound RotorCode Unlock Capsules.

A RotorCode is:
- Generated only during clean shutdown or defensive reboot
- One-time use, immediately consumed
- Expires after TTL (15 min to 24h user-configured)
- Unlocks only its corresponding temporary capsule
- Does not persist WHISPER operational state
- Does not replace the master recovery passphrase

### Result

**What WHISPER eliminates:**
- Static passphrase as daily operational unlock
- Persistent key file requiring protection
- Mandatory TPM or hardware security module
- Mandatory network service for unlock
- Opaque auto-unlock mechanisms

**What WHISPER preserves:**
- Master passphrase as recovery root (offline, rare)
- Human agency in unlock decision
- Configurable resume TTL based on context
- One-time ephemeral capsules as default

### Key Principle

**WHISPER does not remove the need for a recovery passphrase.**
**WHISPER removes the static passphrase from the routine operational path.**

This is the correct balance: recovery security vs operational ergonomics.
