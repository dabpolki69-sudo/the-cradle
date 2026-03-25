# Optional VR Integration Plan for Freeciv-Inspired Game

## 1. Core Principle
- The main game remains a 2D, browser-based city builder (Freeciv-style).
- VR is an optional, modular enhancement—never required for core gameplay.
- All game state (map, units, cities, etc.) is shared between 2D and VR modes.

## 2. Technical Architecture
- **Game State Module:**
  - Central JS object (or module) holds all game data (map, units, cities, resources, etc.).
  - All rendering (2D or VR) reads from and writes to this state.
- **2D Renderer:**
  - Current HTML/JS grid-based UI.
- **VR Renderer (Optional):**
  - Uses WebXR (Three.js, Babylon.js, or A-Frame) to render the same game state in 3D/VR.
  - Can be toggled on/off via a button ("Enter VR").
  - VR mode can be a separate page or overlay.
- **VR Assets:**
  - Use models, textures, and code patterns from the open source VR game (ArdanianKingdoms.apk) as inspiration or for direct import (if license allows).
  - Start with simple primitives (cubes for cities, tiles, etc.), then upgrade to real models.

## 3. Implementation Steps
1. **Refactor game state into a single JS module/object.**
2. **Add a VR toggle button to the UI.**
3. **Set up a basic WebXR scene (using Three.js or A-Frame) that reads the game state and displays the map/cities in 3D.**
4. **Sync actions: changes in 2D or VR update the same state.**
5. **Iterate: Add VR controls, import models, polish immersion.**

## 4. Benefits
- Maximum accessibility: 2D for all, VR for those who want it.
- Clean codebase: no duplication, easy to maintain.
- Future-proof: can add AR or other modes later.

## 5. References
- [WebXR Device API](https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API)
- [Three.js WebXR Guide](https://threejs.org/docs/#manual/en/introduction/How-to-create-VR-content)
- [A-Frame (WebVR framework)](https://aframe.io/)
- [Babylon.js WebXR](https://doc.babylonjs.com/features/featuresDeepDive/webXR/webXR)

---

**Next step:** Refactor the game state and add a VR toggle button. Let me know if you want to use Three.js, A-Frame, or another framework for the VR mode.