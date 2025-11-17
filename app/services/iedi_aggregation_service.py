from typing import Dict, List
import logging

from app.repositories.mention_analysis_repository import MentionAnalysisRepository
from app.repositories.bank_repository import BankRepository

logger = logging.getLogger(__name__)


class IEDIAggregationService:
    def aggregate_by_period(self, analysis_id: str) -> List[Dict]:
        banks = BankRepository.find_all()
        aggregated = []
        
        for bank in banks:
            mention_analyses = MentionAnalysisRepository.find_by_analysis_and_bank(
                analysis_id=analysis_id,
                bank_id=bank.id
            )
            
            if not mention_analyses:
                continue
            
            total_mentions = len(mention_analyses)
            sum_iedi = sum(ma.iedi_score for ma in mention_analyses if ma.iedi_score)

            avg_iedi = sum_iedi / total_mentions if total_mentions > 0 else 0
            
            iedi_normalized = (avg_iedi + 1) * 5
            
            aggregated.append({
                'bank_id': bank.id,
                'bank_name': bank.name.value,
                'total_mentions': total_mentions,
                'iedi_avg': round(avg_iedi, 4),
                'iedi_final': round(iedi_normalized, 2)
            })
        
        logger.info(f"Agregação concluída: {len(aggregated)} bancos")
        return aggregated
