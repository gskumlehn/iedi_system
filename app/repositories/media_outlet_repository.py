from typing import List
from app.infra.bq_sa import get_session
from app.models.media_outlet import NicheMediaOutlet, RelevantMediaOutlet

class RelevantMediaOutletRepository:

    def find_all_active(self) -> List[RelevantMediaOutlet]:
        session = get_session()
        return session.query(RelevantMediaOutlet).filter(RelevantMediaOutlet.active == True).all()

class NicheMediaOutletRepository:

    def find_all_active(self) -> List[NicheMediaOutlet]:
        session = get_session()
        return session.query(NicheMediaOutlet).filter(NicheMediaOutlet.active == True).all()
