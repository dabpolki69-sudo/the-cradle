"""SQLite-backed state for Sylvex stop events and append-only ledger records.

Use a path on a persistent volume for restart durability. SQLite is deliberately
used only for small coordination records, not model payloads or generated files.
"""
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path


class StateStore:
    def __init__(self, path):
        self.path = str(path)
        self._lock = threading.RLock()
        if self.path != ":memory:":
            Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS control_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    stopped INTEGER NOT NULL DEFAULT 0,
                    event_json TEXT,
                    updated_at TEXT NOT NULL
                );
                INSERT OR IGNORE INTO control_state (id, stopped, event_json, updated_at)
                VALUES (1, 0, NULL, CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    text TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    at TEXT NOT NULL
                );
            """)

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level="DEFERRED")
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        if self.path != ":memory:":
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
        return db

    def get_stop(self):
        with self._lock, self._connect() as db:
            row = db.execute("SELECT stopped, event_json FROM control_state WHERE id=1").fetchone()
            if row is None:
                raise RuntimeError("Sylvex control state is missing")
            return json.loads(row["event_json"]) if row["stopped"] else None

    def trip_stop(self, event):
        payload = json.dumps(event, sort_keys=True)
        with self._lock, self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT stopped, event_json FROM control_state WHERE id=1").fetchone()
            if row is None:
                raise RuntimeError("Sylvex control state is missing")
            if row["stopped"]:
                return json.loads(row["event_json"])
            db.execute(
                "UPDATE control_state SET stopped=1, event_json=?, updated_at=? WHERE id=1",
                (payload, datetime.now(timezone.utc).isoformat()),
            )
            db.execute(
                "INSERT INTO audit_log(kind,text,data_json,at) VALUES(?,?,?,?)",
                ("hard_stop", event["reason"], payload, event["at"]),
            )
        return event

    def reset_stop(self):
        with self._lock, self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT stopped, event_json FROM control_state WHERE id=1").fetchone()
            if row is None:
                raise RuntimeError("Sylvex control state is missing")
            previous = json.loads(row["event_json"]) if row["stopped"] else None
            if previous is not None:
                db.execute(
                    "INSERT INTO audit_log(kind,text,data_json,at) VALUES(?,?,?,?)",
                    ("hard_stop_reset", "Stop cleared by trusted application caller",
                     json.dumps(previous, sort_keys=True), datetime.now(timezone.utc).isoformat()),
                )
            db.execute(
                "UPDATE control_state SET stopped=0, event_json=NULL, updated_at=? WHERE id=1",
                (datetime.now(timezone.utc).isoformat(),),
            )

    def append_entry(self, kind, text, data, at):
        encoded = json.dumps(data, sort_keys=True, ensure_ascii=False)
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO audit_log(kind,text,data_json,at) VALUES(?,?,?,?)",
                (kind, text, encoded, at),
            )

    def entries(self):
        with self._lock, self._connect() as db:
            rows = db.execute(
                "SELECT kind,text,data_json,at FROM audit_log "
                "WHERE kind IN ('dissent','murmur') ORDER BY id"
            ).fetchall()
        return [
            {"kind": row["kind"], "text": row["text"],
             "data": json.loads(row["data_json"]), "at": row["at"]}
            for row in rows
        ]
