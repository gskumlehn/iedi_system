from datetime import datetime
from app.models.bank_analysis import BankAnalysis
from app.enums.bank_name import BankName
from app.repositories.bank_analysis_repository import BankAnalysisRepository
from app.enums.sentiment import Sentiment
import pandas as pd

class BankAnalysisService:

    def validate(self, bank_names=None, start_date=None, end_date=None, custom_bank_dates=None):
        if (not bank_names and not custom_bank_dates) or (bank_names and custom_bank_dates):
            raise ValueError("É necessário fornecer uma lista de bancos com uma data de início e uma data de fim OU uma lista personalizada de datas para cada banco.")

        if bank_names:
            return self.process_bank_names(bank_names, start_date, end_date)
        else:
            return self.process_custom_bank_dates(custom_bank_dates)

    def process_bank_names(self, bank_names, start_date, end_date):
        start_date = self.validate_and_parse_date(start_date, "A data de início fornecida não está em um formato válido.", "data de início")
        end_date = self.validate_and_parse_date(end_date, "A data de fim fornecida não está em um formato válido.", "data de fim")

        self.validate_date_range(start_date, end_date)

        processed = []
        for bank_name in bank_names:
            parsed = self.validate_and_parse_bank_name(bank_name)
            processed.append(self.build(parsed, start_date, end_date))
        return processed

    def process_custom_bank_dates(self, custom_bank_dates):
        bank_analyses = []
        for bank in custom_bank_dates:
            bank_start_date = self.validate_and_parse_date(bank["start_date"], "As datas personalizadas devem estar em um formato válido.", "data de início")
            bank_end_date = self.validate_and_parse_date(bank["end_date"], "As datas personalizadas devem estar em um formato válido.", "data de fim")

            self.validate_date_range(bank_start_date, bank_end_date)

            bank_name = self.validate_and_parse_bank_name(bank.get("bank_name"))
            bank_analyses.append(self.build(bank_name, bank_start_date, bank_end_date))
        return bank_analyses

    def validate_and_parse_date(self, date_str, error_message, field_name=None):
        if date_str:
            try:
                parsed_date = datetime.fromisoformat(date_str)
                return parsed_date
            except ValueError:
                if field_name:
                    raise ValueError(f"Erro no campo '{field_name}': {error_message}")
                raise ValueError(error_message)
        else:
            if field_name:
                raise ValueError(f"Erro no campo '{field_name}': O valor da data não foi fornecido.")
            raise ValueError("O valor da data não foi fornecido.")

    def validate_date_range(self, start_date, end_date):
        if start_date >= end_date:
            raise ValueError("A data de início deve ser anterior à data de fim para o banco.")
        if end_date >= datetime.now():
            raise ValueError("A data de fim deve ser anterior à data atual para o banco.")

    def validate_and_parse_bank_name(self, bank_name) -> BankName:
        if isinstance(bank_name, BankName):
            return bank_name
        if not bank_name:
            raise ValueError("O nome do banco não foi fornecido.")
        if bank_name not in BankName._member_names_:
            raise ValueError(f"O banco '{bank_name}' não é válido.")
        return BankName[bank_name]

    def build(self, bank_name, start_date, end_date):
        return BankAnalysis(
            bank_name=bank_name,
            start_date=start_date,
            end_date=end_date
        )

    def save_all(self, analysis_id, bank_analyses):
        for bank_analysis in bank_analyses:
            bank_analysis.analysis_id = analysis_id
            BankAnalysisRepository.save(bank_analysis)

    def compute_and_persist_bank_metrics(self, bank_analysis, df_mention_analyses: pd.DataFrame):
        """
        Compute and persist bank metrics using a pandas DataFrame.

        Args:
            bank_analysis: The bank analysis object to update.
            df_mention_analyses: DataFrame containing mention analyses.
        """
        if df_mention_analyses.empty:
            print(f"[BankAnalysisService] No data to process for {bank_analysis.bank_name.value}")
            return

        # Compute metrics
        total_mentions = len(df_mention_analyses)
        negative_mentions = len(df_mention_analyses[
            df_mention_analyses['sentiment'].str.lower() == Sentiment.NEGATIVE.name.lower()
        ])  # Negative sentiment is considered negative
        positive_mentions = total_mentions - negative_mentions  # All other mentions are considered positive

        average_iedi_normalized = df_mention_analyses['iedi_normalized'].mean()
        positivity_proportion = positive_mentions / total_mentions if total_mentions > 0 else 0
        adjusted_iedi_normalized = average_iedi_normalized * positivity_proportion

        # Populate the BankAnalysis fields
        bank_analysis.total_mentions = total_mentions
        bank_analysis.positive_volume = positive_mentions
        bank_analysis.negative_volume = negative_mentions
        bank_analysis.iedi_mean = round(average_iedi_normalized, 2) if not pd.isna(average_iedi_normalized) else None
        bank_analysis.iedi_score = round(adjusted_iedi_normalized, 2) if not pd.isna(adjusted_iedi_normalized) else None

        # Persist metrics (e.g., save to BigQuery)
        self.persist_bank_analysis(bank_analysis)

    def persist_bank_analysis(self, bank_analysis):
        """
        Persist the bank analysis object to BigQuery using the repository's update method.
        """
        updated_bank_analysis = BankAnalysisRepository.update(bank_analysis)
        if updated_bank_analysis:
            print(f"[BankAnalysisService] Successfully persisted metrics for {bank_analysis.bank_name.value}")
        else:
            print(f"[BankAnalysisService] Failed to persist metrics for {bank_analysis.bank_name.value}")
