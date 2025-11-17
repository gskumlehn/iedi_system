from app.infra.bq_sa import get_session
from app.models.analysis import Analysis

class AnalysisRepository:

    @staticmethod
    def save(analysis: Analysis):
        with get_session() as session:
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
        return analysis
