from typing import Dict, List
import logging
import re

from app.repositories.bank_repository import BankRepository
from app.models.bank import Bank
from app.enums.bank_name import BankName

logger = logging.getLogger(__name__)


class BankDetectionService:
    """
    Service para detecção de bancos em menções.
    Usa categoryDetails da Brandwatch com nome de grupo específico.
    """

    # Nome do grupo de categorias que contém os bancos
    BANK_CATEGORY_GROUP = "Bancos"  # Ajustar conforme configuração Brandwatch

    def __init__(self, bank_repo: BankRepository):
        self.bank_repo = bank_repo
        self._banks_cache = None

    def detect_banks(self, mention_data: Dict) -> List[Bank]:
        """
        Detecta bancos mencionados usando categoryDetails da Brandwatch.
        
        Args:
            mention_data: Dados brutos da menção Brandwatch
        
        Returns:
            Lista de bancos detectados
        """
        detected_banks = []
        
        # 1. Verificar categoryDetails (fonte primária)
        category_banks = self._detect_from_categories(mention_data)
        if category_banks:
            detected_banks.extend(category_banks)
            logger.debug(
                f"Bancos detectados via categoryDetails: "
                f"{[b.name for b in category_banks]}"
            )
        
        # 2. Fallback: Busca no texto (se categoryDetails vazio)
        if not detected_banks:
            text_banks = self._detect_from_text(mention_data)
            if text_banks:
                detected_banks.extend(text_banks)
                logger.debug(
                    f"Bancos detectados via texto: "
                    f"{[b.name for b in text_banks]}"
                )
        
        # Remover duplicatas
        unique_banks = list({bank.id: bank for bank in detected_banks}.values())
        
        return unique_banks

    def _detect_from_categories(self, mention_data: Dict) -> List[Bank]:
        """
        Detecta bancos a partir de categoryDetails.
        
        Estrutura esperada:
        {
            "categoryDetails": [
                {
                    "name": "Banco do Brasil",
                    "group": "Bancos"
                },
                {
                    "name": "Tecnologia",
                    "group": "Temas"  # Ignorar - grupo diferente
                }
            ]
        }
        """
        category_details = mention_data.get('categoryDetails', [])
        if not category_details:
            return []
        
        detected_banks = []
        banks = self._get_all_banks()
        
        for category in category_details:
            # Verificar se é do grupo de bancos
            if category.get('group') != self.BANK_CATEGORY_GROUP:
                continue
            
            category_name = category.get('name', '').lower()
            
            # Mapear nome da categoria para banco
            for bank in banks:
                if self._matches_bank(category_name, bank):
                    detected_banks.append(bank)
                    break
        
        return detected_banks

    def _detect_from_text(self, mention_data: Dict) -> List[Bank]:
        """
        Fallback: Detecta bancos no texto (título + primeiro parágrafo).
        Usado apenas se categoryDetails estiver vazio.
        """
        title = mention_data.get('title', '')
        snippet = mention_data.get('snippet', '')
        
        text_to_search = f"{title} {snippet}".lower()
        
        detected_banks = []
        banks = self._get_all_banks()
        
        for bank in banks:
            if self._bank_in_text(bank, text_to_search):
                detected_banks.append(bank)
        
        return detected_banks

    def _matches_bank(self, category_name: str, bank: Bank) -> bool:
        """Verifica se nome da categoria corresponde ao banco."""
        bank_name_lower = bank.name.lower()
        
        # Match exato
        if category_name == bank_name_lower:
            return True
        
        # Match parcial (ex: "bb" em "banco do brasil")
        if bank_name_lower in category_name or category_name in bank_name_lower:
            return True
        
        return False

    def _bank_in_text(self, bank: Bank, text: str) -> bool:
        """Verifica se banco está mencionado no texto com word boundary."""
        bank_name_lower = bank.name.lower()
        
        # Regex com word boundary
        pattern = r'\b' + re.escape(bank_name_lower) + r'\b'
        
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _get_all_banks(self) -> List[Bank]:
        """Retorna lista de bancos (com cache)."""
        if self._banks_cache is None:
            self._banks_cache = self.bank_repo.find_all()
        
        return self._banks_cache
