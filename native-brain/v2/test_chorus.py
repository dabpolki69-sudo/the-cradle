from .chorus import ORGANS, TISSUE, LANGUAGE_TISSUE, Chorus, Signal, Position
from .economy import Budget
from .voice import Voice


def test_structure():
    assert len(ORGANS) == 9
    assert sum(map(len, TISSUE.values())) == 78
    assert len(LANGUAGE_TISSUE) == 2
    assert all(len(v) == 9 for k, v in TISSUE.items() if k != "auditor")
    assert len(TISSUE["auditor"]) == 6
    all_units = [unit for units in TISSUE.values() for unit in units]
    assert len(all_units) == len(set(all_units)) == 78


def test_route():
    routing = Chorus().route(Signal("x", salience=0.8, stakes=0.9, surprise=0.7))
    assert abs(sum(routing.values()) - 1) < 1e-9
    assert all(value > 0 for value in routing.values())


def test_weight():
    chorus = Chorus()
    position = Position("auditor", "check", 0.8, relevance=0.5)
    assert chorus.weight(position) == 0.5 * 0.8 * 0.5


def test_budget_limits_are_atomic():
    budget = Budget(tokens=10, calls=2, reflex_units=5)
    assert budget.spend(tokens=5, calls=1, reflex=3)
    before = budget.remaining.copy()
    assert not budget.spend(tokens=6, calls=1, reflex=1)
    assert budget.remaining == before
    assert not budget.spend(reflex=3)
    assert budget.remaining == before


def test_budget_rejects_negative_spend():
    budget = Budget()
    try:
        budget.spend(calls=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative budget spend should raise ValueError")


def test_budget_rejects_negative_limits():
    try:
        Budget(reflex_units=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative budget limit should raise ValueError")


def test_voice_refuses_when_reflex_budget_is_too_small():
    budget = Budget(calls=2, reflex_units=77)
    voice = Voice(budget=budget)
    result = voice.receive("hello")
    assert result["budget_exhausted"] is True
    assert result["positions"] == []
    assert budget.spent_calls == 0
    assert budget.spent_reflex == 0


def test_voice_processes_when_budget_is_available():
    budget = Budget()
    result = Voice(budget=budget).receive("hello")
    assert "speech" in result and "routing" in result
    assert result["budget_exhausted"] is False
    assert budget.spent_calls == 1
    assert budget.spent_reflex == 78
