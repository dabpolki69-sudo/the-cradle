import json
from .chorus import ORGANS, TISSUE, LANGUAGE_TISSUE, Chorus, Signal, Position
from .economy import Budget
from .voice import Voice
from .tissue import ModelTissue, build_tissue
from .provider import OpenAICompatibleProvider, ProviderConfig, ProviderError


def test_structure():
    assert len(ORGANS) == 9
    assert sum(map(len, TISSUE.values())) == 78
    assert len(LANGUAGE_TISSUE) == 2
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
        raise AssertionError("negative spend should raise ValueError")


def test_budget_rejects_negative_limits():
    try:
        Budget(reflex_units=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative limit should raise ValueError")


def test_voice_refuses_when_reflex_budget_is_too_small():
    budget = Budget(calls=2, reflex_units=77)
    result = Voice(budget=budget).receive("hello")
    assert result["budget_exhausted"] is True
    assert result["tissue_results"] == []
    assert budget.spent_calls == 0


def test_voice_processes_when_budget_is_available():
    budget = Budget()
    result = Voice(budget=budget).receive("hello")
    assert result["budget_exhausted"] is False
    assert budget.spent_calls == 1
    assert budget.spent_reflex == 78


def test_voice_runs_and_traces_all_tissue_units():
    result = Voice().receive("inspectable baseline input")
    assert len(result["tissue_results"]) == 78
    assert {item["unit"] for item in result["tissue_results"]} == {
        unit for units in TISSUE.values() for unit in units
    }
    assert {position.organ for position in result["positions"]} == set(ORGANS)
    assert all(item["mode"] == "deterministic_placeholder" for item in result["tissue_results"])


def test_supplied_positions_skip_tissue_execution():
    budget = Budget()
    supplied = [Position("weaver", "external observation", 0.9)]
    result = Voice(budget=budget).receive("input", positions=supplied)
    assert result["tissue_results"] == []
    assert budget.spent_calls == 1
    assert budget.spent_reflex == 0


def test_provider_config_is_opt_in(monkeypatch):
    monkeypatch.delenv("SYLVEX_MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("SYLVEX_MODEL_NAME", raising=False)
    assert ProviderConfig.from_env() is None


def test_provider_requires_model_name(monkeypatch):
    monkeypatch.setenv("SYLVEX_MODEL_BASE_URL", "https://example.invalid/v1")
    monkeypatch.delenv("SYLVEX_MODEL_NAME", raising=False)
    try:
        ProviderConfig.from_env()
    except ValueError:
        pass
    else:
        raise AssertionError("missing model name should be rejected")


def test_provider_parses_valid_assessment():
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, limit):
            return json.dumps({"choices":[{"message":{"content":json.dumps({
                "value":"evidence supports claim",
                "confidence":0.82
            })}}]}).encode()
    def opener(request, timeout):
        assert request.full_url == "https://example.invalid/v1/chat/completions"
        assert timeout == 20.0
        return Response()
    provider = OpenAICompatibleProvider(
        ProviderConfig("https://example.invalid/v1", "test-model"), opener=opener
    )
    assert provider.assess("input", "Verbalizer", "deliberator") == (
        "evidence supports claim", 0.82
    )


def test_provider_rejects_invalid_confidence():
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, limit):
            return json.dumps({"choices":[{"message":{"content":'{"value":"x","confidence":9}'}}]}).encode()
    provider = OpenAICompatibleProvider(
        ProviderConfig("https://example.invalid/v1", "test-model"),
        opener=lambda request, timeout: Response(),
    )
    try:
        provider.assess("input", "Verbalizer", "deliberator")
    except ProviderError:
        pass
    else:
        raise AssertionError("out-of-range confidence should fail")


def test_model_tissue_failure_is_explicit():
    class BrokenProvider:
        class Config:
            max_input_chars = 8000
        config = Config()
        def assess(self, *args):
            raise ProviderError("simulated outage")
    tissue = ModelTissue("Verbalizer", "deliberator", BrokenProvider())
    result = tissue.predict("hello")
    assert result.mode == "provider_error"
    assert result.confidence == 0
    assert "simulated outage" in result.error


def test_provider_backed_position_is_not_outvoted_by_placeholders():
    class Provider:
        class Config:
            max_input_chars = 8000
        config = Config()
        def assess(self, *args):
            return "model-supported observation", 0.82
    tissues = build_tissue(provider=Provider())
    result = Voice(tissues=tissues).receive("input")
    deliberator = next(p for p in result["positions"] if p.organ == "deliberator")
    assert deliberator.position == "model-supported observation"
    assert any(t["mode"] == "model_provider" for t in result["tissue_results"])
    assert result["budget"]["calls"] == 38
    assert result["budget"]["tokens"] == 79_490
