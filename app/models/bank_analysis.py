from datetime import datetime
from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo
from sqlalchemy.ext.hybrid import hybrid_property
from app.enums.bank_name import BankName

Base = declarative_base()

class BankAnalysis(Base):
    __tablename__ = "bank_analysis"
    __table_args__ = {"schema": "iedi"}

    id = Column(String, primary_key=True)
    analysis_id = Column(String, nullable=False)
    _bank_name = Column("bank_name", String, nullable=False)
    _start_date = Column("start_date", TIMESTAMP, nullable=False)
    _end_date = Column("end_date", TIMESTAMP, nullable=False)
    positive_volume = Column(Float, default=0.0, nullable=True)
    negative_volume = Column(Float, default=0.0, nullable=True)
    iedi_score = Column(Float, nullable=True)

    UTC_TZ = ZoneInfo("UTC")
    BR_TZ = ZoneInfo("America/Sao_Paulo")

    @hybrid_property
    def bank_name(self) -> BankName:
        return BankName[self._bank_name]

    @bank_name.setter
    def bank_name(self, name: BankName):
        self._bank_name = name.name

    @bank_name.expression
    def bank_name(cls):
        return cls._bank_name

    @hybrid_property
    def start_date(self) -> datetime:
        if self._start_date is None:
            return None
        return self._start_date.astimezone(self.BR_TZ)

    @start_date.setter
    def start_date(self, value: datetime):
        if value is None:
            self._start_date = None
            return
        if not isinstance(value, datetime):
            raise TypeError("start_date deve ser uma instância de datetime")
        self._start_date = value

    @start_date.expression
    def start_date(cls):
        return cls._start_date

    @hybrid_property
    def end_date(self) -> datetime:
        if self._end_date is None:
            return None
        return self._end_date.astimezone(self.BR_TZ)

    @end_date.setter
    def end_date(self, value: datetime):
        if value is None:
            self._end_date = None
            return
        if not isinstance(value, datetime):
            raise TypeError("end_date deve ser uma instância de datetime")
        self._end_date = value

    @end_date.expression
    def end_date(cls):
        return cls._end_date

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'bank_name': self.bank_name,  # Changed from bank_id to bank_name
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'positive_volume': self.positive_volume,
            'negative_volume': self.negative_volume,
            'iedi_score': self.iedi_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
