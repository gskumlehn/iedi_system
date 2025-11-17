from sqlalchemy import Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from app.enums.bank_name import BankName
from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup

Base = declarative_base()

class MentionAnalysis(Base):
    __tablename__ = "mention_analysis"
    __table_args__ = {"schema": "iedi"}

    mention_id = Column(String(36), primary_key=True, nullable=False)
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
    def bank_name(self) -> BankName:
        return BankName[self._bank_name]

    @bank_name.setter
    def bank_name(self, name):
        # accept either BankName enum or a string that already is the enum name
        if isinstance(name, BankName):
            self._bank_name = name.name
        elif isinstance(name, str):
            self._bank_name = name
        else:
            raise ValueError("bank_name must be BankName or str")

    @bank_name.expression
    def bank_name(cls):
        return cls._bank_name

    @hybrid_property
    def sentiment(self) -> Sentiment:
        if self._sentiment:
            return Sentiment[self._sentiment]
        return None

    @sentiment.setter
    def sentiment(self, value):
        # accept either Sentiment enum or string
        if value is None:
            self._sentiment = None
        elif isinstance(value, Sentiment):
            self._sentiment = value.name
        elif isinstance(value, str):
            self._sentiment = value
        else:
            raise ValueError("sentiment must be Sentiment or str")

    @sentiment.expression
    def sentiment(cls):
        return cls._sentiment

    @hybrid_property
    def reach_group(self) -> ReachGroup:
        if self._reach_group:
            return ReachGroup[self._reach_group]
        return None

    @reach_group.setter
    def reach_group(self, value):
        # accept ReachGroup enum or string (name or value)
        if value is None:
            self._reach_group = None
            return
        if isinstance(value, ReachGroup):
            self._reach_group = value.name
            return
        if isinstance(value, str):
            # accept name 'A' or value 'A'
            val_up = value.upper()
            if val_up in ReachGroup.__members__:
                self._reach_group = val_up
                return
            # try match by enum value
            for m in ReachGroup:
                if m.value == value:
                    self._reach_group = m.name
                    return
        raise ValueError("reach_group must be ReachGroup or str")

    @reach_group.expression
    def reach_group(cls):
        return cls._reach_group
