from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mention(Base):
    __tablename__ = "mentions"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, nullable=False)
    bank_id = Column(Integer, nullable=False)
    brandwatch_id = Column(String(255), unique=True)
    category_detail = Column(String(255))
    sentiment = Column(String(20), nullable=False)
    title = Column(Text)
    snippet = Column(Text)
    full_text = Column(Text)
    domain = Column(String(255))
    monthly_visitors = Column(Integer)
    reach_group = Column(String(1))
    published_date = Column(DateTime)
    iedi_score = Column(Float)
    iedi_normalized = Column(Float)
    numerator = Column(Integer)
    denominator = Column(Integer)
    title_verified = Column(Boolean)
    subtitle_verified = Column(Boolean)
    relevant_outlet_verified = Column(Boolean)
    niche_outlet_verified = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
