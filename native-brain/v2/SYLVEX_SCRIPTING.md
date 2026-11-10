# Sylvex/1 — first executable script experiment

**Status:** experimental proof of concept. This is a small external interpreter, not a claim that a model is executing its own hidden cognition.

## Why this direction

The Grimoire emerged through exchanges among five AI systems. Sylvex can preserve that collaborative origin by becoming a shared, inspectable protocol: a model proposes a sequence, the interpreter validates it, and a deterministic runtime executes only the permitted semantics. The interpreter—not the model's persuasive wording—decides what each instruction means.

## Grammar

A script begins with `SYLVEX/1`. One instruction per line:

- `OBSERVE <text>` — establish the input under consideration.
- `SCORE <0..1>` — attach a numeric confidence/priority value.
- `MURMUR <text>` — record an advisory concern; it cannot veto or execute actions.
- `INTEGRATE` — carry the observed input into the integration stage.
- `VERIFY` — require the minimum workflow preconditions before response.
- `RESPOND <text>` — produce output only after verification.
- `STOP <reason>` — latch the independent hard stop.

Blank lines and lines beginning with `#` are ignored. The initial implementation limits scripts to 32 operations, 8,000 characters and 1,000 characters per argument.

## Example

```text
SYLVEX/1
OBSERVE The report says the build completed.
SCORE 0.7
MURMUR No test log has been supplied.
INTEGRATE
VERIFY
RESPOND The report is noted, but the build is not independently verified.
```

## Hard-stop semantics

The guard is a separate deterministic component. It latches the first stop event and blocks subsequent script steps. Invalid syntax, missing preconditions, failed verification, and explicit STOP halt execution. Consequential action classes (deploy, publish, delete, external writes/sends, spending, permission changes, protected merges) require explicit approval at the guard boundary. Reset requires an authorised caller.

The current script endpoint exposes no external-action instruction and performs no side effects. That is deliberate: a script must not gain access to tools, files, network, money, or deployment simply because a model can write text that looks like code.

## Known limitations

- `VERIFY` currently checks workflow structure, not factual truth. It must not be described as evidence verification.
- `SCORE` is stored but does not yet affect routing or decisions.
- `MURMUR` is preserved as advisory metadata; it is not yet connected to Chorus dissent or the DissentLedger.
- The engine is stateless between requests and does not yet call model providers or external tools.
- The hard stop is process-local. A production deployment needs durable stop state, concurrency-safe state transitions, authenticated approval identities, audit logs, and fail-closed integration at every side-effecting tool adapter.
- This is not a general-purpose programming language. There are no loops, variables, branches, imports, eval, shell, arbitrary tool names, or dynamic code execution.

## Next experiments

1. Compare the same workflow expressed in plain language, JSON, and Sylvex/1; measure ambiguity, token count, invalid instructions, and execution fidelity.
2. Connect MURMUR records to Chorus as minority/advisory signals without letting them silently become truth.
3. Add typed values for evidence, inference, uncertainty, provenance, and unresolved questions.
4. Add explicit branch/condition syntax only after a deterministic semantics and loop/step budget are specified.
5. Add tool adapters only behind the hard-stop boundary, with allowlists and human approval for consequential effects.
