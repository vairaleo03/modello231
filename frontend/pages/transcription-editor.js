import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import TextStyle from "@tiptap/extension-text-style";
import Color from "@tiptap/extension-color";
import Highlight from "@tiptap/extension-highlight";
import 'prosemirror-view/style/prosemirror.css';
import styles from "../styles/transcription-editor.module.css";
import { FaCheckCircle } from "react-icons/fa";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import Toolbar from "../components/Editor-toolbar";
import OneDriveButton from '../components/OneDriveButton';
import { useOneDrive } from '../context/OneDriveContext';

const TranscriptionEditor = () => {
    const router = useRouter();
    const { transcript_id } = router.query;
    const [content, setContent] = useState('');
    const [isMounted, setIsMounted] = useState(false);
    const [debounceTimeout, setDebounceTimeout] = useState(null);
    const [socket, setSocket] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [progress, setProgress] = useState(null);
    const { isAuthenticated } = useOneDrive();

    useEffect(() => {
        setIsMounted(true);
        const ws = new WebSocket('ws://localhost:8000/ws/notifications');
        ws.onopen = () => {
            console.log('✅ WebSocket connesso per aggiornamenti di salvataggio');
        };
        ws.onmessage = (event) => {
            console.log("📩 Messaggio dal WebSocket:", event.data);
            const data = JSON.parse(event.data);
            if (data.type === "notification") {
              setNotifications((prev) => [...prev, data.message]);
              setTimeout(() => {
                setNotifications((prev) => prev.filter((msg) => msg !== data.message));
              }, 2500);
            } else if (data.type === "progress") {
              setProgress(data.message);
            }
          };
        ws.onerror = (error) => {
            console.error('❌ Errore WebSocket:', error);
        };
        ws.onclose = () => {
            console.log('❌ Connessione WebSocket chiusa.');
        };
        setSocket(ws);

        return () => {
            if (ws.readyState === WebSocket.OPEN) {
              console.log("🔄 Chiudendo WebSocket...");
              ws.close();
            }
          };
    }, []);

    const editor = useEditor({
        extensions: [
            StarterKit,
            Underline,
            // TextStyle,
            // TextAlign.configure({ types: ["heading", "paragraph"] }),
            // Color.configure({ types: ["textStyle"] }),
            // Highlight.configure({ multicolor: true }),
          ],
        content: '',
        onUpdate: ({ editor }) => {
            const newContent = editor.getHTML();
            setContent(newContent);
            handleDebouncedSave(newContent);
        },
        editorProps: {
            attributes: {
                class: `${styles.editorContainer}`,
                style: 'white-space: pre-wrap;',
            },
        },
        injectCSS: false,
        editable: true,
        immediatelyRender: false,
    });

    const handleDebouncedSave = (newContent) => {
        if (debounceTimeout) clearTimeout(debounceTimeout);
        const timeout = setTimeout(() => saveTranscription(newContent), 4000);
        setDebounceTimeout(timeout);
    };

    const saveTranscription = async (text) => {
        if (!transcript_id) return;
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}/transcriptions/${transcript_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transcript_text: text }),
            });
            if (response.ok) {
                console.log('✅ Trascrizione aggiornata correttamente');
            } else {
                console.error('❌ Errore durante il salvataggio della trascrizione');
            }
        } catch (error) {
            console.error('❌ Errore di rete: ', error);
        }
    };

    const handleWordAction = async (action) => {
        if (!transcript_id) {
            console.error("❌ Nessuna trascrizione selezionata");
            return;
        }
    
        console.log("💾 Salvando la trascrizione prima di eseguire l'azione...");
        await saveTranscription(content); // ✅ Salva la trascrizione prima di eseguire l'azione
        console.log(content);
    
        setTimeout(async () => {
            try {
                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_BE_API_URL}/transcriptions/${transcript_id}/word?action=${action}`,
                    { method: "POST" }
                );
    
                if (action === "download" && response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `trascrizione_${transcript_id}.docx`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    console.log("✅ Download completato");
                } else if (action === "upload" && response.ok) {
                    console.log("✅ File caricato su OneDrive con successo");
                } else {
                    console.error("❌ Errore durante l'operazione:", response.statusText);
                }
            } catch (error) {
                console.error("❌ Errore di rete:", error);
            }
        }, 1000); 
    };

    const startSummary = async () => {
        if (!transcript_id) {
            console.error("❌ Nessuna trascrizione selezionata");
            return;
        }

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_BE_API_URL}/summary/start/${transcript_id}`,
                { method: "POST" }
            );
            if(response.ok){
                const data = await response.json();
                console.log('risposta --> ', data);
                router.push(
                    `/summary-editor?summary_id=${data}`
                  );
            }
        } catch(e){
            console.error('Errore: ', e)
        }
    }
    
    const handleOneDriveSuccess = (result) => {
        setNotifications(prev => [...prev, "Trascrizione caricata su OneDrive con successo"]);
        setTimeout(() => {
            setNotifications(prev => 
                prev.filter(msg => msg !== "Trascrizione caricata su OneDrive con successo")
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
    
    useEffect(() => {
        const fetchTranscription = async () => {
            if (!transcript_id) return;
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}/transcriptions/${transcript_id}`);
                if (response.ok) {
                    const data = await response.json();

                    if (data.transcript_text) {
                    editor?.commands.setContent(data.transcript_text);
                    setContent(data.transcript_text); // 🔹 Ora `content` ha sempre un valore
                    }
                } else {
                    console.error('Errore nel recupero della trascrizione');
                }
            } catch (error) {
                console.error('Errore di rete: ', error);
            }
        };
        if (isMounted) {
            fetchTranscription();
        }
    }, [transcript_id, editor, isMounted]);

    if (!isMounted) return null;

    return (
        <>
            {notifications.map((message, index) => (
                <div key={index} className={styles.notification}>
                <FaCheckCircle className={styles.successIcon} /> {message}
                </div>
            ))}
            <div className={styles.editorWrapper}>
                <h1 className={styles.editorTitle}>Editor di Trascrizione</h1>
                <Toolbar editor={editor} /> 
                <div className={styles.editorBox}>
                    <EditorContent editor={editor} />
                </div>
                <div className={styles.buttonsContainer}>
                    <button onClick={() => handleWordAction("download")} className={styles.saveButton}>
                        Scarica come .docx
                    </button>
                    <button onClick={() => startSummary()} className={styles.saveButton}>
                        Riassumi
                    </button>
                    <OneDriveButton
                        endpoint={`/onedrive/upload/transcription/${transcript_id}`}
                        onSuccess={handleOneDriveSuccess}
                        onError={handleOneDriveError}
                        className={styles.saveButton}
                    />
                </div>
            </div>
        </>
    );
};

export default TranscriptionEditor;