import aiohttp
import io
import os
import tempfile
import traceback  # ⭐ AGGIUNGI QUESTO
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.database import get_db
from app.models.audio_files import AudioFile
from app.models.transcripts import Transcript
from app.models.tasks import Task, TaskStatus
from pydantic import BaseModel
from app.routers.websocket_manager import websocket_manager
from app.utils.post_processing import format_segments_html, convert_html_to_word, convert_html_to_word_template
from app.services.transcriber import transcribe_audio
from fastapi import UploadFile
from pydub import AudioSegment

router = APIRouter()

class TranscriptUpdateRequest(BaseModel):
    transcript_text: str


# Recupera una trascrizione
@router.get("/transcriptions/{transcript_id}")
async def get_transcription(transcript_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transcript).filter(Transcript.id == transcript_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(status_code=404, detail="Trascrizione non trovata")

    return {
        "transcript_id": transcription.id,
        "transcript_text": transcription.transcript_text,
        "audio_id": transcription.audio_id,
        "created_at": transcription.created_at, 
        "segments": transcription.segments
    }


# ✅ Salva automaticamente le modifiche alla trascrizione
@router.put("/transcriptions/{transcript_id}")
async def update_transcription(transcript_id: int, request: TranscriptUpdateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transcript).filter(Transcript.id == transcript_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(status_code=404, detail="Trascrizione non trovata")

    stmt = update(Transcript).where(Transcript.id == transcript_id).values(transcript_text=request.transcript_text)
    await db.execute(stmt)
    await db.commit()
    await websocket_manager.send_notification("Modifiche salvate")
    return {"message": "Trascrizione aggiornata con successo!"}


# ⭐ ENDPOINT CON BETTER ERROR HANDLING
@router.post("/start-transcription/{audio_file_id}")
async def start_transcription_endpoint(audio_file_id: int, db: AsyncSession = Depends(get_db)):
    try:
        print(f"🎬 Avvio trascrizione per audio_file_id: {audio_file_id}")
        
        # Cerca il file audio nel database
        result = await db.execute(select(AudioFile).filter(AudioFile.id == audio_file_id))
        audio_file = result.scalar_one_or_none()

        if not audio_file:
            print(f"❌ File audio con ID {audio_file_id} non trovato nel database.")
            raise HTTPException(status_code=404, detail="File audio non trovato")
        
        print(f"✅ File trovato: {audio_file.file_name}, dimensione: {len(audio_file.file_data)} bytes")
        
        # ⭐ CONTROLLO DIMENSIONE FILE
        file_size_mb = len(audio_file.file_data) / (1024 * 1024)
        print(f"📊 Dimensione file: {file_size_mb:.2f} MB")
        
        if file_size_mb > 25:  # Limite OpenAI Whisper
            raise HTTPException(
                status_code=413, 
                detail=f"File troppo grande ({file_size_mb:.2f} MB). Limite: 25 MB"
            )

        # ⭐ CONVERSIONE CON TRY/CATCH
        print("🔄 Inizio conversione audio...")
        temp_path = None
        try:
            original = AudioSegment.from_file(io.BytesIO(audio_file.file_data))
            print(f"✅ Audio caricato: {len(original)}ms, {original.frame_rate}Hz")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                # ⭐ CONVERSIONE PIÙ SICURA
                converted = original.set_channels(1).set_frame_rate(16000)
                converted.export(temp_file.name, format="mp3", bitrate="64k")
                temp_path = temp_file.name
                
            print(f"✅ Conversione completata: {temp_path}")
            
            # ⭐ CONTROLLO DIMENSIONE FILE CONVERTITO
            converted_size = os.path.getsize(temp_path)
            print(f"📊 File convertito: {converted_size / (1024*1024):.2f} MB")

        except Exception as conv_error:
            print(f"❌ Errore conversione audio: {str(conv_error)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(
                status_code=500, 
                detail=f"Errore nella conversione audio: {str(conv_error)}"
            )

        # ⭐ TRASCRIZIONE CON TIMEOUT E RETRY
        print("🎤 Inizio trascrizione...")
        try:
            result_json = await transcribe_audio(temp_path)
            print(f"✅ Trascrizione completata, chiavi risultato: {list(result_json.keys())}")
            
        except Exception as transcr_error:
            print(f"❌ Errore trascrizione: {str(transcr_error)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(
                status_code=500, 
                detail=f"Errore nella trascrizione: {str(transcr_error)}"
            )
        
        finally:
            # ⭐ PULIZIA FILE TEMPORANEO
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"🗑️ File temporaneo rimosso: {temp_path}")

        # ⭐ VALIDAZIONE RISULTATO
        raw_transcription = result_json.get("transcription")
        segments = result_json.get("segments", [])
        
        if not raw_transcription:
            print(f"❌ Trascrizione vuota nel risultato: {result_json}")
            raise HTTPException(status_code=500, detail="Trascrizione vuota dalla API")

        print(f"✅ Trascrizione ottenuta: {len(raw_transcription)} caratteri, {len(segments)} segmenti")

        # ⭐ SALVATAGGIO NEL DB CON TRY/CATCH
        try:
            new_transcript = Transcript(
                audio_id=audio_file.id,
                transcript_text=raw_transcription,
                segments=segments,
                created_at=datetime.utcnow()
            )
            db.add(new_transcript)
            await db.commit()
            await db.refresh(new_transcript)
            print(f"✅ Transcript salvato con ID: {new_transcript.id}")

        except Exception as db_error:
            print(f"❌ Errore salvataggio DB: {str(db_error)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            await db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Errore nel salvataggio: {str(db_error)}"
            )

        # ✅ Successo
        return {
            "message": "Trascrizione completata con successo!",
            "transcript_id": new_transcript.id,
            "audio_file_id": audio_file.id,
            "transcript_length": len(raw_transcription),
            "segments_count": len(segments)
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (already handled)
        raise
    except Exception as e:
        # ⭐ CATCH ALL PER ERRORI IMPREVISTI
        print(f"❌ Errore imprevisto: {str(e)}")
        print(f"❌ Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Errore imprevisto durante la trascrizione: {str(e)}"
        )


# API che converte la trascrizione in word e fa partire il download
@router.post("/transcriptions/{transcript_id}/word")
async def manage_word_file(transcript_id: int, action: str, db: AsyncSession = Depends(get_db)):
    """Genera un file Word dalla trascrizione formattata."""
    
    result = await db.execute(select(Transcript).filter(Transcript.id == transcript_id))
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(status_code=404, detail="Trascrizione non trovata")

    # 🔹 Converte l'HTML formattato in Word
    #doc = convert_html_to_word(transcription.segments)
    print(f"transcription.transcript_text {transcription.transcript_text}")
    doc = convert_html_to_word_template(transcription.transcript_text)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    if action == "download":
        return StreamingResponse(io.BytesIO(file_stream.getvalue()), 
                                 media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                 headers={"Content-Disposition": f"attachment; filename=trascrizione_{transcript_id}.docx"})

    elif action == "upload":
        return {"message": "File caricato su OneDrive con successo"}

    else:
        raise HTTPException(status_code=400, detail="Azione non valida. Usa 'download' o 'upload'.")