from .memory import MemoryStore
from .models import Message, Thread, Memory


class SylvexBrain:
    """Core orchestration object. Model generation remains an injected dependency."""
    def __init__(self, memory: MemoryStore | None = None):
        self.memory = memory or MemoryStore()

    def create_thread(self, title: str = "Untitled thread") -> Thread:
        thread = Thread(title=title)
        self.memory.save_thread(thread)
        return thread

    def add_message(self, thread: Thread, role: str, content: str, source: str = "user") -> Message:
        msg = Message(role=role, content=content, source=source)
        thread.messages.append(msg)
        self.memory.save_thread(thread)
        return msg

    def relevant_memory(self, limit: int = 12) -> list[Memory]:
        return sorted(self.memory.memories(), key=lambda m: m.confidence, reverse=True)[:limit]

    def context(self, thread: Thread, limit: int = 12) -> list[dict]:
        durable = [{"kind": m.kind, "text": m.text} for m in self.relevant_memory(limit)]
        recent = [{"role": m.role, "content": m.content, "source": m.source} for m in thread.messages[-20:]]
        return [{"type": "memory", "items": durable}, {"type": "thread", "items": recent}]
