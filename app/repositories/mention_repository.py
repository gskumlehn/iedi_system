from typing import List, Optional
from datetime import datetime
from app.infra.bq_sa import get_session
from app.models.mention import Mention
from app.models.analysis_mention import AnalysisMention
from app.utils.uuid_generator import generate_uuid


class MentionRepository:
    def create(self, **kwargs) -> Mention:
        if 'url' not in kwargs:
            raise ValueError("Campo 'url' é obrigatório para criar menção")
        
        session = get_session()
        if 'id' not in kwargs:
            kwargs['id'] = generate_uuid()
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()
        
        mention = Mention(**kwargs)
        session.add(mention)
        session.commit()
        session.refresh(mention)
        return mention

    def find_by_url(self, url: str) -> Optional[Mention]:
        session = get_session()
        return session.query(Mention).filter(
            Mention.url == url
        ).first()
    
    def find_by_brandwatch_id(self, brandwatch_id: str) -> Optional[Mention]:
        session = get_session()
        return session.query(Mention).filter(
            Mention.brandwatch_id == brandwatch_id
        ).first()

    def find_or_create(self, url: str, **kwargs) -> Mention:
        existing = self.find_by_url(url)
        if existing:
            return existing
        
        kwargs['url'] = url
        return self.create(**kwargs)
    
    @staticmethod
    def extract_unique_url(mention_data: dict) -> str:
        url = mention_data.get('url') or mention_data.get('originalUrl')
        
        if not url:
            raise ValueError(
                f"Menção sem URL: {mention_data.get('id')} - "
                "Campos 'url' e 'originalUrl' vazios"
            )
        
        return url

    def find_by_domain(self, domain: str) -> List[Mention]:
        session = get_session()
        return session.query(Mention).filter(Mention.domain == domain).all()

    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Mention]:
        session = get_session()
        return session.query(Mention).filter(
            Mention.published_date >= start_date,
            Mention.published_date <= end_date
        ).all()

    def update(self, mention_id: str, **kwargs) -> Optional[Mention]:
        session = get_session()
        mention = session.query(Mention).filter(Mention.id == mention_id).first()
        
        if not mention:
            return None
        
        for key, value in kwargs.items():
            if hasattr(mention, key):
                setattr(mention, key, value)
        
        mention.updated_at = datetime.now()
        session.commit()
        session.refresh(mention)
        return mention


class AnalysisMentionRepository:
    def create(self, analysis_id: str, mention_id: str, bank_id: str, **kwargs) -> AnalysisMention:
        session = get_session()
        
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

    def find_by_analysis(self, analysis_id: str) -> List[AnalysisMention]:
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id
        ).all()

    def find_by_analysis_and_bank(self, analysis_id: str, bank_id: str) -> List[AnalysisMention]:
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id,
            AnalysisMention.bank_id == bank_id
        ).all()

    def find_by_mention(self, mention_id: str) -> List[AnalysisMention]:
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.mention_id == mention_id
        ).all()

    def find_by_key(self, analysis_id: str, mention_id: str, bank_id: str) -> Optional[AnalysisMention]:
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id,
            AnalysisMention.mention_id == mention_id,
            AnalysisMention.bank_id == bank_id
        ).first()

    def update_iedi_scores(self, analysis_id: str, mention_id: str, bank_id: str, 
                          iedi_score: float, numerator: int, denominator: int, **kwargs) -> Optional[AnalysisMention]:
        session = get_session()
        analysis_mention = self.find_by_key(analysis_id, mention_id, bank_id)
        
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
