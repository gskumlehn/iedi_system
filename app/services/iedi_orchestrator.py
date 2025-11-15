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
        iedi_aggregation_service: IEDIAggregationService,
        analysis_mention_repo: AnalysisMentionRepository,
        bank_period_repo: BankPeriodRepository,
        iedi_result_repo: IEDIResultRepository
    ):
        self.brandwatch = brandwatch_service
        self.mention_service = mention_service
        self.bank_detection = bank_detection_service
        self.iedi_calculation = iedi_calculation_service
        self.iedi_aggregation = iedi_aggregation_service
        self.analysis_mention_repo = analysis_mention_repo
        self.bank_period_repo = bank_period_repo
        self.iedi_result_repo = iedi_result_repo

    def process_analysis(
        self,
        analysis_id: str,
        start_date: datetime,
        end_date: datetime,
        query_name: str
    ) -> Dict:
        logger.info(
            f"Iniciando processamento: {analysis_id} "
            f"({start_date} - {end_date})"
        )
        
        mentions_data = self.brandwatch.extract_mentions(
            start_date=start_date,
            end_date=end_date,
            query_name=query_name
        )
        logger.info(f"Coletadas {len(mentions_data)} menções da Brandwatch")
        
        processed_count = 0
        for mention_data in mentions_data:
            try:
                self._process_single_mention(analysis_id, mention_data)
                processed_count += 1
            except Exception as e:
                logger.error(
                    f"Erro ao processar menção {mention_data.get('id')}: {e}"
                )
                continue
        
        logger.info(f"Processadas {processed_count} menções")
        
        aggregated = self.iedi_aggregation.aggregate_by_period(analysis_id)
        logger.info(f"Agregação concluída: {len(aggregated)} bancos")
        
        ranking = self._generate_ranking(analysis_id, aggregated)
        logger.info(f"Ranking gerado: {len(ranking)} bancos")
        
        return {
            'analysis_id': analysis_id,
            'total_mentions': len(mentions_data),
            'processed_mentions': processed_count,
            'ranking': ranking
        }

    def _process_single_mention(self, analysis_id: str, mention_data: Dict):
        mention = self.mention_service.process_mention(mention_data)
        
        detected_banks = self.bank_detection.detect_banks(mention_data)
        
        if not detected_banks:
            logger.debug(f"Nenhum banco detectado: {mention.url}")
            return
        
        for bank in detected_banks:
            iedi_result = self.iedi_calculation.calculate_iedi(
                mention_data=mention_data,
                bank=bank
            )
            
            self.analysis_mention_repo.create(
                analysis_id=analysis_id,
                mention_id=mention.id,
                bank_id=bank.id,
                **iedi_result
            )

    def _generate_ranking(
        self,
        analysis_id: str,
        aggregated: List[Dict]
    ) -> List[Dict]:
        ranking = sorted(
            aggregated,
            key=lambda x: x['iedi_final'],
            reverse=True
        )
        
        for idx, item in enumerate(ranking, start=1):
            item['position'] = idx
        
        return ranking
