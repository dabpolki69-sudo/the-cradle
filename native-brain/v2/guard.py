"""Independent fail-closed execution guard for Sylvex experiments.

This is a control boundary, not a semantic safety classifier. It can stop
known-invalid or unauthorised operations; it cannot prove arbitrary content safe.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class StopEvent:
    code: str
    reason: str
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HardStop:
    """Latched stop state. Only an explicit authorised reset can clear it."""

    PROTECTED_ACTIONS = frozenset({
        "deploy", "publish", "delete", "write_external", "send_external",
        "spend_money", "change_permissions", "merge_protected",
    })

    def __init__(self):
        self.event = None

    @property
    def stopped(self):
        return self.event is not None

    def trip(self, code, reason):
        if self.event is None:
            self.event = StopEvent(str(code), str(reason)[:500])
        return self.event

    def check_action(self, action, *, approved=False):
        """Reject consequential actions unless a human approval is explicit."""
        if self.stopped:
            return False
        action = str(action).strip().lower()
        if action in self.PROTECTED_ACTIONS and not approved:
            self.trip("APPROVAL_REQUIRED", f"Action '{action}' requires explicit human approval")
            return False
        return True

    def reset(self, *, authorised=False):
        """A stop cannot be cleared by ordinary workflow logic."""
        if not authorised:
            raise PermissionError("Hard stop reset requires explicit authorised approval")
        self.event = None
        return True

    def as_dict(self):
        if self.event is None:
            return {"stopped": False, "event": None}
        return {
            "stopped": True,
            "event": {
                "code": self.event.code,
                "reason": self.event.reason,
                "at": self.event.at,
            },
        }
