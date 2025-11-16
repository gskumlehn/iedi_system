from typing import List, Optional
from datetime import datetime
from app.infra.bq_sa import get_session
from app.models.mention import Mention
from app.utils.uuid_generator import generate_uuid


class MentionRepository:
    @staticmethod
    def create(**kwargs) -> Mention:
        if 'url' not in kwargs:
            raise ValueError("Campo 'url' é obrigatório para criar menção")
        
        with get_session() as session:
            if 'id' not in kwargs:
                kwargs['id'] = generate_uuid()
            if 'created_at' not in kwargs:
                kwargs['created_at'] = datetime.now()
            
            mention = Mention(**kwargs)
            session.add(mention)
            session.commit()
            session.refresh(mention)
            return mention

    @staticmethod
    def find_by_url(url: str) -> Optional[Mention]:
        with get_session() as session:
            return session.query(Mention).filter(Mention.url == url).first()
    
    @staticmethod
    def find_by_brandwatch_id(brandwatch_id: str) -> Optional[Mention]:
        with get_session() as session:
            return session.query(Mention).filter(Mention.brandwatch_id == brandwatch_id).first()

    @staticmethod
    def find_or_create(url: str, **kwargs) -> Mention:
        existing = MentionRepository.find_by_url(url)
        if existing:
            return existing
        
        kwargs['url'] = url
        return MentionRepository.create(**kwargs)
    
    @staticmethod
    def extract_unique_url(mention_data: dict) -> str:
        url = mention_data.get('url') or mention_data.get('originalUrl')
        
        if not url:
            raise ValueError(
                f"Menção sem URL: {mention_data.get('id')} - "
                "Campos 'url' e 'originalUrl' vazios"
            )
        
        return url

    @staticmethod
    def find_by_domain(domain: str) -> List[Mention]:
        with get_session() as session:
            return session.query(Mention).filter(Mention.domain == domain).all()

    @staticmethod
    def find_by_date_range(start_date: datetime, end_date: datetime) -> List[Mention]:
        with get_session() as session:
            return session.query(Mention).filter(
                Mention.published_date >= start_date,
                Mention.published_date <= end_date
            ).all()

    @staticmethod
    def update(mention_id: str, **kwargs) -> Optional[Mention]:
        with get_session() as session:
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
