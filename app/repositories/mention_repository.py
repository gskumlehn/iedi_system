from app.infra.bq_sa import get_session
from app.models.mention import Mention
from sqlalchemy.orm import joinedload

class MentionRepository:
    @staticmethod
    def save(mention: Mention) -> Mention:
        with get_session() as session:
            session.add(mention)
            session.commit()
            session.refresh(mention)
            return mention

    @staticmethod
    def update(mention: Mention) -> Mention | None:
        with get_session() as session:
            merged = session.merge(mention)
            session.commit()
            session.refresh(merged)
            return merged

    @staticmethod
    def find_by_url(url: str) -> Mention:
        with get_session() as session:
            return session.query(Mention).options(joinedload('*')).filter(Mention.url == url).first()
