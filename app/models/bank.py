from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy_bigquery import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    variations = Column(ARRAY(String))
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'variations': self.variations or [],
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
