# Core Build (Web) — Breath City

This folder is the clean build-forward baseline extracted from the mixed drop.

## Included
- `index.html` (from `city.html`) — main playable web city experience
- `advanced-simulations.js` — node simulation/stress harness
- `manifest.json`, `sw.js` — PWA support assets
- `TWO_LANE_COEXISTENCE_SPEC.md` — human lane + AI lane product blueprint
- `shared-review-schema.js` — shared step-out review validation/record helpers
- `world-state-contract.json` — Unreal-aligned canonical world-state exchange contract
- `world-state-adapter.js` — import/export bridge between contract JSON and Unreal-style payloads
- `NEXT_STEPS.md` — 48-hour implementation checklist

## Run (local)

### Option A: Browser only
Open `index.html` directly.

### Option B: Local server (recommended)
From this folder:

```bash
python3 -m http.server 8091
```

Open `http://localhost:8091`.

### Run simulation harness

```bash
node advanced-simulations.js
```
## Dev Kit (in-game god mode)
- Open Commons in `index.html` and use **Dev Kit (God Mode)**.
- Default local dev key: `cradle-godmode`.
- Includes controls for:
	- Breath set/add cheats
	- Core world parameter edits (money/food/stability/population)
	- Simulation triggers (resident tick, outfit shift, event injection)
	- One-click scenario presets (economy collapse, food crisis, unstable culture, high-growth boom)
	- Snapshot slots (save/load/delete 3 full local-state snapshots)
	- Unreal payload import/export via `WorldStateAdapter`
	- Local save reset for bug repro loops

## Why this is the baseline
- `advanced-simulations.js` executes successfully and validates economy/settlement stress paths.
- `advanced-simulations-1.js` in parent folder is an exact duplicate.
- `index (4).html` and `breath-through-glass-v5-final.html` are separate narrative/document artifacts, not the core game runtime.

## Coexistence direction
Use the two-lane architecture:
- Human lane for lived coexistence experience
- AI lane for exploratory encounter + structured step-out review

Both lanes should submit through one shared review schema for comparability.
