# NOTE: MediaOutlet.niche == True  -> outlet is a "niche" outlet
#       MediaOutlet.niche == False -> outlet is a "relevant" (general) outlet
from typing import List
from app.infra.bq_sa import get_session
from app.models.media_outlet import MediaOutlet
from sqlalchemy.orm import joinedload

class MediaOutletRepository:

    @staticmethod
    def find_by_niche(is_niche: bool) -> List[MediaOutlet]:
        with get_session() as session:
            return session.query(MediaOutlet).options(joinedload('*')).filter(MediaOutlet.niche == is_niche).all()

    @staticmethod
    def find_all_domains() -> List[str]:
        with get_session() as session:
            return [outlet.domain for outlet in session.query(MediaOutlet).options(joinedload('*')).all()]
