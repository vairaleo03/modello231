import React from 'react';
import { useOneDrive } from '../context/OneDriveContext';
import styles from '../styles/onedrive-button.module.css';

/**
 * Pulsante per caricare file su OneDrive
 * @param {Object} props - Proprietà del componente
 * @param {string} props.endpoint - Endpoint API per il caricamento
 * @param {Function} props.onSuccess - Callback da eseguire in caso di successo
 * @param {Function} props.onError - Callback da eseguire in caso di errore
 * @param {string} props.className - Classe CSS aggiuntiva
 * @param {JSX.Element} props.children - Testo del pulsante
 */
const OneDriveButton = ({ 
  endpoint, 
  onSuccess, 
  onError, 
  className = '',
  children = 'Salva in OneDrive',
  ...props
}) => {
  const { isAuthenticated, isLoading, uploadToOneDrive } = useOneDrive();
  const [isUploading, setIsUploading] = React.useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    
    try {
      setIsUploading(true);
      
      const result = await uploadToOneDrive(endpoint);
      
      if (result.needsAuth) {
        // Reindirizzamento all'autenticazione avverrà automaticamente
        return;
      }
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (error) {
      console.error('Errore durante il caricamento su OneDrive:', error);
      if (onError) {
        onError(error);
      }
    } finally {
      setIsUploading(false);
    }
  };

  const buttonClassNames = `${styles.button} ${className} ${isUploading ? styles.loading : ''}`;

  return (
    <button
      onClick={handleUpload}
      className={buttonClassNames}
      disabled={isLoading || isUploading}
      {...props}
    >
      {isUploading ? (
        <>
          <span className={styles.spinner}></span>
          Caricamento...
        </>
      ) : (
        children
      )}
    </button>
  );
};

export default OneDriveButton;