from datetime import datetime
from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo

Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analysis"
    __table_args__ = {"schema": "iedi"}

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    query_name = Column(String(255), nullable=False)
    _start_date = Column("start_date", TIMESTAMP, nullable=False)
    _end_date = Column("end_date", TIMESTAMP, nullable=False)
    custom_period = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default='pending', nullable=False)
    _created_at = Column("created_at", TIMESTAMP, nullable=False)
    _updated_at = Column("updated_at", TIMESTAMP, nullable=False)

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
            raise TypeError("start_date must be a datetime instance")
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
            raise TypeError("end_date must be a datetime instance")
        self._end_date = value

    @end_date.expression
    def end_date(cls):
        return cls._end_date

    @hybrid_property
    def updated_at(self) -> datetime:
        if self._updated_at is None:
            return None
        return self._updated_at.astimezone(self.BR_TZ)

    @updated_at.setter
    def updated_at(self, value: datetime):
        if value is None:
            self._updated_at = None
            return
        if not isinstance(value, datetime):
            raise TypeError("updated_at must be a datetime instance")
        self._updated_at = value

    @updated_at.expression
    def updated_at(cls):
        return cls._updated_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'query_name': self.query_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'custom_period': self.custom_period,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
