// Mirrors the JSON contract written by `python -m forecaster.export`
// (forecaster/export.py). Change one side, change the other.

export type ModelKey =
  | "seasonal_naive_7d"
  | "regression_lags_7_14_28"
  | "regression_calendar"
  | "naive_last"
  | "moving_average_7d";

export interface Point {
  date: string; // ISO YYYY-MM-DD
  value: number;
}

export interface Scores {
  mae: number;
  rmse: number;
}

export interface LeaderboardRow {
  model: ModelKey;
  label: string;
  blurb: string;
  mae: number;
  rmse: number;
  champion: boolean;
}

export interface Fold {
  fold: number;
  start: string;
  end: string;
  actual: Point[];
  forecasts: Record<ModelKey, Point[]>;
  scores: Record<ModelKey, Scores>;
}

export interface Meta {
  dataset: string;
  protocol: string;
  horizon: number;
  n_folds: number;
  train_start: string;
  train_end: string;
  generated_at: string;
}
