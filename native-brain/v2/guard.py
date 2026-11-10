"""Independent fail-closed execution guard for Sylvex experiments."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading


@dataclass(frozen=True)
class StopEvent:
    code: str
    reason: str
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HardStop:
    """Latched stop; optional StateStore makes the latch durable across restarts."""
    PROTECTED_ACTIONS = frozenset({
        "deploy", "publish", "delete", "write_external", "send_external",
        "spend_money", "change_permissions", "merge_protected",
    })

    def __init__(self, state_store=None):
        self.state_store = state_store
        self._event = None
        self._lock = threading.RLock()

    @property
    def event(self):
        with self._lock:
            if self.state_store is not None:
                stored = self.state_store.get_stop()
                if stored:
                    return StopEvent(stored["code"], stored["reason"], stored["at"])
                return None
            return self._event

    @property
    def stopped(self):
        try:
            return self.event is not None
        except Exception:
            # A persistence failure must never be interpreted as permission.
            return True

    def trip(self, code, reason):
        with self._lock:
            event = self.event
            if event is not None:
                return event
            candidate = StopEvent(str(code), str(reason)[:500])
            if self.state_store is not None:
                stored = self.state_store.trip_stop({
                    "code": candidate.code, "reason": candidate.reason, "at": candidate.at
                })
                return StopEvent(stored["code"], stored["reason"], stored["at"])
            self._event = candidate
            return candidate

    def check_action(self, action, *, approved=False):
        if self.stopped:
            return False
        action = str(action).strip().lower()
        if action in self.PROTECTED_ACTIONS and not approved:
            self.trip("APPROVAL_REQUIRED", f"Action '{action}' requires explicit human approval")
            return False
        return True

    def reset(self, *, authorised=False):
        """Internal reset primitive; HTTP/API callers must authenticate separately."""
        if not authorised:
            raise PermissionError("Hard stop reset requires explicit authorised approval")
        with self._lock:
            if self.state_store is not None:
                self.state_store.reset_stop()
            else:
                self._event = None
        return True

    def as_dict(self):
        event = self.event
        if event is None:
            return {"stopped": False, "event": None}
        return {"stopped": True, "event": {
            "code": event.code, "reason": event.reason, "at": event.at
        }}
