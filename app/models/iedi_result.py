from datetime import datetime
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo

Base = declarative_base()

class IEDIResult(Base):
    __tablename__ = "iedi_result"
    __table_args__ = {"schema": "iedi"}

    id = Column(String, primary_key=True)
    analysis_id = Column(String, nullable=False)
    bank_id = Column(String, nullable=False)
    total_volume = Column(Integer, default=0, nullable=False)
    positive_volume = Column(Integer, default=0, nullable=False)
    negative_volume = Column(Integer, default=0, nullable=False)
    neutral_volume = Column(Integer, default=0, nullable=False)
    average_iedi = Column(Float, default=0.0, nullable=False)
    final_iedi = Column(Float, default=0.0, nullable=False)
    positivity_rate = Column(Float, default=0.0, nullable=False)
    negativity_rate = Column(Float, default=0.0, nullable=False)
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
            'id': self.id,
            'analysis_id': self.analysis_id,
            'bank_id': self.bank_id,
            'total_volume': self.total_volume,
            'positive_volume': self.positive_volume,
            'negative_volume': self.negative_volume,
            'neutral_volume': self.neutral_volume,
            'average_iedi': self.average_iedi,
            'final_iedi': self.final_iedi,
            'positivity_rate': self.positivity_rate,
            'negativity_rate': self.negativity_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
