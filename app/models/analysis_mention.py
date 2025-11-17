from datetime import datetime
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo

Base = declarative_base()

class MentionAnalysis(Base):
    __tablename__ = "mention_analysis"
    __table_args__ = {"schema": "iedi"}

    analysis_id = Column(String(36), primary_key=True, nullable=False)
    mention_id = Column(String(36), primary_key=True, nullable=False)
    bank_id = Column(String(36), primary_key=True, nullable=False)
    
    iedi_score = Column(Float, nullable=True)
    iedi_normalized = Column(Float, nullable=True)
    numerator = Column(Integer, nullable=True)
    denominator = Column(Integer, nullable=True)
    
    title_verified = Column(Integer, default=0, nullable=False)
    subtitle_verified = Column(Integer, default=0, nullable=False)
    relevant_outlet_verified = Column(Integer, default=0, nullable=False)
    niche_outlet_verified = Column(Integer, default=0, nullable=False)
    
    _created_at = Column("created_at", TIMESTAMP, nullable=False)

    UTC_TZ = ZoneInfo("UTC")
    BR_TZ = ZoneInfo("America/Sao_Paulo")

    @hybrid_property
    def created_at(self) -> datetime:
        if self._created_at is None:
            return None
        return self._created_at.astimezone(self.BR_TZ)

    @created_at.setter
    def created_at(self, value: datetime):
        if value is None:
            self._created_at = None
            return
        if not isinstance(value, datetime):
            raise TypeError("created_at must be a datetime instance")
        self._created_at = value

    @created_at.expression
    def created_at(cls):
        return cls._created_at

    def to_dict(self):
        return {
            'analysis_id': self.analysis_id,
            'mention_id': self.mention_id,
            'bank_id': self.bank_id,
            'iedi_score': self.iedi_score,
            'iedi_normalized': self.iedi_normalized,
            'numerator': self.numerator,
            'denominator': self.denominator,
            'title_verified': self.title_verified,
            'subtitle_verified': self.subtitle_verified,
            'relevant_outlet_verified': self.relevant_outlet_verified,
            'niche_outlet_verified': self.niche_outlet_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
