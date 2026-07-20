import json

import numpy as np
import pandas as pd

from forecaster.export import (
    MODELS,
    build_folds,
    build_leaderboard,
    build_meta,
    main,
)


def _series(days: int = 120) -> pd.Series:
    idx = pd.date_range("2011-01-03", periods=days, freq="D")
    dow_effect = np.array([100, 120, 140, 160, 180, 60, 10], dtype=float)
    rng = np.random.default_rng(7)
    return pd.Series(dow_effect[idx.dayofweek] + rng.normal(0, 5, days), index=idx)


def test_folds_shape_and_contract():
    folds = build_folds(_series(), horizon=7, n_folds=4)
    assert len(folds) == 4
    assert [f["fold"] for f in folds] == [1, 2, 3, 4]
    for f in folds:
        assert len(f["actual"]) == 7
        assert f["start"] == f["actual"][0]["date"]
        assert f["end"] == f["actual"][-1]["date"]
        # ISO date strings, JSON-safe floats
        assert len(f["actual"][0]["date"]) == 10
        assert isinstance(f["actual"][0]["value"], float)
        for name in MODELS:
            assert len(f["forecasts"][name]) == 7
            assert set(f["scores"][name]) == {"mae", "rmse"}


def test_forecast_dates_match_actual_dates():
    folds = build_folds(_series(), horizon=7, n_folds=2)
    for f in folds:
        actual_dates = [p["date"] for p in f["actual"]]
        for name in MODELS:
            assert [p["date"] for p in f["forecasts"][name]] == actual_dates


def test_leaderboard_sorted_with_single_champion():
    folds = build_folds(_series(), horizon=7, n_folds=4)
    board = build_leaderboard(folds)
    assert len(board) == len(MODELS)
    maes = [row["mae"] for row in board]
    assert maes == sorted(maes)
    assert [row["champion"] for row in board] == [True] + [False] * (len(board) - 1)
    for row in board:
        assert row["label"] and row["blurb"]


def test_leaderboard_mae_is_mean_of_fold_scores():
    folds = build_folds(_series(), horizon=7, n_folds=4)
    board = build_leaderboard(folds)
    for row in board:
        expected = sum(f["scores"][row["model"]]["mae"] for f in folds) / len(folds)
        assert abs(row["mae"] - expected) < 0.01


def test_meta_fields():
    series = _series()
    meta = build_meta(series, horizon=7, n_folds=4)
    assert meta["horizon"] == 7
    assert meta["n_folds"] == 4
    assert meta["train_start"] == "2011-01-03"
    assert meta["train_end"] == series.index[-1].date().isoformat()
    assert "generated_at" in meta and "protocol" in meta


def test_main_writes_three_json_files(tmp_path):
    main(out_dir=tmp_path, series=_series(), horizon=7, n_folds=2)
    for name in ("leaderboard", "folds", "meta"):
        payload = json.loads((tmp_path / f"{name}.json").read_text())
        assert payload  # non-empty, valid JSON
