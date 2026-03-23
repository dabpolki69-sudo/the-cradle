# Game Drop Triage — Keep / Build / Archive

Date: 2026-03-23

## Verdict
**KEEP and BUILD** (do not ditch).

There is a runnable core with clear value:
- emergent citizen economy loops
- autonomous resident tick behavior
- persistence via localStorage
- executable stress simulation harness

## Canonical Build Path (use this now)
Use:
- `game_drop/core_build_web/index.html`
- `game_drop/core_build_web/advanced-simulations.js`

This is the cleaned baseline extracted from the mixed drop.

## Evidence of viability
- `advanced-simulations.js` executes successfully via Node.
- `advanced-simulations-1.js` is an exact duplicate of `advanced-simulations.js`.
- `city.html` contains substantial gameplay systems (economy, jobs, residents, debate, events, fishing/garden loops).

## What to treat as secondary/reference
- `App-Enhanced.js`, `App-Premium.js` (React Native branch; useful later, but separate runtime)
- `BP_WorldStateSubsystem.*`, `ST_WorldData.h`, `installation_guide.txt` (Unreal branch; separate stack)
- `breath-through-glass-v5-final.html`, `index (4).html` (narrative/web-doc artifacts)

## What to archive (low immediate build value)
- `advanced-simulations-1.js` (duplicate)
- `files.zip` (contains old index/readme pair)
- non-game/patent/thesis docs if your next milestone is playable build only

## Recommended 72-hour plan
1. Ship a playable web slice from `core_build_web/index.html`.
2. Keep simulation harness (`advanced-simulations.js`) as your balancing regression check.
3. Add one explicit "Step Out / Review" screen in the web game that captures:
   - what emerged,
   - uncertainty,
   - standout patterns,
   - grounded vs imagined.
4. Freeze feature scope until this loop feels good.

## Notes
`game_drop/` is proprietary/all-rights-reserved by default unless file-level license says otherwise.
