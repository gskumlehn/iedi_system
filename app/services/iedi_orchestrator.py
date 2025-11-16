from datetime import datetime
from typing import Dict, List
import logging

from app.services.brandwatch_service import BrandwatchService
from app.services.mention_service import MentionService
from app.services.bank_detection_service import BankDetectionService
from app.services.iedi_calculation_service import IEDICalculationService
from app.services.iedi_aggregation_service import IEDIAggregationService
from app.repositories.analysis_mention_repository import AnalysisMentionRepository
from app.repositories.bank_period_repository import BankPeriodRepository
from app.repositories.iedi_result_repository import IEDIResultRepository

logger = logging.getLogger(__name__)


class IEDIOrchestrator:
    def __init__(
        self,
        brandwatch_service: BrandwatchService,
        mention_service: MentionService,
        bank_detection_service: BankDetectionService,
        iedi_calculation_service: IEDICalculationService,
        iedi_aggregation_service: IEDIAggregationService
    ):
        self.brandwatch_service = brandwatch_service
        self.mention_service = mention_service
        self.bank_detection_service = bank_detection_service
        self.iedi_calculation_service = iedi_calculation_service
        self.iedi_aggregation_service = iedi_aggregation_service

    def process_analysis(
        self,
        analysis_id: str,
        start_date: datetime,
        end_date: datetime,
        query_name: str
    ) -> Dict:
        logger.info(f"Iniciando processamento da análise {analysis_id}")
        
        mentions_data = self.brandwatch_service.extract_mentions(
            start_date=start_date,
            end_date=end_date,
            query_name=query_name
        )
        logger.info(f"Coletadas {len(mentions_data)} menções da Brandwatch")
        
        processed_count = 0
        bank_mention_counts = {}
        
        for mention_data in mentions_data:
            mention = self.mention_service.process_mention(mention_data)
            
            detected_banks = self.bank_detection_service.detect_banks(mention_data)
            
            if not detected_banks:
                continue
            
            for bank in detected_banks:
                iedi_result = self.iedi_calculation_service.calculate_iedi(
                    mention_data=mention_data,
                    bank=bank
                )
                
                AnalysisMentionRepository.create(
                    analysis_id=analysis_id,
                    mention_id=mention.id,
                    bank_id=bank.id,
                    **iedi_result
                )
                
                bank_mention_counts[bank.id] = bank_mention_counts.get(bank.id, 0) + 1
            
            processed_count += 1
        
        logger.info(f"Processadas {processed_count} menções")
        
        for bank_id, count in bank_mention_counts.items():
            BankPeriodRepository.create(
                analysis_id=analysis_id,
                bank_id=bank_id,
                category_detail="Bancos",
                start_date=start_date,
                end_date=end_date
            )
        
        aggregated = self.iedi_aggregation_service.aggregate_by_period(analysis_id)
        logger.info(f"Agregação concluída: {len(aggregated)} bancos")
        
        for agg in aggregated:
            IEDIResultRepository.create(
                analysis_id=analysis_id,
                bank_id=agg['bank_id'],
                total_mentions=agg['total_mentions'],
                final_iedi=agg['iedi_final']
            )
        
        ranking = sorted(aggregated, key=lambda x: x['iedi_final'], reverse=True)
        for idx, item in enumerate(ranking, 1):
            item['position'] = idx
        
        logger.info(f"Ranking gerado: {len(ranking)} bancos")
        
        return {
            'analysis_id': analysis_id,
            'total_mentions': len(mentions_data),
            'processed_mentions': processed_count,
            'ranking': ranking
        }
