from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.iedi_result import IEDIResult
from app.utils.uuid_generator import generate_uuid


class IEDIResultRepository:
    @staticmethod
    def create(**kwargs) -> IEDIResult:
        with get_session() as session:
            if 'id' not in kwargs:
                kwargs['id'] = generate_uuid()
            result = IEDIResult(**kwargs)
            session.add(result)
            session.commit()
            session.refresh(result)
            return result

    @staticmethod
    def find_by_analysis(analysis_id: str) -> List[IEDIResult]:
        with get_session() as session:
            return session.query(IEDIResult).filter(
                IEDIResult.analysis_id == analysis_id
            ).order_by(IEDIResult.final_iedi.desc()).all()

    @staticmethod
    def find_by_analysis_and_bank(analysis_id: str, bank_id: str) -> Optional[IEDIResult]:
        with get_session() as session:
            return session.query(IEDIResult).filter(
                IEDIResult.analysis_id == analysis_id,
                IEDIResult.bank_id == bank_id
            ).first()
