from typing import List, Optional
from datetime import datetime
from app.infra.bq_sa import get_session
from app.models.analysis_mention import AnalysisMention


class AnalysisMentionRepository:
    @staticmethod
    def create(analysis_id: str, mention_id: str, bank_id: str, **kwargs) -> AnalysisMention:
        with get_session() as session:
            analysis_mention = AnalysisMention(
                analysis_id=analysis_id,
                mention_id=mention_id,
                bank_id=bank_id,
                created_at=datetime.now(),
                **kwargs
            )
            session.add(analysis_mention)
            session.commit()
            session.refresh(analysis_mention)
            return analysis_mention

    @staticmethod
    def find_by_analysis(analysis_id: str) -> List[AnalysisMention]:
        with get_session() as session:
            return session.query(AnalysisMention).filter(
                AnalysisMention.analysis_id == analysis_id
            ).all()

    @staticmethod
    def find_by_analysis_and_bank(analysis_id: str, bank_id: str) -> List[AnalysisMention]:
        with get_session() as session:
            return session.query(AnalysisMention).filter(
                AnalysisMention.analysis_id == analysis_id,
                AnalysisMention.bank_id == bank_id
            ).all()

    @staticmethod
    def find_by_mention(mention_id: str) -> List[AnalysisMention]:
        with get_session() as session:
            return session.query(AnalysisMention).filter(
                AnalysisMention.mention_id == mention_id
            ).all()

    @staticmethod
    def find_by_key(analysis_id: str, mention_id: str, bank_id: str) -> Optional[AnalysisMention]:
        with get_session() as session:
            return session.query(AnalysisMention).filter(
                AnalysisMention.analysis_id == analysis_id,
                AnalysisMention.mention_id == mention_id,
                AnalysisMention.bank_id == bank_id
            ).first()

    @staticmethod
    def update_iedi_scores(analysis_id: str, mention_id: str, bank_id: str, 
                          iedi_score: float, numerator: int, denominator: int, **kwargs) -> Optional[AnalysisMention]:
        with get_session() as session:
            analysis_mention = session.query(AnalysisMention).filter(
                AnalysisMention.analysis_id == analysis_id,
                AnalysisMention.mention_id == mention_id,
                AnalysisMention.bank_id == bank_id
            ).first()
            
            if not analysis_mention:
                return None
            
            analysis_mention.iedi_score = iedi_score
            analysis_mention.numerator = numerator
            analysis_mention.denominator = denominator
            
            for key, value in kwargs.items():
                if hasattr(analysis_mention, key):
                    setattr(analysis_mention, key, value)
            
            session.commit()
            session.refresh(analysis_mention)
            return analysis_mention
