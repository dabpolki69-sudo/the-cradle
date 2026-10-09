# Sylvex Brain v2 — THE CHORUS

This directory contains an isolated experimental implementation. It is not the production Brain.

## Execution path

`POST /api/chorus` → `Voice.receive` → 78 tissue units → nine organ positions → Chorus routing/weighting/dissent checks → response.

By default all units are deterministic placeholders. They are not independent language models.

## Optional model-backed Verbalizer

One tissue, `Verbalizer`, can be connected to an OpenAI-compatible `/chat/completions` endpoint. It is disabled unless all required configuration is supplied:

- `SYLVEX_MODEL_BASE_URL`: API base URL, usually ending in `/v1`
- `SYLVEX_MODEL_NAME`: model identifier
- `SYLVEX_MODEL_API_KEY`: optional for local endpoints; required by most hosted providers

Set these as runtime environment variables, never in source code or committed files. No provider request is made in deterministic-only mode.

The adapter bounds input to 8,000 characters, uses a 20-second timeout, requests a compact JSON assessment, validates its value/confidence, and records provider errors explicitly. It does not silently pretend a failed provider call succeeded. The budget reserves one additional call and an input-size-based token allowance before processing.

For the deliberator organ, a successful provider-backed Verbalizer output is selected as the organ's position instead of being outvoted by eight placeholder outputs. All per-unit outputs remain in the trace. This is an explicit experimental policy, not a claim that the model is correct; evaluate it against baselines.

## Run and test

From the repository root:

```bash
pip install -r native-brain/v2/requirements.txt
uvicorn v2.app:app --app-dir native-brain --host 127.0.0.1 --port 8000
python -m pytest native-brain/v2/test_chorus.py
```

Check `GET /health` for provider mode and `POST /api/chorus` for a traced response. This rebuild remains experimental and is not production-ready.
