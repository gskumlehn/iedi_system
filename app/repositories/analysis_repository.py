from datetime import datetime
from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.analysis import Analysis, BankPeriod

class AnalysisRepository:

    def create(self, name: str, query: str, custom_period: bool) -> Analysis:
        session = get_session()
        analysis = Analysis(name=name, query=query, custom_period=custom_period)
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        return analysis

    def find_by_id(self, analysis_id: int) -> Optional[Analysis]:
        session = get_session()
        return session.query(Analysis).filter(Analysis.id == analysis_id).first()

    def find_all(self) -> List[Analysis]:
        session = get_session()
        return session.query(Analysis).order_by(Analysis.created_at.desc()).all()

class BankPeriodRepository:

    def create(self, analysis_id: int, bank_id: int, category_detail: str, 
               start_date: datetime, end_date: datetime) -> BankPeriod:
        session = get_session()
        period = BankPeriod(
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

    def find_by_analysis(self, analysis_id: int) -> List[BankPeriod]:
        session = get_session()
        return session.query(BankPeriod).filter(BankPeriod.analysis_id == analysis_id).all()

    def find_by_analysis_and_bank(self, analysis_id: int, bank_id: int) -> Optional[BankPeriod]:
        session = get_session()
        return session.query(BankPeriod).filter(
            BankPeriod.analysis_id == analysis_id,
            BankPeriod.bank_id == bank_id
        ).first()
