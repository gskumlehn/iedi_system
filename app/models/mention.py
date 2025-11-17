from datetime import datetime
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import ARRAY, TIMESTAMP
from zoneinfo import ZoneInfo
from typing import List

Base = declarative_base()

class Mention(Base):
    __tablename__ = "mention"
    __table_args__ = {"schema": "iedi"}

    url = Column(String(500), unique=True, nullable=False)

    _categories = Column("categories", ARRAY(String), nullable=True)
    sentiment = Column(String(50), nullable=True)  # Matches the exact column name in the database

    title = Column(Text, nullable=False)
    snippet = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False)
    _published_date = Column("published_date", TIMESTAMP, nullable=False)

    monthly_visitors = Column(Integer, default=0, nullable=False)

    UTC_TZ = ZoneInfo("UTC")
    BR_TZ = ZoneInfo("America/Sao_Paulo")

    @hybrid_property
    def categories(self) -> List[str]:
        return self._categories or []

    @categories.setter
    def categories(self, bank_names: List[str]):
        self._categories = bank_names if bank_names else []

    @categories.expression
    def categories(cls):
        return cls._categories

    @hybrid_property
    def published_date(self) -> datetime:
        if self._published_date is None:
            return None
        return self._published_date.astimezone(self.BR_TZ)

    @published_date.setter
    def published_date(self, value: datetime):
        if value is None:
            self._published_date = None
            return
        if not isinstance(value, datetime):
            raise TypeError("published_date must be a datetime instance")
        self._published_date = value

    @published_date.expression
    def published_date(cls):
        return cls._published_date
