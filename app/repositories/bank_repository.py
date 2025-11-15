from typing import List, Optional
from app.infra.mysql_sa import get_session
from app.models.bank import Bank
from app.enums.bank_name import BankName
from app.utils.uuid_generator import generate_uuid


class BankRepository:
    @staticmethod
    def list_all(ativo_only: bool = False) -> List[dict]:
        with get_session() as session:
            query = session.query(Bank)
            if ativo_only:
                query = query.filter(Bank.active == True)
            banks = query.order_by(Bank._name).all()
            return [bank.to_dict() for bank in banks]
    
    @staticmethod
    def get_by_id(bank_id: str) -> Optional[dict]:
        with get_session() as session:
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            return bank.to_dict() if bank else None
    
    @staticmethod
    def create(name: BankName, variations: List[str], active: bool = True) -> str:
        with get_session() as session:
            bank = Bank(id=generate_uuid(), name=name, variations=variations, active=active)
            session.add(bank)
            session.flush()
            return bank.id
    
    @staticmethod
    def update(bank_id: str, name: BankName, variations: List[str], active: bool) -> None:
        with get_session() as session:
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if bank:
                bank.name = name
                bank.variations = variations
                bank.active = active
    
    @staticmethod
    def delete(bank_id: str) -> None:
        with get_session() as session:
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if bank:
                session.delete(bank)
    
    @staticmethod
    def find_all() -> List[Bank]:
        with get_session() as session:
            return session.query(Bank).filter(Bank.active == True).all()
