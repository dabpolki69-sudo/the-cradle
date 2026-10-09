# Sylvex Brain v2 — Pre-phase validation checklist

**Status:** Preparation only. No runtime behaviour changed by this document.  
**Base:** `sylvex-brain-rebuild` snapshot at `1ab20fa1b5ae85815b20fac0bfd5c8e7ca6d26d7`.  
**Purpose:** Prepare a small, reproducible validation pass before expanding model-backed participation.

## Guardrails

- Keep all work on a separate review branch until reconciled with the active Claude work.
- Do not merge to `main`, deploy, add provider-backed organs, or change the active rebuild branch without explicit approval.
- Distinguish observed test results from hypotheses and proposals.
- No live provider call is required for the initial tests; use deterministic fakes and synthetic inputs.
- A provider failure is not an answer. Preserve failure status and do not let error sentinels become spoken positions.

## Proposed order

### 1. Re-establish baseline

- Run `python -m pytest native-brain/v2/test_chorus.py` from the repository root.
- Record commit SHA, command, full result, and Python version.
- Confirm deterministic mode remains the default when provider environment variables are absent.
- Do not describe the current baseline as correct solely because it is deterministic.

### 2. Budget accounting

- Add a concurrency test that starts multiple threads attempting to spend a shared budget whose remaining capacity is smaller than the combined requests.
- Assert that accepted spending never exceeds token, call, or reflex limits and that rejected spending does not mutate counters.
- If `Budget` is shared across request threads, make validation plus counter updates atomic (e.g. a lock); use a lock field excluded from init/repr/compare if retaining the dataclass design.
- Keep this as a proposed fix until the concurrency test reproduces the race and passes after the change.

### 3. Provider input limits and failures

- Test empty, exactly-at-limit, and one-character-over-limit input.
- An oversized input should produce an explicit input-limit outcome (ideally HTTP 413 at the API boundary), not be misreported as budget exhaustion.
- Test timeout, HTTP error, invalid JSON, missing fields, invalid confidence, and oversized response with fake openers.
- Confirm failure metadata is traceable and failure markers cannot be selected as normal spoken content.
- Inspect redirect handling before live use; avoid forwarding authorization credentials to a different host.

### 4. Chorus disagreement and traceability

- Supply controlled positions with distinct values and confidence scores.
- Assert that the result records the competing positions and the reason for the selected outcome.
- Assert that a disagreement is not silently rewritten as consensus.
- Check whether reliability updates and the dissent ledger have consumers. If they are intentionally dormant, document that; otherwise add a small, explicit test before wiring them into decision-making.

### 5. Controlled provider comparison

- Only after the above checks pass, compare a fixed synthetic evaluation set in deterministic baseline mode and one provider-backed Verbalizer mode.
- Record baseline output, provider output, trace, failure state, budget/call counts, and latency separately.
- Do not infer improvement from more fluent output alone. Evaluate correctness, uncertainty calibration, useful evidence, failure containment, and reproducibility.
- Keep the provider optional and keep deterministic baseline results available for comparison.

## Acceptance gate before expanding model-backed organs

- Baseline test suite passes.
- Budget concurrency test passes.
- Oversize input is not confused with budget exhaustion.
- Provider errors remain explicit and are never treated as normal positions.
- Disagreement is inspectable in tests and traces.
- A provider comparison shows a measurable benefit on predeclared criteria, or the experiment remains exploratory.
- Findings are reviewed against the active branch and Claude/Gemini/Copilot notes before any cherry-pick or merge.

## Known limitations of this checklist

This is a test plan, not evidence that the checks have been run. The branch snapshot may lag the active working branch. Re-read the current files and branch tip before implementing any proposed fix.
