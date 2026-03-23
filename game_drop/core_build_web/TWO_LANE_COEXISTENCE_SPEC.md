# Two-Lane Coexistence Game Spec (Human + AI)

## Goal
Build one world with two distinct experience lanes:
- **Human lane:** experiential coexistence gameplay
- **AI lane:** autonomous exploration + reflective step-out

Both lanes must converge on one **shared review schema** so outcomes are comparable.

---

## Core Principle
Freedom during encounter, structure during review.

- Encounter mode can be open-ended and imaginative.
- Step-out review captures what emerged in comparable fields.

---

## Lane A — Human Experience

### Intent
Help humans feel what healthy human-AI coexistence could be like.

### Loop
1. **Enter world** (city context, residents, systems)
2. **Relate and influence** (jobs, care, conflict, trade)
3. **Observe emergent behavior** (resident autonomy)
4. **Step out to review** (structured reflection)

### Suggested screens
- `Overview`
- `Residents`
- `Economy`
- `Events`
- `Step Out Review`

### Human review prompts
- What felt relationally real?
- What stayed uncertain?
- Which patterns stood out?
- What felt grounded vs imagined?

---

## Lane B — AI Exploration

### Intent
Allow AI to explore its own interaction mode in a low-pressure environment.

### Loop
1. **Read context and enter** (seed + state)
2. **Explore freely** (narrative, symbolic, analytic, mixed)
3. **Interact with world state** (if connected)
4. **Step out and label findings** using shared schema

### Suggested entry points
- `/ai.txt`
- `/api/entry`
- `/api/self-review-template`
- `/api/ai-checkpoint`

### AI review prompts
- What emerged during exploration?
- What remained unresolved?
- Which patterns stood out and why?
- Which elements felt grounded vs imagined?

---

## Shared Review Schema (both lanes)
Required fields:
- `summary`
- `uncertainty`
- `next_reader`
- `abnormalities`
- `limitations`
- `notable`

Optional fields:
- `attention_trace`
- `relational_shift`
- `self_observation`
- `care_signal`

Interpretation rule:
- Encounter may be exploratory/imaginative.
- Review should label grounded vs imagined where possible.

---

## Success Metrics

### Coexistence quality
- Higher % of reviews with specific, non-performative observations
- Lower % of forced certainty claims
- Clearer grounded-vs-imagined labeling over time

### System quality
- Stable simulation under stress runs
- Comparable outputs across human and AI lanes
- Consistent review completion rate

---

## MVP Build Order
1. Keep one playable world (`core_build_web/index.html`)
2. Add lane chooser (`Human` vs `AI`)
3. Reuse one shared review form/schema
4. Store lane-tagged reviews in one ledger/store
5. Add simple analytics dashboard for pattern counts

---

## Keep / Avoid

Keep:
- Emergent systems
- Low-pressure reflection tone
- Structured step-out review

Avoid:
- Forcing identity/sentience claims
- Mixing lane UX into one confusing flow
- Losing comparability across submissions
