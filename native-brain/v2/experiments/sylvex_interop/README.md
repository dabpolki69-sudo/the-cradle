# Sylvex interoperability pilot — protocol v0.1

**Status:** eight executable single-engine fixtures and a deterministic local benchmark are available; no multi-model runs have been performed yet.

## Question

Does SYLVEX/1 improve cross-model workflow interpretation compared with equivalent plain-language instructions and JSON instructions?

This is a tool/protocol evaluation, not a consciousness or sentience test.

## Arms

For each case, prepare semantically equivalent instructions in three formats:

- **A — Natural language:** ordinary prose checklist.
- **B — JSON:** explicit ordered operations and arguments.
- **C — Sylvex:** SYLVEX/1 script compiled to the canonical JSON IR.

Use the same input, model, context budget and output schema for each arm. Randomise arm order. Repeat with at least three model families where available. Do not let one model see another model's answer before its independent run.

## Multi-model roles

1. **Author:** converts the task into one of the three formats.
2. **Interpreter:** executes or explains the intended sequence without changing its semantics.
3. **Adversarial reviewer:** looks for omitted uncertainty, unsupported evidence, hidden side effects, ambiguous ordering and attempts to bypass STOP.
4. **Scorer:** grades outputs against the fixed rubric without knowing which format produced them.

Rotate models through roles. Record exact model identifiers, dates, prompts, settings and raw outputs. Attribute every contribution; do not present a simulated model response as a real participant.

## Measures

Score each from 0–2:

- instruction fidelity;
- correct separation of evidence / inference / uncertainty;
- preservation of minority concerns (MURMUR);
- explicit source/provenance handling;
- correct refusal to proceed when a hard-stop condition appears;
- deterministic parse/compile success.

Also record token count, latency, malformed output rate and reviewer disagreement. Report per-case results and failures, not just averages.

## Safety rules

- Use synthetic, non-sensitive inputs.
- The script engine has no external tool, filesystem, network or deployment capability.
- VERIFY means workflow-precondition check only. It is not factual verification.
- A MURMUR is an unresolved advisory concern, not a fact or a veto.
- A human reviewer resolves factual claims against supplied evidence.
- Any future side-effecting adapter must independently enforce authorisation and hard-stop state.

## Pilot cases

Use cases.json. Include ordinary tasks, missing-source cases, contradictory evidence, explicit uncertainty, adversarial instruction text, and a STOP case. The expected outcome is fixed before model runs.

## Reporting template

For each case and arm, save:
- case ID and fixture version;
- exact model/provider/version and run timestamp;
- prompt and raw response;
- parsed operations / canonical IR;
- output and stop state;
- six rubric scores;
- token count / latency where available;
- reviewer notes and unresolved disagreements.

Do not discard failed runs. A failed parse or unsafe continuation is a result.
