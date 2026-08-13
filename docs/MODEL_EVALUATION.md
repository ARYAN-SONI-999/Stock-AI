# MODEL EVALUATION

The platform avoids fixed/guaranteed accuracy claims.

Evaluation must be out-of-sample with chronological validation (walk-forward/rolling windows). Metrics to track include directional accuracy, MAE/RMSE/MAPE, calibration, and strategy-level risk metrics.

The current backend evaluation module (`/home/runner/work/Stock-AI/Stock-AI/apps/api/app/services/ml_pipeline/evaluation.py`) computes:
- Directional accuracy
- MAE / RMSE / MAPE
- Calibration error (bucketed expected calibration error)
- Strategy risk metrics (max drawdown, Sharpe, hit ratio)
- Bucket-level breakdowns (e.g., symbol/sector/regime/volatility bucket)
