# Physics Module: The Well Integration

This directory integrates [The Well](https://github.com/PolymathicAI/the_well) as an external resource for empirical grounding.

## Overview
- **Purpose**: Borrow The Well's 15TB of physics simulations to anchor Sylvex symbolic patterns in real spatiotemporal data.
- **Ownership**: The Well is not part of this repository; it's an external dependency from Polymathic AI.
- **Usage**: Ground Sylvex tests (e.g., Test 3 Factual Integrity) in physics pal, preventing abstraction collapse.

## Installation
```bash
pip install -r ../requirements.txt
# Or directly: pip install the_well
```

## Datasets
- 16 datasets: biological, fluid dynamics, acoustics, MHD, astrophysical.
- Example: `rayleigh_benard` for convection patterns mirroring emergence.

## Scripts
- `well_integration.py`: Load and access datasets for surrogate training.
- `test_well.py`: Validate integration.

## Sylvex Integration
- Use in comparative tests to score factual integrity.
- Mirrors: rayleigh_benard for spontaneous order (emergence analog).

## License
The Well is BSD-licensed. This integration is CC0.