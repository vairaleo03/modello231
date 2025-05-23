import React from 'react';
import { useOneDrive } from '../context/OneDriveContext';
import styles from '../styles/onedrive-status.module.css';
import { FaCloudUploadAlt, FaSyncAlt, FaSignInAlt, FaSignOutAlt, FaBug } from 'react-icons/fa';

const OneDriveStatus = () => {
  const { isAuthenticated, isLoading, startAuthentication, logout, testConnection } = useOneDrive();

  // ⭐ HANDLER PER TEST DEBUG
  const handleTestConnection = async () => {
    const result = await testConnection();
    alert(`Test Result:\nStatus: ${result.status}\nMessage: ${result.message}`);
  };

  if (isLoading) {
    return (
      <div className={styles.status}>
        <FaSyncAlt className={styles.loadingIcon} />
      </div>
    );
  }

  if (isAuthenticated) {
    return (
      <div className={styles.status}>
        <FaCloudUploadAlt className={styles.connectedIcon} />
        <span className={styles.statusText}>OneDrive Connesso</span>
        {/* ⭐ BOTTONE TEST DEBUG */}
        <button className={styles.testButton} onClick={handleTestConnection} title="Test connessione">
          <FaBug />
        </button>
        <button className={styles.logoutButton} onClick={logout}>
          <FaSignOutAlt />
        </button>
      </div>
    );
  }

  return (
    <div className={styles.status}>
      <button className={styles.connectButton} onClick={startAuthentication}>
        <FaSignInAlt /> Connetti OneDrive
      </button>
      {/* ⭐ BOTTONE TEST ANCHE QUANDO NON AUTENTICATO */}
      <button className={styles.testButton} onClick={handleTestConnection} title="Test connessione">
        <FaBug />
      </button>
    </div>
  );
};

export default OneDriveStatus;