from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IEDIResult(Base):
    __tablename__ = "iedi_results"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, nullable=False)
    bank_id = Column(Integer, nullable=False)
    total_volume = Column(Integer, default=0)
    positive_volume = Column(Integer, default=0)
    negative_volume = Column(Integer, default=0)
    neutral_volume = Column(Integer, default=0)
    average_iedi = Column(Float, default=0.0)
    final_iedi = Column(Float, default=0.0)
    positivity_rate = Column(Float, default=0.0)
    negativity_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
