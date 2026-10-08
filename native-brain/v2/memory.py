import json
from pathlib import Path
from .models import Memory, Thread


class MemoryStore:
    """Small transparent JSON store; replaceable by a database later."""
    def __init__(self, root: str = "brain_data"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.root / "memories.json"
        self.thread_file = self.root / "threads.json"

    def _load(self, path: Path, default):
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, path: Path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    def memories(self) -> list[Memory]:
        return [Memory(**x) for x in self._load(self.memory_file, [])]

    def add_memory(self, memory: Memory) -> Memory:
        items = self._load(self.memory_file, [])
        items.append(memory.__dict__)
        self._save(self.memory_file, items)
        return memory

    def threads(self) -> list[Thread]:
        result = []
        for x in self._load(self.thread_file, []):
            x["messages"] = []
            result.append(Thread(**x))
        return result

    def save_thread(self, thread: Thread) -> Thread:
        items = self._load(self.thread_file, [])
        record = thread.__dict__.copy()
        record["messages"] = [m.__dict__ for m in thread.messages]
        for i, existing in enumerate(items):
            if existing.get("thread_id") == thread.thread_id:
                items[i] = record
                break
        else:
            items.append(record)
        self._save(self.thread_file, items)
        return thread
