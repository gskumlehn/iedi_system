from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import json

Base = declarative_base()

class Bank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    _variations = Column("variations", Text, nullable=True)  # JSON array as text
    earnings_release_date = Column(DateTime, nullable=True)
    collection_days = Column(Integer, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @hybrid_property
    def variations(self) -> list[str]:
        """Retorna variations como lista Python"""
        if not self._variations:
            return []
        try:
            return json.loads(self._variations)
        except (json.JSONDecodeError, TypeError):
            return []

    @variations.setter
    def variations(self, value: list[str]):
        """Armazena variations como JSON string"""
        if value is None or value == []:
            self._variations = None
        else:
            self._variations = json.dumps(value, ensure_ascii=False)

    @variations.expression
    def variations(cls):
        return cls._variations
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'variations': self.variations,
            'earnings_release_date': self.earnings_release_date.isoformat() if self.earnings_release_date else None,
            'collection_days': self.collection_days,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
