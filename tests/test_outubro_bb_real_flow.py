"""
Teste End-to-End: Análise IEDI - Outubro 2024 - Banco do Brasil

Este teste segue o fluxo REAL do sistema:
1. Criar Analysis via AnalysisService.save()
2. Aguardar processamento assíncrono (ou executar sincronamente para teste)
3. Verificar BankAnalysis criados e métricas calculadas

IMPORTANTE:
- Requer variáveis de ambiente: BW_PROJECT, BW_EMAIL, BW_PASSWORD
- Requer banco "Banco do Brasil" cadastrado no banco de dados
- Requer media outlets cadastrados
- Mentions da Brandwatch DEVEM ter categoryDetails com "Banco do Brasil"
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from collections import Counter
from dotenv import load_dotenv
import time

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.analysis_service import AnalysisService
from app.repositories.bank_analysis_repository import BankAnalysisRepository
from app.repositories.bank_repository import BankRepository
from app.repositories.mention_analysis_repository import MentionAnalysisRepository
from app.enums.bank_name import BankName


def extract_domain(url: str) -> str:
    """Extrai domínio de uma URL"""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ''


def save_analysis_results(analysis_id: str, bank_analyses: list, output_dir: str = "test_output"):
    """Salva resultados da análise em arquivo JSON"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {
        'analysis_id': analysis_id,
        'timestamp': timestamp,
        'banks': []
    }
    
    for ba in bank_analyses:
        results['banks'].append({
            'id': ba.id,
            'bank_name': ba.bank_name.value,
            'start_date': ba.start_date.isoformat() if ba.start_date else None,
            'end_date': ba.end_date.isoformat() if ba.end_date else None,
            'total_mentions': ba.total_mentions,
            'positive_volume': ba.positive_volume,
            'negative_volume': ba.negative_volume,
            'iedi_mean': ba.iedi_mean,
            'iedi_score': ba.iedi_score
        })
    
    results_file = os.path.join(output_dir, f"analysis_results_{timestamp}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Resultados salvos em: {results_file}")
    return results_file


def wait_for_processing(analysis_id: str, max_wait: int = 300, check_interval: int = 5):
    """
    Aguarda processamento assíncrono ser concluído
    
    Args:
        analysis_id: ID da análise
        max_wait: Tempo máximo de espera em segundos (padrão: 5 minutos)
        check_interval: Intervalo entre verificações em segundos (padrão: 5s)
    
    Returns:
        bool: True se processamento concluído, False se timeout
    """
    print(f"\nAguardando processamento assíncrono (máx {max_wait}s)...")
    
    elapsed = 0
    while elapsed < max_wait:
        bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis_id)
        
        if bank_analyses:
            # Verificar se pelo menos um BankAnalysis tem métricas calculadas
            has_metrics = any(ba.total_mentions > 0 for ba in bank_analyses)
            
            if has_metrics:
                print(f"✓ Processamento concluído após {elapsed}s")
                return True
        
        time.sleep(check_interval)
        elapsed += check_interval
        print(f"  Aguardando... ({elapsed}s/{max_wait}s)")
    
    print(f"✗ Timeout: Processamento não concluído em {max_wait}s")
    return False


