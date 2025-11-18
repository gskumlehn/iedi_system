from app.models.bank_analysis import BankAnalysis
from app.infra.bq_sa import get_session

class BankAnalysisRepository:

    @staticmethod
    def save(bank_analysis: BankAnalysis):
        with get_session() as session:
            session.add(bank_analysis)
            session.commit()

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
            return session.query(BankAnalysis).filter(
                BankAnalysis.analysis_id == analysis_id
            ).all()
