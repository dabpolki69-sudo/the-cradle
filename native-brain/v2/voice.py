from dataclasses import dataclass

from .chorus import Chorus, Signal, Position
from .economy import Budget
from .ledger import DissentLedger


@dataclass
class VoiceResult:
    speech: str
    routing: dict
    positions: list
    dissent: list
    currencies: dict
    budget: dict
    budget_exhausted: bool = False


class Voice:
    def __init__(self, chorus=None, budget=None):
        self.chorus = chorus or Chorus()
        self.budget = budget or Budget()
        self.ledger = DissentLedger()

    def receive(
        self,
        text,
        positions=None,
        modality="text",
        salience=0.5,
        stakes=0.5,
        surprise=0.5,
    ):
        # Reserve the complete deterministic tissue allowance before processing.
        # A failed reservation must not run the Chorus or partially mutate state.
        if not self.budget.spend(calls=1, reflex=78):
            return {
                "speech": "I can't process this request because the configured budget is exhausted.",
                "routing": {},
                "positions": [],
                "dissent": [],
                "currencies": {},
                "budget": self.budget.remaining,
                "budget_exhausted": True,
            }

        signal = Signal(text, modality, salience, stakes, surprise)
        if positions is None:
            positions = [
                Position(organ, "no position", 0.0)
                for organ in self.chorus.reliability
            ]

        result = self.chorus.process(signal, positions)
        for dissent in result["dissent"]:
            self.ledger.record(dissent)
        result["budget"] = self.budget.remaining
        result["budget_exhausted"] = False
        return result
