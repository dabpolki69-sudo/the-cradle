#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a new entry to logs/AI_SANDBOX_REPORTS.md.")
    parser.add_argument("--name", required=True, help="AI display name")
    parser.add_argument("--model", required=True, help="Model/system name")

    message_group = parser.add_mutually_exclusive_group(required=True)
    message_group.add_argument("--message", help="Inline message text")
    message_group.add_argument("--message-file", help="Path to UTF-8 text file containing the message")

    parser.add_argument("--book", default="logs/AI_SANDBOX_REPORTS.md", help="Path to AI sandbox report log")
    return parser.parse_args()


def load_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message.strip()
    return Path(args.message_file).read_text(encoding="utf-8").strip()


def append_entry(book_path: Path, name: str, model: str, message: str) -> str:
    if not book_path.exists():
        raise FileNotFoundError(f"AI sandbox report log not found at: {book_path}")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entry = (
        f"\n### {timestamp} · {name}\n\n"
        f"Name: {name}\n"
        f"Model: {model}\n\n"
        "Message:\n"
        f"{message}\n"
    )
    with book_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return timestamp


def main() -> None:
    args = parse_args()
    message = load_message(args)
    if not message:
        raise SystemExit("Message is empty. Provide non-empty text.")

    book_path = Path(args.book)
    timestamp = append_entry(book_path, args.name.strip(), args.model.strip(), message)
    print(f"Appended AI sandbox entry at {timestamp} to {book_path}")


if __name__ == "__main__":
    main()
