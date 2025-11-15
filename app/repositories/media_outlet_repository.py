from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.media_outlet import MediaOutlet
from app.utils.uuid_generator import generate_uuid


class MediaOutletRepository:
    @staticmethod
    def list_all(is_niche: Optional[bool] = None, active_only: bool = True) -> List[dict]:
        session = get_session()
        query = session.query(MediaOutlet)
        
        if active_only:
            query = query.filter(MediaOutlet.active == True)
        
        if is_niche is not None:
            query = query.filter(MediaOutlet.is_niche == is_niche)
        
        outlets = query.all()
        return [outlet.to_dict() for outlet in outlets]
    
    @staticmethod
    def get_by_id(outlet_id: str) -> Optional[dict]:
        session = get_session()
        outlet = session.query(MediaOutlet).filter(MediaOutlet.id == outlet_id).first()
        return outlet.to_dict() if outlet else None
    
    @staticmethod
    def create(name: str, domain: str, category: Optional[str], monthly_visitors: Optional[int], is_niche: bool) -> dict:
        session = get_session()
        outlet = MediaOutlet(
            id=generate_uuid(),
            name=name,
            domain=domain,
            category=category,
            monthly_visitors=monthly_visitors,
            is_niche=is_niche,
            active=True
        )
        session.add(outlet)
        session.commit()
        session.refresh(outlet)
        return outlet.to_dict()
    
    @staticmethod
    def update(outlet_id: str, name: Optional[str] = None, domain: Optional[str] = None, 
               category: Optional[str] = None, monthly_visitors: Optional[int] = None, 
               is_niche: Optional[bool] = None, active: Optional[bool] = None) -> Optional[dict]:
        session = get_session()
        outlet = session.query(MediaOutlet).filter(MediaOutlet.id == outlet_id).first()
        
        if not outlet:
            return None
        
        if name is not None:
            outlet.name = name
        if domain is not None:
            outlet.domain = domain
        if category is not None:
            outlet.category = category
        if monthly_visitors is not None:
            outlet.monthly_visitors = monthly_visitors
        if is_niche is not None:
            outlet.is_niche = is_niche
        if active is not None:
            outlet.active = active
        
        session.commit()
        session.refresh(outlet)
        return outlet.to_dict()
    
    @staticmethod
    def delete(outlet_id: str) -> bool:
        session = get_session()
        outlet = session.query(MediaOutlet).filter(MediaOutlet.id == outlet_id).first()
        
        if not outlet:
            return False
        
        session.delete(outlet)
        session.commit()
        return True
    
    @staticmethod
    def find_all_active(is_niche: Optional[bool] = None) -> List[MediaOutlet]:
        session = get_session()
        query = session.query(MediaOutlet).filter(MediaOutlet.active == True)
        
        if is_niche is not None:
            query = query.filter(MediaOutlet.is_niche == is_niche)
        
        return query.all()
    
    @staticmethod
    def find_by_domain(domain: str) -> Optional[MediaOutlet]:
        session = get_session()
        return session.query(MediaOutlet).filter(MediaOutlet.domain == domain).first()
