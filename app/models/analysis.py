from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    custom_period = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BankPeriod(Base):
    __tablename__ = "bank_periods"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, nullable=False)
    bank_id = Column(Integer, nullable=False)
    category_detail = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_mentions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
