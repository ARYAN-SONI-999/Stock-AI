# ML PIPELINE

Current baseline establishes model registry and metrics schema so all future model training can be versioned and tracked.

Implemented backend pipeline modules in `/home/runner/work/Stock-AI/Stock-AI/apps/api/app/services/ml_pipeline`:
- `data_quality.py`: data cleaning, missing/invalid row filtering, outlier clamping, split/dividend adjustment, freshness + source reliability scoring.
- `features.py`: leakage-safe feature rows with multi-timeframe trend, momentum, volatility, volume pressure, market context, and event-aligned sentiment features.
- `models.py`: ensemble predictor (linear baseline + tree heuristic + sequence momentum), probability calibration, confidence gating, abstain mode, and explanation contributions.
- `validation.py`: strict walk-forward split builder for chronological train/validation/test windows.
- `evaluation.py`: directional accuracy, MAE/RMSE/MAPE, calibration error, and strategy risk metrics (max drawdown, Sharpe, hit ratio) with bucket-level evaluation.
- `monitoring.py`: prediction/outcome logging hooks, drift checks, and threshold-based performance alerts.
- `governance.py`: lightweight model registry and shadow→canary→production rollout controller.

API integration:
- `/api/v1/stocks/{symbol}/prediction` now provides calibrated confidence, abstain behavior, interval bounds, freshness, source reliability, regime, and explanation payload.
