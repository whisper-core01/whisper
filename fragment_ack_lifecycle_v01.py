from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class FragmentAckState(str, Enum):
    CREATED = "created"
    SENT = "sent"
    ACK_PENDING = "ack_pending"
    ACKED = "acked"
    RETRY_SCHEDULED = "retry_scheduled"
    FAILED = "failed"
    EXPIRED = "expired"


class BearerSignalState(str, Enum):
    PRESENT = "present"
    LOST = "lost"
    ABSENT = "absent"


@dataclass(frozen=True)
class AckEvent:
    timestamp_ms: int
    fragment_id: str
    event: str
    detail: str = ""


@dataclass
class FragmentAckRecord:
    fragment_id: str
    created_at_ms: int
    state: FragmentAckState = FragmentAckState.CREATED
    sent_at_ms: Optional[int] = None
    acked_at_ms: Optional[int] = None
    last_attempt_at_ms: Optional[int] = None
    attempts: int = 0
    max_attempts: int = 3
    ack_timeout_ms: int = 5_000
    retry_backoff_ms: int = 1_000
    bearer: str = "unknown"
    signal_state: BearerSignalState = BearerSignalState.PRESENT
    phone_required: bool = False
    history: List[AckEvent] = field(default_factory=list)

    def log(self, timestamp_ms: int, event: str, detail: str = "") -> None:
        self.history.append(
            AckEvent(
                timestamp_ms=timestamp_ms,
                fragment_id=self.fragment_id,
                event=event,
                detail=detail,
            )
        )

    @property
    def is_terminal(self) -> bool:
        return self.state in {
            FragmentAckState.ACKED,
            FragmentAckState.FAILED,
            FragmentAckState.EXPIRED,
        }

    @property
    def delivery_allowed(self) -> bool:
        """
        No-phone doctrine:
        - phone absence must not block sovereign local delivery attempts.
        - if phone_required=False, delivery remains allowed without phone.
        """
        if self.phone_required and self.signal_state == BearerSignalState.ABSENT:
            return False
        return not self.is_terminal

    @property
    def ack_pending(self) -> bool:
        return self.state == FragmentAckState.ACK_PENDING

    def mark_sent(self, timestamp_ms: int, bearer: str = "unknown") -> None:
        if self.is_terminal:
            self.log(timestamp_ms, "send_ignored", f"terminal_state={self.state.value}")
            return

        if not self.delivery_allowed:
            self.log(timestamp_ms, "send_blocked", "delivery_not_allowed")
            return

        self.bearer = bearer
        self.sent_at_ms = timestamp_ms
        self.last_attempt_at_ms = timestamp_ms
        self.attempts += 1
        self.state = FragmentAckState.ACK_PENDING
        self.log(timestamp_ms, "sent", f"bearer={bearer};attempt={self.attempts}")

    def mark_ack(self, timestamp_ms: int) -> None:
        if self.state not in {
            FragmentAckState.SENT,
            FragmentAckState.ACK_PENDING,
            FragmentAckState.RETRY_SCHEDULED,
        }:
            self.log(timestamp_ms, "ack_ignored", f"state={self.state.value}")
            return

        self.acked_at_ms = timestamp_ms
        self.state = FragmentAckState.ACKED
        self.log(timestamp_ms, "acked")

    def mark_signal_lost(self, timestamp_ms: int) -> None:
        self.signal_state = BearerSignalState.LOST
        self.log(timestamp_ms, "signal_lost", f"bearer={self.bearer}")

    def mark_signal_absent(self, timestamp_ms: int) -> None:
        self.signal_state = BearerSignalState.ABSENT
        self.log(timestamp_ms, "signal_absent", f"bearer={self.bearer}")

    def mark_signal_present(self, timestamp_ms: int) -> None:
        self.signal_state = BearerSignalState.PRESENT
        self.log(timestamp_ms, "signal_present", f"bearer={self.bearer}")

    def should_retry(self, timestamp_ms: int) -> bool:
        if self.is_terminal:
            return False

        if self.state != FragmentAckState.ACK_PENDING:
            return False

        if self.last_attempt_at_ms is None:
            return False

        if self.attempts >= self.max_attempts:
            return False

        elapsed = timestamp_ms - self.last_attempt_at_ms
        return elapsed >= self.ack_timeout_ms

    def tick(self, timestamp_ms: int) -> FragmentAckState:
        """
        Advance lifecycle.

        ACK timeout:
        - if ACK not received and attempts remain, schedule retry.
        - if attempts exhausted, fail.
        """
        if self.is_terminal:
            return self.state

        if self.state == FragmentAckState.ACK_PENDING:
            if self.last_attempt_at_ms is None:
                return self.state

            elapsed = timestamp_ms - self.last_attempt_at_ms

            if elapsed >= self.ack_timeout_ms:
                if self.attempts >= self.max_attempts:
                    self.state = FragmentAckState.FAILED
                    self.log(timestamp_ms, "failed", "max_attempts_exhausted")
                else:
                    self.state = FragmentAckState.RETRY_SCHEDULED
                    self.log(timestamp_ms, "retry_scheduled", f"attempts={self.attempts}")

        return self.state

    def retry(self, timestamp_ms: int, bearer: Optional[str] = None) -> None:
        if self.is_terminal:
            self.log(timestamp_ms, "retry_ignored", f"terminal_state={self.state.value}")
            return

        if self.state != FragmentAckState.RETRY_SCHEDULED:
            self.log(timestamp_ms, "retry_ignored", f"state={self.state.value}")
            return

        if not self.delivery_allowed:
            self.log(timestamp_ms, "retry_blocked", "delivery_not_allowed")
            return

        retry_bearer = bearer if bearer is not None else self.bearer
        self.mark_sent(timestamp_ms, bearer=retry_bearer)

    def expire(self, timestamp_ms: int) -> None:
        if self.state == FragmentAckState.ACKED:
            self.log(timestamp_ms, "expire_ignored", "already_acked")
            return

        if self.is_terminal:
            self.log(timestamp_ms, "expire_ignored", f"terminal_state={self.state.value}")
            return

        self.state = FragmentAckState.EXPIRED
        self.log(timestamp_ms, "expired")


