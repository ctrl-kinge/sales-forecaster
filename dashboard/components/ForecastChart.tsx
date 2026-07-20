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
import { gbp, leaderboard } from "@/lib/data";
import { foldsToSeries } from "@/lib/transform";
import type { Fold, ModelKey } from "@/lib/types";
import styles from "./ForecastChart.module.css";

const LABELS: Record<ModelKey, string> = Object.fromEntries(
  leaderboard.map((r) => [r.model, r.label]),
) as Record<ModelKey, string>;

// Off by default so the champion vs. actual comparison reads first; the
// visitor opts models in.
const INITIAL_ON: Record<ModelKey, boolean> = {
  seasonal_naive_7d: true,
  regression_lags_7_14_28: false,
  regression_calendar: false,
  naive_last: false,
  moving_average_7d: false,
};

function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
  });
}

export default function ForecastChart({ folds }: { folds: Fold[] }) {
  const series = useMemo(() => foldsToSeries(folds), [folds]);
  const [visible, setVisible] = useState(INITIAL_ON);

  const toggle = (key: ModelKey) =>
    setVisible((v) => ({ ...v, [key]: !v[key] }));

  return (
    <section className={styles.section}>
      <div className="container">
        <p className="label">The evidence</p>
        <h2 className={styles.title}>
          Every 7-day forecast against what actually happened
        </h2>
        <p className={styles.caption}>
          {series.length} test days across all folds. Actual revenue in ink;
          toggle any model to overlay its forecasts.
        </p>

        <div className={styles.legend}>
          {MODEL_KEYS.map((key) => (
            <button
              key={key}
              type="button"
              className={`${styles.chip} ${visible[key] ? styles.chipOn : ""}`}
              onClick={() => toggle(key)}
              style={
                visible[key]
                  ? { borderColor: MODEL_COLORS[key], color: MODEL_COLORS[key] }
                  : undefined
              }
            >
              <span
                className={styles.swatch}
                style={{ background: MODEL_COLORS[key] }}
              />
              {LABELS[key]}
            </button>
          ))}
        </div>

        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={420}>
            <LineChart
              data={series}
              margin={{ top: 8, right: 16, bottom: 8, left: 8 }}
            >
              <CartesianGrid stroke="#e8e0d2" vertical={false} />
              <XAxis
                dataKey="date"
                tickFormatter={shortDate}
                tick={{ fontSize: 12, fill: "#6b5f4e" }}
                minTickGap={28}
              />
              <YAxis
                tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                tick={{ fontSize: 12, fill: "#6b5f4e" }}
                width={44}
              />
              <Tooltip
                formatter={(value, name) => [
                  gbp(Number(value)),
                  name === "actual" ? "Actual" : LABELS[name as ModelKey],
                ]}
                labelFormatter={(iso) => shortDate(iso as string)}
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
                dot={false}
                isAnimationActive={false}
              />
              {MODEL_KEYS.filter((k) => visible[k]).map((key) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={MODEL_COLORS[key]}
                  strokeWidth={1.75}
                  dot={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
