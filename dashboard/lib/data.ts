import foldsJson from "@/data/folds.json";
import leaderboardJson from "@/data/leaderboard.json";
import metaJson from "@/data/meta.json";
import type { Fold, LeaderboardRow, Meta } from "./types";

// JSON imports arrive with widened types (model: string); the cast to the
// contract types happens here, in one place, and nowhere else.
export const leaderboard = leaderboardJson as unknown as LeaderboardRow[];
export const folds = foldsJson as unknown as Fold[];
export const meta = metaJson as Meta;

export function gbp(value: number): string {
  return value.toLocaleString("en-GB", { maximumFractionDigits: 0 });
}
