from typing import List
from app.models.bank import Bank
from app.repositories.bank_repository import BankRepository

class BankService:

    def __init__(self):
        self.repository = BankRepository()

    def get_all_active(self) -> List[dict]:
        banks = self.repository.find_all_active()
        return [self._to_dict(bank) for bank in banks]

    def _to_dict(self, bank: Bank) -> dict:
        return {
            "id": bank.id,
            "name": bank.name,
            "variations": bank.variations,
            "active": bank.active
        }
