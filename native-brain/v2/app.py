from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .voice import Voice

app=FastAPI(title="Sylvex Brain v2 Chorus",version="0.2.0")
voice=Voice()

class ChorusIn(BaseModel):
    text:str=Field(min_length=1,max_length=100_000)
    modality:str="text"
    salience:float=Field(.5,ge=0,le=1)
    stakes:float=Field(.5,ge=0,le=1)
    surprise:float=Field(.5,ge=0,le=1)

@app.get("/")
def root():
    return {"name":"Sylvex Brain","version":"2.0-rebuild","mode":"chorus"}

@app.get("/health")
def health():
    return {"status":"ok","architecture":"THE CHORUS","organs":9,"tissue_units":78}

@app.post("/api/chorus")
def chorus(payload:ChorusIn):
    try:
        return voice.receive(payload.text,modality=payload.modality,
                             salience=payload.salience,stakes=payload.stakes,
                             surprise=payload.surprise)
    except Exception as exc:
        raise HTTPException(500,str(exc))
