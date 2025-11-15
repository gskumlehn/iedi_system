from datetime import datetime
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo

Base = declarative_base()

class AnalysisMention(Base):
    __tablename__ = "analysis_mentions"
    __table_args__ = {"schema": "iedi"}

    analysis_id = Column(String, primary_key=True, nullable=False)
    mention_id = Column(String, primary_key=True, nullable=False)
    bank_id = Column(String, primary_key=True, nullable=False)
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
