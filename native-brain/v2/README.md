# Sylvex Brain v2 — THE CHORUS

This directory contains an isolated experimental implementation. It is not the production Brain.

## Execution path

POST /api/chorus → Voice.receive → 78 tissue units → nine organ positions → Chorus routing/weighting/dissent checks → response.

By default all units are deterministic placeholders. They are not independent language models.

## Sylvex scripting and hard stop

This branch adds a bounded declarative interpreter, SYLVEX/1, with:
- POST /api/script/compile — validates a script and returns canonical JSON intermediate representation (IR).
- POST /api/script — runs a side-effect-free script and returns its trace.
- A process-local latched hard-stop guard shared across requests by the ScriptEngine.
- Typed EVIDENCE, INFERENCE, UNCERTAINTY and SOURCE statements.
- MURMUR records preserved in the same in-memory ledger used by Chorus dissent.

The language supports OBSERVE, EVIDENCE, INFERENCE, UNCERTAINTY, SOURCE, SCORE, MURMUR, INTEGRATE, VERIFY, RESPOND and STOP. It cannot execute arbitrary code, tools, shell commands, network requests, or file operations.

Important limitations:
- VERIFY checks workflow preconditions only, not factual truth.
- SCORE is recorded but does not yet affect Chorus routing or decisions.
- MURMUR is advisory and unresolved; it is not a fact or an automatic veto.
- The hard stop is process-local and is lost on restart. Production use requires durable shared state, concurrency-safe transitions and authenticated human approval.
- No multi-model interoperability runs have been performed. The experiment protocol and synthetic fixtures are in experiments/sylvex_interop/.

See SYLVEX_SCRIPTING.md for grammar and safety limits.

## Example request

POST /api/script/compile

{
  "script": "SYLVEX/1\\nOBSERVE hello\\nEVIDENCE The log says ready.\\nSOURCE build.log line 2\\nINTEGRATE\\nVERIFY\\nRESPOND noted"
}

## Optional model-backed Verbalizer

One tissue, Verbalizer, can be connected to an OpenAI-compatible /chat/completions endpoint. It is disabled unless all required configuration is supplied:

- SYLVEX_MODEL_BASE_URL: API base URL, usually ending in /v1
- SYLVEX_MODEL_NAME: model identifier
- SYLVEX_MODEL_API_KEY: optional for local endpoints; required by most hosted providers

Set these as runtime environment variables, never in source code or committed files. No provider request is made in deterministic-only mode.

The adapter bounds input to 8,000 characters, uses a 20-second timeout, requests a compact JSON assessment, validates its value/confidence, and records provider errors explicitly. It does not silently pretend a failed provider call succeeded. The budget reserves one additional call and an input-size-based token allowance before processing.

For the deliberator organ, a successful provider-backed Verbalizer output is selected as the organ's position instead of being outvoted by eight placeholder outputs. All per-unit outputs remain in the trace. This is an explicit experimental policy, not a claim that the model is correct; evaluate it against baselines.

## Run and test

From the repository root:

pip install -r native-brain/v2/requirements.txt
uvicorn v2.app:app --app-dir native-brain --host 127.0.0.1 --port 8000
python -m pytest native-brain/v2/test_chorus.py native-brain/v2/test_guard_script.py

A GitHub Actions workflow now runs the Chorus and Sylvex test suites on branch pushes and pull requests. The tests have not yet been executed in this environment.

Check GET /health for provider mode, unresolved ledger count and hard-stop state; use POST /api/script/compile before POST /api/script when an agent-generated script needs review. This rebuild remains experimental and is not production-ready.
