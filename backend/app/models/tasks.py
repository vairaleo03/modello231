from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class TaskStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # es. 'transcription', 'summary'
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)
    result = Column(Text, nullable=True)  # Es. URL del .docx o ID del risultato
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # opzionale se vuoi collegarlo a una trascrizione
    #transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=True)
    #transcript = relationship("Transcript", back_populates="tasks")
