import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "../styles/upload-audio.module.css";
import { FaCheckCircle } from "react-icons/fa";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import OneDriveButton from '../components/OneDriveButton';
import { useOneDrive } from '../context/OneDriveContext';

const UploadPage = () => {
  const [audioFile, setAudioFile] = useState(null);
  const [audioPreview, setAudioPreview] = useState(null);
  const [audioFileId, setAudioFileId] = useState(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [progress, setProgress] = useState(null);
  const router = useRouter();
  const { isAuthenticated } = useOneDrive();
  
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/notifications");  

    socket.onopen = () => {
      console.log("✅ Connessione WebSocket stabilita.");
    };

    socket.onmessage = (event) => {
      console.log("📩 Messaggio dal WebSocket:", event.data);
      const data = JSON.parse(event.data);
      if (data.type === "notification") {
        setNotifications((prev) => [...prev, data.message]);
        setTimeout(() => {
          setNotifications((prev) => prev.filter((msg) => msg !== data.message));
        }, 5000);
      } else if (data.type === "progress") {
        setProgress(data.message);
      }
    };

    socket.onerror = (error) => {
      console.error("❌ Errore WebSocket:", error);
    };

    socket.onclose = () => {
      console.log("❌ Connessione WebSocket chiusa.");
    };

    setWs(socket);

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        console.log("🔄 Chiudendo WebSocket...");
        socket.close();
      }
    };
  }, []);

  // Gestisce il caricamento automatico del file audio
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudioFile(file);
      setAudioPreview(URL.createObjectURL(file));
      console.log("File selezionato:", file);
      await handleUpload(file); // Avvia subito l'upload al backend
    }
  };

  // Esegue l'upload automatico del file al backend
  const handleUpload = async (file) => {
    if (!file) {
      alert("Seleziona un file audio prima di caricare.");
      return;
    }

    const formData = new FormData();
    formData.append("audio_file", file);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BE_API_URL}/audio/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log("Dati ricevuti dall'API:", data);

        // Imposta l'ID del file audio appena caricato
        setAudioFileId(data.audio_file_id);
      } else {
        alert("Errore durante il caricamento del file.");
      }
    } catch (error) {
      console.error("Errore:", error);
      alert("Errore di rete durante il caricamento del file.");
    }
  };

  // Invia una richiesta al backend per avviare la trascrizione
  const handleStartTranscription = async () => {
    if (!audioFileId) {
      alert("ID del file audio non trovato.");
      return;
    }

    setIsTranscribing(true); 

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BE_API_URL}/start-transcription/${audioFileId}`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log("transcript_id: ", data.transcript_id);
        setProgress("Reindirizzo alla pagina editor...");

        // attende 2 secondi prima di reindirizzare
        setTimeout(() => {
            router.push(
                `/transcription-editor?transcript_id=${data.transcript_id}`
              );
        }, 2500);

        
      } else {
        const errorData = await response.json();
        console.error("Errore backend: ", errorData.detail);
        alert(`Errore durante l'avvio della trascrizione: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Errore:", error);
      alert("Errore di rete durante l'avvio della trascrizione.");
      setIsTranscribing(false);
    }
  };

  // ⭐ FUNZIONE TEST ONEDRIVE
  const testOneDriveConnection = async () => {
    try {
      console.log("🧪 Avvio test connessione OneDrive...");
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BE_API_URL}/onedrive/test/connection`,
        { 
          credentials: 'include' 
        }
      );
      
      const data = await response.json();
      console.log("OneDrive Test Result:", data);
      
      // Mostra il risultato in un alert formattato
      if (data.status === 'success') {
        const driveInfo = data.drive_info || {};
        const message = `✅ Connessione OneDrive OK!\n\n` +
          `📁 Nome: ${driveInfo.name || 'N/A'}\n` +
          `👤 Owner: ${driveInfo.owner || driveInfo.created_by || 'N/A'}\n` +
          `💾 Size: ${driveInfo.size ? (driveInfo.size / (1024*1024*1024)).toFixed(2) + ' GB' : 'N/A'}\n` +
          `📊 Quota: ${driveInfo.quota?.total ? (driveInfo.quota.total / (1024*1024*1024)).toFixed(2) + ' GB totali' : 'N/A'}`;
        
        alert(message);
        
        // Aggiungi notifica di successo
        setNotifications(prev => [...prev, "Test OneDrive completato con successo!"]);
        setTimeout(() => {
          setNotifications(prev => 
            prev.filter(msg => msg !== "Test OneDrive completato con successo!")
          );
        }, 3000);
        
      } else {
        alert(`❌ Test OneDrive fallito:\n\n${data.message}\n\nDettagli: ${data.details || 'Nessun dettaglio'}`);
      }
      
    } catch (error) {
      console.error("Test failed:", error);
      alert("❌ Test fallito: " + error.message);
      
      // Aggiungi notifica di errore
      setNotifications(prev => [...prev, `Errore test OneDrive: ${error.message}`]);
      setTimeout(() => {
        setNotifications(prev => 
          prev.filter(msg => msg.startsWith("Errore test OneDrive:"))
        );
      }, 3000);
    }
  };

  const handleOneDriveSuccess = (result) => {
    setNotifications(prev => [...prev, "File audio caricato su OneDrive con successo"]);
    setTimeout(() => {
        setNotifications(prev => 
            prev.filter(msg => msg !== "File audio caricato su OneDrive con successo")
        );
    }, 3000);
  };
  
  const handleOneDriveError = (error) => {
    setNotifications(prev => [...prev, `Errore: ${error.message}`]);
    setTimeout(() => {
        setNotifications(prev => 
            prev.filter(msg => msg.startsWith("Errore:"))
        );
    }, 3000);
  };

  return (
    <>
      {notifications.map((message, index) => (
        <div key={index} className={styles.notification}>
          <FaCheckCircle className={styles.successIcon} /> {message}
        </div>
      ))}
      <div className={styles.modalContainer}>
        {!audioPreview && (
          <div className={styles.uploadContainer}>
            <h1 className={styles.uploadTitle}>Carica il tuo file audio</h1>
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className={styles.hiddenInput}
              id="fileInput"
            />
            <label htmlFor="fileInput" className={styles.uploadButton}>
                Seleziona un file
            </label>
            
            {/* ⭐ PULSANTE TEST ONEDRIVE */}
            <div style={{ marginTop: '20px' }}>
              <button 
                onClick={testOneDriveConnection} 
                className={`${styles.button} ${styles.secondary}`}
                style={{ fontSize: '14px', padding: '8px 16px' }}
              >
                🧪 Test OneDrive Connection
              </button>
            </div>
          </div>
        )}

        {audioPreview && (
          <div className={styles.modalPreview}>
            <h2>{audioFile?.name}</h2>
            <audio controls>
              <source src={audioPreview} type="audio/mpeg" />
              Il tuo browser non supporta l'elemento audio.
            </audio>
            <div className={styles.buttons}>
              <button
                className={styles.button}
                onClick={handleStartTranscription}
                disabled={isTranscribing}
              >
                {isTranscribing ? "Trascrizione in corso..." : "Avvia Trascrizione"}
              </button>
              {audioFileId && (
                <OneDriveButton
                  endpoint={`/onedrive/upload/audio/${audioFileId}`}
                  onSuccess={handleOneDriveSuccess}
                  onError={handleOneDriveError}
                  className={styles.button}
                >
                  Salva in OneDrive
                </OneDriveButton>
              )}
              
              {/* ⭐ PULSANTE TEST ONEDRIVE ANCHE NELLA PREVIEW */}
              <button
                onClick={testOneDriveConnection}
                className={`${styles.button} ${styles.secondary}`}
                style={{ fontSize: '12px' }}
              >
                🧪 Test OneDrive
              </button>
              
              <button
                className={`${styles.button} ${styles.secondary}`}
                onClick={() => setAudioPreview(null)}
              >
                Chiudi
              </button>
            </div>
          </div>
        )}

        {/* Banner di progresso */}
        {progress !== null && (
          <div className={styles.progressModal}>
            <AiOutlineLoading3Quarters className={styles.spinner} /> {progress}
          </div>
        )}

      </div>
    </>
  );
};

export default UploadPage;