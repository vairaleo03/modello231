from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class TranscriptionSummary(Base): 
    __tablename__ = "transcriptions_summaries"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcript = relationship("Transcript", back_populates="summary", foreign_keys=[transcript_id])