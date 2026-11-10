from .guard import HardStop
from .script import ScriptEngine, ScriptSyntaxError, parse_script


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
