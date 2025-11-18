import os
import sys
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.brandwatch_service import BrandwatchService
from app.services.mention_service import MentionService
from app.services.bank_detection_service import BankDetectionService
from app.services.iedi_calculation_service import IEDICalculationService
from app.services.iedi_aggregation_service import IEDIAggregationService
from app.services.iedi_orchestrator import IEDIOrchestrator
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.bank_period_repository import BankPeriodRepository
from app.repositories.bank_repository import BankRepository

from app.enums.bank_name import BankName
from app.utils.uuid_generator import generate_uuid


def extract_domain(url: str) -> str:
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ''


def save_mentions_to_file(mentions_data: list, output_dir: str = "test_output"):
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    full_data_file = os.path.join(output_dir, f"mentions_full_{timestamp}.json")
    with open(full_data_file, 'w', encoding='utf-8') as f:
        json.dump(mentions_data, f, ensure_ascii=False, indent=2, default=str)

    domains = []
    for mention in mentions_data:
        url = mention.get('url') or mention.get('originalUrl')
        if url:
            domain = extract_domain(url)
            if domain:
                domains.append(domain)

    domain_counts = Counter(domains)

    domain_analysis = {
        'total_mentions': len(mentions_data),
        'unique_domains': len(domain_counts),
        'domain_distribution': [
            {'domain': domain, 'count': count, 'percentage': round(count / len(mentions_data) * 100, 2)}
            for domain, count in domain_counts.most_common()
        ]
    }

    domain_file = os.path.join(output_dir, f"domains_analysis_{timestamp}.json")
    with open(domain_file, 'w', encoding='utf-8') as f:
        json.dump(domain_analysis, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Menções salvas em: {full_data_file}")
    print(f"✓ Análise de domínios salva em: {domain_file}")

    return full_data_file, domain_file, domain_analysis


def test_outubro_bb():
    print("=" * 80)
    print("TESTE END-TO-END: Análise IEDI - Outubro 2024 - Banco do Brasil")
    print("=" * 80)
    print()

    # Configuração do teste
    analysis_id = generate_uuid()
    start_date = datetime(2024, 10, 1)
    end_date = datetime(2024, 10, 31, 23, 59, 59)
    query_name = "OPERAÇÃO BB :: MONITORAMENTO"

    print(f"ID da Análise: {analysis_id}")
    print(f"Período: {start_date.date()} a {end_date.date()}")
    print(f"Query Brandwatch: {query_name}")
    print()

    # Buscar Banco do Brasil
    print("Buscando Banco do Brasil no banco de dados...")
    bb_bank = None
    all_banks = BankRepository.find_all()
    for bank in all_banks:
        if bank.name == BankName.BANCO_DO_BRASIL:
            bb_bank = bank
            break

    if not bb_bank:
        print("✗ Banco do Brasil não encontrado no banco de dados")
        print("Execute os scripts SQL de insert primeiro:")
        print("  - sql/09_insert_banks.sql")
        return

    print(f"✓ Banco do Brasil encontrado: {bb_bank.id}")
    print()

    # Criar registro de análise (NOVA ASSINATURA)
    print("Criando registro de análise...")
    analysis = AnalysisRepository.create(
        name="Análise Outubro 2024 - Banco do Brasil",
        query_name=query_name,
        custom_period=False,
        start_date=start_date,
        end_date=end_date
    )
    print(f"✓ Análise criada: {analysis.id}")
    print(f"  - Nome: {analysis.name}")
    print(f"  - Query: {analysis.query_name}")
    print(f"  - Status: {analysis.status}")
    print()

    # Criar período do banco
    print("Criando período do Banco do Brasil...")
    bank_period = BankPeriodRepository.create(
        analysis_id=analysis.id,
        bank_id=bb_bank.id,
        category_detail="Banco do Brasil",  # Categoria na Brandwatch
        start_date=start_date,
        end_date=end_date
    )
    print(f"✓ Período criado: {bank_period.id}")
    print(f"  - Banco: {bb_bank.name.value}")
    print(f"  - Categoria: {bank_period.category_detail}")
    print()

    # Inicializar services
    print("Inicializando services...")
    brandwatch_service = BrandwatchService()
    mention_service = MentionService()
    iedi_calculation_service = IEDICalculationService()
    iedi_aggregation_service = IEDIAggregationService()

    # MOCK: BankDetectionService sempre retorna Banco do Brasil
    print("Configurando mocks...")
    bank_detection_service = Mock(spec=BankDetectionService)
    bank_detection_service.detect_banks = Mock(return_value=[bb_bank])
    print("✓ BankDetectionService mockado - todas menções = Banco do Brasil")

    # NOTA: Como não temos a query com categoria configurada na Brandwatch,
    # estamos usando uma query que só retorna mentions do BB.
    # Quando a categoria estiver configurada, o BankDetectionService
    # detectará automaticamente via categoryDetails.

    orchestrator = IEDIOrchestrator(
        brandwatch_service=brandwatch_service,
        mention_service=mention_service,
        bank_detection_service=bank_detection_service,
        iedi_calculation_service=iedi_calculation_service,
        iedi_aggregation_service=iedi_aggregation_service
    )
    print("✓ IEDIOrchestrator inicializado")
    print()

    # Testar conexão Brandwatch
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

    # Coletar mentions
    print("Coletando menções da Brandwatch...")
    print("-" * 80)

    try:
        mentions_data = brandwatch_service.extract_mentions(
            start_date=start_date,
            end_date=end_date,
            query_name=query_name
        )

        print(f"✓ Coletadas {len(mentions_data)} menções")
        print()

        # Salvar mentions para análise
        print("Salvando menções em arquivo para análise posterior...")
        full_file, domain_file, domain_analysis = save_mentions_to_file(mentions_data)
        print()

        # Análise de domínios
        print("=" * 80)
        print("ANÁLISE DE DOMÍNIOS")
        print("=" * 80)
        print(f"Total de menções: {domain_analysis['total_mentions']}")
        print(f"Domínios únicos: {domain_analysis['unique_domains']}")
        print()
        print("Top 20 domínios:")
        print("-" * 80)
        print(f"{'#':<4} {'Domínio':<40} {'Menções':<10} {'%':<8}")
        print("-" * 80)

        for idx, item in enumerate(domain_analysis['domain_distribution'][:20], 1):
            print(f"{idx:<4} {item['domain']:<40} {item['count']:<10} {item['percentage']:<8.2f}%")

        print("-" * 80)
        print()

        # Processar análise
        print("Executando processamento IEDI...")
        print("-" * 80)
        print("NOTA: BankDetectionService mockado - todas menções atribuídas ao BB")
        print("      Quando a categoria 'Bancos' estiver configurada na Brandwatch,")
        print("      o sistema detectará automaticamente via categoryDetails")
        print("-" * 80)

        result = orchestrator.process_analysis(
            analysis_id=analysis.id,
            start_date=start_date,
            end_date=end_date,
            query_name=query_name
        )

        print("-" * 80)
        print()

        # Resultados
        print("=" * 80)
        print("RESULTADOS IEDI")
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

        # Atualizar total_mentions do BankPeriod
        print("Atualizando total de mentions no BankPeriod...")
        bank_period.total_mentions = result['processed_mentions']
        print(f"✓ BankPeriod atualizado: {bank_period.total_mentions} mentions")
        print()

        # Atualizar status da análise
        print("Atualizando status da análise...")
        analysis.status = 'completed'
        print(f"✓ Status atualizado: {analysis.status}")
        print()

        print("✓ Teste concluído com sucesso!")
        print()

        # Próximos passos
        print("=" * 80)
        print("PRÓXIMOS PASSOS")
        print("=" * 80)
        print(f"1. Analisar domínios em: {domain_file}")
        print(f"2. Comparar com media outlets cadastrados")
        print(f"3. Identificar variações de domínios (www, mobile, amp, etc)")
        print(f"4. Atualizar sql/10_insert_media_outlets.sql com variações")
        print()
        print("CONFIGURAÇÃO BRANDWATCH:")
        print(f"5. Criar grupo de categorias 'Bancos' na Brandwatch")
        print(f"6. Adicionar categoria 'Banco do Brasil' no grupo 'Bancos'")
        print(f"7. Configurar regras para categorizar mentions automaticamente")
        print(f"8. Criar query para todos os bancos (não apenas BB)")
        print(f"9. Remover mock do BankDetectionService")
        print()
        print("VALIDAÇÃO:")
        print(f"10. Executar teste novamente com detecção automática via categoryDetails")
        print(f"11. Validar que BankDetectionService detecta corretamente via categoria")
        print(f"12. Comparar resultados com detecção manual vs automática")

    except Exception as e:
        print()
        print("✗ Erro durante processamento:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_outubro_bb()
