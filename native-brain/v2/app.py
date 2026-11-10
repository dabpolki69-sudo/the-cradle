import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .voice import Voice
from .tissue import ModelTissue
from .script import ScriptEngine, compile_script, ScriptSyntaxError
from .guard import HardStop
from .ledger import DissentLedger
from .state_store import StateStore

app = FastAPI(title="Sylvex Brain v2 Chorus", version="0.6.0")
# For restart durability, point SYLVEX_STATE_PATH at a persistent mounted volume.
state_path = os.environ.get("SYLVEX_STATE_PATH", "./data/sylvex-state.sqlite3")
state_store = StateStore(state_path)
voice = Voice()
voice.ledger = DissentLedger(state_store=state_store)
script_engine = ScriptEngine(ledger=voice.ledger, guard=HardStop(state_store=state_store))


class ChorusIn(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    modality: str = "text"
    salience: float = Field(default=0.5, ge=0, le=1)
    stakes: float = Field(default=0.5, ge=0, le=1)
    surprise: float = Field(default=0.5, ge=0, le=1)


class ScriptIn(BaseModel):
    script: str = Field(min_length=1, max_length=8_000)
    input_text: str = Field(default="", max_length=100_000)


@app.get("/")
def root():
    return {"name": "Sylvex Brain", "version": "2.0-rebuild", "mode": "chorus"}


@app.get("/health")
def health():
    model_units = sum(isinstance(unit, ModelTissue) for unit in voice.tissues.values())
    return {
        "status": "ok",
        "architecture": "THE CHORUS",
        "organs": 9,
        "tissue_units": len(voice.tissues),
        "model_backed_tissues": model_units,
        "provider_mode": "configured" if model_units else "deterministic_baseline",
        "script_engine": "SYLVEX/1",
        "script_side_effects": False,
        "state_store": "sqlite",
        "state_path_configured": bool(os.environ.get("SYLVEX_STATE_PATH")),
        "unresolved_ledger_entries": len(voice.ledger.unresolved()),
        "hard_stop": script_engine.guard.as_dict(),
    }


@app.get("/api/ledger/unresolved")
def unresolved_ledger():
    entries = voice.ledger.unresolved()
    return {"count": len(entries), "entries": [voice.ledger.as_dict(entry) for entry in entries]}


@app.post("/api/chorus")
def chorus(payload: ChorusIn):
    try:
        return voice.receive(
            payload.text, modality=payload.modality, salience=payload.salience,
            stakes=payload.stakes, surprise=payload.surprise,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chorus processing failed") from exc


@app.post("/api/script/compile")
def compile_sylvex(payload: ScriptIn):
    try:
        return compile_script(payload.script)
    except ScriptSyntaxError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/script")
def run_script(payload: ScriptIn):
    try:
        return script_engine.run(payload.script, input_text=payload.input_text)
    except Exception as exc:
        # Persistence failures must not be converted into a successful workflow.
        raise HTTPException(status_code=503, detail="Script processing unavailable; state safety could not be confirmed") from exc
