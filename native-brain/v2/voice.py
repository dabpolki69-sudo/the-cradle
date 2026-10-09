from collections import Counter, defaultdict
from dataclasses import dataclass

from .chorus import Chorus, Signal, Position, ORGANS
from .economy import Budget
from .ledger import DissentLedger
from .tissue import build_tissue, ModelTissue


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
        """Run every unit and aggregate its output per organ.

        A provider-backed output is selected as that organ's explicit position
        instead of being outvoted by placeholder stubs. Provider failures are
        also surfaced as that organ's position; they do not silently fall back
        to the deterministic majority.
        """
        grouped = defaultdict(list)
        trace = []
        for unit, tissue in self.tissues.items():
            result = tissue.predict(text)
            grouped[result.organ].append(result)
            item = {
                "unit": result.unit,
                "organ": result.organ,
                "value": result.value,
                "confidence": result.confidence,
                "cost": result.cost,
                "mode": result.mode,
            }
            if result.error:
                item["error"] = result.error
            trace.append(item)

        positions = []
        for organ in ORGANS:
            results = grouped.get(organ, [])
            if not results:
                continue
            external_results = [
                r for r in results if r.mode in ("model_provider", "provider_error")
            ]
            if external_results:
                selected = external_results[0]
                value, confidence = selected.value, selected.confidence
            else:
                counts = Counter(item.value for item in results)
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
        provider_units = [
            unit for unit in self.tissues.values() if isinstance(unit, ModelTissue)
        ] if positions is None else []
        if provider_units and len(text) > provider_units[0].provider.config.max_input_chars:
            return {
                "speech": "Input exceeds the configured model-tissue character limit.",
                "routing": {},
                "positions": [],
                "dissent": [],
                "currencies": {},
                "budget": self.budget.remaining,
                "budget_exhausted": True,
                "tissue_results": [],
            }
        reflex_cost = 78 if positions is None else 0
        provider_calls = len(provider_units)
        token_reserve = (len(text) * 2 + 512) if provider_calls else 0
        if not self.budget.spend(
            tokens=token_reserve,
            calls=1 + provider_calls,
            reflex=reflex_cost,
        ):
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
