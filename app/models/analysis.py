from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.enums.analysis_status import AnalysisStatus
from app.utils.uuid_generator import generate_uuid

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analysis"
    __table_args__ = {"schema": "iedi"}

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    query_name = Column(String(255), nullable=False)
    _status = Column("status", String(50), default=AnalysisStatus.PENDING.value, nullable=False)
    is_custom_dates = Column(Boolean, default=False, nullable=False)

    @hybrid_property
    def status(self) -> AnalysisStatus:
        return AnalysisStatus[self._status]

    @status.setter
    def status(self, value: AnalysisStatus):
        if not isinstance(value, AnalysisStatus):
            raise ValueError("O status deve ser uma instância válida de AnalysisStatus.")
        self._status = value.name

    @status.expression
    def status(cls):
        return cls._status

