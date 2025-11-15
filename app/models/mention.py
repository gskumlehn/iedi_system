from datetime import datetime
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_bigquery import ARRAY, TIMESTAMP
from zoneinfo import ZoneInfo

from app.enums.bank_name import BankName
from app.enums.reach_group import ReachGroup
from app.enums.sentiment import Sentiment

Base = declarative_base()


class Mention(Base):
    __tablename__ = "mentions"
    __table_args__ = {"schema": "iedi"}

    id = Column(String(36), primary_key=True)
    url = Column(String(500), unique=True, nullable=False)
    brandwatch_id = Column(String(255), nullable=True)
    original_url = Column(String(500), nullable=True)
    
    _categories = Column("categories", ARRAY(String), nullable=False)
    _sentiment = Column("sentiment", String(50), nullable=False)
    title = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    domain = Column(String(255), nullable=True)
    _published_date = Column("published_date", TIMESTAMP, nullable=True)
    
    media_outlet_id = Column(String(36), nullable=True)
    monthly_visitors = Column(Integer, default=0, nullable=False)
    _reach_group = Column("reach_group", String(10), nullable=False)
    
    _created_at = Column("created_at", TIMESTAMP, nullable=False)
    _updated_at = Column("updated_at", TIMESTAMP, nullable=True)

    UTC_TZ = ZoneInfo("UTC")
    BR_TZ = ZoneInfo("America/Sao_Paulo")

    @hybrid_property
    def categories(self) -> list[BankName]:
        return [BankName.from_name(name) for name in self._categories or []]

    @categories.setter
    def categories(self, bank_names: list[BankName]):
        self._categories = [bank.name for bank in bank_names] if bank_names else []

    @categories.expression
    def categories(cls):
        return cls._categories

    @hybrid_property
    def sentiment(self) -> Sentiment:
        return Sentiment.from_name(self._sentiment)

    @sentiment.setter
    def sentiment(self, value: Sentiment):
        self._sentiment = value.name

    @sentiment.expression
    def sentiment(cls):
        return cls._sentiment

    @hybrid_property
    def reach_group(self) -> ReachGroup:
        return ReachGroup.from_name(self._reach_group)

    @reach_group.setter
    def reach_group(self, value: ReachGroup):
        self._reach_group = value.name

    @reach_group.expression
    def reach_group(cls):
        return cls._reach_group

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
            'url': self.url,
            'brandwatch_id': self.brandwatch_id,
            'original_url': self.original_url,
            'categories': [cat.name for cat in self.categories] if self.categories else [],
            'sentiment': self.sentiment.name if self.sentiment else None,
            'title': self.title,
            'snippet': self.snippet,
            'full_text': self.full_text,
            'domain': self.domain,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'media_outlet_id': self.media_outlet_id,
            'monthly_visitors': self.monthly_visitors,
            'reach_group': self.reach_group.name if self.reach_group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
