from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base 

class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)  
    file_data = Column(LargeBinary, nullable=False)  
    uploaded_at = Column(DateTime, default=datetime.utcnow)  

    transcripts = relationship("Transcript", back_populates="audio") 
