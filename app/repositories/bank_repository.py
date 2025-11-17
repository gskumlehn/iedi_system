from typing import Optional
from app.infra.bq_sa import get_session
from app.models.bank import Bank
from app.enums.bank_name import BankName

class BankRepository:

    @staticmethod
    def find_by_name(name: BankName) -> Optional[Bank]:
        with get_session() as session:
            return session.query(Bank).filter(Bank.name == name.name).one_or_none()
