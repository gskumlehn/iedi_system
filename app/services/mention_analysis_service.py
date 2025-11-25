from app.repositories.bank_repository import BankRepository
from app.services.brandwatch_service import BrandwatchService
from app.services.mention_service import MentionService
from app.models.mention_analysis import MentionAnalysis
from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup
from app.constants.weights import TITLE_WEIGHT, SUBTITLE_WEIGHT, RELEVANT_OUTLET_WEIGHT, NICHE_OUTLET_WEIGHT
from app.constants.weights import REACH_GROUP_THRESHOLDS, REACH_GROUP_WEIGHTS
from app.repositories.media_outlet_repository import MediaOutletRepository
from app.repositories.mention_analysis_repository import MentionAnalysisRepository
from app.services.bank_analysis_service import BankAnalysisService

class MentionAnalysisService:

    brandwatch_service = BrandwatchService()
    mention_service = MentionService()
    bank_analysis_service = BankAnalysisService()

    def process_mention_analysis(self, analysis, bank_analyses, parent_name):
        if analysis.is_custom_dates:
            self.process_custom_dates(analysis, bank_analyses, parent_name)
        else:
            self.process_standard_dates(analysis, bank_analyses, parent_name)

    def process_standard_dates(self, analysis, bank_analyses, parent_name):
        results = {}
        if bank_analyses:
            start_date = bank_analyses[0].start_date
            end_date = bank_analyses[0].end_date
            category_names = [bank.bank_name.value for bank in bank_analyses]  # List of categories for banks
            mentions = self.mention_service.fetch_and_filter_mentions(
                start_date=start_date,
                end_date=end_date,
                query_name=analysis.query_name,
                parent_name=parent_name,
                category_names=category_names
            )

            for bank_analysis in bank_analyses:
                processed = self.process_mentions(mentions, bank_analysis.bank_name)
                results[bank_analysis.bank_name.value] = processed

                self.bank_analysis_service.compute_and_persist_bank_metrics(bank_analysis, processed)
        return results

    def process_custom_dates(self, analysis, bank_analyses, parent_name):
        results = {}
        for bank_analysis in bank_analyses:
            mentions = self.mention_service.fetch_and_filter_mentions(
                start_date=bank_analysis.start_date,
                end_date=bank_analysis.end_date,
                query_name=analysis.query_name,
                parent_name=parent_name,
                category_names=[bank_analysis.bank_name.value]  # Specific category for the bank
            )
            processed = self.process_mentions(mentions, bank_analysis.bank_name)
            results[bank_analysis.bank_name.value] = processed

            self.bank_analysis_service.compute_and_persist_bank_metrics(bank_analysis, processed)
        return results

    def process_mentions(self, mentions, bank_name):
        mention_analyses = []
        bank = BankRepository.find_by_name(bank_name)
        for mention in mentions:
            if self.is_valid_for_bank(mention, bank):
                mention_analysis = self.create_mention_analysis(mention, bank)
                mention_analyses.append(mention_analysis)

        if mention_analyses:
            for analysis in mention_analyses:
                existing_analysis = MentionAnalysisRepository.find_by_mention_id_and_bank_name(
                    analysis.mention_id, analysis.bank_name
                )
                if existing_analysis:
                    MentionAnalysisRepository.update(existing_analysis, analysis)
                else:
                    MentionAnalysisRepository.save(analysis)

        return mention_analyses

    def is_valid_for_bank(self, mention, bank):
        return bank.name.value in mention.categories

    def create_mention_analysis(self, mention, bank):
        mentions_analysis = MentionAnalysis()
        mentions_analysis.mention_id = mention.url
        mentions_analysis.bank_name = bank.name

        mentions_analysis.sentiment = Sentiment.from_string(mention.sentiment) if mention.sentiment else None
        mentions_analysis.reach_group = self.classify_reach_group(mention.monthlyVisitors)

        mentions_analysis.title_mentioned = False
        for v in bank.variations:
            if v and v.lower() in mention.title.lower():
                mentions_analysis.title_mentioned = True
                break

        mentions_analysis.subtitle_used = mention.snippet != mention.full_text
        mentions_analysis.subtitle_mentioned = False
        if mentions_analysis.subtitle_used:
            first_para = self.extract_first_paragraph(mention.full_text)
            para_lower = first_para.lower()

            for v in bank.variations:
                if v and v.lower() in para_lower:
                    mentions_analysis.subtitle_mentioned = True
                    break

        relevant_domains = MediaOutletRepository.find_by_niche(False)
        niche_domains = MediaOutletRepository.find_by_niche(True)

        relevant_vehicle = mention.domain in relevant_domains
        niche_vehicle = mention.domain in niche_domains
        mentions_analysis.niche_vehicle = niche_vehicle

        reach_weight = REACH_GROUP_WEIGHTS.get(mentions_analysis.reach_group.name, 0)

        title_pts = TITLE_WEIGHT if mentions_analysis.title_mentioned else 0
        subtitle_pts = SUBTITLE_WEIGHT if (mentions_analysis.subtitle_mentioned and mentions_analysis.subtitle_used) else 0
        relevant_pts = RELEVANT_OUTLET_WEIGHT if relevant_vehicle else 0
        niche_pts = NICHE_OUTLET_WEIGHT if niche_vehicle else 0

        mentions_analysis.numerator = title_pts + subtitle_pts + reach_weight + relevant_pts + niche_pts

        if mentions_analysis.subtitle_used:
            if mentions_analysis.reach_group == ReachGroup.A:
                mentions_analysis.denominator = TITLE_WEIGHT + SUBTITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT
            else:
                mentions_analysis.denominator = TITLE_WEIGHT + SUBTITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT
        else:
            if mentions_analysis.reach_group == ReachGroup.A:
                mentions_analysis.denominator = TITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT
            else:
                mentions_analysis.denominator = TITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT


        if mentions_analysis.sentiment == Sentiment.NEGATIVE:
            sign = -1
        else:
            sign = 1

        if mentions_analysis.denominator:
            mentions_analysis.iedi_score = (mentions_analysis.numerator / mentions_analysis.denominator) * sign
            mentions_analysis.iedi_normalized = ((mentions_analysis.iedi_score + 1) / 2) * 10
        else:
            mentions_analysis.iedi_score = 0
            mentions_analysis.iedi_normalized = 0

        return mentions_analysis

    def extract_first_paragraph(self, full_text: str) -> str:
        if not full_text:
            return ""
        parts = full_text.split("\n\n")
        return parts[0].strip() if len(parts) > 0 else full_text[:300].strip()

    def classify_reach_group(self, monthly_visitors: int):
        if monthly_visitors is None:
            return None
        try:
            mv = int(monthly_visitors)
        except Exception:
            return None

        if mv > REACH_GROUP_THRESHOLDS["A"]:
            return ReachGroup.A
        if mv > REACH_GROUP_THRESHOLDS["B"]:
            return ReachGroup.B
        if mv >= REACH_GROUP_THRESHOLDS["C"]:
            return ReachGroup.C
        return ReachGroup.D
