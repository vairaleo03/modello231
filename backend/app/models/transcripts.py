from sqlalchemy import JSON, Column, Integer, Text, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from .audio_files import AudioFile
from datetime import datetime
from app.database import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_files.id"), nullable=False)
    #chunk = Column(Integer, ForeignKey("transcription_chunks.id"), nullable=True)  # Modifica qui
    word_doc_url = Column(Text, nullable=True)
    word_doc = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    transcript_text = Column(Text, nullable=True)
    segments = Column(JSON, nullable=True)
    audio = relationship("AudioFile", back_populates="transcripts")
    chunks = relationship("TranscriptionChunk", back_populates="transcript")  # Specifica la chiave esplicitamente
    summary = relationship("TranscriptionSummary", back_populates="transcript")