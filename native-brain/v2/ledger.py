from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LedgerEntry:
    kind: str
    text: str
    data: dict = field(default_factory=dict)
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DissentLedger:
    """Append-only in-memory record of dissent and script-originated murmurs."""

    def __init__(self):
        self.entries = []

    def record(self, dissent):
        self.entries.append(LedgerEntry(
            "dissent",
            dissent.reason,
            {
                "status": dissent.status,
                "positions": [
                    {"organ": p.organ, "position": p.position, "confidence": p.confidence}
                    for p in dissent.positions
                ],
            },
        ))

    def record_murmur(self, message, *, line=None, source="sylvex_script"):
        """Preserve an advisory concern without promoting it to a verified fact."""
        self.entries.append(LedgerEntry(
            "murmur",
            str(message)[:1000],
            {
                "status": "unresolved",
                "advisory": True,
                "source": source,
                "line": line,
            },
        ))

    def unresolved(self):
        return [entry for entry in self.entries if entry.data.get("status") == "unresolved"]

    def as_dict(self, entry):
        return {
            "kind": entry.kind,
            "text": entry.text,
            "data": dict(entry.data),
            "at": entry.at,
        }
