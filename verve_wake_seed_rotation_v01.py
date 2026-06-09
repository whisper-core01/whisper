"""
WHISPER v1.8.0 — Verve Wake Seed Rotation v0.1

Purpose:
Model the pre-LUKS wake seed mechanism.

Core idea:
WHISPER does not know the future rotating code.
Before clean shutdown, WHISPER generates a 64-character wake_seed, configures
a dedicated Verve LUKS keyslot, transmits the wake_seed to Verve, and zeroizes
its local copy.

Before LUKS unlock, Verve derives rotating human-readable codes from wake_seed.
The rotating code is a surface representation, not the sovereign secret.

Doctrine:
The seed sleeps in Verve.
The code rotates on its surface.
LUKS recognizes the seed.
WHISPER is born after unlock.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Dict, Literal, Set


WakeSeedState = Literal[
    "GENERATED",
    "HANDED_TO_VERVE",
    "ZEROIZED",
]

LuksUnlockDecision = Literal[
    "unlock_allowed",
    "unlock_rejected",
]

CodeState = Literal[
    "ROTATING",
    "FROZEN",
    "EXPIRED",
    "CONSUMED",
]


WAKE_SEED_LENGTH = 64
ROTATION_WINDOW_SECONDS = 10
FROZEN_WINDOW_SECONDS = 60

ALPHABET = "abcdef0123456789"


@dataclass
class WakeSeedMaterial:
    seed: str
    state: WakeSeedState = "GENERATED"


@dataclass
class VerveVault:
    wake_seed: str | None = None
    zeroized_after_unlock: bool = False
    keyslot_id: str | None = None
    revoked_keyslots: Set[str] = field(default_factory=set)


@dataclass
class LuksHeaderMock:
    verve_keyslots: Dict[str, str] = field(default_factory=dict)
    human_passphrase_available: bool = True


@dataclass(frozen=True)
class RotatingCode:
    code: str
    block_index: int
    state: CodeState = "ROTATING"


@dataclass
class RotatingCodeSession:
    current_code: RotatingCode
    frozen_at_second: int | None = None
    consumed: bool = False


@dataclass
class VerveUnlockAttempt:
    keyslot_id: str
    presented_seed: str
    zeroized_after_attempt: bool = False


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "verve_wake_seed_rotation::"
        f"{test_name}"
    )


def _stable_hex(*parts: str, length: int = 64) -> str:
    digest = sha256()

    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\x00")

    return digest.hexdigest()[:length]


def generate_wake_seed(entropy: str) -> WakeSeedMaterial:
    if not entropy:
        raise ValueError("entropy must be non-empty")

    return WakeSeedMaterial(
        seed=_stable_hex(
            "WHISPER_VERVE_WAKE_SEED_V1",
            entropy,
            length=WAKE_SEED_LENGTH,
        ),
        state="GENERATED",
    )


def wake_seed_is_64_chars(seed: str) -> bool:
    return len(seed) == WAKE_SEED_LENGTH


def wake_seed_is_well_formed(seed: str) -> bool:
    return wake_seed_is_64_chars(seed) and all(ch in ALPHABET for ch in seed)


def configure_luks_verve_keyslot(
    luks: LuksHeaderMock,
    keyslot_id: str,
    wake_seed: WakeSeedMaterial,
) -> None:
    if not wake_seed_is_well_formed(wake_seed.seed):
        raise ValueError("wake_seed must be 64 lowercase hex characters")

    luks.verve_keyslots[keyslot_id] = _stable_hex(
        "LUKS_VERVE_KEYSLOT_BINDING",
        keyslot_id,
        wake_seed.seed,
        length=64,
    )


def handoff_wake_seed_to_verve(
    wake_seed: WakeSeedMaterial,
    verve: VerveVault,
    keyslot_id: str,
) -> WakeSeedMaterial:
    if not wake_seed_is_well_formed(wake_seed.seed):
        raise ValueError("invalid wake_seed")

    verve.wake_seed = wake_seed.seed
    verve.keyslot_id = keyslot_id
    wake_seed.state = "HANDED_TO_VERVE"

    return wake_seed


def zeroize_wake_seed(wake_seed: WakeSeedMaterial) -> WakeSeedMaterial:
    wake_seed.seed = "\x00" * WAKE_SEED_LENGTH
    wake_seed.state = "ZEROIZED"
    return wake_seed


def derive_rotating_code(
    wake_seed: str,
    epoch_second: int,
) -> RotatingCode:
    if not wake_seed_is_well_formed(wake_seed):
        raise ValueError("invalid wake_seed")

    if epoch_second < 0:
        raise ValueError("epoch_second must be >= 0")

    block_index = epoch_second // ROTATION_WINDOW_SECONDS

    code = _stable_hex(
        "WHISPER_ROTATING_WAKE_CODE_V1",
        wake_seed,
        str(block_index),
        length=16,
    )

    return RotatingCode(
        code=code,
        block_index=block_index,
        state="ROTATING",
    )


def start_rotating_code_session(
    wake_seed: str,
    epoch_second: int,
) -> RotatingCodeSession:
    return RotatingCodeSession(
        current_code=derive_rotating_code(wake_seed, epoch_second),
        frozen_at_second=None,
        consumed=False,
    )


def update_rotating_code_session(
    session: RotatingCodeSession,
    wake_seed: str,
    epoch_second: int,
) -> RotatingCodeSession:
    if session.current_code.state == "FROZEN":
        return session

    if session.consumed:
        session.current_code = RotatingCode(
            code=session.current_code.code,
            block_index=session.current_code.block_index,
            state="CONSUMED",
        )
        return session

    session.current_code = derive_rotating_code(wake_seed, epoch_second)
    return session


def freeze_code_on_first_input(
    session: RotatingCodeSession,
    epoch_second: int,
) -> RotatingCodeSession:
    if epoch_second < 0:
        raise ValueError("epoch_second must be >= 0")

    session.frozen_at_second = epoch_second
    session.current_code = RotatingCode(
        code=session.current_code.code,
        block_index=session.current_code.block_index,
        state="FROZEN",
    )

    return session


def frozen_code_expired(
    session: RotatingCodeSession,
    epoch_second: int,
) -> bool:
    if session.frozen_at_second is None:
        return False

    return (epoch_second - session.frozen_at_second) > FROZEN_WINDOW_SECONDS


def consume_rotating_code(session: RotatingCodeSession) -> RotatingCodeSession:
    session.consumed = True
    session.current_code = RotatingCode(
        code=session.current_code.code,
        block_index=session.current_code.block_index,
        state="CONSUMED",
    )

    return session


def verve_attempt_luks_unlock(
    luks: LuksHeaderMock,
    verve: VerveVault,
) -> tuple[LuksUnlockDecision, VerveUnlockAttempt | None]:
    if verve.wake_seed is None or verve.keyslot_id is None:
        return "unlock_rejected", None

    if verve.keyslot_id in verve.revoked_keyslots:
        return "unlock_rejected", None

    expected = luks.verve_keyslots.get(verve.keyslot_id)

    if expected is None:
        return "unlock_rejected", None

    presented = _stable_hex(
        "LUKS_VERVE_KEYSLOT_BINDING",
        verve.keyslot_id,
        verve.wake_seed,
        length=64,
    )

    attempt = VerveUnlockAttempt(
        keyslot_id=verve.keyslot_id,
        presented_seed=verve.wake_seed,
        zeroized_after_attempt=False,
    )

    if presented != expected:
        attempt.zeroized_after_attempt = True
        verve.wake_seed = None
        verve.zeroized_after_unlock = True
        return "unlock_rejected", attempt

    attempt.zeroized_after_attempt = True
    verve.wake_seed = None
    verve.zeroized_after_unlock = True

    return "unlock_allowed", attempt


def revoke_verve_keyslot(
    luks: LuksHeaderMock,
    verve: VerveVault,
    keyslot_id: str,
) -> None:
    luks.verve_keyslots.pop(keyslot_id, None)
    verve.revoked_keyslots.add(keyslot_id)


def human_passphrase_is_fallback(luks: LuksHeaderMock) -> bool:
    return luks.human_passphrase_available


def pre_luks_stage_contains_core_secrets() -> bool:
    return False


def verve_contains_vault_or_flv() -> bool:
    return False


def rotating_code_contains_luks_key() -> bool:
    return False


def clean_shutdown_prepare_verve_wake_path(
    entropy: str,
    keyslot_id: str = "verve-slot-1",
) -> tuple[LuksHeaderMock, VerveVault, WakeSeedMaterial]:
    luks = LuksHeaderMock()
    verve = VerveVault()

    wake_seed = generate_wake_seed(entropy)
    configure_luks_verve_keyslot(luks, keyslot_id, wake_seed)
    handoff_wake_seed_to_verve(wake_seed, verve, keyslot_id)
    zeroize_wake_seed(wake_seed)

    return luks, verve, wake_seed


def verve_wake_seed_summary() -> Dict[str, object]:
    luks, verve, wake_seed = clean_shutdown_prepare_verve_wake_path(
        entropy="demo-entropy",
    )

    code_0 = derive_rotating_code(verve.wake_seed or "", 0)
    code_10 = derive_rotating_code(verve.wake_seed or "", 10)

    decision, _attempt = verve_attempt_luks_unlock(luks, verve)

    return {
        "wake_seed_zeroized_in_whisper": wake_seed.state == "ZEROIZED",
        "wake_seed_length": WAKE_SEED_LENGTH,
        "code_rotates": code_0.code != code_10.code,
        "unlock_decision": decision,
        "verve_zeroized_after_unlock": verve.zeroized_after_unlock,
        "human_fallback": human_passphrase_is_fallback(luks),
        "pre_luks_contains_core_secrets": pre_luks_stage_contains_core_secrets(),
    }


if __name__ == "__main__":
    summary = verve_wake_seed_summary()

    print("Wake seed zeroized in WHISPER:", summary["wake_seed_zeroized_in_whisper"])
    print("Wake seed length:", summary["wake_seed_length"])
    print("Code rotates:", summary["code_rotates"])
    print("Unlock decision:", summary["unlock_decision"])
    print("Verve zeroized after unlock:", summary["verve_zeroized_after_unlock"])
    print("Human fallback:", summary["human_fallback"])
    print("Pre-LUKS contains Core secrets:", summary["pre_luks_contains_core_secrets"])
