# WHISPER RotorCode Unlock — Three-Level Architecture

## Principle

WHISPER does not persist operational state.

Instead, at each critical event, temporary unlock mechanisms 
create ephemeral access paths without static secrets.

## Three Levels

### Level 1: Master Recovery Passphrase
- Secret racine, rarement utilisé
- Accès offline uniquement
- Filet de sécurité final
- NOT daily operational unlock

### Level 2: RotorCode Temporaire
- Code tournant généré à chaque événement
- 30 caractères (6 × 5), haute entropie
- Livraison: texte local ou QR
- Fallback optionnel: email (moins sûr)
- One-time use, event-bound

### Level 3: Unlock Capsule
- Petit secret temporaire chiffré
- Lié au RotorCode (non du keyslot LUKS direct)
- Encapsule nécessaire pour ouvrir Vault
- Consommé et invalidé après unlock
- Permet crypto plus sophistiquée future (multi-factor, smartphone)

## Two Event Modes

### Clean Shutdown
User closes WHISPER
→ RotorMachine generates RotorCode
→ Capsule created (Vault-specific, not LUKS keyslot)
→ Code displayed: text + QR
→ Lemonade purges runtime state
→ Vault locked
→ Capsule persisted (minimal state)
Next open:
→ User enters/scans RotorCode
→ RotorCode unlocks capsule
→ Capsule opens Vault
→ Capsule invalidated
→ New code required next close

### Emergency Defensive Reboot
Wasm anomaly detected
→ RotorMachine generates Emergency RotorCode
→ Capsule prepared (minimal state)
→ Code displayed urgently: text + QR
→ Lemonade: random memory rewrite
→ Lemonade: purge sensitive state
→ Dome: reboot Nix
Post-reboot:
→ User enters/scans Emergency RotorCode
→ Capsule unlocks Vault
→ WHISPER enters post-reset cautious mode
→ Capsule consumed
→ Rotation required for next close

## Invariants

- RotorCode never stored in clear
- RotorCode never reused
- RotorCode never logged
- RotorCode one-time or short TTL
- Capsule contains zero operational state
- Capsule deleted/invalidated post-unlock
- Master passphrase for recovery only
- No auto-unlock (human-mediated)

## Why This Over Direct Keyslot

Direct RotorCode → LUKS keyslot:
- Creates critical window (add → reboot → delete)
- Keyslot must be removed or becomes debt
- No extensibility for multi-factor

RotorCode → Capsule → Vault:
- Shorter, more controlled window
- Capsule is application-level, not LUKS-level
- Future: smartphone as second factor, zero-knowledge proof, etc.
- Aligns with "WHISPER does not persist"

## Delivery Modes

**Primary: Local Display**
- Text: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
- User photographs for re-entry

**Recommended: QR Scan**
- Same security as text
- Better UX
- User scans to enter code

**Fallback: Email (Optional, Explicitly Weaker)**
- Disabled by default
- Must be explicitly enabled
- Code + no context, no logs, no hostname
- Weakens ephemerality (email persistence)
- Warning: email compromise = code leaks

## Recovery Hierarchy

1. **Daily unlock**: RotorCode → Capsule → Vault
2. **Emergency unlock**: Emergency RotorCode → Capsule → Vault
3. **Ultimate recovery**: Master passphrase (offline, rare)

## Non-Claims

- No TPM required
- No network required
- No persistent key files
- No static passphrase as primary unlock
- No dangerous auto-unlock
- No operational state persisted

## Implementation

Deferred to v1.1.0 full integration.
v1.0.0 documents design and hypothesis only.
