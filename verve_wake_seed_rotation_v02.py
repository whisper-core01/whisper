"""
WHISPER v1.8.0 — Verve Wake Seed Rotation v0.2

Purpose:
Model wake_seed rotation with temporal depth.

v01 doctrine remains valid:
WHISPER does not know the future code.
It entrusts Verve with the seed that will rotate the code.
The seed sleeps inside Verve.
The code turns on its surface.
LUKS recognizes the seed.
WHISPER is reborn after opening.

v02 refines the model:
- wake_seed_root is long-lived and revocable/rotatable
- wake_seed_session is derived from root
- every clean shutdown rotates the session seed
- Verve LUKS keyslot is updated on rotation
- old session seed cannot unlock after rotation
- human passphrase remains valid fallback
- no network is required for any rotation step
- rotation log is local-only and minimal

Doctrine:
Before LUKS, there is no WHISPER Core.
There is only the threshold.

The pre-LUKS stage may open the door.
It must never contain the house.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Set


WakeSeedLabel = Literal[
    "wake_seed_root",
    "wake_seed_session",
    "wake_seed_rotates_on_clean_shutdown",
    "wake_seed_not_reused_after_boot",
    "wake_seed_split_optional",
    "verve_rotation_log_local_only",
]

UnlockDecision = Literal[
    "unlock_allowed",
    "unlock_rejected",
]

RotationStatus = Literal[
    "rotation_ok",
    "rotation_nok",
    "not_rotated",
]

ShutdownKind = Literal[
    "clean_shutdown",
    "dirty_shutdown",
]

SeedState = Literal[
    "active",
    "invalidated",
    "zeroized",
]


WAKE_SEED_LABELS: Set[str] = {
    "wake_seed_root",
    "wake_seed_session",
    "wake_seed_rotates_on_clean_shutdown",
    "wake_seed_not_reused_after_boot",
    "wake_seed_split_optional",
    "verve_rotation_log_local_only",
}


@dataclass
class WakeSeedRoot:
    """
    Root seed material.

    In this model, root material exists only inside Verve.
    It is never returned by public summary functions.
    """

    _material: bytes
    generation: int = 1
    exposed: bool = False
    zeroized: bool = False

    def derive_session_material(self, boot_counter: int, rotation_nonce: bytes) -> bytes:
        if self.zeroized:
            raise ValueError("wake_seed_root is zeroized")

        context = (
            b"WHISPER::VERVE::WAKE_SEED_SESSION::v0.2::"
            + str(self.generation).encode("utf-8")
            + b"::"
            + str(boot_counter).encode("utf-8")
            + b"::"
            + rotation_nonce
        )

        return hmac.new(
            self._material,
            context,
            hashlib.sha256,
        ).digest()

    def rotate_root(self, new_material: bytes) -> None:
        self._material = new_material
        self.generation += 1
        self.exposed = False
        self.zeroized = False

    def zeroize(self) -> None:
        self._material = b""
        self.zeroized = True


@dataclass
class WakeSeedSession:
    material: bytes
    boot_counter: int
    root_generation: int
    state: SeedState = "active"
    used_for_unlock: bool = False

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            b"WHISPER::VERVE::SESSION_FINGERPRINT::" + self.material
        ).hexdigest()

    def invalidate(self) -> None:
        self.material = b""
        self.state = "invalidated"

    def zeroize(self) -> None:
        self.material = b""
        self.state = "zeroized"


@dataclass
class LocalShard:
    """
    Optional local shard.

    This models local-only split support.
    It does not require network access.
    """

    enabled: bool = False
    encrypted_local_file_present: bool = False
    human_passphrase_required: bool = False
    network_required: bool = False

    def is_local_only(self) -> bool:
        return not self.network_required

    def is_available(self) -> bool:
        if not self.enabled:
            return True

        return self.is_local_only() and (
            self.encrypted_local_file_present or self.human_passphrase_required
        )


@dataclass
class RotationLog:
    """
    Minimal sovereign log.

    No telemetry.
    No network.
    Only last local rotation state.
    """

    last_rotation_status: RotationStatus = "not_rotated"
    last_boot_counter: int = 0
    local_only: bool = True
    telemetry_enabled: bool = False
    network_log_enabled: bool = False

    def mark_ok(self, boot_counter: int) -> None:
        self.last_rotation_status = "rotation_ok"
        self.last_boot_counter = boot_counter

    def mark_nok(self, boot_counter: int) -> None:
        self.last_rotation_status = "rotation_nok"
        self.last_boot_counter = boot_counter

    def is_sovereign_local_only(self) -> bool:
        return (
            self.local_only
            and not self.telemetry_enabled
            and not self.network_log_enabled
        )


@dataclass
class VerveLuksKeyslot:
    """
    Mock LUKS keyslot.

    The Verve slot accepts only the current session fingerprint.
    The human passphrase remains valid fallback.
    """

    accepted_session_fingerprint: str
    human_passphrase_hash: str
    updated_on_rotation: bool = False

    def update_for_session(self, session: WakeSeedSession) -> None:
        self.accepted_session_fingerprint = session.fingerprint
        self.updated_on_rotation = True

    def accepts_session(self, session: WakeSeedSession) -> bool:
        return (
            session.state == "active"
            and session.fingerprint == self.accepted_session_fingerprint
        )

    def accepts_human_passphrase(self, passphrase: str) -> bool:
        return hash_human_passphrase(passphrase) == self.human_passphrase_hash


@dataclass
class VerveWakeSeedRotation:
    root: WakeSeedRoot
    current_session: WakeSeedSession
    keyslot: VerveLuksKeyslot
    rotation_log: RotationLog = field(default_factory=RotationLog)
    shard: LocalShard = field(default_factory=LocalShard)
    boot_counter: int = 1
    network_required: bool = False
    old_session_fingerprints: Set[str] = field(default_factory=set)

    def no_network_required(self) -> bool:
        return (
            not self.network_required
            and self.shard.is_local_only()
            and self.rotation_log.is_sovereign_local_only()
        )

    def rotate_on_shutdown(
        self,
        shutdown_kind: ShutdownKind,
        rotation_nonce: bytes,
    ) -> RotationStatus:
        if shutdown_kind != "clean_shutdown":
            self.rotation_log.mark_nok(self.boot_counter)
            return "rotation_nok"

        if not self.no_network_required():
            self.rotation_log.mark_nok(self.boot_counter)
            return "rotation_nok"

        if not self.shard.is_available():
            self.rotation_log.mark_nok(self.boot_counter)
            return "rotation_nok"

        old_session = self.current_session
        old_fingerprint = old_session.fingerprint
        self.old_session_fingerprints.add(old_fingerprint)

        self.boot_counter += 1

        new_material = self.root.derive_session_material(
            boot_counter=self.boot_counter,
            rotation_nonce=rotation_nonce,
        )

        new_session = WakeSeedSession(
            material=new_material,
            boot_counter=self.boot_counter,
            root_generation=self.root.generation,
        )

        self.current_session = new_session
        self.keyslot.update_for_session(new_session)

        old_session.invalidate()

        self.rotation_log.mark_ok(self.boot_counter)

        return "rotation_ok"

    def unlock_with_session(self, session: WakeSeedSession) -> UnlockDecision:
        if self.keyslot.accepts_session(session):
            session.used_for_unlock = True
            session.zeroize()
            return "unlock_allowed"

        session.zeroize()
        return "unlock_rejected"

    def unlock_with_human_passphrase(self, passphrase: str) -> UnlockDecision:
        if self.keyslot.accepts_human_passphrase(passphrase):
            return "unlock_allowed"

        return "unlock_rejected"

    def zeroize_all_seeds_after_unlock(self) -> None:
        self.current_session.zeroize()
        self.root.zeroize()


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "verve_wake_seed_rotation_v02::"
        f"{test_name}"
    )


def hash_human_passphrase(passphrase: str) -> str:
    return hashlib.sha256(
        b"WHISPER::VERVE::HUMAN_FALLBACK::v0.2::"
        + passphrase.encode("utf-8")
    ).hexdigest()


def create_wake_seed_root(material: bytes) -> WakeSeedRoot:
    return WakeSeedRoot(_material=material)


def derive_wake_seed_session(
    root: WakeSeedRoot,
    boot_counter: int,
    rotation_nonce: bytes,
) -> WakeSeedSession:
    material = root.derive_session_material(
        boot_counter=boot_counter,
        rotation_nonce=rotation_nonce,
    )

    return WakeSeedSession(
        material=material,
        boot_counter=boot_counter,
        root_generation=root.generation,
    )


def create_rotation_model(
    root_material: bytes = b"verve-root-seed-v02",
    rotation_nonce: bytes = b"initial-session-nonce",
    human_passphrase: str = "human-valid-fallback",
    shard: Optional[LocalShard] = None,
) -> VerveWakeSeedRotation:
    root = create_wake_seed_root(root_material)

    session = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=rotation_nonce,
    )

    keyslot = VerveLuksKeyslot(
        accepted_session_fingerprint=session.fingerprint,
        human_passphrase_hash=hash_human_passphrase(human_passphrase),
    )

    return VerveWakeSeedRotation(
        root=root,
        current_session=session,
        keyslot=keyslot,
        shard=shard or LocalShard(),
    )


def wake_seed_root_is_never_exposed(model: VerveWakeSeedRotation) -> bool:
    return model.root.exposed is False


def wake_seed_session_is_derived_from_root(
    root: WakeSeedRoot,
    session: WakeSeedSession,
    rotation_nonce: bytes,
) -> bool:
    expected = root.derive_session_material(
        boot_counter=session.boot_counter,
        rotation_nonce=rotation_nonce,
    )

    return hmac.compare_digest(expected, session.material)


def clean_shutdown_rotates_session_seed(
    model: VerveWakeSeedRotation,
    rotation_nonce: bytes,
) -> bool:
    old_fingerprint = model.current_session.fingerprint

    status = model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=rotation_nonce,
    )

    return (
        status == "rotation_ok"
        and model.current_session.fingerprint != old_fingerprint
    )


def verve_luks_keyslot_updates_on_rotation(model: VerveWakeSeedRotation) -> bool:
    return (
        model.keyslot.updated_on_rotation
        and model.keyslot.accepted_session_fingerprint
        == model.current_session.fingerprint
    )


def old_session_seed_cannot_unlock_luks_after_rotation(
    model: VerveWakeSeedRotation,
    old_session: WakeSeedSession,
) -> bool:
    return model.keyslot.accepts_session(old_session) is False


def verve_zeroizes_all_seeds_after_unlock(model: VerveWakeSeedRotation) -> bool:
    model.zeroize_all_seeds_after_unlock()

    return (
        model.root.zeroized is True
        and model.current_session.state == "zeroized"
    )


def human_passphrase_remains_valid_fallback(
    model: VerveWakeSeedRotation,
    passphrase: str,
) -> bool:
    return model.unlock_with_human_passphrase(passphrase) == "unlock_allowed"


def no_network_required_for_any_rotation_step(model: VerveWakeSeedRotation) -> bool:
    return model.no_network_required()


def wake_seed_rotation_summary() -> Dict[str, object]:
    model = create_rotation_model()

    initial_session_fingerprint = model.current_session.fingerprint
    old_session = model.current_session

    rotation_status = model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=b"next-session-nonce",
    )

    old_session_unlock_allowed = model.keyslot.accepts_session(old_session)

    human_fallback_decision = model.unlock_with_human_passphrase(
        "human-valid-fallback"
    )

    session_seed_changed = model.current_session.fingerprint != initial_session_fingerprint

    model.zeroize_all_seeds_after_unlock()

    return {
        "labels": sorted(WAKE_SEED_LABELS),
        "wake_seed_root_is_never_exposed": wake_seed_root_is_never_exposed(model),
        "rotation_status": rotation_status,
        "session_seed_changed": session_seed_changed,
        "verve_luks_keyslot_updates_on_rotation": (
            model.keyslot.updated_on_rotation
        ),
        "old_session_seed_can_unlock_after_rotation": old_session_unlock_allowed,
        "human_passphrase_fallback": human_fallback_decision,
        "rotation_log_local_only": model.rotation_log.is_sovereign_local_only(),
        "no_network_required": model.no_network_required(),
        "root_zeroized_after_unlock": model.root.zeroized,
        "session_zeroized_after_unlock": model.current_session.state == "zeroized",
    }


if __name__ == "__main__":
    summary = wake_seed_rotation_summary()

    print("Wake seed labels:", summary["labels"])
    print("Root never exposed:", summary["wake_seed_root_is_never_exposed"])
    print("Rotation status:", summary["rotation_status"])
    print("Session seed changed:", summary["session_seed_changed"])
    print(
        "Verve LUKS keyslot updated:",
        summary["verve_luks_keyslot_updates_on_rotation"],
    )
    print(
        "Old session seed can unlock after rotation:",
        summary["old_session_seed_can_unlock_after_rotation"],
    )
    print("Human passphrase fallback:", summary["human_passphrase_fallback"])
    print("Rotation log local only:", summary["rotation_log_local_only"])
    print("No network required:", summary["no_network_required"])
    print("Root zeroized after unlock:", summary["root_zeroized_after_unlock"])
    print("Session zeroized after unlock:", summary["session_zeroized_after_unlock"])
