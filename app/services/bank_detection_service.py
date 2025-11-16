from typing import Dict, List
import logging
import re

from app.models.bank import Bank
from app.repositories.bank_repository import BankRepository

logger = logging.getLogger(__name__)


class BankDetectionService:
    BANK_GROUP_NAME = "Bancos"
    
    def __init__(self):
        self._banks_cache = None

    def detect_banks(self, mention_data: Dict) -> List[Bank]:
        detected_from_categories = self._detect_from_categories(mention_data)
        
        if detected_from_categories:
            logger.info(f"Bancos detectados via categoryDetails: {[b.name.value for b in detected_from_categories]}")
            return detected_from_categories
        
        detected_from_text = self._detect_from_text(mention_data)
        
        if detected_from_text:
            logger.info(f"Bancos detectados via texto: {[b.name.value for b in detected_from_text]}")
        else:
            logger.warning("Nenhum banco detectado na menção")
        
        return detected_from_text

    def _detect_from_categories(self, mention_data: Dict) -> List[Bank]:
        category_details = mention_data.get('categoryDetails', [])
        
        if not category_details:
            return []
        
        bank_categories = [
            cat['name'] 
            for cat in category_details 
            if cat.get('group') == self.BANK_GROUP_NAME
        ]
        
        if not bank_categories:
            return []
        
        banks = self._get_all_banks()
        detected = []
        
        for bank in banks:
            for category_name in bank_categories:
                if self._matches_bank(category_name, bank):
                    detected.append(bank)
                    break
        
        return detected

    def _detect_from_text(self, mention_data: Dict) -> List[Bank]:
        title = mention_data.get('title', '').lower()
        snippet = mention_data.get('snippet', '').lower()
        text = f"{title} {snippet}"
        
        banks = self._get_all_banks()
        detected = []
        
        for bank in banks:
            if self._bank_mentioned_in_text(text, bank):
                detected.append(bank)
        
        return detected

    def _matches_bank(self, category_name: str, bank: Bank) -> bool:
        category_lower = category_name.lower()
        bank_name_lower = bank.name.value.lower()
        
        if category_lower == bank_name_lower:
            return True
        
        for variation in bank.variations:
            if category_lower == variation.lower():
                return True
        
        return False

    def _bank_mentioned_in_text(self, text: str, bank: Bank) -> bool:
        bank_name = bank.name.value.lower()
        pattern = r'\b' + re.escape(bank_name) + r'\b'
        
        if re.search(pattern, text, re.IGNORECASE):
            return True
        
        for variation in bank.variations:
            pattern = r'\b' + re.escape(variation.lower()) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def _get_all_banks(self) -> List[Bank]:
        if self._banks_cache is None:
            self._banks_cache = BankRepository.find_all()
        
        return self._banks_cache
