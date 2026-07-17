"""Rolling-origin (walk-forward) backtesting.

A single holdout window lets one weird month decide the whole
leaderboard, and forcing a 28-day horizon makes every horizon-safe lag
stale (issue #7 post-mortem). Rolling the forecast origin forward
scores each model over many short windows instead — the operationally
realistic setup, where a model is re-fit every week and only ever asked
to look `horizon` days ahead.
"""
from collections.abc import Callable, Iterator

import pandas as pd

from forecaster.metrics import mae, rmse

Model = Callable[[pd.Series, int], pd.Series]


def rolling_origin_splits(
    series: pd.Series, horizon: int, n_folds: int, step: int | None = None,
) -> Iterator[tuple[pd.Series, pd.Series]]:
    """Yield (train, test) folds with the forecast origin rolling forward.

    The last fold's test window is the final `horizon` observations; each
    earlier fold moves the origin back by `step` days (default: `horizon`,
    so the test windows tile the tail of the series without overlap).
    Folds are yielded oldest origin first.
    """
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    if n_folds <= 0:
        raise ValueError("n_folds must be positive")
    step = horizon if step is None else step
    if step <= 0:
        raise ValueError("step must be positive")

    span = horizon + (n_folds - 1) * step
    if span >= len(series):
        raise ValueError(
            f"{n_folds} folds of horizon {horizon} (step {step}) need {span} "
            f"test days, leaving no training data in a {len(series)}-day series"
        )

    for i in range(n_folds):
        test_end = len(series) - (n_folds - 1 - i) * step
        test = series.iloc[test_end - horizon:test_end]
        train = series.iloc[:test_end - horizon]
        yield train, test


def backtest(
    series: pd.Series,
    models: dict[str, Model],
    horizon: int,
    n_folds: int,
    step: int | None = None,
) -> pd.DataFrame:
    """Score each model across all folds; return mean MAE/RMSE per model.

    Every model sees exactly the same folds, so the resulting table is a
    fair leaderboard. A model is any (train, horizon) -> forecast Series
    callable — baselines and trained models plug in identically.
    """
    scores: dict[str, dict[str, list[float]]] = {
        name: {"MAE": [], "RMSE": []} for name in models
    }
    for train, test in rolling_origin_splits(series, horizon, n_folds, step):
        for name, model in models.items():
            forecast = model(train, horizon).set_axis(test.index)
            scores[name]["MAE"].append(mae(test, forecast))
            scores[name]["RMSE"].append(rmse(test, forecast))

    rows = {
        name: {metric: sum(vals) / len(vals) for metric, vals in folds.items()}
        for name, folds in scores.items()
    }
    return pd.DataFrame.from_dict(rows, orient="index")[["MAE", "RMSE"]]
