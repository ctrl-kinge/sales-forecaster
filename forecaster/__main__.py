"""Evaluate all models on the real daily revenue series.

Two protocols:
1. Legacy 28-day single holdout (Phases 2a-2c) — kept for comparison.
2. Rolling-origin backtest at a 7-day horizon (Phase 2d) — the headline.
   Re-fit weekly, forecast one week out; lag-7 is legal here.

Usage: python -m forecaster [test_days]
"""
import sys

from forecaster.backtest import backtest
from forecaster.baselines import moving_average, naive_last, seasonal_naive
from forecaster.data import load_raw
from forecaster.metrics import score_forecasts
from forecaster.models import lag_regression_forecast, regression_forecast
from forecaster.prep import clean_sales, daily_revenue
from forecaster.split import split_train_test


def holdout_eval(series, test_days: int) -> None:
    train, test = split_train_test(series, test_days)
    horizon = len(test)

    forecasts = {
        "naive_last": naive_last(train, horizon),
        "moving_average_7d": moving_average(train, horizon, window=7),
        "seasonal_naive_7d": seasonal_naive(train, horizon, season=7),
        "regression_calendar": regression_forecast(train, horizon),
        "regression_lags_28_35": lag_regression_forecast(train, horizon),
    }
    # score against the same index as the test set
    forecasts = {name: fc.set_axis(test.index) for name, fc in forecasts.items()}

    print(f"=== Single holdout: last {horizon} days ===")
    print(f"Train: {train.index[0].date()} .. {train.index[-1].date()} ({len(train)} days)")
    print(f"Test:  {test.index[0].date()} .. {test.index[-1].date()} ({horizon} days)\n")
    print(score_forecasts(test, forecasts).round(0).to_string())


def rolling_eval(series, horizon: int = 7, n_folds: int = 8) -> None:
    models = {
        "naive_last": naive_last,
        "moving_average_7d": lambda tr, h: moving_average(tr, h, window=7),
        "seasonal_naive_7d": lambda tr, h: seasonal_naive(tr, h, season=7),
        "regression_calendar": regression_forecast,
        "regression_lags_7_14_28": lambda tr, h: lag_regression_forecast(tr, h, lags=(7, 14, 28)),
    }
    result = backtest(series, models, horizon=horizon, n_folds=n_folds)

    print(f"\n=== Rolling origin: {n_folds} folds x {horizon}-day horizon ===")
    print(f"Test span: last {n_folds * horizon} days, origin advancing weekly\n")
    print(result.round(0).sort_values("MAE").to_string())


def main(test_days: int = 28) -> None:
    series = daily_revenue(clean_sales(load_raw()))
    holdout_eval(series, test_days)
    rolling_eval(series)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 28)
