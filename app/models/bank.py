from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bank(Base):
    __tablename__ = "banks"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    variations = Column(JSON, nullable=False, default=list)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
