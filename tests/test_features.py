import pandas as pd

from forecaster.features import make_calendar_features


def test_one_row_per_date():
    idx = pd.date_range("2011-01-03", periods=14, freq="D")
    X = make_calendar_features(idx)
    assert len(X) == 14
    assert list(X.index) == list(idx)

def test_day_of_week_one_hot():
    idx = pd.date_range("2011-01-03", periods=7, freq="D")  # Mon..Sun
    X = make_calendar_features(idx)
    dow_cols = [c for c in X.columns if c.startswith("dow_")]
    assert len(dow_cols) == 7
    # each day activates exactly one dow column
    assert (X[dow_cols].sum(axis=1) == 1).all()
    assert X.loc["2011-01-03", "dow_0"] == 1  # Monday

def test_month_one_hot():
    idx = pd.date_range("2011-01-30", periods=3, freq="D")  # Jan 30, 31, Feb 1
    X = make_calendar_features(idx)
    assert X.loc["2011-01-31", "month_1"] == 1
    assert X.loc["2011-02-01", "month_2"] == 1

def test_all_12_months_and_7_days_always_present():
    # single date must still produce the full fixed-width design matrix,
    # otherwise train and forecast matrices wouldn't line up
    X = make_calendar_features(pd.DatetimeIndex(["2011-06-15"]))
    assert len([c for c in X.columns if c.startswith("dow_")]) == 7
    assert len([c for c in X.columns if c.startswith("month_")]) == 12

def test_trend_is_days_since_epoch_anchor():
    idx = pd.date_range("2011-01-01", periods=3, freq="D")
    X = make_calendar_features(idx)
    diffs = X["trend"].diff().dropna()
    assert (diffs == 1).all()
