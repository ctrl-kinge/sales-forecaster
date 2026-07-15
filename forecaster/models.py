"""Trained forecasting models.

regression_forecast fits a linear model on calendar features — it can
express "Mondays are low, Decembers are high, revenue drifts upward"
but nothing the calendar doesn't encode. Judged against the baselines
on the same harness (see `python -m forecaster`).
"""
import pandas as pd
from sklearn.linear_model import LinearRegression

from forecaster.features import make_calendar_features


def regression_forecast(train: pd.Series, horizon: int) -> pd.Series:
    """Fit linear regression on calendar features; predict the next `horizon` days."""
    model = LinearRegression()
    model.fit(make_calendar_features(train.index), train.to_numpy())

    future_index = pd.date_range(
        train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D",
    )
    predictions = model.predict(make_calendar_features(future_index))
    return pd.Series(predictions, index=future_index)
