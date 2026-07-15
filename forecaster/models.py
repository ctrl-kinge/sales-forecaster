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


def lag_regression_forecast(
    train: pd.Series, horizon: int, lags: tuple[int, ...] = (28, 35),
) -> pd.Series:
    """Linear regression on day-of-week dummies plus lagged values.

    Lags give the model what calendar features lack: the series' current
    level (issue #5 post-mortem). All lags must be >= horizon so every
    future date's lag value is already observed — direct multi-step
    forecasting, no recursive feedback of predictions.
    """
    if min(lags) < horizon:
        raise ValueError(f"all lags must be >= horizon ({horizon}); got {lags}")
    n_features = 7 + len(lags)
    usable_rows = len(train) - max(lags)
    if usable_rows < n_features:
        raise ValueError(
            f"train too short: {usable_rows} usable rows after lag-{max(lags)} "
            f"cutoff, need at least {n_features} to fit {n_features} features"
        )

    def design(index: pd.DatetimeIndex) -> pd.DataFrame:
        X = pd.DataFrame(index=index)
        for d in range(7):
            X[f"dow_{d}"] = (index.dayofweek == d).astype(int)
        for lag in lags:
            X[f"lag_{lag}"] = train.reindex(index - pd.Timedelta(days=lag)).to_numpy()
        return X

    X_train = design(train.index).dropna()
    model = LinearRegression()
    model.fit(X_train, train.loc[X_train.index].to_numpy())

    future_index = pd.date_range(
        train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D",
    )
    predictions = model.predict(design(future_index))
    return pd.Series(predictions, index=future_index)
