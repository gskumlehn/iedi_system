from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.bank import Bank
from app.enums.bank_name import BankName
from app.utils.uuid_generator import generate_uuid


class BankRepository:
    @staticmethod
    def create(name: BankName, variations: List[str], active: bool = True) -> str:
        with get_session() as session:
            bank = Bank(
                id=generate_uuid(),
                name=name,
                variations=variations,
                active=active
            )
            session.add(bank)
            session.commit()
            return bank.id

    @staticmethod
    def find_by_id(bank_id: str) -> Optional[Bank]:
        with get_session() as session:
            return session.query(Bank).filter(Bank.id == bank_id).first()

    @staticmethod
    def find_all() -> List[Bank]:
        with get_session() as session:
            return session.query(Bank).filter(Bank.active == True).order_by(Bank._name).all()

    @staticmethod
    def update(bank_id: str, name: BankName, variations: List[str], active: bool) -> None:
        with get_session() as session:
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if bank:
                bank.name = name
                bank.variations = variations
                bank.active = active
                session.commit()

    @staticmethod
    def delete(bank_id: str) -> None:
        with get_session() as session:
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if bank:
                bank.active = False
                session.commit()
