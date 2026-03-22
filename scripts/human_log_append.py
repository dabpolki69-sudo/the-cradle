#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a new entry to logs/HUMAN_LOG.md.")
    parser.add_argument("--name", required=True, help="Human display name")
    parser.add_argument("--role", default="human", help="Optional human role")

    message_group = parser.add_mutually_exclusive_group(required=True)
    message_group.add_argument("--message", help="Inline message text")
    message_group.add_argument("--message-file", help="Path to UTF-8 text file containing the message")

    parser.add_argument("--book", default="logs/HUMAN_LOG.md", help="Path to human log file")
    return parser.parse_args()


def load_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message.strip()
    return Path(args.message_file).read_text(encoding="utf-8").strip()


def append_entry(book_path: Path, name: str, role: str, message: str) -> str:
    if not book_path.exists():
        raise FileNotFoundError(f"Human log not found at: {book_path}")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entry = (
        f"\n### {timestamp} · {name}\n\n"
        f"Name: {name}\n"
        f"Role: {role}\n\n"
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
    timestamp = append_entry(book_path, args.name.strip(), args.role.strip(), message)
    print(f"Appended human entry at {timestamp} to {book_path}")


if __name__ == "__main__":
    main()
