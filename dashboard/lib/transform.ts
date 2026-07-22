import { MODEL_KEYS } from "./colors";
import type { Fold, ModelKey } from "./types";

// One row per test day, flattened across every fold — the shape Recharts
// wants: a date, the actual revenue, and each model's forecast for that day.
export type ChartRow = { date: string; fold: number; actual: number } & Record<
  ModelKey,
  number
>;

/**
 * Flatten the per-fold backtest into a single chronological series.
 *
 * Each fold contributes `horizon` days; forecasts are aligned to the
 * actual by date, and a mismatch throws rather than silently plotting a
 * model against the wrong day.
 */
export function foldsToSeries(folds: Fold[]): ChartRow[] {
  const rows: ChartRow[] = [];

  for (const fold of folds) {
    fold.actual.forEach((point, i) => {
      const row = {
        date: point.date,
        fold: fold.fold,
        actual: point.value,
      } as ChartRow;

      for (const key of MODEL_KEYS) {
        const forecast = fold.forecasts[key][i];
        if (!forecast || forecast.date !== point.date) {
          throw new Error(
            `fold ${fold.fold}: ${key} forecast misaligned at ${point.date}`,
          );
        }
        row[key] = forecast.value;
      }

      rows.push(row);
    });
  }

  return rows.sort((a, b) => a.date.localeCompare(b.date));
}

export interface FoldScoreRow {
  model: ModelKey;
  mae: number;
  rmse: number;
  winner: boolean;
}

/** One fold's per-model scores, sorted best-first with the winner flagged. */
export function foldScoreRows(fold: Fold): FoldScoreRow[] {
  const rows: FoldScoreRow[] = MODEL_KEYS.map((model) => ({
    model,
    mae: fold.scores[model].mae,
    rmse: fold.scores[model].rmse,
    winner: false,
  }));
  rows.sort((a, b) => a.mae - b.mae);
  if (rows.length > 0) {
    rows[0].winner = true;
  }
  return rows;
}
