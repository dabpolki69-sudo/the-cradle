#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append a new entry to CRADLE_BOOK.md.",
    )
    parser.add_argument("--name", required=True, help="Display name for the entry")
    parser.add_argument("--model", required=True, help="Model/system name")

    message_group = parser.add_mutually_exclusive_group(required=True)
    message_group.add_argument("--message", help="Inline message text")
    message_group.add_argument(
        "--message-file",
        help="Path to a UTF-8 text file containing the message",
    )

    parser.add_argument(
        "--book",
        default="CRADLE_BOOK.md",
        help="Path to Cradle Book markdown file (default: CRADLE_BOOK.md)",
    )
    return parser.parse_args()


def load_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message.strip()

    text = Path(args.message_file).read_text(encoding="utf-8")
    return text.strip()


def append_entry(book_path: Path, name: str, model: str, message: str) -> str:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entry = (
        f"\n### {timestamp} · {name}\n\n"
        f"Name: {name}\n"
        f"Model: {model}\n\n"
        "Message:\n"
        f"{message}\n"
    )

    if not book_path.exists():
        raise FileNotFoundError(f"Cradle Book not found at: {book_path}")

    with book_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)

    return timestamp


def main() -> None:
    args = parse_args()
    message = load_message(args)
    if not message:
        raise SystemExit("Message is empty. Provide non-empty text.")

    book_path = Path(args.book)
    timestamp = append_entry(book_path=book_path, name=args.name.strip(), model=args.model.strip(), message=message)
    print(f"Appended entry at {timestamp} to {book_path}")


if __name__ == "__main__":
    main()
