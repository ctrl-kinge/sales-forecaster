"""Export backtest results as JSON for the dashboard.

`python -m forecaster.export` runs the same 8-fold x 7-day rolling
backtest as `python -m forecaster` and writes three files into
`dashboard/data/`: leaderboard.json, folds.json, meta.json. The
dashboard imports them at build time — the JSON contract here is
mirrored by dashboard/lib/types.ts.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from forecaster.backtest import rolling_origin_splits
from forecaster.baselines import moving_average, naive_last, seasonal_naive
from forecaster.metrics import mae, rmse
from forecaster.models import lag_regression_forecast, regression_forecast

# name -> (human label, forecast fn, one-line story for the leaderboard card)
MODELS = {
    "seasonal_naive_7d": (
        "Seasonal naive (7d)",
        lambda tr, h: seasonal_naive(tr, h, season=7),
        "Copies last week day-for-day — an implicit lag-7 coefficient of "
        "exactly 1.0, which this series rewards.",
    ),
    "regression_lags_7_14_28": (
        "Lag regression (7/14/28)",
        lambda tr, h: lag_regression_forecast(tr, h, lags=(7, 14, 28)),
        "Sees recent levels, but least squares shrinks the lag weights and "
        "under-reacts to the holiday ramp.",
    ),
    "regression_calendar": (
        "Calendar regression",
        regression_forecast,
        "Knows weekdays and months, but can't see the series' current "
        "level at all.",
    ),
    "naive_last": (
        "Naive last-value",
        naive_last,
        "Repeats yesterday forever — flat lines through a weekly cycle.",
    ),
    "moving_average_7d": (
        "Moving average (7d)",
        lambda tr, h: moving_average(tr, h, window=7),
        "Smooths the weekly cycle away instead of exploiting it.",
    ),
}


def _points(series: pd.Series) -> list[dict]:
    return [
        {"date": ts.date().isoformat(), "value": round(float(v), 2)}
        for ts, v in series.items()
    ]


def build_folds(series: pd.Series, horizon: int, n_folds: int) -> list[dict]:
    """One dict per fold: actuals, every model's forecast, per-fold scores."""
    folds = []
    for i, (train, test) in enumerate(
        rolling_origin_splits(series, horizon, n_folds), start=1
    ):
        forecasts = {
            name: fn(train, horizon).set_axis(test.index)
            for name, (_, fn, _) in MODELS.items()
        }
        folds.append({
            "fold": i,
            "start": test.index[0].date().isoformat(),
            "end": test.index[-1].date().isoformat(),
            "actual": _points(test),
            "forecasts": {name: _points(fc) for name, fc in forecasts.items()},
            "scores": {
                name: {
                    "mae": round(mae(test, fc), 2),
                    "rmse": round(rmse(test, fc), 2),
                }
                for name, fc in forecasts.items()
            },
        })
    return folds


def build_leaderboard(folds: list[dict]) -> list[dict]:
    """Mean MAE/RMSE per model across folds, sorted best-first; one champion."""
    rows = []
    for name, (label, _, blurb) in MODELS.items():
        rows.append({
            "model": name,
            "label": label,
            "blurb": blurb,
            "mae": round(
                sum(f["scores"][name]["mae"] for f in folds) / len(folds), 2
            ),
            "rmse": round(
                sum(f["scores"][name]["rmse"] for f in folds) / len(folds), 2
            ),
        })
    rows.sort(key=lambda r: r["mae"])
    for i, row in enumerate(rows):
        row["champion"] = i == 0
    return rows


def build_meta(series: pd.Series, horizon: int, n_folds: int) -> dict:
    return {
        "dataset": "UCI Online Retail — daily revenue (GBP)",
        "protocol": (
            f"Rolling-origin backtest: {n_folds} folds x {horizon}-day "
            "horizon, origin advancing weekly, models re-fit per fold."
        ),
        "horizon": horizon,
        "n_folds": n_folds,
        "train_start": series.index[0].date().isoformat(),
        "train_end": series.index[-1].date().isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main(
    out_dir: Path,
    series: pd.Series | None = None,
    horizon: int = 7,
    n_folds: int = 8,
) -> None:
    if series is None:
        from forecaster.data import load_raw
        from forecaster.prep import clean_sales, daily_revenue

        series = daily_revenue(clean_sales(load_raw()))

    folds = build_folds(series, horizon, n_folds)
    payloads = {
        "folds": folds,
        "leaderboard": build_leaderboard(folds),
        "meta": build_meta(series, horizon, n_folds),
    }
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"wrote {path}")


if __name__ == "__main__":
    main(out_dir=Path(__file__).resolve().parent.parent / "dashboard" / "data")
