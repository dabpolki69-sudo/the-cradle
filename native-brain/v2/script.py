"""Bounded, declarative Sylvex workflow interpreter (SYLVEX/1).

No eval, imports, shell, network, file writes, dynamic dispatch, loops, or
arbitrary tool execution. VERIFY checks workflow preconditions only; it does
not certify that claims are factually true.
"""
from dataclasses import dataclass, field

from .guard import HardStop


OPERATIONS = frozenset({
    "OBSERVE", "EVIDENCE", "INFERENCE", "UNCERTAINTY", "SOURCE",
    "SCORE", "MURMUR", "INTEGRATE", "VERIFY", "RESPOND", "STOP",
})


@dataclass
class ScriptStep:
    operation: str
    argument: str = ""
    line: int = 0


@dataclass
class ScriptResult:
    status: str
    output: str
    trace: list = field(default_factory=list)
    murmurs: list = field(default_factory=list)
    claims: list = field(default_factory=list)
    hard_stop: dict = field(default_factory=dict)
    verification_scope: str = "workflow_preconditions_only"


class ScriptSyntaxError(ValueError):
    pass


def parse_script(source, *, max_steps=32, max_chars=8000):
    if not isinstance(source, str) or len(source) > max_chars:
        raise ScriptSyntaxError("Script must be text within the configured size limit")
    lines = [line.strip() for line in source.splitlines()]
    if not lines or lines[0] != "SYLVEX/1":
        raise ScriptSyntaxError("First line must be SYLVEX/1")
    steps = []
    for number, line in enumerate(lines[1:], start=2):
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        operation = parts[0].upper()
        argument = parts[1].strip() if len(parts) == 2 else ""
        if operation not in OPERATIONS:
            raise ScriptSyntaxError(f"Unknown operation on line {number}: {operation}")
        if len(argument) > 1000:
            raise ScriptSyntaxError(f"Argument too long on line {number}")
        steps.append(ScriptStep(operation, argument, number))
        if len(steps) > max_steps:
            raise ScriptSyntaxError(f"Script exceeds {max_steps} steps")
    if not steps:
        raise ScriptSyntaxError("Script contains no operations")
    return steps


class ScriptEngine:
    """Execute a bounded workflow; all side effects are deliberately disabled."""

    def __init__(self, *, max_steps=32, ledger=None):
        self.max_steps = max_steps
        self.ledger = ledger

    def run(self, source, *, input_text=""):
        guard = HardStop()
        state = {
            "observed": "",
            "score": None,
            "integrated": "",
            "workflow_verified": False,
            "last_claim": None,
        }
        trace, murmurs, claims, output = [], [], [], ""
        try:
            steps = parse_script(source, max_steps=self.max_steps)
        except ScriptSyntaxError as exc:
            guard.trip("SCRIPT_INVALID", str(exc))
            return ScriptResult("stopped", "", [], [], [], guard.as_dict()).__dict__

        for step in steps:
            if guard.stopped:
                break
            record = {"line": step.line, "operation": step.operation, "status": "ok"}
            arg = step.argument
            if step.operation == "OBSERVE":
                state["observed"] = arg or input_text
                if not state["observed"]:
                    guard.trip("OBSERVATION_MISSING", "OBSERVE requires an argument or input_text")
            elif step.operation in {"EVIDENCE", "INFERENCE", "UNCERTAINTY"}:
                if not arg:
                    guard.trip("CLAIM_EMPTY", f"{step.operation} requires a non-empty statement")
                else:
                    claim = {"type": step.operation.lower(), "text": arg, "source": None, "line": step.line}
                    claims.append(claim)
                    state["last_claim"] = claim
            elif step.operation == "SOURCE":
                if not arg or state["last_claim"] is None:
                    guard.trip("SOURCE_WITHOUT_CLAIM", "SOURCE requires a preceding EVIDENCE, INFERENCE or UNCERTAINTY")
                else:
                    state["last_claim"]["source"] = arg
            elif step.operation == "SCORE":
                try:
                    score = float(arg)
                    if not 0 <= score <= 1:
                        raise ValueError
                    state["score"] = score
                except ValueError:
                    guard.trip("SCORE_INVALID", "SCORE requires a number between 0 and 1")
            elif step.operation == "MURMUR":
                if not arg:
                    guard.trip("MURMUR_EMPTY", "MURMUR requires an advisory message")
                else:
                    item = {"message": arg, "advisory": True, "status": "unresolved", "line": step.line}
                    murmurs.append(item)
                    if self.ledger is not None:
                        self.ledger.record_murmur(arg, line=step.line)
            elif step.operation == "INTEGRATE":
                if not state["observed"]:
                    guard.trip("INTEGRATION_WITHOUT_INPUT", "INTEGRATE requires a prior OBSERVE")
                else:
                    state["integrated"] = state["observed"]
            elif step.operation == "VERIFY":
                state["workflow_verified"] = bool(state["integrated"])
                if not state["workflow_verified"]:
                    guard.trip("VERIFICATION_FAILED", "VERIFY requires a successful observation and integration")
            elif step.operation == "RESPOND":
                if not state["workflow_verified"]:
                    guard.trip("UNVERIFIED_RESPONSE", "RESPOND is blocked until workflow VERIFY succeeds")
                else:
                    output = arg or state["integrated"]
            elif step.operation == "STOP":
                guard.trip("SCRIPT_STOP", arg or "Script requested STOP")
            record["state"] = "stopped" if guard.stopped else "ok"
            trace.append(record)

        status = "stopped" if guard.stopped else ("completed" if output else "incomplete")
        return ScriptResult(status, output, trace, murmurs, claims, guard.as_dict()).__dict__
