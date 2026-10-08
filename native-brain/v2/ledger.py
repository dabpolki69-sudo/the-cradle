from dataclasses import dataclass,field
from datetime import datetime,timezone

@dataclass
class LedgerEntry:
    kind:str
    text:str
    data:dict=field(default_factory=dict)
    at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())

class DissentLedger:
    def __init__(self): self.entries=[]
    def record(self,dissent):
        self.entries.append(LedgerEntry("dissent",dissent.reason,{"status":dissent.status,
            "positions":[{"organ":p.organ,"position":p.position,"confidence":p.confidence} for p in dissent.positions]}))
    def unresolved(self): return [e for e in self.entries if e.data.get("status")=="unresolved"]
