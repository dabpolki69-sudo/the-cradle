from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LedgerEntry:
    kind: str
    text: str
    data: dict = field(default_factory=dict)
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: int | None = None


class DissentLedger:
    """Append-only ledger; optional StateStore persists entries across restarts."""
    def __init__(self, state_store=None):
        self.state_store = state_store
        self.entries = []
        if state_store is not None:
            self.entries = [
                LedgerEntry(item["kind"], item["text"], item["data"], item["at"], item["id"])
                for item in state_store.entries()
            ]

    def _append(self, kind, text, data):
        entry = LedgerEntry(kind, str(text)[:1000], data)
        if self.state_store is not None:
            entry.id = self.state_store.append_entry(kind, entry.text, data, entry.at)
        else:
            entry.id = len(self.entries) + 1
        self.entries.append(entry)
        return entry

    def record(self, dissent):
        return self._append("dissent", dissent.reason, {
            "status": dissent.status,
            "positions": [
                {"organ": p.organ, "position": p.position, "confidence": p.confidence}
                for p in dissent.positions
            ],
        })

    def record_murmur(self, message, *, line=None, source="sylvex_script"):
        return self._append("murmur", message, {
            "status": "unresolved", "advisory": True,
            "source": source, "line": line,
        })

    def refresh(self):
        if self.state_store is not None:
            self.entries = [
                LedgerEntry(item["kind"], item["text"], item["data"], item["at"], item["id"])
                for item in self.state_store.entries()
            ]
        return self.entries

    def unresolved(self):
        return [entry for entry in self.refresh() if entry.data.get("status") == "unresolved"]

    def as_dict(self, entry):
        return {"id": entry.id, "kind": entry.kind, "text": entry.text,
                "data": dict(entry.data), "at": entry.at}
