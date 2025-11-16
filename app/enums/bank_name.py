from enum import Enum

class BankName(Enum):
    BANCO_DO_BRASIL = "Banco do Brasil"
    BRADESCO = "Bradesco"
    ITAU = "Itaú"
    SANTANDER = "Santander"

    @classmethod
    def from_name(cls, name: str):
        for member in cls:
            if member.name == name:
                return member
        raise ValueError(f"No {cls.__name__} with name '{name}'")

    @classmethod
    def from_value(cls, value: str):
        for member in cls:
            if member.value == value or member.name == value:
                return member
        raise ValueError(f"No {cls.__name__} with value or name '{value}'")
