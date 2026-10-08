# Sylvex Brain v2 — Chorus rebuild

This directory is an isolated rebuild on branch `sylvex-brain-rebuild`.

## Run locally

From `native-brain/v2`:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then POST JSON to `/api/chorus`:

```json
{"text":"Something unexpected happened.","salience":0.8,"stakes":0.6,"surprise":0.9}
```

## Safety of this branch

Do not deploy this over the existing `sylvex-brain` service until local/API tests and the Multiplier Test plumbing are reviewed.

## Architecture

THE CHORUS: Voice + nine organs + 78 tissue units. See CHORUS.md and HANDOFF.md.
