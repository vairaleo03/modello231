# Modello231 App

Applicazione per la trascrizione automatica, sintesi e generazione dei verbali dell'Organismo di Vigilanza, conforme al D.Lgs. 231/2001.  

---

## 🚀 Avvio rapido del progetto

### ✅ Requisiti

- Python 3.11+
- Node.js 18+
- PostgreSQL (in locale o remoto)
- `ffmpeg` installato nel sistema
- OpenAI API Key (da inserire nel `.env`)

---

## 📦 Backend (FastAPI)

1. Entra nella cartella del backend:
   ```bash
   cd modello231-app/backend
   ```

2. Crea l’ambiente virtuale:
   ```bash
   python3 -m venv venv
   ```

3. Attiva l’ambiente virtuale:

   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

5. (Opzionale) Per aggiungere nuove dipendenze:
   ```bash
   pip install nome-dipendenza
   pip freeze > requirements.txt
   ```

6. Crea un file `.env` nella cartella `backend/`:
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxx
   DATABASE_URL="postgresql-xxxxxxxx"
   REDIS_URL=redis://-xxxxxxxx
   ```

7. Avvia il server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 💻 Frontend (Next.js)

1. Vai nella cartella del frontend:
   ```bash
   cd modello231-app/frontend
   ```

2. Installa le dipendenze:
   ```bash
   npm install
   ```

3. Crea un file `.env.local` nella cartella `frontend/`:
   ```
   NEXT_PUBLIC_BE_API_URL=http://localhost:8000
   ```

4. Avvia il server Next.js:
   ```bash
   npm run dev
   ```

Accedi all'app su: [http://localhost:3000](http://localhost:3000)

---

## 🌱 Modalità di lavoro: GitFlow

Usiamo **GitFlow** per una gestione ordinata dello sviluppo:

- `main`: versione stabile/produzione
- `develop`: integrazione e testing
- `feature/xyz`: nuove funzionalità
- `bugfix/xyz`: correzioni
- `release/x.x.x`: preparazione versioni
- `hotfix/x.x.x`: fix urgenti in produzione

### Esempio:

```bash
git checkout develop
git checkout -b feature/riassunto-openai

# Lavoro...

git add .
git commit -m "feat: integrazione riassunto OpenAI"
git push origin feature/riassunto-openai
```

Al termine, apri una **Pull Request** verso `develop`.

---
