from app.infra.bq_sa import get_session
from app.models.analysis import Analysis
from sqlalchemy.orm import make_transient, joinedload
from typing import Optional

class AnalysisRepository:

    @staticmethod
    def save(analysis: Analysis):
        with get_session() as session:
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            session.expunge(analysis)
            make_transient(analysis)
            return analysis

    @staticmethod
    def find_by_id(analysis_id: str) -> Optional[Analysis]:
        with get_session() as session:
            return session.query(Analysis).options(joinedload('*')).filter(Analysis.id == analysis_id).one_or_none()
