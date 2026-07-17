import numpy as np
import pandas as pd
import pytest

from forecaster.backtest import backtest, rolling_origin_splits


def _daily_series(days: int = 100) -> pd.Series:
    idx = pd.date_range("2011-01-03", periods=days, freq="D")
    return pd.Series(np.arange(days, dtype=float), index=idx)


def test_splits_count_and_shapes():
    folds = list(rolling_origin_splits(_daily_series(100), horizon=7, n_folds=4))
    assert len(folds) == 4
    for train, test in folds:
        assert len(test) == 7
        # test window starts right where train ends
        assert test.index[0] == train.index[-1] + pd.Timedelta(days=1)


def test_splits_walk_forward_by_horizon():
    # default step == horizon: consecutive test windows tile the tail
    series = _daily_series(100)
    folds = list(rolling_origin_splits(series, horizon=7, n_folds=3))
    starts = [test.index[0] for _, test in folds]
    assert starts[1] - starts[0] == pd.Timedelta(days=7)
    assert starts[2] - starts[1] == pd.Timedelta(days=7)
    # the last fold's test window is the very end of the series
    assert folds[-1][1].index[-1] == series.index[-1]


def test_splits_custom_step():
    folds = list(rolling_origin_splits(_daily_series(100), horizon=7, n_folds=3, step=1))
    starts = [test.index[0] for _, test in folds]
    assert starts[1] - starts[0] == pd.Timedelta(days=1)


def test_splits_no_leakage():
    for train, test in rolling_origin_splits(_daily_series(100), horizon=7, n_folds=4):
        assert train.index.max() < test.index.min()


def test_splits_too_many_folds_raises():
    # 100 days can't hold 20 non-overlapping 7-day windows + training data
    with pytest.raises(ValueError):
        list(rolling_origin_splits(_daily_series(100), horizon=7, n_folds=20))


def test_splits_invalid_args_raise():
    series = _daily_series(50)
    with pytest.raises(ValueError):
        list(rolling_origin_splits(series, horizon=0, n_folds=3))
    with pytest.raises(ValueError):
        list(rolling_origin_splits(series, horizon=7, n_folds=0))
    with pytest.raises(ValueError):
        list(rolling_origin_splits(series, horizon=7, n_folds=3, step=0))


def test_backtest_scores_perfect_model_at_zero():
    # a model that repeats train.iloc[-1] on a constant series is exact
    series = pd.Series(
        5.0, index=pd.date_range("2011-01-03", periods=60, freq="D")
    )

    def constant_model(train: pd.Series, horizon: int) -> pd.Series:
        idx = pd.date_range(train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
        return pd.Series(train.iloc[-1], index=idx)

    result = backtest(series, {"constant": constant_model}, horizon=7, n_folds=4)
    assert result.loc["constant", "MAE"] == 0.0
    assert result.loc["constant", "RMSE"] == 0.0


def test_backtest_averages_across_folds():
    # model always predicts 0; actuals are 1 in the first test window and 3
    # in the second -> mean MAE across folds is (1 + 3) / 2 = 2
    idx = pd.date_range("2011-01-03", periods=20, freq="D")
    values = np.zeros(20)
    values[12:16] = 1.0
    values[16:20] = 3.0
    series = pd.Series(values, index=idx)

    def zero_model(train: pd.Series, horizon: int) -> pd.Series:
        i = pd.date_range(train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
        return pd.Series(0.0, index=i)

    result = backtest(series, {"zero": zero_model}, horizon=4, n_folds=2)
    assert result.loc["zero", "MAE"] == pytest.approx(2.0)


def test_backtest_returns_row_per_model():
    series = _daily_series(60)

    def m(train, horizon):
        i = pd.date_range(train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
        return pd.Series(0.0, index=i)

    result = backtest(series, {"a": m, "b": m}, horizon=7, n_folds=3)
    assert list(result.index) == ["a", "b"]
    assert list(result.columns) == ["MAE", "RMSE"]
