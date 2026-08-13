from __future__ import annotations

from math import sqrt


def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def regression_metrics(actual: list[float], pred: list[float]) -> dict[str, float]:
    if not actual or len(actual) != len(pred):
        return {"mae": 0.0, "rmse": 0.0, "mape": 0.0}

    errors = [abs(a - p) for a, p in zip(actual, pred, strict=True)]
    mae = sum(errors) / len(errors)
    rmse = sqrt(sum((a - p) ** 2 for a, p in zip(actual, pred, strict=True)) / len(actual))
    mape = sum(abs((a - p) / a) for a, p in zip(actual, pred, strict=True) if a != 0) / max(1, len(actual))
    return {"mae": round(mae, 6), "rmse": round(rmse, 6), "mape": round(mape, 6)}


def directional_accuracy(actual_next: list[float], pred_next: list[float], base: list[float]) -> float:
    if not (len(actual_next) == len(pred_next) == len(base)) or not actual_next:
        return 0.0

    hits = 0
    for a, p, b in zip(actual_next, pred_next, base, strict=True):
        actual_up = a >= b
        pred_up = p >= b
        if actual_up == pred_up:
            hits += 1
    return round(hits / len(actual_next), 6)


def calibration_error(prob_up: list[float], actual_up: list[int]) -> float:
    if not prob_up or len(prob_up) != len(actual_up):
        return 0.0

    bins = {i: {"p": [], "y": []} for i in range(10)}
    for p, y in zip(prob_up, actual_up, strict=True):
        idx = min(9, max(0, int(p * 10)))
        bins[idx]["p"].append(p)
        bins[idx]["y"].append(y)

    ece = 0.0
    n = len(prob_up)
    for bucket in bins.values():
        if not bucket["p"]:
            continue
        conf = sum(bucket["p"]) / len(bucket["p"])
        acc = sum(bucket["y"]) / len(bucket["y"])
        ece += (len(bucket["p"]) / n) * abs(conf - acc)

    return round(ece, 6)


def strategy_risk_metrics(returns: list[float]) -> dict[str, float]:
    if not returns:
        return {"max_drawdown": 0.0, "sharpe": 0.0, "hit_ratio": 0.0}

    cumulative = []
    value = 1.0
    for r in returns:
        value *= 1 + r
        cumulative.append(value)

    peak = cumulative[0]
    max_drawdown = 0.0
    for v in cumulative:
        peak = max(peak, v)
        drawdown = _safe_div(peak - v, peak)
        max_drawdown = max(max_drawdown, drawdown)

    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / max(1, len(returns) - 1)
    sharpe = _safe_div(mean_ret, sqrt(variance)) * sqrt(252) if variance > 0 else 0.0
    hit_ratio = sum(1 for r in returns if r > 0) / len(returns)

    return {
        "max_drawdown": round(max_drawdown, 6),
        "sharpe": round(sharpe, 6),
        "hit_ratio": round(hit_ratio, 6),
    }


def evaluate_buckets(records: list[dict], bucket_field: str) -> dict[str, dict[str, float]]:
    buckets: dict[str, dict[str, list[float]]] = {}
    for rec in records:
        key = str(rec.get(bucket_field, "unknown"))
        if key not in buckets:
            buckets[key] = {"actual": [], "pred": [], "base": [], "prob": [], "actual_up": [], "returns": []}

        buckets[key]["actual"].append(float(rec.get("actual_price", 0.0)))
        buckets[key]["pred"].append(float(rec.get("pred_price", 0.0)))
        buckets[key]["base"].append(float(rec.get("base_price", 0.0)))
        buckets[key]["prob"].append(float(rec.get("probability_up", 0.5)))
        buckets[key]["actual_up"].append(1 if rec.get("directional_hit") else 0)
        buckets[key]["returns"].append(float(rec.get("strategy_return", 0.0)))

    out: dict[str, dict[str, float]] = {}
    for key, values in buckets.items():
        reg = regression_metrics(values["actual"], values["pred"])
        out[key] = {
            **reg,
            "directional_accuracy": directional_accuracy(values["actual"], values["pred"], values["base"]),
            "calibration_error": calibration_error(values["prob"], values["actual_up"]),
            **strategy_risk_metrics(values["returns"]),
        }

    return out
