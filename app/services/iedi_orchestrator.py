from datetime import datetime
from typing import Dict
import logging

from app.services.brandwatch_service import BrandwatchService
from app.services.mention_service import MentionService
from app.services.bank_detection_service import BankDetectionService
from app.services.iedi_calculation_service import IEDICalculationService
from app.services.iedi_aggregation_service import IEDIAggregationService
from app.repositories.analysis_mention_repository import AnalysisMentionRepository
from app.repositories.iedi_result_repository import IEDIResultRepository
from app.models.mention_analysis import MentionAnalysis
from app.models.iedi_result import IEDIResult
from app.repositories.mention_analysis_repository import MentionAnalysisRepository

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
                
                # Construct the AnalysisMention model in the service
                mention_analysis = MentionAnalysis(
                    analysis_id=analysis_id,
                    mention_id=mention.id,
                    bank_id=bank.id,
                    **iedi_result
                )
                
                # Pass individual parameters to the repository
                MentionAnalysisRepository.create(
                    analysis_id=mention_analysis.analysis_id,
                    mention_id=mention_analysis.mention_id,
                    bank_id=mention_analysis.bank_id,
                    iedi_score=mention_analysis.iedi_score,
                    sentiment=mention_analysis.sentiment
                )

                bank_mention_counts[bank.id] = bank_mention_counts.get(bank.id, 0) + 1
            
            processed_count += 1
        
        logger.info(f"Processadas {processed_count} menções")
        
        for bank_id, count in bank_mention_counts.items():
            # Construct the BankPeriod model in the service
            bank_period = BankPeriod(
                analysis_id=analysis_id,
                bank_id=bank_id,
                category_detail="Bancos",
                start_date=start_date,
                end_date=end_date
            )

            # Pass individual parameters to the repository
            BankPeriodRepository.create(
                analysis_id=bank_period.analysis_id,
                bank_id=bank_period.bank_id,
                category_detail=bank_period.category_detail,
                start_date=bank_period.start_date,
                end_date=bank_period.end_date
            )

        aggregated = self.iedi_aggregation_service.aggregate_by_period(analysis_id)
        logger.info(f"Agregação concluída: {len(aggregated)} bancos")
        
        for agg in aggregated:
            # Construct the IEDIResult model in the service
            iedi_result = IEDIResult(
                analysis_id=analysis_id,
                bank_id=agg['bank_id'],
                total_mentions=agg['total_mentions'],
                final_iedi=agg['iedi_final']
            )

            # Pass individual parameters to the repository
            IEDIResultRepository.create(
                analysis_id=iedi_result.analysis_id,
                bank_id=iedi_result.bank_id,
                total_mentions=iedi_result.total_mentions,
                final_iedi=iedi_result.final_iedi
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
