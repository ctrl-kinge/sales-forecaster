import { meta } from "@/lib/data";
import styles from "./Hero.module.css";

export default function Hero() {
  return (
    <header className={styles.hero}>
      <div className="container">
        <p className="label">sales-forecaster · {meta.dataset}</p>
        <h1 className={styles.headline}>
          Can anything beat copying last&nbsp;week?
        </h1>
        <p className={styles.subtitle}>{meta.protocol}</p>
        <p className={styles.range}>
          Data {meta.train_start} — {meta.train_end} · five models, identical
          folds, mean MAE decides.
        </p>
      </div>
    </header>
  );
}
