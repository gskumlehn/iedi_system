from sqlalchemy import Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from app.enums.bank_name import BankName
from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup
import uuid

Base = declarative_base()

class MentionAnalysis(Base):
    __tablename__ = "mention_analysis"
    __table_args__ = {"schema": "iedi"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mention_id = Column(String(36), nullable=False)
    _bank_name = Column("bank_name", String, nullable=False)

    _sentiment = Column("sentiment", String, nullable=True)
    _reach_group = Column("reach_group", String, nullable=True)

    niche_vehicle = Column(Boolean, nullable=True)
    title_mentioned = Column(Boolean, nullable=True)
    subtitle_used = Column(Boolean, nullable=True)        # whether subtitle was analyzed (snippet != fullText)
    subtitle_mentioned = Column(Boolean, nullable=True)

    iedi_score = Column(Float, nullable=True)
    iedi_normalized = Column(Float, nullable=True)
    numerator = Column(Integer, nullable=True)
    denominator = Column(Integer, nullable=True)

    @hybrid_property
    def bank_name(self):
        return BankName[self._bank_name]

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value.name

    @hybrid_property
    def sentiment(self):
        return Sentiment[self._sentiment] if self._sentiment else None

    @sentiment.setter
    def sentiment(self, value):
        self._sentiment = value.name if value else None

    @hybrid_property
    def reach_group(self):
        return ReachGroup[self._reach_group] if self._reach_group else None

    @reach_group.setter
    def reach_group(self, value):
        self._reach_group = value.name if value else None

    @bank_name.expression
    def bank_name(cls):
        return cls._bank_name

    @sentiment.expression
    def sentiment(cls):
        return cls._sentiment

    @reach_group.expression
    def reach_group(cls):
        return cls._reach_group
