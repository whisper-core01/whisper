# WHISPER RotorCode Emergency & Shutdown Unlock

## Principle

WHISPER does not persist static secrets.

Instead, at each critical event, RotorMachine generates ephemeral unlock tokens 
delivered locally/QR/optional-email. Each token is one-time use.

## Two Modes

### Emergency Defensive Reboot
- Triggered by Wasm anomaly detection
- RotorCode displayed urgently
- User photographs code
- Dome reboots Nix
- Post-reboot: user enters code
- LUKS unlocks
- Lemonade deletes keyslot immediately

### Clean Session Close
- User explicitly closes WHISPER
- RotorCode generated for next open
- Session purged, Vault locked
- On next open: user enters RotorCode
- Lemonade deletes keyslot immediately
- Rotation: new code each close

## Delivery Modes

A) Local Display (recommended)
B) QR Scan (best UX)
C) Email (optional fallback, weakens ephemerality)

## Invariants

- Token is never stored in clear
- Token is never reused
- Token is never logged
- Keyslot deleted immediately post-unlock
- One-time use or short TTL
- No fallback to static passphrase for normal operations

## Master Passphrase (Recovery Only)

Master LUKS passphrase remains as last-resort recovery tool only.
RotorCode is not a replacement for master passphrase.
Master passphrase should be rare, offline, secured separately.

## Implementation (v1.1.0+)

Defer to v1.1.0 full integration.
v1.0.0 documents hypothesis and design only.
