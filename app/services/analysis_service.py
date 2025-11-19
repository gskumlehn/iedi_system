from app.enums.analysis_status import AnalysisStatus
from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.services.bank_analysis_service import BankAnalysisService
from app.services.mention_analysis_service import MentionAnalysisService
import threading

class AnalysisService:

    bank_analysis_service = BankAnalysisService()
    mention_analysis_service = MentionAnalysisService()

    def save(self, name=None, query=None, bank_names=None, start_date=None, end_date=None, custom_bank_dates=None):
        self.validate(name, query)
        validated_bank_analyses = self.bank_analysis_service.validate(bank_names, start_date, end_date, custom_bank_dates)

        is_custom_dates = bool(custom_bank_dates)
        analysis = AnalysisRepository.save(self.build(name=name, query=query, is_custom_dates=is_custom_dates))

        self.bank_analysis_service.save_all(analysis_id=analysis.id, bank_analyses=validated_bank_analyses)

        # threading.Thread(target=self.mention_analysis_service.process_mention_analysis, args=(analysis, validated_bank_analyses)).start()

        return analysis

    def validate(self, name, query):
        if not name:
            raise ValueError("O nome da análise é obrigatório.")

        if not query:
            raise ValueError("A query utilizada na análise é obrigatória.")

    def build(self, name, query, is_custom_dates):
        return Analysis(name=name, query_name=query, status=AnalysisStatus.PENDING, is_custom_dates=is_custom_dates)
