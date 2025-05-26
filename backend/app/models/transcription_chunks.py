from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class TranscriptionChunk(Base):
    __tablename__ = "transcription_chunks"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)  
    chunk_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcript = relationship("Transcript", back_populates="chunks", foreign_keys=[transcript_id])
