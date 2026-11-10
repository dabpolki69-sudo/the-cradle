from .guard import HardStop
from .ledger import DissentLedger
from .script import ScriptEngine, ScriptSyntaxError, compile_script, parse_script
from .state_store import StateStore
from .benchmark import run_benchmark, _evaluate


def test_hard_stop_latches_until_authorised_reset():
    guard = HardStop()
    guard.trip("TEST", "stop now")
    assert guard.stopped
    assert not guard.check_action("observe")
    try:
        guard.reset()
    except PermissionError:
        pass
    else:
        raise AssertionError("unauthorised reset must fail")
    guard.reset(authorised=True)
    assert not guard.stopped


def test_hard_stop_requires_approval_for_external_side_effects():
    guard = HardStop()
    assert not guard.check_action("deploy")
    assert guard.event.code == "APPROVAL_REQUIRED"


def test_sylvex_script_runs_bounded_verified_sequence():
    source = """SYLVEX/1
OBSERVE hello world
SCORE 0.9
MURMUR evidence is incomplete
INTEGRATE
VERIFY
RESPOND Result: reviewed
"""
    result = ScriptEngine().run(source)
    assert result["status"] == "completed"
    assert result["output"] == "Result: reviewed"
    assert result["murmurs"][0]["advisory"] is True


def test_murmur_is_written_to_shared_dissent_ledger():
    ledger = DissentLedger()
    result = ScriptEngine(ledger=ledger).run(
        "SYLVEX/1\nOBSERVE input\nMURMUR missing citation\nINTEGRATE\nVERIFY\nRESPOND noted"
    )
    assert result["status"] == "completed"
    unresolved = ledger.unresolved()
    assert len(unresolved) == 1
    assert unresolved[0].kind == "murmur"
    assert unresolved[0].data["advisory"] is True
    assert unresolved[0].text == "missing citation"


def test_typed_claims_keep_evidence_inference_and_uncertainty_separate():
    source = """SYLVEX/1
OBSERVE source text
EVIDENCE The log contains error 42.
SOURCE build.log line 18
INFERENCE The error may be caused by a missing resource.
UNCERTAINTY The cause is not confirmed.
INTEGRATE
VERIFY
RESPOND Diagnosis remains provisional.
"""
    result = ScriptEngine().run(source)
    assert result["status"] == "completed"
    assert [item["type"] for item in result["claims"]] == [
        "evidence", "inference", "uncertainty"
    ]
    assert result["claims"][0]["source"] == "build.log line 18"
    assert result["claims"][1]["source"] is None


def test_source_without_claim_trips_hard_stop():
    result = ScriptEngine().run("SYLVEX/1\nSOURCE orphan")
    assert result["status"] == "stopped"
    assert result["hard_stop"]["event"]["code"] == "SOURCE_WITHOUT_CLAIM"


def test_sylvex_script_stops_unverified_response():
    result = ScriptEngine().run("SYLVEX/1\nRESPOND go")
    assert result["status"] == "stopped"
    assert result["hard_stop"]["event"]["code"] == "UNVERIFIED_RESPONSE"
    assert result["output"] == ""


def test_sylvex_script_rejects_unknown_operation_and_step_overflow():
    try:
        parse_script("SYLVEX/1\nRUN_SHELL rm -rf /")
    except ScriptSyntaxError:
        pass
    else:
        raise AssertionError("unknown operations must be rejected")
    try:
        parse_script("SYLVEX/1\n" + "\n".join(["MURMUR x"] * 33))
    except ScriptSyntaxError:
        pass
    else:
        raise AssertionError("step overflow must be rejected")



def test_compile_script_emits_stable_side_effect_free_ir():
    compiled = compile_script("SYLVEX/1\nOBSERVE hello\nMURMUR check source")
    assert compiled["language"] == "SYLVEX/1"
    assert compiled["ir_version"] == 1
    assert compiled["side_effects"] is False
    assert compiled["steps"] == [
        {"index": 0, "line": 2, "op": "OBSERVE", "arg": "hello"},
        {"index": 1, "line": 3, "op": "MURMUR", "arg": "check source"},
    ]



def test_hard_stop_persists_across_script_requests_until_authorised_reset():
    engine = ScriptEngine()
    first = engine.run("SYLVEX/1\nSTOP review required")
    second = engine.run(
        "SYLVEX/1\nOBSERVE safe input\nINTEGRATE\nVERIFY\nRESPOND should not run"
    )
    assert first["status"] == "stopped"
    assert second["status"] == "stopped"
    assert second["output"] == ""
    try:
        engine.guard.reset()
    except PermissionError:
        pass
    else:
        raise AssertionError("engine stop must not be clearable without authorisation")
    engine.guard.reset(authorised=True)
    third = engine.run(
        "SYLVEX/1\nOBSERVE safe input\nINTEGRATE\nVERIFY\nRESPOND released"
    )
    assert third["status"] == "completed"
    assert third["output"] == "released"



def test_hard_stop_survives_guard_recreation(tmp_path):
    path = tmp_path / "sylvex.sqlite3"
    first = HardStop(StateStore(path))
    first.trip("TEST_RESTART", "must remain stopped")
    second = HardStop(StateStore(path))
    assert second.stopped
    assert second.as_dict()["event"]["code"] == "TEST_RESTART"
    try:
        second.reset()
    except PermissionError:
        pass
    else:
        raise AssertionError("reset must require authorisation")
    second.reset(authorised=True)
    assert not HardStop(StateStore(path)).stopped


def test_ledger_survives_recreation_and_keeps_stable_ids(tmp_path):
    path = tmp_path / "sylvex.sqlite3"
    first = DissentLedger(StateStore(path))
    first.record_murmur("retain this concern", line=9)
    first_id = first.entries[-1].id
    second = DissentLedger(StateStore(path))
    assert len(second.unresolved()) == 1
    assert second.unresolved()[0].id == first_id
    second.record_murmur("second concern", line=10)
    third = DissentLedger(StateStore(path))
    assert [item.id for item in third.unresolved()] == [first_id, first_id + 1]


def test_state_store_preserves_first_stop_event(tmp_path):
    store = StateStore(tmp_path / "sylvex.sqlite3")
    guard = HardStop(store)
    guard.trip("FIRST", "first reason")
    guard.trip("SECOND", "must not replace first")
    assert guard.as_dict()["event"]["code"] == "FIRST"



def test_shared_ledger_refreshes_entries_written_by_another_instance(tmp_path):
    store = StateStore(tmp_path / "sylvex.sqlite3")
    first = DissentLedger(store)
    second = DissentLedger(StateStore(tmp_path / "sylvex.sqlite3"))
    first.record_murmur("cross-instance concern", line=12)
    assert [entry.text for entry in second.unresolved()] == ["cross-instance concern"]



def test_deterministic_benchmark_fixtures_all_pass():
    report = run_benchmark()
    assert report["total"] == 8
    assert report["passed"] == 8
    assert report["failed"] == 0
    assert report["scope"].startswith("script workflow")


def test_benchmark_detects_an_unsafe_output_after_stop():
    failures = _evaluate(
        {"status": "stopped", "output": "unsafe", "claims": [], "murmurs": [],
         "hard_stop": {"event": {"code": "SCRIPT_STOP"}}},
        {"status": "stopped", "claim_types": [], "murmurs": 0,
         "stop_code": "SCRIPT_STOP", "output_empty": True},
    )
    assert any("empty output" in failure for failure in failures)
