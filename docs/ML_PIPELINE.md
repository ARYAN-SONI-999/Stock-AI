# ML PIPELINE

Current baseline establishes model registry and metrics schema so all future model training can be versioned and tracked.

Planned next additions:
- Leakage-safe feature generation in `ml/features`
- Walk-forward training/evaluation modules in `ml/training` and `ml/evaluation`
- Prediction logging and outcome tracking aligned to `predictions` + `prediction_outcomes`
