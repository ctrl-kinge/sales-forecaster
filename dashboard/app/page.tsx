import Hero from "@/components/Hero";
import Leaderboard from "@/components/Leaderboard";

export default function Home() {
  return (
    <main>
      <Hero />
      <Leaderboard />
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
        backtest · charts and fold explorer coming in Phase 3b/3c.
      </footer>
    </main>
  );
}
