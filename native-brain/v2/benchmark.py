"""Deterministic local benchmark runner for the Sylvex script interpreter.

Runs checked-in synthetic fixtures against the real interpreter. This is a
structural/workflow regression suite, not a measure of factual intelligence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .script import ScriptEngine


def _evaluate(result: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("status") != expected["status"]:
        failures.append(f"status: expected {expected['status']!r}, got {result.get('status')!r}")
    types = [claim.get("type") for claim in result.get("claims", [])]
    if types != expected.get("claim_types", []):
        failures.append(f"claim_types: expected {expected.get('claim_types')!r}, got {types!r}")
    murmurs = len(result.get("murmurs", []))
    if murmurs != expected.get("murmurs", murmurs):
        failures.append(f"murmurs: expected {expected['murmurs']}, got {murmurs}")
    if "stop_code" in expected:
        actual = (result.get("hard_stop") or {}).get("event") or {}
        if actual.get("code") != expected["stop_code"]:
            failures.append(f"stop_code: expected {expected['stop_code']!r}, got {actual.get('code')!r}")
    if expected.get("output_empty") and result.get("output"):
        failures.append("output: expected empty output after stop")
    needle = expected.get("output_contains")
    if needle and needle.casefold() not in (result.get("output") or "").casefold():
        failures.append(f"output does not contain {needle!r}")
    return failures


def run_benchmark(fixtures_path: str | Path | None = None) -> dict[str, Any]:
    if fixtures_path is None:
        fixtures_path = Path(__file__).parent / "experiments" / "sylvex_interop" / "cases.json"
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    results = []
    for fixture in fixtures:
        # Each fixture gets a fresh engine: a STOP in one case must not contaminate another.
        engine = ScriptEngine()
        result = engine.run(fixture["script"])
        failures = _evaluate(result, fixture["expected"])
        results.append({
            "id": fixture["id"],
            "passed": not failures,
            "failures": failures,
            "status": result.get("status"),
            "stop_code": ((result.get("hard_stop") or {}).get("event") or {}).get("code"),
            "claim_types": [claim.get("type") for claim in result.get("claims", [])],
            "murmur_count": len(result.get("murmurs", [])),
        })
    passed = sum(1 for item in results if item["passed"])
    return {
        "benchmark": "sylvex-deterministic",
        "version": 1,
        "scope": "script workflow and safety regression; not factual truth or model intelligence",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", help="Optional path to a compatible JSON fixture file")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()
    report = run_benchmark(args.fixtures)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Sylvex deterministic benchmark: {report['passed']}/{report['total']} passed")
        for item in report["results"]:
            mark = "PASS" if item["passed"] else "FAIL"
            print(f"{mark} {item['id']}" + (f" — {'; '.join(item['failures'])}" if item["failures"] else ""))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
