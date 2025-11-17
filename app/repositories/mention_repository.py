from app.infra.bq_sa import get_session
from app.models.mention import Mention

class MentionRepository:
    @staticmethod
    def save(mention: Mention) -> Mention:
        with get_session() as session:
            session.add(mention)
            session.commit()
            session.refresh(mention)
            return mention

    @staticmethod
    def update(mention: Mention) -> Mention:
        with get_session() as session:
            existing_mention = session.query(Mention).filter(Mention.url == mention.url).first()
            if existing_mention:
                existing_mention.title = mention.title
                existing_mention.snippet = mention.snippet
                existing_mention.full_text = mention.full_text
                existing_mention.published_date = mention.published_date
                existing_mention.sentiment = mention.sentiment
                existing_mention.categories = mention.categories
                existing_mention.monthly_visitors = mention.monthly_visitors
                session.commit()
                session.refresh(existing_mention)
                return existing_mention
            else:
                raise ValueError("Mention not found for update")

    @staticmethod
    def find_by_url(url: str) -> Mention:
        with get_session() as session:
            return session.query(Mention).filter(Mention.url == url).first()
