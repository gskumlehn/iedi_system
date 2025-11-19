from app.models.bank_analysis import BankAnalysis
from app.infra.bq_sa import get_session
from sqlalchemy.orm import joinedload, make_transient

class BankAnalysisRepository:

    @staticmethod
    def save(bank_analysis: BankAnalysis):
        with get_session() as session:
            session.add(bank_analysis)
            session.commit()
            session.refresh(bank_analysis)
            return bank_analysis

    @staticmethod
    def update(bank_analysis: BankAnalysis) -> BankAnalysis | None:
        with get_session() as session:
            merged = session.merge(bank_analysis)
            session.commit()
            session.refresh(merged)
            return merged

    @staticmethod
    def find_by_analysis_id(analysis_id: str):
        """Busca todos os BankAnalysis de uma análise"""
        with get_session() as session:
            bank_analyses = session.query(BankAnalysis).options(joinedload('*')).filter(
                BankAnalysis.analysis_id == analysis_id
            ).all()
            # Ensure all objects are bound to the session
            for ba in bank_analyses:
                session.expunge(ba)
                make_transient(ba)
            return bank_analyses

    @staticmethod
    def find_by_id(bank_analysis_id: str) -> BankAnalysis:
        with get_session() as session:
            return session.query(BankAnalysis).options(joinedload('*')).filter(BankAnalysis.id == bank_analysis_id).one_or_none()
