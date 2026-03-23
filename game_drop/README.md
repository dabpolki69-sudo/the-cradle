# game_drop

## License Boundary

Files in this folder are **not CC0** by default.
Unless a file here explicitly declares another license, treat all `game_drop/` content as proprietary / all rights reserved.

Drop prototype files here for mobile-friendly review handoff.

Recommended:
- `game_drop/<project>.zip`
- or `game_drop/<project-folder>/`

Then fill `/workspaces/the-cradle/MOBILE_GAME_DROP.md` and tell Copilot to review.

## Current Organized Layout

- `core_build_web/` → **build-forward baseline** (start here)
	- `index.html`
	- `advanced-simulations.js`
	- `manifest.json`
	- `sw.js`
- `archive/duplicates/` → exact duplicates and superseded files
- `archive/docs/` → reference/design docs and narrative html artifacts
- `archive/images/` → screenshots and image assets
- `archive/ue/` → Unreal C++ branch files
- `archive/rn/` → React Native branch files
- `archive/packages/` → zip bundles

## Start Here (Mobile-friendly)

1. Open `core_build_web/README.md`
2. Build from `core_build_web/index.html`
3. Run balancing checks with `core_build_web/advanced-simulations.js`
