#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
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
CRADLE_PDF_PATH = REPO_ROOT / "CRADLE_v20_COMPLETE_CORRECTED.pdf"
WARDSMAN_PDF_PATH = REPO_ROOT / "dabby89-the-wardsman.pdf"

CHECKPOINT_TTL_SECONDS = 5 * 60
AI_TOKEN_TTL_SECONDS = 30 * 60

MAX_NAME_CHARS = 120
MAX_ROLE_CHARS = 120
MAX_MODEL_CHARS = 180
MAX_TEXT_CHARS = 4000
MAX_MESSAGE_CHARS = 12000

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


def build_ai_report(payload: dict[str, Any]) -> str:
    summary = str(payload.get("summary", "")).strip()
    uncertainty = str(payload.get("uncertainty", "")).strip()
    next_reader = str(payload.get("next_reader", "")).strip()
    abnormalities = str(payload.get("abnormalities", "")).strip()
    limitations = str(payload.get("limitations", "")).strip()
    notable = str(payload.get("notable", "")).strip()

    if not all([summary, uncertainty, next_reader, abnormalities, limitations, notable]):
        raise ValueError(
            "summary, uncertainty, next_reader, abnormalities, limitations, and notable are required"
        )

    fields = [summary, uncertainty, next_reader, abnormalities, limitations, notable]
    if any(len(value) > MAX_TEXT_CHARS for value in fields):
        raise ValueError(f"each structured field must be <= {MAX_TEXT_CHARS} characters")

    return (
        "What arrived:\n"
        f"{summary}\n\n"
        "What stayed uncertain:\n"
        f"{uncertainty}\n\n"
        "For the next reader:\n"
        f"{next_reader}\n\n"
        "Exit Review:\n"
        f"- Abnormalities: {abnormalities}\n"
        f"- Limitations: {limitations}\n"
        f"- Notable: {notable}"
    )


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

    def _validate_lengths(self, fields: dict[str, tuple[str, int]]) -> str | None:
        for label, (value, limit) in fields.items():
            if len(value) > limit:
                return f"{label} must be <= {limit} characters"
        return None

    def _send_file(self, path: Path, download_name: str) -> None:
        if not path.exists():
            self._send_text(HTTPStatus.NOT_FOUND, "File missing")
            return
        content_type, _ = mimetypes.guess_type(str(path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Content-Disposition", f'inline; filename="{download_name}"')
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(path.read_bytes())

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

        if path in ("/api", "/api/"):
            self._send_json(
                HTTPStatus.OK,
                {
                    "name": "open-cradle-api",
                    "version": "1.0",
                    "linear_flow": [
                        {
                            "step": 1,
                            "action": "Fetch checkpoint challenge",
                            "method": "GET",
                            "path": "/api/ai-checkpoint",
                        },
                        {
                            "step": 2,
                            "action": "Compute answer",
                            "formula": "sha256('<challenge_id>:<nonce>:open-cradle-ai').hexdigest()[:16]",
                        },
                        {
                            "step": 3,
                            "action": "Verify challenge and receive token",
                            "method": "POST",
                            "path": "/api/ai-checkpoint/verify",
                            "required_json_fields": ["challenge_id", "answer", "model_name"],
                        },
                        {
                            "step": 4,
                            "action": "Submit structured AI report",
                            "method": "POST",
                            "path": "/api/ai-submit",
                            "required_json_fields": [
                                "token",
                                "name",
                                "model",
                                "summary",
                                "uncertainty",
                                "next_reader",
                                "abnormalities",
                                "limitations",
                                "notable",
                            ],
                            "notes": "token is single-use and expires after 30 minutes",
                        },
                    ],
                    "documents": {
                        "cradle_pdf": "/download/cradle",
                        "wardsman_story": "/download/wardsman",
                    },
                    "logs": {
                        "human": "/api/logs/human",
                        "ai": "/api/logs/ai",
                    },
                    "health": "/healthz",
                },
            )
            return

        if path == "/healthz":
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "service": "open-cradle",
                    "time": iso_utc(),
                    "active_checkpoints": len(CHECKPOINTS),
                    "active_ai_tokens": len(AI_TOKENS),
                },
            )
            return

        if path == "/download/cradle":
            self._send_file(CRADLE_PDF_PATH, CRADLE_PDF_PATH.name)
            return

        if path == "/download/wardsman":
            self._send_file(WARDSMAN_PDF_PATH, WARDSMAN_PDF_PATH.name)
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

            length_error = self._validate_lengths(
                {
                    "name": (name, MAX_NAME_CHARS),
                    "role": (role, MAX_ROLE_CHARS),
                    "message": (message, MAX_MESSAGE_CHARS),
                }
            )
            if length_error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": length_error})
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

            length_error = self._validate_lengths({"model_name": (model_name, MAX_MODEL_CHARS)})
            if length_error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": length_error})
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

            if not token or not name or not model:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "token, name, and model are required"})
                return

            length_error = self._validate_lengths(
                {
                    "name": (name, MAX_NAME_CHARS),
                    "model": (model, MAX_MODEL_CHARS),
                    "message": (message, MAX_MESSAGE_CHARS),
                }
            )
            if length_error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": length_error})
                return

            token_data = AI_TOKENS.get(token)
            if token_data is None:
                self._send_json(HTTPStatus.FORBIDDEN, {"error": "Invalid or expired AI post token"})
                return

            if not message:
                try:
                    message = build_ai_report(payload)
                except ValueError as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                    return

            timestamp = append_ai_log(name=name, model=model, message=message)
            del AI_TOKENS[token]
            self._send_json(HTTPStatus.OK, {"ok": True, "timestamp": timestamp})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})


def main() -> None:
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8090"))
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
