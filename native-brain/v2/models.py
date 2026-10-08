from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


@dataclass
class Message:
    role: str
    content: str
    source: str = "user"
    timestamp: str = field(default_factory=now_iso)
    message_id: str = field(default_factory=lambda: new_id("msg"))


@dataclass
class Thread:
    thread_id: str = field(default_factory=lambda: new_id("thread"))
    title: str = "Untitled thread"
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    messages: list[Message] = field(default_factory=list)
    memory_refs: list[str] = field(default_factory=list)


@dataclass
class Memory:
    text: str
    kind: str = "durable"
    confidence: float = 0.5
    source_thread: str | None = None
    created_at: str = field(default_factory=now_iso)
    memory_id: str = field(default_factory=lambda: new_id("mem"))


@dataclass
class Exchange:
    thread_id: str
    sender: str
    recipient: str
    content: str
    timestamp: str = field(default_factory=now_iso)
    exchange_id: str = field(default_factory=lambda: new_id("ex"))
    metadata: dict[str, Any] = field(default_factory=dict)
