from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import TIMESTAMP
from zoneinfo import ZoneInfo

Base = declarative_base()

class MediaOutlet(Base):
    __tablename__ = "media_outlets"
    __table_args__ = {"schema": "iedi"}

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    monthly_visitors = Column(Integer, nullable=True)
    is_niche = Column(Boolean, default=False, nullable=False)
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'category': self.category,
            'monthly_visitors': self.monthly_visitors,
            'is_niche': self.is_niche,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
