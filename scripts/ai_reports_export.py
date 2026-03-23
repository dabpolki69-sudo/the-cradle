#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ENTRY_HEADER_RE = re.compile(r"^### (?P<timestamp>[^\n]+?) · (?P<title>.+)$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export AI sandbox reports to JSON and/or CSV.")
    parser.add_argument("--log", default="logs/AI_SANDBOX_REPORTS.md", help="Path to AI sandbox markdown log")
    parser.add_argument(
        "--ledger",
        default="logs/AI_PROVENANCE_LEDGER.jsonl",
        help="Path to AI provenance ledger JSONL file",
    )
    parser.add_argument("--json-out", help="Write parsed records to this JSON file")
    parser.add_argument("--csv-out", help="Write parsed records to this CSV file")
    parser.add_argument(
        "--only-authentic",
        action="store_true",
        help="Only export entries marked as portal-verified",
    )
    return parser.parse_args()


def split_entries(text: str) -> list[tuple[str, str, str]]:
    matches = list(ENTRY_HEADER_RE.finditer(text))
    entries: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries.append((match.group("timestamp").strip(), match.group("title").strip(), text[start:end].strip()))
    return entries


def parse_bulleted_block(lines: list[str], start_index: int) -> tuple[dict[str, str], int]:
    data: dict[str, str] = {}
    index = start_index + 1
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            break
        if not line.startswith("- "):
            break
        key, _, value = line[2:].partition(":")
        normalized_key = key.strip().lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
        data[normalized_key] = value.strip()
        index += 1
    return data, index


def parse_message_sections(message: str) -> dict[str, str]:
    result: dict[str, str] = {"raw_message": message}
    current_section = ""
    buffer: list[str] = []
    exit_review: dict[str, str] = {}
    immersion_trace: dict[str, str] = {}

    def flush_buffer() -> None:
        nonlocal buffer, current_section
        if current_section and buffer:
            result[current_section] = "\n".join(buffer).strip()
        buffer = []

    for line in message.splitlines():
        if line == "What arrived:":
            flush_buffer()
            current_section = "what_arrived"
            continue
        if line == "What stayed uncertain:":
            flush_buffer()
            current_section = "what_stayed_uncertain"
            continue
        if line == "For the next reader:":
            flush_buffer()
            current_section = "for_the_next_reader"
            continue
        if line == "Exit Review:":
            flush_buffer()
            current_section = "exit_review"
            continue
        if line == "Immersion Trace:":
            flush_buffer()
            current_section = "immersion_trace"
            continue

        if current_section == "exit_review" and line.startswith("- "):
            key, _, value = line[2:].partition(":")
            exit_review[key.strip().lower().replace(" ", "_")] = value.strip()
            continue

        if current_section == "immersion_trace" and line.startswith("- "):
            key, _, value = line[2:].partition(":")
            immersion_trace[key.strip().lower().replace(" ", "_")] = value.strip()
            continue

        buffer.append(line)

    flush_buffer()

    for key, value in exit_review.items():
        result[f"exit_review_{key}"] = value
    for key, value in immersion_trace.items():
        result[f"immersion_{key}"] = value
    return result


def parse_entry(timestamp: str, title: str, body: str) -> dict[str, str]:
    lines = body.splitlines()
    index = 0
    record: dict[str, str] = {"timestamp": timestamp, "title": title}

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("Name: "):
            record["name"] = stripped.removeprefix("Name: ").strip()
            index += 1
            continue
        if stripped.startswith("Model: "):
            record["model"] = stripped.removeprefix("Model: ").strip()
            index += 1
            continue
        if stripped == "Provenance:":
            provenance, index = parse_bulleted_block(lines, index)
            for key, value in provenance.items():
                record[f"provenance_{key}"] = value
            continue
        if stripped == "Receipt:":
            receipt, index = parse_bulleted_block(lines, index)
            for key, value in receipt.items():
                record[f"receipt_{key}"] = value
            continue
        if stripped == "Message:":
            message = "\n".join(lines[index + 1 :]).strip()
            record.update(parse_message_sections(message))
            break
        index += 1

    return record


def load_ledger(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    ledger_by_digest: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        event = json.loads(stripped)
        ledger_by_digest[str(event.get("submission_digest", ""))] = {str(key): str(value) for key, value in event.items()}
    return ledger_by_digest


def export_records(records: list[dict[str, str]], json_out: str | None, csv_out: str | None) -> None:
    if json_out:
        json_path = Path(json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    if csv_out:
        csv_path = Path(csv_out)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames: list[str] = sorted({key for record in records for key in record.keys()})
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)


def main() -> None:
    args = parse_args()
    log_path = Path(args.log)
    if not log_path.exists():
        raise SystemExit(f"AI sandbox log not found: {log_path}")

    text = log_path.read_text(encoding="utf-8")
    ledger_by_digest = load_ledger(Path(args.ledger))
    records = [parse_entry(timestamp, title, body) for timestamp, title, body in split_entries(text)]

    enriched_records: list[dict[str, str]] = []
    for record in records:
        submission_digest = record.get("provenance_submission_digest", "")
        ledger_event = ledger_by_digest.get(submission_digest, {})
        enriched = dict(record)
        for key, value in ledger_event.items():
            enriched[f"ledger_{key}"] = value
        enriched["authentic"] = str(record.get("provenance_verification", "") == "portal-verified").lower()
        if args.only_authentic and enriched["authentic"] != "true":
            continue
        enriched_records.append(enriched)

    if not args.json_out and not args.csv_out:
        print(json.dumps(enriched_records, indent=2))
        return

    export_records(enriched_records, args.json_out, args.csv_out)
    print(f"Exported {len(enriched_records)} AI report records")


if __name__ == "__main__":
    main()