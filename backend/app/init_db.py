import asyncio
from database import engine
from models.audio_files import Base as AudioBase
from models.transcripts import Base as TranscriptBase
from models.transcription_chunks import Base as ChunkBase
from models.transcription_summaries import Base as SummariesBase
from sqlalchemy.ext.asyncio import AsyncSession

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(AudioBase.metadata.create_all)
        await conn.run_sync(TranscriptBase.metadata.create_all) 
        await conn.run_sync(ChunkBase.metadata.create_all)
        await conn.run_sync(SummariesBase.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
