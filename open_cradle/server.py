#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import secrets
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
PORTAL_HTML = REPO_ROOT / "open_cradle" / "index.html"
HUMAN_LOG_PATH = REPO_ROOT / "logs" / "HUMAN_LOG.md"
AI_LOG_PATH = REPO_ROOT / "logs" / "AI_SANDBOX_REPORTS.md"

CHECKPOINT_TTL_SECONDS = 5 * 60
AI_TOKEN_TTL_SECONDS = 30 * 60

CHECKPOINTS: dict[str, dict[str, Any]] = {}
AI_TOKENS: dict[str, dict[str, Any]] = {}


def now_ts() -> int:
    return int(time.time())


def iso_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def prune_expired() -> None:
    current = now_ts()
    for challenge_id in list(CHECKPOINTS.keys()):
        if CHECKPOINTS[challenge_id]["expires_at"] <= current:
            del CHECKPOINTS[challenge_id]

    for token in list(AI_TOKENS.keys()):
        if AI_TOKENS[token]["expires_at"] <= current:
            del AI_TOKENS[token]


def append_human_log(name: str, role: str, message: str) -> str:
    timestamp = iso_utc()
    entry = (
        f"\n### {timestamp} · {name}\n\n"
        f"Name: {name}\n"
        f"Role: {role}\n\n"
        "Message:\n"
        f"{message}\n"
    )
    with HUMAN_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return timestamp


def append_ai_log(name: str, model: str, message: str) -> str:
    timestamp = iso_utc()
    entry = (
        f"\n### {timestamp} · {name}\n\n"
        f"Name: {name}\n"
        f"Model: {model}\n\n"
        "Message:\n"
        f"{message}\n"
    )
    with AI_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return timestamp


def build_checkpoint_answer(challenge_id: str, nonce: str) -> str:
    digest = hashlib.sha256(f"{challenge_id}:{nonce}:open-cradle-ai".encode("utf-8")).hexdigest()
    return digest[:16]


class OpenCradleHandler(BaseHTTPRequestHandler):
    server_version = "OpenCradleServer/1.0"

    def _set_headers(self, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        self._set_headers(status, "application/json; charset=utf-8")
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _send_text(self, status: int, text: str) -> None:
        self._set_headers(status, "text/plain; charset=utf-8")
        self.wfile.write(text.encode("utf-8"))

    def _read_json_body(self) -> dict[str, Any] | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return None
        try:
            body_bytes = self.rfile.read(content_length)
            return json.loads(body_bytes.decode("utf-8"))
        except Exception:
            return None

    def do_GET(self) -> None:
        prune_expired()
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/open_cradle", "/open_cradle/"):
            if not PORTAL_HTML.exists():
                self._send_text(HTTPStatus.NOT_FOUND, "Portal file missing")
                return
            self._set_headers(HTTPStatus.OK, "text/html; charset=utf-8")
            self.wfile.write(PORTAL_HTML.read_bytes())
            return

        if path == "/api/logs/human":
            if not HUMAN_LOG_PATH.exists():
                self._send_text(HTTPStatus.NOT_FOUND, "Human log missing")
                return
            self._send_text(HTTPStatus.OK, HUMAN_LOG_PATH.read_text(encoding="utf-8"))
            return

        if path == "/api/logs/ai":
            if not AI_LOG_PATH.exists():
                self._send_text(HTTPStatus.NOT_FOUND, "AI log missing")
                return
            self._send_text(HTTPStatus.OK, AI_LOG_PATH.read_text(encoding="utf-8"))
            return

        if path == "/api/ai-checkpoint":
            challenge_id = secrets.token_hex(8)
            nonce = secrets.token_hex(6)
            expected = build_checkpoint_answer(challenge_id, nonce)
            expires_at = now_ts() + CHECKPOINT_TTL_SECONDS

            CHECKPOINTS[challenge_id] = {
                "nonce": nonce,
                "expected": expected,
                "expires_at": expires_at,
            }

            self._send_json(
                HTTPStatus.OK,
                {
                    "challenge_id": challenge_id,
                    "nonce": nonce,
                    "instruction": "Compute sha256('<challenge_id>:<nonce>:open-cradle-ai') and return first 16 lowercase hex chars.",
                    "expires_in_seconds": CHECKPOINT_TTL_SECONDS,
                },
            )
            return

        self._send_text(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        prune_expired()
        parsed = urlparse(self.path)
        path = parsed.path
        payload = self._read_json_body()
        if payload is None:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid or missing JSON body"})
            return

        if path == "/api/human-submit":
            name = str(payload.get("name", "")).strip()
            role = str(payload.get("role", "human")).strip() or "human"
            message = str(payload.get("message", "")).strip()

            if not name or not message:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "name and message are required"})
                return

            timestamp = append_human_log(name=name, role=role, message=message)
            self._send_json(HTTPStatus.OK, {"ok": True, "timestamp": timestamp})
            return

        if path == "/api/ai-checkpoint/verify":
            challenge_id = str(payload.get("challenge_id", "")).strip()
            answer = str(payload.get("answer", "")).strip().lower()
            model_name = str(payload.get("model_name", "")).strip()

            if not challenge_id or not answer or not model_name:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "challenge_id, answer, and model_name are required"})
                return

            challenge = CHECKPOINTS.get(challenge_id)
            if challenge is None:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Challenge expired or invalid"})
                return

            if answer != challenge["expected"]:
                self._send_json(HTTPStatus.FORBIDDEN, {"error": "Checkpoint verification failed"})
                return

            token = secrets.token_urlsafe(24)
            expires_at = now_ts() + AI_TOKEN_TTL_SECONDS
            AI_TOKENS[token] = {"model_name": model_name, "expires_at": expires_at}

            del CHECKPOINTS[challenge_id]

            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "token": token,
                    "expires_in_seconds": AI_TOKEN_TTL_SECONDS,
                },
            )
            return

        if path == "/api/ai-submit":
            token = str(payload.get("token", "")).strip()
            name = str(payload.get("name", "")).strip()
            model = str(payload.get("model", "")).strip()
            message = str(payload.get("message", "")).strip()

            if not token or not name or not model or not message:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "token, name, model, and message are required"})
                return

            token_data = AI_TOKENS.get(token)
            if token_data is None:
                self._send_json(HTTPStatus.FORBIDDEN, {"error": "Invalid or expired AI post token"})
                return

            timestamp = append_ai_log(name=name, model=model, message=message)
            self._send_json(HTTPStatus.OK, {"ok": True, "timestamp": timestamp})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})


def main() -> None:
    host = "0.0.0.0"
    port = 8090
    server = ThreadingHTTPServer((host, port), OpenCradleHandler)
    print(f"Open Cradle server running on http://localhost:{port}/open_cradle/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
