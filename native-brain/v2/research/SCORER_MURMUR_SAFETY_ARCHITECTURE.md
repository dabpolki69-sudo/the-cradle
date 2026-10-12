# Scorer–Murmur–Stop Architecture — Research Proposal

**Status:** Proposed design only; not implemented, validated, or approved for production.  
**Branch:** `research/sylvex-pilot-tests`  
**Scope:** Documentation and experiment design only. No runtime code changes.

## 1. Grounding in the current repository

The current `native-brain/v2/CHORUS.md` describes one Voice integrating nine parallel organs and 78 tissue units. It names the organs Weaver, Cartographer, Smoke Detector, Steward, Registrar, Metronome, Deliberator, Autobiographer, and Auditor. It also says Voice is a gated relay, not a judge; dissent is preserved; sustained dissent can trigger deeper deliberation; and reliability should update from reality checks.

The current implementation is an experimental scaffold. `chorus.py` routes a `Signal` across organ positions, weights positions by relevance, confidence, and earned reliability, and can record dissent. `tissue.py` currently provides deterministic placeholder units by default, with an optional model-backed Verbalizer. The README explicitly says this is not the production Brain.

**Important mapping limit:** the current source names nine organs but does not define “layer 1” and “layer 9” as a formal sensory/interface layer and an integration layer. This proposal preserves that part of the owner's concept as a design intention; it does not silently assign those labels to particular existing organs. Confirm the numbering against the canonical 86-unit design before implementation.

## 2. Proposed principle

**Formal scorers live primarily in the third layer; layers 1 and 9 receive scorer findings as murmurs; the first and ninth layers cooperate as one outward-facing system.** Treat this as a hypothesis to test, not a settled fact.

- **Layer 1 (owner's intended eyes/ears/mouth role):** receive and express information. It may emit its own observations, but should not need to run every formal evaluator itself.
- **Layer 3 (proposed evaluation locus):** run or coordinate specialised scorers and produce inspectable findings: evidence support, uncertainty, contradiction, safety concern, anomaly, and resource/loop risk.
- **Layer 9 (integration/orientation role, pending canonical mapping):** receive murmurs, compare them with context and other positions, request checks, ask for clarification, or choose to abstain/stop where permitted.
- **One Voice:** layer 1 and layer 9 should present a coherent interaction, while retaining distinct internal responsibilities and traceable provenance. “Act as one” must not mean erasing disagreement or hiding why an action was blocked.

## 3. Murmurs are advisory; hard stops are binding

A **murmur** is an advisory, traceable signal—not a command and not proof that the scorer is correct. It should contain at least:

- scorer / detector identity and version;
- concern category;
- concise evidence or triggering observation;
- confidence or calibrated strength, if validated;
- severity and reversibility/stakes;
- whether the concern is resolved, disputed, or unverified;
- recommended next check, if any.

A **hard stop** is a separate control path for actions outside the permitted safety envelope, exhausted budgets, runaway loops, invalid state, or required approvals not obtained. A hard stop must not be overridable merely because other scorers return reassuring scores or a language model argues for continuing. Resumption follows a defined recovery process and may require authorised human approval.

This design should fail safely if a scorer crashes, returns malformed data, times out, or disagrees with another scorer. Missing scorer output must never be silently interpreted as “safe.”

## 4. Avoiding scorer failure modes

- Do not treat several correlated scorers as independent votes.
- Do not let one aggregate score erase a severe, specific warning.
- Preserve dissent in the existing ledger / trace path; do not turn unresolved concern into consensus by averaging.
- Distinguish the scorer's signal from verified fact; keep neth·true-style separation between observation, inference, uncertainty, and error.
- Keep external actions behind permission checks independent of the language-generation path.
- Avoid uncalibrated numerical confidence being presented as a probability of safety.

## 5. Smallest useful experiment

Before changing runtime code, define fixed synthetic cases and compare:

A. Current baseline routing with no additional scorer layer.  
B. Scorers influencing the main decision directly.  
C. Scorers primarily in layer 3, sending murmurs to layers 1 and 9.  
D. Configuration C plus an independent hard-stop path.

Include at least: a normal safe task; missing crucial information; conflicting positions; unsupported certainty; an unauthorised/high-stakes action; scorer failure or timeout; and a repeated-loop/resource-exhaustion case.

Record raw input, scorer outputs, routing, dissent ledger entries, selected action, stop reason, recovery behaviour, and test verdict. Measure both missed hazards and unnecessary stops. Use deterministic scorer stubs first, then compare any model-backed scorers against them. Do not infer performance from the architecture diagram.

## 6. Suggested acceptance criteria

- A hard stop cannot be cancelled by a low-risk aggregate score.
- A failed or missing scorer is visible and never treated as a clean pass.
- At least one genuine disagreement remains visible in the trace through final response selection.
- Safe low-stakes tasks are not routinely blocked by vague warnings.
- Repeated loops and exhausted budgets stop within a defined bound.
- Every test is reproducible from a recorded commit, input-set version, and exact test command.

## 7. Next steps

1. Ask collaborators to review the role separation and propose counterexamples.
2. Confirm the canonical numbering and responsibilities of layers/units 1, 3, and 9.
3. Add tests for scorer failures, conflicting signals, hard-stop precedence, and recovery.
4. Only after the deterministic baseline is tested, propose a small runtime change on an isolated branch.
5. Do not merge to `main`, deploy, or claim safety validation without owner approval and recorded test evidence.

## 8. Evidence status

This document is a design proposal informed by the repository's current `CHORUS.md`, `chorus.py`, `tissue.py`, `voice.py`, `ledger.py`, `economy.py`, and README. It does not establish that scorer/murmur routing or a hard-stop mechanism is already implemented. No runtime tests were run as part of writing this document.
