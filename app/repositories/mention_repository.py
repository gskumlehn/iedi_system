from typing import List
from app.infra.bq_sa import get_session
from app.models.mention import Mention

class MentionRepository:

    def create(self, **kwargs) -> Mention:
        session = get_session()
        mention = Mention(**kwargs)
        session.add(mention)
        session.commit()
        session.refresh(mention)
        return mention

    def find_by_analysis(self, analysis_id: int) -> List[Mention]:
        session = get_session()
        return session.query(Mention).filter(Mention.analysis_id == analysis_id).all()

    def find_by_analysis_and_bank(self, analysis_id: int, bank_id: int) -> List[Mention]:
        session = get_session()
        return session.query(Mention).filter(
            Mention.analysis_id == analysis_id,
            Mention.bank_id == bank_id
        ).all()
