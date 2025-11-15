from typing import List
from app.infra.bq_sa import get_session
from app.models.mention import Mention
from app.utils.uuid_generator import generate_uuid

class MentionRepository:

    def create(self, **kwargs) -> Mention:
        session = get_session()
        if 'id' not in kwargs:
            kwargs['id'] = generate_uuid()
        mention = Mention(**kwargs)
        session.add(mention)
        session.commit()
        session.refresh(mention)
        return mention

    def find_by_analysis(self, analysis_id: str) -> List[Mention]:
        session = get_session()
        return session.query(Mention).filter(Mention.analysis_id == analysis_id).all()

    def find_by_analysis_and_bank(self, analysis_id: str, bank_id: str) -> List[Mention]:
        session = get_session()
        return session.query(Mention).filter(
            Mention.analysis_id == analysis_id,
            Mention.bank_id == bank_id
        ).all()
