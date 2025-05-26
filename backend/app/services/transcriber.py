import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def transcribe_audio(filepath: str):
    if not openai.api_key:
        return {"error": "❌ OPENAI_API_KEY mancante. Aggiungila nel file .env."}

    try:
        with open(filepath, "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="it"
            )

            print(f"transcription response ---> {transcription}")

        full_text = transcription.text
        segments = [s.dict() for s in transcription.segments]
        return {
            "language": "it",
            "segments": segments,
            "transcription": full_text
        }

    except Exception as e:
        return {"error": f"❌ Errore durante la trascrizione: {str(e)}"}
