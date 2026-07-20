import { MODEL_COLORS } from "@/lib/colors";
import { gbp, leaderboard } from "@/lib/data";
import styles from "./Leaderboard.module.css";

export default function Leaderboard() {
  return (
    <section className={styles.section}>
      <div className="container">
        <p className="label">The verdict</p>
        <h2 className={styles.title}>Mean error across all eight weeks</h2>
        <div className={styles.grid}>
          {leaderboard.map((row, i) => (
            <article
              key={row.model}
              className={styles.card}
              style={{ borderTopColor: MODEL_COLORS[row.model] }}
            >
              <div className={styles.cardHead}>
                <span className={styles.rank}>{i + 1}</span>
                {row.champion && (
                  <span className={styles.champion}>champion</span>
                )}
              </div>
              <h3 className={styles.model}>{row.label}</h3>
              <p className={`numeral ${styles.mae}`}>{gbp(row.mae)}</p>
              <p className={styles.rmse}>
                MAE (GBP) · RMSE {gbp(row.rmse)}
              </p>
              <p className={styles.blurb}>{row.blurb}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
