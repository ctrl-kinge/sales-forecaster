import type { ModelKey } from "./types";

// Earth-tone model palette from the Phase 3 spec (lab-notebook identity).
export const MODEL_COLORS: Record<ModelKey, string> = {
  seasonal_naive_7d: "#3d6b35", // green — the champion
  regression_lags_7_14_28: "#8a6414", // wheat
  regression_calendar: "#a8432e", // clay
  naive_last: "#6b5f4e", // taupe
  moving_average_7d: "#54718a", // slate
};

export const ACTUAL_COLOR = "#1c1a17"; // ink
