from datetime import datetime
from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.bank_period import BankPeriod
from app.utils.uuid_generator import generate_uuid


class BankPeriodRepository:
    @staticmethod
    def create(analysis_id: str, bank_id: str, category_detail: str, 
               start_date: datetime, end_date: datetime) -> BankPeriod:
        with get_session() as session:
            period = BankPeriod(
                id=generate_uuid(),
                analysis_id=analysis_id,
                bank_id=bank_id,
                category_detail=category_detail,
                start_date=start_date,
                end_date=end_date
            )
            session.add(period)
            session.commit()
            session.refresh(period)
            return period

    @staticmethod
    def find_by_analysis(analysis_id: str) -> List[BankPeriod]:
        with get_session() as session:
            return session.query(BankPeriod).filter(BankPeriod.analysis_id == analysis_id).all()

    @staticmethod
    def find_by_analysis_and_bank(analysis_id: str, bank_id: str) -> Optional[BankPeriod]:
        with get_session() as session:
            return session.query(BankPeriod).filter(
                BankPeriod.analysis_id == analysis_id,
                BankPeriod.bank_id == bank_id
            ).first()
