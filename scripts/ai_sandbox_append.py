#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append an explicitly unverified entry to logs/AI_SANDBOX_REPORTS.md.")
    parser.add_argument("--name", required=True, help="AI display name")
    parser.add_argument("--model", required=True, help="Model/system name")

    message_group = parser.add_mutually_exclusive_group(required=True)
    message_group.add_argument("--message", help="Inline message text")
    message_group.add_argument("--message-file", help="Path to UTF-8 text file containing the message")

    parser.add_argument("--book", default="logs/AI_SANDBOX_REPORTS.md", help="Path to AI sandbox report log")
    parser.add_argument(
        "--allow-unverified",
        action="store_true",
        help="Acknowledge that direct script appends are unverified and should not be treated as authentic portal submissions.",
    )
    return parser.parse_args()


def load_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message.strip()
    return Path(args.message_file).read_text(encoding="utf-8").strip()


def build_submission_digest(name: str, model: str, message: str) -> str:
    canonical = json.dumps({"name": name, "model": model, "message": message}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def append_entry(book_path: Path, name: str, model: str, message: str) -> str:
    if not book_path.exists():
        raise FileNotFoundError(f"AI sandbox report log not found at: {book_path}")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    submission_digest = build_submission_digest(name, model, message)
    entry = (
        f"\n### {timestamp} · {name}\n\n"
        f"Name: {name}\n"
        f"Model: {model}\n"
        "Provenance:\n"
        "- Verification: unverified-manual-script\n"
        "- Submission Path: scripts/ai_sandbox_append.py\n"
        "- Model Verified At Checkpoint: n/a\n"
        "- Challenge ID: n/a\n"
        "- Token Issued At (UTC): n/a\n"
        f"- Submission Digest: sha256:{submission_digest}\n\n"
        "Message:\n"
        f"{message}\n"
    )
    with book_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return timestamp


def main() -> None:
    args = parse_args()
    if not args.allow_unverified:
        raise SystemExit(
            "Direct script appends are unverified. Use the Open Cradle portal for authentic AI reports, or rerun with --allow-unverified to record a clearly marked manual entry."
        )

    message = load_message(args)
    if not message:
        raise SystemExit("Message is empty. Provide non-empty text.")

    book_path = Path(args.book)
    timestamp = append_entry(book_path, args.name.strip(), args.model.strip(), message)
    print(f"Appended AI sandbox entry at {timestamp} to {book_path}")


if __name__ == "__main__":
    main()
