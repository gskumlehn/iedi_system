from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.analysis import Analysis
from app.utils.uuid_generator import generate_uuid


class AnalysisRepository:
    @staticmethod
    def create(name: str, query: str, custom_period: bool) -> Analysis:
        session = get_session()
        analysis = Analysis(id=generate_uuid(), name=name, query=query, custom_period=custom_period)
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        return analysis

    @staticmethod
    def find_by_id(analysis_id: str) -> Optional[Analysis]:
        session = get_session()
        return session.query(Analysis).filter(Analysis.id == analysis_id).first()

    @staticmethod
    def find_all() -> List[Analysis]:
        session = get_session()
        return session.query(Analysis).order_by(Analysis.created_at.desc()).all()
