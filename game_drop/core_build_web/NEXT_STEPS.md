# Immediate Next Steps (48-hour execution)

## 1) Add lane chooser to UI
- Add a lightweight start modal:
  - `Enter Human Lane`
  - `Enter AI Lane`
- Store selection in localStorage: `coexistence_lane`.

## 2) Attach shared review schema
- Include `shared-review-schema.js` in `index.html`.
- On submit, call `SharedReviewSchema.buildReviewRecord(formData)`.
- Block submit if validation fails.

## 3) Add grounded-vs-imagined field
- Add a short text area in review form:
  - "Grounded vs imagined (optional but encouraged)"

## 4) Save lane-tagged review records
- Save locally (MVP): `localStorage.reviews` array.
- Include `lane` + `created_at` + `schema_version`.

## 5) Add mini analytics panel
- Show counts:
  - total reviews
  - human vs ai submissions
  - reviews with grounded-vs-imagined labeling

## 6) Keep simulation regression check
- Run `node advanced-simulations.js` before major UI changes.
