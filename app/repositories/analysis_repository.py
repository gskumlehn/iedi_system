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
            analysis = session.query(Analysis).options(joinedload('*')).filter(Analysis.id == analysis_id).one_or_none()
            if analysis:
                session.expunge(analysis)  # Detach the object from the session
            return analysis

    @staticmethod
    def find_all():
        with get_session() as session:
            return session.query(Analysis).order_by(Analysis.created_at.desc()).all()

    @staticmethod
    def update(analysis: Analysis):
        with get_session() as session:
            session.merge(analysis)
            session.commit()
