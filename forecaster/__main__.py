"""Evaluate baseline models on the real daily revenue series.

Usage: python -m forecaster [test_days]
"""
import sys

from forecaster.baselines import moving_average, naive_last, seasonal_naive
from forecaster.data import load_raw
from forecaster.metrics import score_forecasts
from forecaster.models import lag_regression_forecast, regression_forecast
from forecaster.prep import clean_sales, daily_revenue
from forecaster.split import split_train_test


def main(test_days: int = 28) -> None:
    series = daily_revenue(clean_sales(load_raw()))
    train, test = split_train_test(series, test_days)
    horizon = len(test)

    forecasts = {
        "naive_last": naive_last(train, horizon),
        "moving_average_7d": moving_average(train, horizon, window=7),
        "seasonal_naive_7d": seasonal_naive(train, horizon, season=7),
        "regression_calendar": regression_forecast(train, horizon),
        "regression_lags": lag_regression_forecast(train, horizon),
    }
    # score against the same index as the test set
    forecasts = {name: fc.set_axis(test.index) for name, fc in forecasts.items()}

    print(f"Train: {train.index[0].date()} .. {train.index[-1].date()} ({len(train)} days)")
    print(f"Test:  {test.index[0].date()} .. {test.index[-1].date()} ({horizon} days)\n")
    print(score_forecasts(test, forecasts).round(0).to_string())


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 28)
