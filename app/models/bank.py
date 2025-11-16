from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy_bigquery import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from app.enums.bank_name import BankName

Base = declarative_base()


class Bank(Base):
    __tablename__ = "banks"
    __table_args__ = {"schema": "iedi"}
    
    id = Column(String, primary_key=True)
    _name = Column("name", String(255), nullable=False)
    variations = Column(ARRAY(String))
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @hybrid_property
    def name(self) -> BankName:
        return BankName.from_value(self._name)

    @name.setter
    def name(self, value: BankName):
        self._name = value.value

    @name.expression
    def name(cls):
        return cls._name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name.value,
            'variations': self.variations or [],
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
