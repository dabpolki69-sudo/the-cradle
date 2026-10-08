# Sylvex Brain v2 — handoff

## Scope
This branch is `sylvex-brain-rebuild`. The main branch is intentionally untouched because Claude is working there.

## Architecture
The authoritative design is THE CHORUS: one Voice, nine parallel organs, 78 tissue units. Voice senses, presents, weighs and speaks. Organs are cooperative perspectives, not competing agents. Tissue is mostly cheap prediction; only Verbalizer and Hallucination-Sniffer use language.

## Implemented
- `chorus.py`: 9 organs, 78 tissue units, routing, weighted positions, dissent detection, reliability update.
- `tissue.py`: replaceable reflex tissue boundary.
- `voice.py`: Voice orchestration boundary, budget and dissent ledger.
- `economy.py`: surprise/energy/stakes and token/call/reflex budgets.
- `ledger.py`: persistent-in-memory dissent record structure.
- `substrates.py`: provider-neutral substrate registry plus Hugging Face adapter.
- `multiplier.py`: initial Multiplier Test scoring harness and H1 integration calculation.
- `CHORUS.md`: architecture reference.
- `test_chorus.py`: structural tests.

## Important limitation
The current tissue implementation is deliberately a deterministic placeholder. It is NOT evidence that the 78 units are independent intelligent processes. The next layer should connect real substrates to selected tissue/organ roles and preserve compute matching.

## Hugging Face
HF should be treated as a substrate laboratory: small models for cheap tissue, larger models for organs/deliberation, and independent open-weight architectural experiments. The architecture must remain provider-neutral.

## Experimental law
Nothing earns architectural permanence merely because it sounds plausible. Components should justify their cost through surprise, energy and stakes.

## Next tests
1. import/structural tests
2. routing invariants
3. dissent-ledger tests
4. budget accounting
5. substrate adapter tests with a mock client
6. API integration
7. Multiplier Test arms A0–A7
8. local run before any Render deployment
