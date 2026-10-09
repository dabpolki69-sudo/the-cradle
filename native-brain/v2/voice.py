from collections import Counter, defaultdict
from dataclasses import dataclass

from .chorus import Chorus, Signal, Position, ORGANS
from .economy import Budget
from .ledger import DissentLedger
from .tissue import build_tissue


@dataclass
class VoiceResult:
    speech: str
    routing: dict
    positions: list
    dissent: list
    currencies: dict
    budget: dict
    budget_exhausted: bool = False
    tissue_results: list | None = None


class Voice:
    def __init__(self, chorus=None, budget=None, tissues=None):
        self.chorus = chorus or Chorus()
        self.budget = budget or Budget()
        self.ledger = DissentLedger()
        self.tissues = tissues if tissues is not None else build_tissue()

    def _run_tissues(self, text):
        """Run every deterministic tissue unit and aggregate its output per organ.

        These are explicit baseline stubs, not independent language models. The
        per-unit trace is returned so future learned/provider-backed tissues can
        be evaluated against this reproducible baseline.
        """
        grouped = defaultdict(list)
        trace = []
        for unit, tissue in self.tissues.items():
            result = tissue.predict(text)
            grouped[result.organ].append(result)
            trace.append({
                "unit": result.unit,
                "organ": result.organ,
                "value": result.value,
                "confidence": result.confidence,
                "cost": result.cost,
                "mode": "deterministic_placeholder",
            })

        positions = []
        for organ in ORGANS:
            results = grouped.get(organ, [])
            if not results:
                continue
            counts = Counter(item.value for item in results)
            # Counter preserves first-seen order, making ties deterministic.
            value = counts.most_common(1)[0][0]
            confidence = sum(item.confidence for item in results) / len(results)
            positions.append(Position(organ, value, confidence))
        return positions, trace

    def receive(
        self,
        text,
        positions=None,
        modality="text",
        salience=0.5,
        stakes=0.5,
        surprise=0.5,
    ):
        # Supplied positions bypass tissue execution; otherwise reserve the
        # complete 78-unit deterministic baseline before doing any work.
        reflex_cost = 78 if positions is None else 0
        if not self.budget.spend(calls=1, reflex=reflex_cost):
            return {
                "speech": "I can't process this request because the configured budget is exhausted.",
                "routing": {},
                "positions": [],
                "dissent": [],
                "currencies": {},
                "budget": self.budget.remaining,
                "budget_exhausted": True,
                "tissue_results": [],
            }

        tissue_trace = []
        if positions is None:
            positions, tissue_trace = self._run_tissues(text)

        signal = Signal(text, modality, salience, stakes, surprise)
        result = self.chorus.process(signal, positions)
        for dissent in result["dissent"]:
            self.ledger.record(dissent)
        result["budget"] = self.budget.remaining
        result["budget_exhausted"] = False
        result["tissue_results"] = tissue_trace
        return result
