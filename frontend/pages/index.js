import styles from "../styles/index.module.css";

const HomePage = () => {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Dashboard</h1>

      <div className={styles.grid}>
        <div className={styles.card}>📁 Documenti</div>
        <div className={styles.card}>📝 Riassunti AI</div>
        <div className={styles.card}>📅 Appuntamenti</div>
        <div className={styles.card}>📊 Stato Modello 231</div>
        <div className={styles.card}>🔒 Privacy & Compliance</div>
        <div className={styles.card}>⚙️ Impostazioni</div>
      </div>

      <div className={styles.metricsGrid}>
        <div className={styles.metricTile}>
          <h2>📈 Verbali Trascritti</h2>
          <p>Verbali elaborati negli ultimi 30 giorni</p>
          <div className={`${styles.donut} ${styles.donut70}`}>
            <span>42</span>
          </div>
        </div>

        <div className={styles.metricTile}>
          <h2>🗓️ Appuntamenti Settimanali</h2>
          <p>Appuntamenti pianificati questa settimana</p>
          <div className={`${styles.donut} ${styles.donut40}`}>
            <span>5</span>
          </div>
        </div>

        <div className={styles.metricTile}>
          <h2>✅ Completamento Modello 231</h2>
          <p>Percentuale completamento</p>
          <div className={`${styles.donut} ${styles.donut85}`}>
            <span>85%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
