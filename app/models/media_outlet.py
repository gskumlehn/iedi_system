from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo

Base = declarative_base()

class RelevantMediaOutlet(Base):
    __tablename__ = "relevant_media_outlets"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
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

class NicheMediaOutlet(Base):
    __tablename__ = "niche_media_outlets"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    monthly_visitors = Column(Integer, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
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
