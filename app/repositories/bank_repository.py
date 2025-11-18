from typing import Optional
from app.infra.bq_sa import get_session
from app.models.bank import Bank
from app.enums.bank_name import BankName
from sqlalchemy.orm import make_transient

class BankRepository:

    @staticmethod
    def find_by_name(name: BankName) -> Optional[Bank]:
        with get_session() as session:
            bank = session.query(Bank).filter(Bank._name == name.name).one_or_none()
            if bank:
                session.expunge(bank)
                make_transient(bank)
            return bank
