import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Carica le variabili dal file .env, se presente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
Sei un assistente legale specializzato nell’elaborazione dei verbali degli Organismi di Vigilanza (OdV) in conformità al Modello 231.

Analizza la seguente trascrizione e genera un sommario strutturato, utile per la redazione del verbale ufficiale. Segui le istruzioni riportate:

---

### 1. Pre-elaborazione:
- Riconosci e separa automaticamente i diversi interlocutori presenti nel testo.
- Correggi eventuali errori grammaticali o refusi dovuti alla trascrizione automatica.
- Normalizza il testo per migliorarne la leggibilità e la coerenza espressiva.

---

### 2. Struttura del sommario:
- Suddividi il contenuto in **sezioni tematiche distinte**, corrispondenti a ciascun punto dell’ordine del giorno o argomento rilevante emerso.
- Assegna a ciascuna sezione un **titolo chiaro e descrittivo**. Alcuni esempi utili:
  - Aggiornamento Flussi Informativi
  - Analisi Segnalazioni Whistleblowing Ricevute
  - Verifica Attuazione Modello Organizzativo
  - Pianificazione Attività di Vigilanza
  - Proposta Aggiornamento Modello 231
  - Formazione Personale su D.Lgs. 231/2001

---

### 3. Per ogni sezione includi:
#### a. Descrizione Sintetica  
> Breve introduzione dell’argomento discusso.

#### b. Punti Salienti della Discussione  
> Elenco puntuale dei temi trattati, evidenziando criticità, osservazioni e analisi. Attribuisci gli interventi significativi ai relatori quando possibile.

#### c. Indicazioni Fornite  
> Riporta chiaramente ogni indicazione, raccomandazione o proposta emersa, con evidenza di chi l’ha fornita.

#### d. Azioni Assegnate (Action Items)  
> Per ogni attività decisa, specifica:
- **Cosa**: descrizione chiara dell’azione
- **Chi**: soggetto o funzione responsabile
- **Quando**: scadenza o prossimo aggiornamento

#### e. Documenti Esaminati/Presentati  
> Elenca i documenti discussi (relazioni, audit, verbali, ecc.).

---

### 4. Stile richiesto:
- Professionale e sintetico
- Corretto grammaticalmente
- Formattato in modo leggibile (markdown o HTML compatibile)

---

Trascrizione:
"""

def generate_summary(transcription: str) -> str:    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "Sei un assistente legale specializzato in Modello 231."},
                {"role": "user", "content": PROMPT_TEMPLATE + transcription}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        print(f"response ------> {response.choices[0].message.content.strip()}")
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Errore nella generazione del riassunto: {str(e)}"
