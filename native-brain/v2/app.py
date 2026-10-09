from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .voice import Voice
from .tissue import ModelTissue

app = FastAPI(title="Sylvex Brain v2 Chorus", version="0.3.0")
voice = Voice()


class ChorusIn(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    modality: str = "text"
    salience: float = Field(default=0.5, ge=0, le=1)
    stakes: float = Field(default=0.5, ge=0, le=1)
    surprise: float = Field(default=0.5, ge=0, le=1)


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
        # Keep internal exception details out of public API responses.
        raise HTTPException(status_code=500, detail="Chorus processing failed") from exc