def test_outubro_bb():
    """Teste end-to-end seguindo fluxo real do sistema"""
    
    print("=" * 80)
    print("TESTE END-TO-END: Análise IEDI - Outubro 2024 - Banco do Brasil")
    print("=" * 80)
    print()
    
    # Configuração do teste
    analysis_name = "Análise Outubro 2024 - Banco do Brasil"
    query_name = "OPERAÇÃO BB :: MONITORAMENTO"
    bank_name = "Banco do Brasil"
    start_date = "2024-10-01T00:00:00"
    end_date = "2024-10-31T23:59:59"
    
    print(f"Nome da Análise: {analysis_name}")
    print(f"Query Brandwatch: {query_name}")
    print(f"Banco: {bank_name}")
    print(f"Período: {start_date} a {end_date}")
    print()
    
    # Validar variáveis de ambiente
    print("Validando variáveis de ambiente...")
    required_envs = ['BW_PROJECT', 'BW_EMAIL', 'BW_PASSWORD']
    missing_envs = [env for env in required_envs if not os.getenv(env)]
    
    if missing_envs:
        print(f"✗ Variáveis de ambiente faltando: {', '.join(missing_envs)}")
        print("Configure no arquivo .env:")
        for env in missing_envs:
            print(f"  {env}=<valor>")
        return
    
    print("✓ Variáveis de ambiente OK")
    print()
    
    # Verificar se banco existe no banco de dados
    print("Verificando se banco existe no banco de dados...")
    try:
        bank = BankRepository.find_by_name(BankName.BANCO_DO_BRASIL)
        if not bank:
            print("✗ Banco do Brasil não encontrado no banco de dados")
            print("Execute os scripts SQL de insert primeiro:")
            print("  - sql/09_insert_banks.sql")
            return
        
        print(f"✓ Banco encontrado: {bank.name.value}")
        print(f"  Variações: {', '.join(bank.variations)}")
        print()
    except Exception as e:
        print(f"✗ Erro ao buscar banco: {e}")
        return
    
    # Criar análise via AnalysisService
    print("Criando análise via AnalysisService.save()...")
    print("-" * 80)
    
    try:
        analysis_service = AnalysisService()
        
        analysis = analysis_service.save(
            name=analysis_name,
            query=query_name,
            bank_names=[bank_name],
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"✓ Análise criada com sucesso!")
        print(f"  ID: {analysis.id}")
        print(f"  Nome: {analysis.name}")
        print(f"  Query: {analysis.query_name}")
        print(f"  Status: {analysis.status.value}")
        print(f"  Custom Dates: {analysis.is_custom_dates}")
        print()
        
    except Exception as e:
        print(f"✗ Erro ao criar análise: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Aguardar processamento assíncrono
    print("=" * 80)
    print("PROCESSAMENTO ASSÍNCRONO")
    print("=" * 80)
    print()
    print("NOTA: O processamento ocorre em thread separada e inclui:")
    print("  1. Busca de mentions na Brandwatch")
    print("  2. Filtragem por contentSource='News'")
    print("  3. Salvamento de mentions no banco")
    print("  4. Filtragem por categoria (banco in mention.categories)")
    print("  5. Cálculo de IEDI para cada mention")
    print("  6. Cálculo de métricas agregadas por banco")
    print()
    
    # Aguardar processamento (máx 5 minutos)
    if not wait_for_processing(analysis.id, max_wait=300, check_interval=5):
        print()
        print("✗ Processamento não concluído no tempo esperado")
        print("Possíveis causas:")
        print("  - Erro na conexão com Brandwatch")
        print("  - Query não encontrada")
        print("  - Nenhuma mention com categoria 'Banco do Brasil'")
        print("  - Erro no processamento")
        return
    
    # Buscar resultados
    print()
    print("=" * 80)
    print("RESULTADOS")
    print("=" * 80)
    print()
    
    try:
        bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis.id)
        
        if not bank_analyses:
            print("✗ Nenhum BankAnalysis encontrado")
            return
        
        print(f"Total de bancos analisados: {len(bank_analyses)}")
        print()
        
        for ba in bank_analyses:
            print("-" * 80)
            print(f"Banco: {ba.bank_name.value}")
            print(f"Período: {ba.start_date.date()} a {ba.end_date.date()}")
            print()
            print(f"Total de Mentions: {ba.total_mentions}")
            print(f"Mentions Positivas: {ba.positive_volume}")
            print(f"Mentions Negativas: {ba.negative_volume}")
            print()
            print(f"IEDI Médio: {ba.iedi_mean:.4f}")
            print(f"IEDI Final: {ba.iedi_score:.4f}")
            print()
            
            # Calcular taxas
            if ba.total_mentions > 0:
                positivity_rate = (ba.positive_volume / ba.total_mentions) * 100
                negativity_rate = (ba.negative_volume / ba.total_mentions) * 100
                print(f"Taxa de Positividade: {positivity_rate:.2f}%")
                print(f"Taxa de Negatividade: {negativity_rate:.2f}%")
                print()
        
        print("-" * 80)
        print()
        
        # Salvar resultados em arquivo
        results_file = save_analysis_results(analysis.id, bank_analyses)
        
        # Buscar mention_analyses para análise detalhada
        print("Buscando mention_analyses para análise detalhada...")
        mention_analyses = MentionAnalysisRepository.find_by_bank_name(BankName.BANCO_DO_BRASIL)
        
        if mention_analyses:
            print(f"✓ Encontradas {len(mention_analyses)} mention_analyses")
            print()
            
            # Análise de distribuição de sentimentos
            sentiments = Counter([ma.sentiment.value for ma in mention_analyses if ma.sentiment])
            print("Distribuição de Sentimentos:")
            for sentiment, count in sentiments.most_common():
                percentage = (count / len(mention_analyses)) * 100
                print(f"  {sentiment}: {count} ({percentage:.2f}%)")
            print()
            
            # Análise de reach groups
            reach_groups = Counter([ma.reach_group.value for ma in mention_analyses if ma.reach_group])
            print("Distribuição de Reach Groups:")
            for rg, count in reach_groups.most_common():
                percentage = (count / len(mention_analyses)) * 100
                print(f"  Grupo {rg}: {count} ({percentage:.2f}%)")
            print()
            
            # Estatísticas de IEDI
            iedi_scores = [ma.iedi_normalized for ma in mention_analyses if ma.iedi_normalized is not None]
            if iedi_scores:
                print("Estatísticas de IEDI Normalizado:")
                print(f"  Mínimo: {min(iedi_scores):.4f}")
                print(f"  Máximo: {max(iedi_scores):.4f}")
                print(f"  Média: {sum(iedi_scores) / len(iedi_scores):.4f}")
                print()
        
        print("=" * 80)
        print("TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print()
        
        # Próximos passos
        print("PRÓXIMOS PASSOS:")
        print()
        print("1. Analisar resultados em:", results_file)
        print("2. Validar métricas calculadas")
        print("3. Comparar com análises anteriores")
        print()
        print("VALIDAÇÕES IMPORTANTES:")
        print()
        print("✓ Verificar se mentions têm categoria 'Banco do Brasil' na Brandwatch")
        print("✓ Verificar se domínios dos veículos estão cadastrados em media_outlets")
        print("✓ Verificar se variações do banco estão corretas")
        print("✓ Validar cálculo de IEDI manualmente para algumas mentions")
        
    except Exception as e:
        print(f"✗ Erro ao buscar resultados: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_outubro_bb()
