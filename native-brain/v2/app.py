from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .voice import Voice
from .tissue import ModelTissue
from .script import ScriptEngine

app = FastAPI(title="Sylvex Brain v2 Chorus", version="0.5.0")
voice = Voice()
# Share the same in-memory ledger so script murmurs and Chorus dissent are visible together.
script_engine = ScriptEngine(ledger=voice.ledger)


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
        "unresolved_ledger_entries": len(voice.ledger.unresolved()),
    }


@app.post("/api/chorus")
def chorus(payload: ChorusIn):
    try:
        return voice.receive(
            payload.text,
            modality=payload.modality,
            salience=payload.salience,
            stakes=payload.stakes,
            surprise=payload.surprise,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chorus processing failed") from exc


@app.post("/api/script")
def run_script(payload: ScriptIn):
    """Run a bounded workflow; script murmurs enter the shared dissent ledger."""
    try:
        return script_engine.run(payload.script, input_text=payload.input_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Script processing failed") from exc
