from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.audio_files import AudioFile
from app.database import get_db
from app.models import *
from app.routers.websocket_manager import websocket_manager;
import uuid

router = APIRouter()

# API che permette il caricamento di un file audio e il salvataggio a DB
@router.post("/audio/upload")
async def upload_audio(audio_file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not audio_file:
        print("Nessun file ricevuto")
        raise HTTPException(status_code=400, detail="Nessun file ricevuto")
    
    print(f"Nome del file ricevuto: {audio_file.filename}")
    
    try:
        file_content = await audio_file.read()  
        print(f"📦 Dimensione del file: {len(file_content)} byte")

        # Crea un nuovo record nel database
        new_audio = AudioFile(file_name=audio_file.filename, file_data=file_content)
        db.add(new_audio)
        await db.commit()
        await db.refresh(new_audio)

        job_id = str(uuid.uuid4())  
        print(f"🆔 Job ID generato: {job_id}")
        # Restituisce l'ID del file audio creato
        await websocket_manager.send_notification("File salvato con successo")
        return {
            "audio_file_id": new_audio.id, 
            "job_id": job_id, 
            "message": "File caricato con successo!"
        }

    except Exception as e:
        print(f"Errore durante l'upload: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante l'upload: {str(e)}")


# API per ottenere la lista dei file audio caricati, Restituisce ID, nome file e data di caricamento.
@router.get("/audio")
async def get_audio_files(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AudioFile))
    audio_files = result.scalars().all()

    return [
        {"id": file.id, "file_name": file.file_name, "uploaded_at": file.uploaded_at}
        for file in audio_files
    ]
