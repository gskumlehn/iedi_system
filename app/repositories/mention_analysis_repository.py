from typing import List, Optional
from datetime import datetime
from app.infra.bq_sa import get_session
from app.models.mention_analysis import MentionAnalysis

class MentionAnalysisRepository:

    @staticmethod
    def create(analysis_id: str, mention_id: str, bank_id: str, **kwargs) -> MentionAnalysis:
        with get_session() as session:
            mention_analysis = MentionAnalysis(
                analysis_id=analysis_id,
                mention_id=mention_id,
                bank_id=bank_id,
                created_at=datetime.now(),
                **kwargs
            )
            session.add(mention_analysis)
            session.commit()
            session.refresh(mention_analysis)
            return mention_analysis

    @staticmethod
    def find_by_mention(mention_id: str) -> List[MentionAnalysis]:
        with get_session() as session:
            return session.query(MentionAnalysis).filter(
                MentionAnalysis.mention_id == mention_id
            ).all()

    @staticmethod
    def update_iedi_scores(analysis_id: str, mention_id: str, bank_id: str,
                          iedi_score: float, numerator: int, denominator: int, **kwargs) -> Optional[MentionAnalysis]:
        with get_session() as session:
            mention_analysis = session.query(MentionAnalysis).filter(
                MentionAnalysis.analysis_id == analysis_id,
                MentionAnalysis.mention_id == mention_id,
                MentionAnalysis.bank_id == bank_id
            ).first()

            if not mention_analysis:
                return None

            mention_analysis.iedi_score = iedi_score
            mention_analysis.numerator = numerator
            mention_analysis.denominator = denominator

            for key, value in kwargs.items():
                if hasattr(mention_analysis, key):
                    setattr(mention_analysis, key, value)

            session.commit()
            session.refresh(mention_analysis)
            return mention_analysis

    @staticmethod
    def bulk_save(mention_analyses: List[MentionAnalysis]):
       with get_session() as session:
            session.add_all(mention_analyses)
            session.commit()

    @staticmethod
    def find_by_bank_name(bank_name):
        """Busca todos os MentionAnalysis de um banco"""
        with get_session() as session:
            return session.query(MentionAnalysis).filter(
                MentionAnalysis._bank_name == bank_name.name
            ).all()

    @staticmethod
    def find_by_mention_id_and_bank_name(mention_id: str, bank_name: str) -> Optional[MentionAnalysis]:
        with get_session() as session:
            return session.query(MentionAnalysis).filter(
                MentionAnalysis.mention_id == mention_id,
                MentionAnalysis._bank_name == bank_name
            ).first()

    @staticmethod
    def update(existing_analysis: MentionAnalysis, new_analysis: MentionAnalysis):
        with get_session() as session:
            for attr in vars(new_analysis):
                if hasattr(existing_analysis, attr):
                    setattr(existing_analysis, attr, getattr(new_analysis, attr))
            session.commit()

    @staticmethod
    def save(analysis: MentionAnalysis):
        with get_session() as session:
            session.add(analysis)
            session.commit()
