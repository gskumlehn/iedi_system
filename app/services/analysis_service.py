from app.enums.analysis_status import AnalysisStatus
from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.services.bank_analysis_service import BankAnalysisService
from app.services.mention_analysis_service import MentionAnalysisService
import threading

class AnalysisService:

    bank_analysis_service = BankAnalysisService()
    mention_analysis_service = MentionAnalysisService()

    def save(self, name, query_name, parent_name, bank_names=None, start_date=None, end_date=None, custom_bank_dates=None):
        self.validate(name, query_name)
        validated_bank_analyses = self.bank_analysis_service.validate(bank_names, start_date, end_date, custom_bank_dates)

        is_custom_dates = bool(custom_bank_dates)
        analysis = AnalysisRepository.save(self.build(name=name, query_name=query_name, is_custom_dates=is_custom_dates))

        self.bank_analysis_service.save_all(analysis_id=analysis.id, bank_analyses=validated_bank_analyses)

        threading.Thread(target=self.process_and_update_status, args=(analysis, validated_bank_analyses, parent_name)).start()

        return analysis

    def validate(self, name, query_name):
        if not name:
            raise ValueError("O nome da análise é obrigatório.")

        if not query_name:
            raise ValueError("A query utilizada na análise é obrigatória.")

    def build(self, name, query_name, is_custom_dates):
        return Analysis(name=name, query_name=query_name, status=AnalysisStatus.PENDING, is_custom_dates=is_custom_dates)

    def find_all(self):
        return AnalysisRepository.find_all()

    def find_by_id(self, analysis_id):
        analysis = AnalysisRepository.find_by_id(analysis_id)
        if not analysis:
            raise ValueError("Análise não encontrada.")
        return analysis

    def update_status(self, analysis_id, new_status):
        analysis = self.find_by_id(analysis_id)
        if not isinstance(new_status, AnalysisStatus):
            raise ValueError("O novo status deve ser uma instância válida de AnalysisStatus.")
        analysis.status = new_status
        AnalysisRepository.update(analysis)
        return analysis

    def process_and_update_status(self, analysis, bank_analyses, parent_name):
        self.mention_analysis_service.process_mention_analysis(analysis, bank_analyses, parent_name)
        self.update_status(analysis.id, AnalysisStatus.DONE)
