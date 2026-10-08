from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .brain import SylvexBrain
from .models import Exchange

app = FastAPI(title="Sylvex Brain v2", version="0.1.0")
brain = SylvexBrain()


class ThreadCreate(BaseModel):
    title: str = "Untitled thread"


class MessageIn(BaseModel):
    role: str = "user"
    source: str = "user"
    content: str = Field(min_length=1, max_length=100_000)


@app.get("/")
def root():
    return {"name": "Sylvex Brain", "version": "2.0-rebuild", "status": "awake", "mode": "orchestration"}


@app.get("/health")
def health():
    return {"status": "ok", "brain": "sylvex-v2", "storage": "json"}


@app.post("/api/threads")
def create_thread(payload: ThreadCreate):
    return brain.create_thread(payload.title)


@app.post("/api/threads/{thread_id}/messages")
def add_message(thread_id: str, payload: MessageIn):
    thread = next((t for t in brain.memory.threads() if t.thread_id == thread_id), None)
    if not thread:
        raise HTTPException(404, "thread not found")
    msg = brain.add_message(thread, payload.role, payload.content, payload.source)
    return {"message": msg.__dict__, "context": brain.context(thread)}


@app.get("/api/threads")
def list_threads():
    return brain.memory.threads()


@app.get("/api/memory")
def list_memory():
    return brain.relevant_memory(100)


@app.post("/api/exchange")
def external_exchange(payload: MessageIn):
    thread = brain.create_thread("External exchange")
    brain.add_message(thread, "user", payload.content, payload.source)
    return {"thread_id": thread.thread_id, "context": brain.context(thread)}
