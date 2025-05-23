import React from "react";
import {
    Bold,
    Italic,
    Underline,
    Heading1,
    Heading2,
    Heading3,
    List,
    ListOrdered,
    AlignLeft,
    AlignCenter,
    AlignRight,
    PaintBucket,
    Palette,
  } from "lucide-react";
import styles from "../styles/editor-toolbar.module.css";

const Toolbar = ({ editor }) => {
  if (!editor) {
    return null;
  }

  const applyTextColor = (color) => {
    editor.chain().focus().setColor(color).run();
  };

  const applyHighlight = (color) => {
    editor.chain().focus().toggleHighlight({ color }).run();
  };

  return (
    <div className={styles.toolbar}>
      <button onClick={() => editor.chain().focus().toggleBold().run()} disabled={!editor.can().chain().focus().toggleBold().run()}>
        <Bold size={20} />
      </button>
      <button onClick={() => editor.chain().focus().toggleItalic().run()} disabled={!editor.can().chain().focus().toggleItalic().run()}>
        <Italic size={20} />
      </button>
      <button onClick={() => editor.chain().focus().toggleUnderline().run()} disabled={!editor.can().chain().focus().toggleUnderline().run()}>
        <Underline size={20} />
      </button>

      {/* 🔹 Pulsanti per gli Heading con nuove icone */}
      {/* <button onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}>
        <Heading1 size={20} />
      </button>
      <button onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}>
        <Heading2 size={20} />
      </button>
      <button onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}>
        <Heading3 size={20} />
      </button> */}

      {/* 🔹 Liste Puntate e Numerate */}
      {/* <button onClick={() => editor.chain().focus().toggleBulletList().run()}>
        <List size={20} />
      </button>
      <button onClick={() => editor.chain().focus().toggleOrderedList().run()}>
        <ListOrdered size={20} />
      </button> */}

      {/* 🔹 Pulsanti di Allineamento */}
      {/* <button onClick={() => editor.chain().focus().setTextAlign("left").run()}>
        <AlignLeft size={20} />
      </button>
      <button onClick={() => editor.chain().focus().setTextAlign("center").run()}>
        <AlignCenter size={20} />
      </button>
      <button onClick={() => editor.chain().focus().setTextAlign("right").run()}>
        <AlignRight size={20} />
      </button> */}

      {/* 🔹 Pulsante per l'Evidenziazione */}
      {/* <button onClick={() => applyHighlight("#FFFF00")}>
        <PaintBucket size={20} />
      </button> */}

      {/* 🔹 Pulsante per Cambiare il Colore del Testo
      <button onClick={() => applyTextColor("#FF5733")}>
        <Palette size={20} />
      </button> */}
    </div>
  );
};

export default Toolbar;
