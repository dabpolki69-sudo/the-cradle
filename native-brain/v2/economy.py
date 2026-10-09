from dataclasses import dataclass


@dataclass
class Budget:
    tokens: int = 80_000
    calls: int = 40
    reflex_units: int = 78
    spent_tokens: int = 0
    spent_calls: int = 0
    spent_reflex: int = 0

    def __post_init__(self):
        for name in ("tokens", "calls", "reflex_units", "spent_tokens", "spent_calls", "spent_reflex"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.spent_tokens > self.tokens:
            raise ValueError("spent_tokens cannot exceed tokens")
        if self.spent_calls > self.calls:
            raise ValueError("spent_calls cannot exceed calls")
        if self.spent_reflex > self.reflex_units:
            raise ValueError("spent_reflex cannot exceed reflex_units")

    def spend(self, tokens=0, calls=0, reflex=0):
        """Atomically reserve budget; leave counters unchanged if it cannot fit."""
        for name, value in (("tokens", tokens), ("calls", calls), ("reflex", reflex)):
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        if (
            self.spent_tokens + tokens > self.tokens
            or self.spent_calls + calls > self.calls
            or self.spent_reflex + reflex > self.reflex_units
        ):
            return False

        self.spent_tokens += tokens
        self.spent_calls += calls
        self.spent_reflex += reflex
        return True

    @property
    def remaining(self):
        return {
            "tokens": self.tokens - self.spent_tokens,
            "calls": self.calls - self.spent_calls,
            "reflex_units": self.reflex_units - self.spent_reflex,
        }


@dataclass
class Currencies:
    surprise: float = 0.0
    energy: float = 0.0
    stakes: float = 0.0

    def as_dict(self):
        return {
            "surprise": self.surprise,
            "energy": self.energy,
            "stakes": self.stakes,
        }
