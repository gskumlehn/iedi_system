from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.iedi_result import IEDIResult

class IEDIResultRepository:

    def create(self, **kwargs) -> IEDIResult:
        session = get_session()
        result = IEDIResult(**kwargs)
        session.add(result)
        session.commit()
        session.refresh(result)
        return result

    def find_by_analysis(self, analysis_id: int) -> List[IEDIResult]:
        session = get_session()
        return session.query(IEDIResult).filter(
            IEDIResult.analysis_id == analysis_id
        ).order_by(IEDIResult.final_iedi.desc()).all()

    def find_by_analysis_and_bank(self, analysis_id: int, bank_id: int) -> Optional[IEDIResult]:
        session = get_session()
        return session.query(IEDIResult).filter(
            IEDIResult.analysis_id == analysis_id,
            IEDIResult.bank_id == bank_id
        ).first()
