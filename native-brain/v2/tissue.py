from dataclasses import dataclass

from .chorus import TISSUE, LANGUAGE_TISSUE
from .provider import OpenAICompatibleProvider, ProviderConfig, ProviderError


@dataclass
class TissueResult:
    unit: str
    organ: str
    value: str
    confidence: float = 0.5
    cost: int = 1
    mode: str = "deterministic_placeholder"
    error: str = ""


class ReflexTissue:
    def __init__(self, unit, organ):
        self.unit, self.organ = unit, organ

    def predict(self, text):
        # Cheap deterministic baseline. Replace only through an explicit adapter.
        confidence = 0.35 if self.unit in LANGUAGE_TISSUE else 0.45
        return TissueResult(self.unit, self.organ, "signal", confidence, 1)


class ModelTissue:
    def __init__(self, unit, organ, provider):
        self.unit, self.organ, self.provider = unit, organ, provider

    def predict(self, text):
        try:
            value, confidence = self.provider.assess(text, self.unit, self.organ)
            return TissueResult(
                self.unit, self.organ, value, confidence, 1, "model_provider"
            )
        except ProviderError as exc:
            # Fail visibly and preserve the unit's place in the trace. Never
            # silently substitute a fabricated successful model result.
            return TissueResult(
                self.unit, self.organ, "provider_error", 0.0, 1,
                "provider_error", str(exc)
            )


def build_tissue(provider=None):
    """Build 78 units; optionally replace Verbalizer with one model-backed unit."""
    units = {
        unit: ReflexTissue(unit, organ)
        for organ, names in TISSUE.items()
        for unit in names
    }
    config = ProviderConfig.from_env() if provider is None else None
    if provider is None and config is not None:
        provider = OpenAICompatibleProvider(config)
    if provider is not None:
        units["Verbalizer"] = ModelTissue("Verbalizer", "deliberator", provider)
    return units
