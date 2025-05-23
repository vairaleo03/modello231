import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import TextStyle from "@tiptap/extension-text-style";
import Color from "@tiptap/extension-color";
import Highlight from "@tiptap/extension-highlight";
import HardBreak from '@tiptap/extension-hard-break';
import 'prosemirror-view/style/prosemirror.css';
import styles from "../styles/transcription-editor.module.css";
import { FaCheckCircle } from "react-icons/fa";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import Toolbar from "../components/Editor-toolbar";
import OneDriveButton from '../components/OneDriveButton';
import { useOneDrive } from '../context/OneDriveContext';

const SummaryEditor = () => {
    const router = useRouter();
    const { summary_id } = router.query;
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
            StarterKit.configure({
                hardBreak: true,
            }),
            Underline,
            TextStyle,
            TextAlign.configure({ types: ["heading", "paragraph"] }),
            Color.configure({ types: ["textStyle"] }),
            Highlight.configure({ multicolor: true }),
            
        ],
        content: '',
        onUpdate: ({ editor }) => {
            const newContent = editor.getHTML();
            setContent(newContent);
            //handleDebouncedSave(newContent);
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
        const timeout = setTimeout(() => saveSummary(newContent), 4000);
        setDebounceTimeout(timeout);
    };

    const saveSummary = async (summaryText) => {
        if (!summary_id) return;
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}/summary/${summary_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ summary_text: summaryText }),
            });
            if (response.ok) {
                console.log('✅ Riassunto aggiornato correttamente');
            } else {
                console.error('❌ Errore durante il salvataggio del riassunto');
            }
        } catch (error) {
            console.error('❌ Errore di rete: ', error);
        }
    };

    const downloadSummaryDocx = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_BE_API_URL}/summary/${summary_id}/word`,
                { method: "POST" }
            );
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `riassunto_${summary_id}.docx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (err) {
            console.error("❌ Errore nel download del riassunto Word", err);
        }
    };
    
    const handleOneDriveSuccess = (result) => {
        setNotifications(prev => [...prev, "Riassunto caricato su OneDrive con successo"]);
        setTimeout(() => {
            setNotifications(prev => 
                prev.filter(msg => msg !== "Riassunto caricato su OneDrive con successo")
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
        const fetchSummary = async () => {
            if (!summary_id) return;
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}/summary/${summary_id}`);
                if (response.ok) {
                    const data = await response.json();
                    console.log(data);
                    if (data.summary_text) {
                        const htmlFormatted = data.summary_text
                        .split('\n')
                        .map(line => line.trim())
                        .filter(line => line !== '')
                        .map(line => {
                          if (line.endsWith(':')) return `<h3>${line}</h3>`;
                          if (line.startsWith('- ')) return `<p style="margin-left: 20px;">• ${line.slice(2)}</p>`;
                          return `<p>${line}</p>`;
                        })
                        .join('');
                      
                      editor?.commands.setContent(htmlFormatted);
                    console.log(data.summary_text);
                    setContent(data.summary_text); // 🔹 Ora `content` ha sempre un valore
                }
                } else {
                    console.error('Errore nel recupero del riassunto');
                }
            } catch (error) {
                console.error('Errore di rete: ', error);
            }
        };
        if (isMounted) {
            fetchSummary();
        }
    }, [summary_id, editor, isMounted]);

    if (!isMounted) return null;

    return (
        <>
            {notifications.map((message, index) => (
                <div key={index} className={styles.notification}>
                <FaCheckCircle className={styles.successIcon} /> {message}
                </div>
            ))}
            <div className={styles.editorWrapper}>
                <h1 className={styles.editorTitle}>Editor Riassunto</h1>
                <Toolbar editor={editor} /> 
                <div className={styles.editorBox}>
                    <EditorContent editor={editor} />
                </div>
                <div className={styles.buttonsContainer}>
                    <button onClick={() => downloadSummaryDocx()} className={styles.saveButton}>
                        Scarica come .docx
                    </button>
                    <OneDriveButton
                        endpoint={`/onedrive/upload/summary/${summary_id}`}
                        onSuccess={handleOneDriveSuccess}
                        onError={handleOneDriveError}
                        className={styles.saveButton}
                    />
                </div>
            </div>
        </>
    );
};

export default SummaryEditor;