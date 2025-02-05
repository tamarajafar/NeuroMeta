from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Study(Base):
    __tablename__ = 'studies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    authors = Column(String)
    publication_date = Column(DateTime)
    keywords = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    brain_maps = relationship("BrainMap", back_populates="study")

class BrainMap(Base):
    __tablename__ = 'brain_maps'
    
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer, ForeignKey('studies.id'))
    map_type = Column(String)  # 'vbm', 'ale', etc.
    data = Column(LargeBinary, nullable=False)  # Store NIfTI data
    statistics = Column(String)  # JSON string of statistics
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    study = relationship("Study", back_populates="brain_maps")
