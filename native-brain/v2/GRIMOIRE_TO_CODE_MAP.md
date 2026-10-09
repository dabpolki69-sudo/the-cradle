# Grimoire-to-Code Map (Draft 0.1)

**Status:** review aid; not a claim that every principle is implemented  
**Code scope:** `native-brain/v2` on `sylvex-brain-rebuild`  
**Review rule:** implementation claims must be confirmed against the current branch and tests. A concept in a design document is not evidence of working behaviour.

## Status vocabulary

- **Observed:** verified in the reviewed code or test suite.
- **Partial:** some related mechanism exists, but does not yet satisfy the full principle.
- **Planned:** useful proposed work, not implemented.
- **Unverified:** not demonstrated by current evidence.

## Mapping

| Grimoire / design principle | Proposed engineering meaning | Relevant code / artefact | Current status to carry forward | Evidence needed next |
|---|---|---|---|---|
| Violet Principle / 98% model | Keep unknowns open while distinguishing possibility from evidence; permit revision | Moral guidance charter; experiment records | Planned as an explicit software requirement; no dedicated gate established here | Tests where evidence is insufficient and the correct outcome is to remain unresolved |
| neth·true | Separate observation, inference, uncertainty, and error; don't overclaim verification | `provider.py`, `tissue.py`, `voice.py`, `app.py`; comms board | Partial: provider adapter and visible error representation were described in prior review; error must be proven not to reach ordinary speech | Provider error-path test from adapter through API response and trace |
| thal·both | Preserve conflicting positions and minority warnings rather than erasing them | `chorus.py`, `ledger.py`, `voice.py`, `CHORUS.md` | Partial / unverified: design describes dissent; previous independent review reported ledger is write-only and deterministic reflexes all return the same value | Inject two or more distinct positions; assert dissent is recorded, retrievable, and visible in output metadata |
| Chorus weighting | Aggregate using inspectable criteria, not fluency or model count alone | `chorus.py`, `economy.py`, `CHORUS.md` | Partial: weighting machinery exists according to review; its behaviour and reliability inputs need tests | Unit tests for ranking, ties, missing values, confidence boundaries, and weight calculations |
| Earned reliability | Reliability changes only in response to recorded evidence and validated outcomes | `chorus.py` | Unverified: prior review reported `update_reliability` has no callers | Prove caller path or mark the feature as planned; test expected updates and bounds |
| Bounded provider experiment | Model-backed language is optional, budgeted, and cannot silently override failures | `provider.py`, `tissue.py`, `voice.py`, `app.py` | Partial: provider is opt-in; a live provider run and API-level smoke test have not been established in the recorded evidence | Synthetic env-gated smoke test; malformed response, timeout, HTTP error, size limit, and budget assertions |
| Resource stewardship | Budgets are bounded, correctly accounted, and safe with concurrent requests | `economy.py`, `app.py`, `test_chorus.py` | Risk flagged by prior review: shared budget and check-then-increment may race under concurrent requests; not reproduced yet | Concurrency test, then lock or per-request accounting fix and regression test |
| Care / harm minimisation | Escalate safeguards with severity and irreversibility; do not let model output alone authorize high-impact action | Charter and future action boundaries | Planned; no claim of a complete harm-policy enforcement layer | Define actions in scope and test refusal/defer/approval outcomes before connecting external actions |
| Human oversight / reversibility | Explicit approval for deploy, merge, permissions, and consequential external actions | Branch and release workflow; comms board working agreement | Process rule documented in collaboration notes; runtime enforcement not established | Protected branch/release settings and documented rollback/approval checks |
| Privacy / security | Treat inputs/outputs as untrusted; protect credentials; constrain redirects, size, and logs | `provider.py`, `app.py`, experiment logs | Partial / unverified: prior review flagged redirect/key exposure as a low-probability risk and over-length input semantics as confusing | Tests for cross-host redirect handling, oversized input status, redacted errors, and prompt/data separation |
| Provenance / accountability | Preserve authorship, commit identity, configuration, test command, outcomes, and unresolved risks | `COMMS_BOARD.md`, Git history, future experiment record | Partial: collaboration board exists; experiment-record schema is proposed | Add a template and verify records point to an exact commit and reproducible command |
| Architectural honesty | Distinguish live serving path from scaffolding and unused modules | `app.py`, imports across `native-brain/v2`, README | Prior review reported several modules are not imported by the serving path; independently re-check before treating as current | Automated import/entrypoint inventory and docs that label experimental/unwired components |

## Safest next work sequence

1. **Documentation only:** review and approve the Moral Guidance Charter; keep it clearly marked as a draft until the owner approves it.
2. **Test-only:** add synthetic tests for error propagation, conflicting Chorus positions, oversized input, and concurrent budget accounting. Tests should describe current behaviour first; failing tests are findings, not a reason to weaken assertions.
3. **Small runtime fixes after review:** prioritize budget atomicity and explicit provider-error status. Do not add a second model-backed organ.
4. **Experiment reproducibility:** introduce a template that captures commit SHA, test command and result, synthetic input-set version, provider mode, budget accounting, error mode, dissent record, and caveats. Never record API keys or unnecessary personal data.
5. **Independent review:** ask Claude, Copilot, and Gemini to challenge the charter and mapping with counterexamples; attribute each response accurately.
6. **Gate expansion:** no broader model-backed extension until the deterministic baseline is stable, dissent and error paths are testable, concurrent accounting is verified, and a live-provider smoke test is explicitly approved and completed.

## Experiment record template (proposal)

```yaml
experiment_id: "<unique-id>"
date_utc: "<ISO-8601>"
code_commit: "<full-commit-sha>"
owner_approval: "<reference or not-required>"
purpose: "<one testable question>"
input_set: "<synthetic dataset name and version>"
provider_mode: "deterministic | configured-provider"
provider_model: "<name or none>"
budget_before: "<value>"
budget_after: "<value>"
test_command: "<exact command>"
test_result: "pass | fail | not-run"
observations:
  - "<directly observed result>"
inferences:
  - "<interpretation, labelled as inference>"
errors:
  - "<error type, without secrets or private input>"
dissent:
  - "<positions/reasons preserved, or none observed>"
limitations:
  - "<what this experiment did not establish>"
next_step: "<small reversible follow-up>"
```

This template is a proposal; it does not imply that the current application records these fields automatically.
