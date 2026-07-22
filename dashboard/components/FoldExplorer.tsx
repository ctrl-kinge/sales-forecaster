"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ACTUAL_COLOR, MODEL_COLORS, MODEL_KEYS } from "@/lib/colors";
import { gbp, MODEL_LABELS } from "@/lib/data";
import { foldScoreRows, foldsToSeries } from "@/lib/transform";
import type { Fold, ModelKey } from "@/lib/types";
import styles from "./FoldExplorer.module.css";

function dayLabel(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
  });
}

function range(fold: Fold): string {
  const opts: Intl.DateTimeFormatOptions = { day: "numeric", month: "short" };
  const start = new Date(fold.start).toLocaleDateString("en-GB", opts);
  const end = new Date(fold.end).toLocaleDateString("en-GB", opts);
  return `${start} – ${end}`;
}

export default function FoldExplorer({ folds }: { folds: Fold[] }) {
  const [selected, setSelected] = useState(folds[0]?.fold ?? 1);
  const fold = folds.find((f) => f.fold === selected) ?? folds[0];

  const series = useMemo(() => foldsToSeries([fold]), [fold]);
  const scores = useMemo(() => foldScoreRows(fold), [fold]);

  return (
    <section className={styles.section}>
      <div className="container">
        <p className="label">The microscope</p>
        <h2 className={styles.title}>Week by week, who actually won?</h2>
        <p className={styles.caption}>
          Pick a fold to zoom into its seven days. Different weeks crown
          different models — the leaderboard is an average over all of them.
        </p>

        <div className={styles.weeks}>
          {folds.map((f) => (
            <button
              key={f.fold}
              type="button"
              className={`${styles.week} ${
                f.fold === selected ? styles.weekOn : ""
              }`}
              onClick={() => setSelected(f.fold)}
            >
              <span className={styles.weekNum}>Week {f.fold}</span>
              <span className={styles.weekRange}>{range(f)}</span>
            </button>
          ))}
        </div>

        <div className={styles.panel}>
          <div className={styles.chart}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={series}
                margin={{ top: 8, right: 12, bottom: 8, left: 8 }}
              >
                <CartesianGrid stroke="#e8e0d2" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={dayLabel}
                  tick={{ fontSize: 12, fill: "#6b5f4e" }}
                />
                <YAxis
                  tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                  tick={{ fontSize: 12, fill: "#6b5f4e" }}
                  width={44}
                />
                <Tooltip
                  formatter={(value, name) => [
                    gbp(Number(value)),
                    name === "actual"
                      ? "Actual"
                      : MODEL_LABELS[name as ModelKey],
                  ]}
                  labelFormatter={(iso) => dayLabel(iso as string)}
                  contentStyle={{
                    background: "#fffdf8",
                    border: "1px solid #d8cfbc",
                    fontSize: 13,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke={ACTUAL_COLOR}
                  strokeWidth={2.5}
                  dot={{ r: 2 }}
                  isAnimationActive={false}
                />
                {MODEL_KEYS.map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={MODEL_COLORS[key]}
                    strokeWidth={1.5}
                    dot={false}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          <table className={styles.table}>
            <thead>
              <tr>
                <th>Model</th>
                <th className={styles.num}>MAE</th>
                <th className={styles.num}>RMSE</th>
              </tr>
            </thead>
            <tbody>
              {scores.map((row) => (
                <tr
                  key={row.model}
                  className={row.winner ? styles.winner : ""}
                >
                  <td>
                    <span
                      className={styles.swatch}
                      style={{ background: MODEL_COLORS[row.model] }}
                    />
                    {MODEL_LABELS[row.model]}
                    {row.winner && <span className={styles.tag}>best</span>}
                  </td>
                  <td className={styles.num}>{gbp(row.mae)}</td>
                  <td className={styles.num}>{gbp(row.rmse)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
