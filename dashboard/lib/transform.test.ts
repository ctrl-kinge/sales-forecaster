import { describe, expect, it } from "vitest";
import { MODEL_KEYS } from "./colors";
import { foldsToSeries } from "./transform";
import type { Fold } from "./types";

function makeFold(fold: number, dates: string[]): Fold {
  const pts = (base: number) =>
    dates.map((date, i) => ({ date, value: base + i }));
  const forecasts = Object.fromEntries(
    MODEL_KEYS.map((k, mi) => [k, pts(100 * (mi + 1))]),
  ) as Fold["forecasts"];
  const scores = Object.fromEntries(
    MODEL_KEYS.map((k) => [k, { mae: 1, rmse: 2 }]),
  ) as Fold["scores"];
  return {
    fold,
    start: dates[0],
    end: dates[dates.length - 1],
    actual: pts(0),
    forecasts,
    scores,
  };
}

const twoFolds: Fold[] = [
  makeFold(1, ["2011-10-15", "2011-10-16", "2011-10-17"]),
  makeFold(2, ["2011-10-22", "2011-10-23", "2011-10-24"]),
];

describe("foldsToSeries", () => {
  it("produces one row per test day across all folds", () => {
    const series = foldsToSeries(twoFolds);
    expect(series).toHaveLength(6);
  });

  it("rows are in chronological order", () => {
    const dates = foldsToSeries(twoFolds).map((r) => r.date);
    expect(dates).toEqual([...dates].sort());
  });

  it("each row carries the actual and every model's forecast", () => {
    const [row] = foldsToSeries(twoFolds);
    expect(row.date).toBe("2011-10-15");
    expect(row.actual).toBe(0);
    for (const k of MODEL_KEYS) {
      expect(typeof row[k]).toBe("number");
    }
    // first model's base is 100, first day offset 0
    expect(row.seasonal_naive_7d).toBe(100);
  });

  it("tags each row with its fold number", () => {
    const series = foldsToSeries(twoFolds);
    expect(series[0].fold).toBe(1);
    expect(series[5].fold).toBe(2);
  });

  it("returns an empty array for no folds", () => {
    expect(foldsToSeries([])).toEqual([]);
  });

  it("throws if a forecast date does not line up with the actual date", () => {
    const broken = structuredClone(twoFolds);
    broken[0].forecasts.seasonal_naive_7d[0].date = "2099-01-01";
    expect(() => foldsToSeries(broken)).toThrow();
  });
});
