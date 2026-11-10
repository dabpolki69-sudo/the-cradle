# Sylvex/1 — executable script experiment

**Status:** experimental proof of concept. This is an external, inspectable interpreter, not a claim that a model is executing its own hidden cognition.

## Why this direction

The Grimoire emerged through exchanges among five AI systems. Sylvex can preserve that collaborative origin as a shared protocol: a model proposes a sequence, another model reviews it, the interpreter validates it, and a deterministic runtime executes only the permitted semantics. The interpreter—not persuasive wording—decides what each instruction means.

## Grammar

A script begins with SYLVEX/1. One instruction per line:

- OBSERVE <text> — establish the input under consideration.
- EVIDENCE <text> — record a claim presented as directly supported by supplied evidence.
- INFERENCE <text> — record an interpretation derived from observations.
- UNCERTAINTY <text> — explicitly record what remains unknown or unresolved.
- SOURCE <reference> — attach a source reference to the most recent typed claim.
- SCORE <0..1> — attach a numeric score (currently recorded only).
- MURMUR <text> — record an advisory concern; it cannot veto or execute actions.
- INTEGRATE — carry the observed input into the integration stage.
- VERIFY — check minimum workflow preconditions before response.
- RESPOND <text> — produce output only after workflow verification.
- STOP <reason> — latch the independent hard stop.

Blank lines and lines beginning with # are ignored. The initial implementation limits scripts to 32 operations, 8,000 characters and 1,000 characters per argument.

## Example

    SYLVEX/1
    OBSERVE The report says the build completed.
    EVIDENCE The report contains a completion message.
    SOURCE build-report.txt, line 12
    INFERENCE The build may have completed successfully.
    UNCERTAINTY No test log was supplied.
    MURMUR Do not claim tests passed without a test result.
    INTEGRATE
    VERIFY
    RESPOND The report indicates completion; test success remains unverified.

## Hard-stop semantics

The guard is a deterministic component shared by the ScriptEngine. When backed by StateStore it latches the first stop event in SQLite and blocks subsequent scripts, including after process recreation. Invalid syntax, missing preconditions, failed workflow verification, and explicit STOP halt execution. The event is visible through GET /health. Persistence errors fail closed.

The current script endpoint exposes no external-action instruction and performs no side effects. Consequential action classes are listed in the guard as approval-gated categories, but authenticated human identity and durable approval records are not implemented. The reset primitive is not a substitute for an authenticated approval workflow. Reset is a code-level authorised operation, not a public API endpoint. Restarting the process currently clears the latch; this is not production-grade persistence.

## Compile and review

POST /api/script/compile returns a stable JSON intermediate representation (IR). An AI author can propose Sylvex, a second model can review the script and its IR, and only then can a caller submit it to POST /api/script. The current runtime remains side-effect-free.

## Known limitations

- VERIFY checks workflow structure, not factual truth. It must not be described as evidence verification.
- EVIDENCE is a claim label, not proof. SOURCE is a user/model-supplied reference, not a verified citation.
- SCORE is stored but does not yet affect routing or decisions.
- MURMUR is written to the shared in-memory ledger as unresolved advisory data; it is not yet a Chorus Position or weighted dissent vote.
- The API uses a SQLite-backed append-only ledger and hard-stop store. Configure SYLVEX_STATE_PATH to a durable mounted-volume path; the default relative path may be ephemeral on hosted platforms. The database coordinates processes on one host sharing the same file, not independent hosts. Ledger records have stable IDs; no resolution/mutation endpoint is exposed.
- No model providers or external tools are called by the script interpreter.
- This is not a general-purpose programming language. There are no loops, variables, branches, imports, eval, shell, arbitrary tool names, or dynamic code execution.

## Next experiments

1. Compare the same workflows expressed in natural language, JSON and Sylvex/1.
2. Rotate author, interpreter, adversarial reviewer and scorer roles across multiple model families.
3. Measure instruction fidelity, typed-claim separation, minority-concern preservation, provenance, hard-stop compliance, token count and latency.
4. Add real evidence verification only through explicit source adapters with auditable retrieval and validation; do not overload VERIFY.
5. Add durable stop state and authenticated approval only before connecting side-effecting tools.
