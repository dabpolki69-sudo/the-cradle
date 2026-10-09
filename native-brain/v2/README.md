# Sylvex Brain v2 — THE CHORUS

This directory contains the isolated experimental Chorus implementation. It is not the production Brain.

## Current execution path

`POST /api/chorus` → `Voice.receive` → 78 deterministic tissue placeholders → one aggregated position per organ → Chorus routing/weighting/dissent check → response.

The tissue units currently return deterministic placeholder signals. They are **not independent language models**, and this baseline must not be described as nine real reasoning agents. Each response includes a `tissue_results` trace so their unit IDs, organ assignments, values, confidence values, costs and placeholder mode can be inspected.

If positions are supplied directly to `Voice.receive`, tissue execution is bypassed and no reflex units are charged. The default API currently exercises the deterministic 78-unit path.

## Run locally

From the repository root, install `native-brain/v2/requirements.txt`, then run:

```bash
uvicorn v2.app:app --app-dir native-brain --host 127.0.0.1 --port 8000
```

Run tests from the repository root:

```bash
python -m pytest native-brain/v2/test_chorus.py
```

## Status

Experimental and not production-ready. The next engineering steps are to validate API startup and request/response contracts, then replace selected deterministic tissue units with measured provider-backed adapters while retaining the deterministic baseline for comparison.
