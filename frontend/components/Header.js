import Link from "next/link";
import styles from "../styles/header.module.css";
import { FaUserCircle } from "react-icons/fa"; // aggiunto
import OneDriveStatus from "./OneDriveStatus";

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Link href="/">
          <span>MA.VI.</span>
        </Link>
      </div>

      <nav className={styles.nav}>
        <Link href="/upload-audio">Carica Audio</Link>
        <a href="#">Documenti</a>
        <a href="#">Verbali OdV</a>
        <a href="#">Appuntamenti</a>
      </nav>

      <div className={styles.userActions}>
        <OneDriveStatus />
        <div className={styles.userIcon}>
          <FaUserCircle size={28} />
        </div>
      </div>
    </header>
  );
};

export default Header;