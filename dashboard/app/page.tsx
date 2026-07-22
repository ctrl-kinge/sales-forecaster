import FoldExplorer from "@/components/FoldExplorer";
import ForecastChart from "@/components/ForecastChart";
import Hero from "@/components/Hero";
import Leaderboard from "@/components/Leaderboard";
import { folds } from "@/lib/data";

export default function Home() {
  return (
    <main>
      <Hero />
      <Leaderboard />
      <ForecastChart folds={folds} />
      <FoldExplorer folds={folds} />
      <footer
        className="container"
        style={{
          padding: "2rem 1.5rem 3rem",
          fontSize: "0.85rem",
          color: "var(--ink-soft)",
        }}
      >
        Built from the{" "}
        <a href="https://github.com/ctrl-kinge/sales-forecaster">
          sales-forecaster
        </a>{" "}
        backtest · every number regenerated with{" "}
        <code>python -m forecaster.export</code>.
      </footer>
    </main>
  );
}