class FragmentAckLifecycle:
    def __init__(
        self,
        *,
        ack_timeout_ms: int = 5_000,
        retry_backoff_ms: int = 1_000,
        max_attempts: int = 3,
        phone_required: bool = False,
    ) -> None:
        if ack_timeout_ms <= 0:
            raise ValueError("ack_timeout_ms must be > 0")
        if retry_backoff_ms < 0:
            raise ValueError("retry_backoff_ms must be >= 0")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be > 0")

        self.ack_timeout_ms = ack_timeout_ms
        self.retry_backoff_ms = retry_backoff_ms
        self.max_attempts = max_attempts
        self.phone_required = phone_required
        self._records: Dict[str, FragmentAckRecord] = {}

    def create(self, fragment_id: str, timestamp_ms: int) -> FragmentAckRecord:
        if not fragment_id:
            raise ValueError("fragment_id must not be empty")
        if fragment_id in self._records:
            raise ValueError(f"fragment already exists: {fragment_id}")

        rec = FragmentAckRecord(
            fragment_id=fragment_id,
            created_at_ms=timestamp_ms,
            ack_timeout_ms=self.ack_timeout_ms,
            retry_backoff_ms=self.retry_backoff_ms,
            max_attempts=self.max_attempts,
            phone_required=self.phone_required,
        )
        rec.log(timestamp_ms, "created")
        self._records[fragment_id] = rec
        return rec

    def get(self, fragment_id: str) -> FragmentAckRecord:
        try:
            return self._records[fragment_id]
        except KeyError as exc:
            raise KeyError(f"unknown fragment_id: {fragment_id}") from exc

    def send(self, fragment_id: str, timestamp_ms: int, bearer: str = "unknown") -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.mark_sent(timestamp_ms, bearer=bearer)
        return rec

    def ack(self, fragment_id: str, timestamp_ms: int) -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.mark_ack(timestamp_ms)
        return rec

    def tick(self, timestamp_ms: int) -> None:
        for rec in self._records.values():
            rec.tick(timestamp_ms)

    def retry_due(self, timestamp_ms: int) -> List[FragmentAckRecord]:
        due: List[FragmentAckRecord] = []

        for rec in self._records.values():
            rec.tick(timestamp_ms)
            if rec.state == FragmentAckState.RETRY_SCHEDULED:
                last = rec.last_attempt_at_ms or rec.created_at_ms
                if timestamp_ms - last >= rec.ack_timeout_ms + rec.retry_backoff_ms:
                    due.append(rec)

        return due

    def retry(self, fragment_id: str, timestamp_ms: int, bearer: Optional[str] = None) -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.retry(timestamp_ms, bearer=bearer)
        return rec

    def mark_signal_lost(self, fragment_id: str, timestamp_ms: int) -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.mark_signal_lost(timestamp_ms)
        return rec

    def mark_signal_absent(self, fragment_id: str, timestamp_ms: int) -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.mark_signal_absent(timestamp_ms)
        return rec

    def mark_signal_present(self, fragment_id: str, timestamp_ms: int) -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.mark_signal_present(timestamp_ms)
        return rec

    def expire(self, fragment_id: str, timestamp_ms: int) -> FragmentAckRecord:
        rec = self.get(fragment_id)
        rec.expire(timestamp_ms)
        return rec

    def summary(self) -> Dict[str, int]:
        result = {state.value: 0 for state in FragmentAckState}
        for rec in self._records.values():
            result[rec.state.value] += 1
        return result
