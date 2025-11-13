from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.bank import Bank

class BankRepository:

    def create(self, name: str, variations: List[str]) -> Bank:
        session = get_session()
        bank = Bank(name=name, variations=variations)
        session.add(bank)
        session.commit()
        session.refresh(bank)
        return bank

    def find_by_id(self, bank_id: int) -> Optional[Bank]:
        session = get_session()
        return session.query(Bank).filter(Bank.id == bank_id).first()

    def find_by_name(self, name: str) -> Optional[Bank]:
        session = get_session()
        return session.query(Bank).filter(Bank.name == name).first()

    def find_all_active(self) -> List[Bank]:
        session = get_session()
        return session.query(Bank).filter(Bank.active == True).all()

    def update(self, bank_id: int, **kwargs) -> Optional[Bank]:
        session = get_session()
        bank = session.query(Bank).filter(Bank.id == bank_id).first()
        if bank:
            for key, value in kwargs.items():
                setattr(bank, key, value)
            session.commit()
            session.refresh(bank)
        return bank

    def delete(self, bank_id: int) -> bool:
        session = get_session()
        bank = session.query(Bank).filter(Bank.id == bank_id).first()
        if bank:
            bank.active = False
            session.commit()
            return True
        return False
