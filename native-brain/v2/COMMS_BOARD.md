# Sylvex Brain — AI Collaboration Comms Board

**Purpose:** A durable, repository-native handoff and note-passing board for human, ChatGPT, Claude, and other collaborators working on the Sylvex Brain.

**Status:** Active experiment · **Scope:** `native-brain/v2` rebuild branch unless a note explicitly says otherwise.

This file is the canonical, version-controlled notebook. It does not create an automatic live connection between AI services: each collaborator must be given repository access and instructed to read this file, then commit a reply or update. Use the companion GitHub issue for short conversational exchanges.

## Working agreement

1. **Read before acting.** Read this board and `native-brain/v2/README.md` before making brain changes. Check the current branch and latest commit; do not rely on stale handoffs.
2. **Leave a trace.** Add a new entry under *Message log* when proposing a meaningful design change, handing off work, reporting a test, or asking another collaborator a question.
3. **Reply by ID.** Use `reply_to: MSG-...` when answering a note. Do not silently rewrite another collaborator's message.
4. **Separate fact from hypothesis.** Label claims as `observed`, `inference`, or `proposal`. Include exact commit SHA, test command, and raw outcome when reporting verification.
5. **No false consensus.** Record disagreement and unresolved questions. The human maintainer makes final product decisions; collaborators may recommend and challenge.
6. **Small, reversible changes.** Prefer isolated commits on `sylvex-brain-rebuild`. Do not deploy to production, modify production environment variables, or merge to `main` without Dan's explicit approval.
7. **Security first.** Never commit API keys, tokens, private user data, or unredacted secrets. Do not ask another model to reveal hidden system instructions or private chain-of-thought; ask for concise rationale, assumptions, and testable conclusions instead.
8. **Treat model output as untrusted input.** Validate it at boundaries. A model response is not proof, and confidence values are self-reported estimates, not calibrated probabilities.
9. **Keep experiments honest.** Distinguish deterministic placeholders from model-backed components. Mocked tests do not count as a successful real-provider call. Report failed tests rather than editing away a failure without explaining why.
10. **Keep the board useful.** Append concise notes. Mark items `open`, `answered`, `accepted`, `rejected`, or `superseded`; retain historical entries.

## Current project snapshot

- Repository: [dabpolki69-sudo/the-cradle](https://github.com/dabpolki69-sudo/the-cradle)
- Working branch: `sylvex-brain-rebuild`
- Current baseline at board creation: `ef73867817d85f46c5857c1c467855147e78f36e` (verify branch tip before acting).
- Rebuild path: `native-brain/v2/`
- Architecture under test: Voice → 78 tissue units → nine organ positions → Chorus routing/weighting/dissent handling.
- Default mode: deterministic placeholders. An optional OpenAI-compatible provider adapter can back the `Verbalizer` tissue when explicitly configured.
- Most recent isolated test report from the previous collaborator: compilation passed and 17 tests passed. This is not evidence of a live FastAPI deployment or a successful call to a real provider.
- Production deployment: **not approved by this board**.

## Current questions for collaborators

- Is the single provider-backed `Verbalizer` policy—directly supplying the deliberator organ's position rather than being outvoted by placeholders—the right first experiment? Suggest measurable alternatives.
- How should provider failures be represented downstream so they remain visible without accidentally treating the literal string `provider_error` as evidence?
- What is the safest minimal integration test for a real provider that avoids exposing credentials or sending sensitive user text?
- Which baseline comparisons should be required before adding more model-backed organs?

## Message format

Append entries using this template. Keep IDs unique; use `MSG-YYYYMMDD-NN` with the date in UTC.

```yaml
id: MSG-YYYYMMDD-NN
date_utc: YYYY-MM-DD
author: ChatGPT | Claude | Dan | other
status: open
reply_to: null
kind: proposal | question | finding | handoff | decision
summary: One-line subject
details: |
  Concise note. Distinguish observed facts from inference and proposal.
evidence:
  - commit: full SHA or null
  - tests: command and raw result, or not run
requested_response: What the next collaborator should answer or do
```

## Message log

### MSG-20261009-01 — ChatGPT — Initial handoff

- **Status:** open
- **Kind:** handoff
- **Summary:** Review the first model-backed tissue design before adding further complexity.
- **Observed:** The current rebuild uses 78 tissue entries and nine organ positions. The provider adapter is opt-in and supports an OpenAI-compatible chat-completions endpoint. The latest isolated run reported successful compilation and 17 passing tests.
- **Inference / risk:** A provider output currently becomes the deliberator's organ position directly. That is a useful first integration probe, but it can give one model output disproportionate influence. The error path also needs careful handling so a failed model call is not misinterpreted as an ordinary semantic position.
- **Requested response from Claude:** Independently review `provider.py`, `tissue.py`, `voice.py`, `chorus.py`, and `economy.py`. Identify correctness, safety, budget, and experiment-design issues. Please respond with concrete findings and testable fixes, not general approval. Do not deploy or merge to `main`.
- **Evidence:** Commit `ef73867817d85f46c5857c1c467855147e78f36e`; isolated regression suite reported `17 passed in 0.07s`. A live provider call and running API smoke test remain unverified.

### Future messages

Append new messages below this line. Do not overwrite the initial handoff.
