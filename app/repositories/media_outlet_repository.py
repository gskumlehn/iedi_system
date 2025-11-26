from typing import List, Dict
from app.infra.bq_sa import get_session
from app.models.media_outlet import MediaOutlet
from sqlalchemy.orm import joinedload
from sqlalchemy import inspect

class MediaOutletRepository:

    @staticmethod
    def find_by_niche(is_niche: bool) -> List[MediaOutlet]:
        with get_session() as session:
            rows = session.query(MediaOutlet).filter(MediaOutlet.is_niche == is_niche).all()
            # ensure column attributes are loaded and detach instances so they can be used outside the session
            for r in rows:
                for col in r.__table__.columns:
                    getattr(r, col.key)
                session.expunge(r)
            return rows

    @staticmethod
    def find_all_domains() -> List[str]:
        with get_session() as session:
            rows = session.query(MediaOutlet).all()
            return [getattr(outlet, 'domain') for outlet in rows]
