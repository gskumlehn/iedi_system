import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.brandwatch_service import BrandwatchService
from app.services.mention_service import MentionService
from app.services.bank_detection_service import BankDetectionService
from app.services.iedi_calculation_service import IEDICalculationService
from app.services.iedi_aggregation_service import IEDIAggregationService
from app.services.iedi_orchestrator import IEDIOrchestrator
from app.repositories.mention_repository import MentionRepository, AnalysisMentionRepository
from app.repositories.bank_repository import BankRepository
from app.repositories.media_outlet_repository import MediaOutletRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.bank_period_repository import BankPeriodRepository
from app.repositories.iedi_result_repository import IEDIResultRepository
from app.utils.uuid_generator import generate_uuid
from app.enums.period_type import PeriodType


def test_outubro_bb():
    print("=" * 80)
    print("TESTE END-TO-END: Análise IEDI - Outubro 2024 - Banco do Brasil")
    print("=" * 80)
    print()
    
    analysis_id = generate_uuid()
    start_date = datetime(2024, 10, 1)
    end_date = datetime(2024, 10, 31, 23, 59, 59)
    query_name = "OPERAÇÃO BB :: MONITORAMENTO"
    
    print(f"ID da Análise: {analysis_id}")
    print(f"Período: {start_date.date()} a {end_date.date()}")
    print(f"Query Brandwatch: {query_name}")
    print()
    
    print("Inicializando services...")
    brandwatch_service = BrandwatchService()
    mention_repo = MentionRepository()
    media_outlet_repo = MediaOutletRepository()
    mention_service = MentionService(mention_repo, media_outlet_repo)
    bank_repo = BankRepository()
    bank_detection_service = BankDetectionService(bank_repo)
    iedi_calculation_service = IEDICalculationService()
    analysis_mention_repo = AnalysisMentionRepository()
    iedi_aggregation_service = IEDIAggregationService(analysis_mention_repo, bank_repo)
    bank_period_repo = BankPeriodRepository()
    iedi_result_repo = IEDIResultRepository()
    
    orchestrator = IEDIOrchestrator(
        brandwatch_service=brandwatch_service,
        mention_service=mention_service,
        bank_detection_service=bank_detection_service,
        iedi_calculation_service=iedi_calculation_service,
        iedi_aggregation_service=iedi_aggregation_service,
        analysis_mention_repo=analysis_mention_repo,
        bank_period_repo=bank_period_repo,
        iedi_result_repo=iedi_result_repo
    )
    print("✓ Services inicializados")
    print()
    
    print("Testando conexão Brandwatch...")
    if not brandwatch_service.test_connection():
        print("✗ Falha na conexão com Brandwatch")
        print("Verifique as variáveis de ambiente:")
        print("  - BRANDWATCH_USERNAME")
        print("  - BRANDWATCH_PASSWORD")
        print("  - BRANDWATCH_PROJECT_ID")
        return
    print("✓ Conexão com Brandwatch OK")
    print()
    
    print("Criando registro de análise...")
    analysis_repo = AnalysisRepository()
    analysis_repo.create(
        id=analysis_id,
        period_type=PeriodType.MONTHLY,
        start_date=start_date,
        end_date=end_date,
        query_name=query_name
    )
    print(f"✓ Análise criada: {analysis_id}")
    print()
    
    print("Executando processamento IEDI...")
    print("-" * 80)
    
    try:
        result = orchestrator.process_analysis(
            analysis_id=analysis_id,
            start_date=start_date,
            end_date=end_date,
            query_name=query_name
        )
        
        print("-" * 80)
        print()
        print("=" * 80)
        print("RESULTADOS")
        print("=" * 80)
        print()
        print(f"Total de menções coletadas: {result['total_mentions']}")
        print(f"Menções processadas: {result['processed_mentions']}")
        print()
        print("RANKING IEDI:")
        print("-" * 80)
        print(f"{'Pos':<5} {'Banco':<25} {'Menções':<10} {'IEDI Final':<12}")
        print("-" * 80)
        
        for item in result['ranking']:
            print(
                f"{item['position']:<5} "
                f"{item['bank_name']:<25} "
                f"{item['total_mentions']:<10} "
                f"{item['iedi_final']:<12.2f}"
            )
        
        print("-" * 80)
        print()
        print("✓ Teste concluído com sucesso!")
        
    except Exception as e:
        print()
        print("✗ Erro durante processamento:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_outubro_bb()
