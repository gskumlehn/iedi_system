import os
from datetime import datetime, timedelta
from app.services.mention_analysis_service import MentionAnalysisService
from app.repositories.bank_repository import BankRepository
from app.models.analysis import Analysis
from app.enums.bank_name import BankName
from app.services.analysis_service import AnalysisService

def test_multiple_banks_analysis():
    """
    Teste para verificar análise de múltiplos bancos com períodos e horários específicos.
    """
    # Configuração dos bancos e períodos
    banks_periods = [
        {"bank": BankName.BANCO_DO_BRASIL, "start_date": "2025-11-13T00:00:00", "end_date": "2025-11-15T23:59:59"},
        {"bank": BankName.SANTANDER, "start_date": "2025-10-28T00:00:00", "end_date": "2025-10-30T23:59:59"}
    ]

    # Nome da query
    query_name = "BB | Monitoramento | + Lagos"

    # Parent category para identificar o banco
    parent_category_name = "Análise de Resultado - Bancos"

    # Iterar sobre os bancos e períodos
    for bank_period in banks_periods:
        bank_name = bank_period["bank"]
        start_date = bank_period["start_date"]
        end_date = bank_period["end_date"]

        # Verificar se o banco existe no banco de dados
        bank = BankRepository.find_by_name(bank_name)
        if not bank:
            print(f"Banco {bank_name.value} não encontrado no banco de dados.")
            continue

        # Criar análise
        analysis_service = AnalysisService()
        analysis = analysis_service.save(
            name=f"Análise {bank_name.value} - {start_date[:10]} a {end_date[:10]}",
            query_name=query_name,
            bank_names=[bank_name.value],
            start_date=start_date,
            end_date=end_date
        )

        # Processar análise
        mention_analysis_service = MentionAnalysisService()
        bank_analyses = mention_analysis_service.get_bank_analyses(analysis.id)

        # Processar menções sincronamente
        mention_analysis_service.process_mention_analysis(analysis, bank_analyses)

        # Verificar menções processadas
        mentions = mention_analysis_service.fetch_mentions_by_analysis_id(analysis.id)
        for mention in mentions:
            category_details = mention.category_details
            bank_detected = None
            for category in category_details:
                if category.get("parentName") == parent_category_name:
                    bank_detected = category.get("name")
                    break

            assert bank_detected == bank_name.value, f"Menção não corresponde ao banco esperado: {bank_name.value}"

        print(f"Teste para {bank_name.value} concluído com sucesso.")
