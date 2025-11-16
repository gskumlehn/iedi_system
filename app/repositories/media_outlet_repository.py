from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.media_outlet import MediaOutlet
from app.utils.uuid_generator import generate_uuid


class MediaOutletRepository:
    @staticmethod
    def create(name: str, domain: str, monthly_visitors: int, is_niche: bool, active: bool = True) -> str:
        with get_session() as session:
            outlet = MediaOutlet(
                id=generate_uuid(),
                name=name,
                domain=domain,
                monthly_visitors=monthly_visitors,
                is_niche=is_niche,
                active=active
            )
            session.add(outlet)
            session.commit()
            return outlet.id

    @staticmethod
    def find_by_id(outlet_id: str) -> Optional[MediaOutlet]:
        with get_session() as session:
            return session.query(MediaOutlet).filter(MediaOutlet.id == outlet_id).first()

    @staticmethod
    def find_by_domain(domain: str) -> Optional[MediaOutlet]:
        with get_session() as session:
            return session.query(MediaOutlet).filter(MediaOutlet.domain == domain).first()

    @staticmethod
    def find_all() -> List[MediaOutlet]:
        with get_session() as session:
            return session.query(MediaOutlet).filter(MediaOutlet.active == True).all()

    @staticmethod
    def update(outlet_id: str, name: str, domain: str, monthly_visitors: int, is_niche: bool, active: bool) -> None:
        with get_session() as session:
            outlet = session.query(MediaOutlet).filter(MediaOutlet.id == outlet_id).first()
            if outlet:
                outlet.name = name
                outlet.domain = domain
                outlet.monthly_visitors = monthly_visitors
                outlet.is_niche = is_niche
                outlet.active = active
                session.commit()

    @staticmethod
    def delete(outlet_id: str) -> None:
        with get_session() as session:
            outlet = session.query(MediaOutlet).filter(MediaOutlet.id == outlet_id).first()
            if outlet:
                outlet.active = False
                session.commit()
