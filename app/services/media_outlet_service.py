from typing import List
from app.models.media_outlet import NicheMediaOutlet, RelevantMediaOutlet
from app.repositories.media_outlet_repository import NicheMediaOutletRepository, RelevantMediaOutletRepository

class MediaOutletService:

    def __init__(self):
        self.relevant_repo = RelevantMediaOutletRepository()
        self.niche_repo = NicheMediaOutletRepository()

    def get_all_relevant(self) -> List[dict]:
        outlets = self.relevant_repo.find_all_active()
        return [self._relevant_to_dict(o) for o in outlets]

    def get_all_niche(self) -> List[dict]:
        outlets = self.niche_repo.find_all_active()
        return [self._niche_to_dict(o) for o in outlets]

    def _relevant_to_dict(self, outlet: RelevantMediaOutlet) -> dict:
        return {
            "id": outlet.id,
            "name": outlet.name,
            "domain": outlet.domain,
            "category": outlet.category
        }

    def _niche_to_dict(self, outlet: NicheMediaOutlet) -> dict:
        return {
            "id": outlet.id,
            "name": outlet.name,
            "domain": outlet.domain,
            "category": outlet.category,
            "monthly_visitors": outlet.monthly_visitors
        }
