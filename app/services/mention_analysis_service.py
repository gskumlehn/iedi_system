from app.repositories.bank_repository import BankRepository
from app.services.brandwatch_service import BrandwatchService
from app.services.mention_service import MentionService
from app.models.mention_analysis import MentionAnalysis
from app.utils.date_utils import DateUtils
from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup
from app.constants.weights import TITLE_WEIGHT, SUBTITLE_WEIGHT, RELEVANT_OUTLET_WEIGHT, NICHE_OUTLET_WEIGHT
from app.constants.weights import REACH_GROUP_THRESHOLDS

class MentionAnalysisService:

    brandwatch_service = BrandwatchService()
    mention_service = MentionService()

    def process_mention_analysis(self, analysis, bank_analyses):
        if analysis.is_custom_dates:
            self.process_custom_dates(analysis, bank_analyses)
        else:
            self.process_standard_dates(analysis, bank_analyses)

    def process_custom_dates(self, analysis, bank_analyses):
        for bank_analysis in bank_analyses:
            mentions = self.mention_service.fetch_and_filter_mentions(
                start_date=bank_analysis.start_date,
                end_date=bank_analysis.end_date,
                query_name=analysis.query_name
            )
            self.process_mentions(mentions, bank_analysis.bank_name)

    def process_standard_dates(self, analysis, bank_analyses):
        if bank_analyses:
            start_date = bank_analyses[0].start_date
            end_date = bank_analyses[0].end_date
            mentions = self.mention_service.fetch_and_filter_mentions(
                start_date=start_date,
                end_date=end_date,
                query_name=analysis.query_name
            )

            for bank_analysis in bank_analyses:
                self.process_mentions(mentions, bank_analysis.bank_name)

    def process_mentions(self, mentions, bank_name):
        mention_analyses = []

        bank = BankRepository.find_by_name(bank_name)
        for mention in mentions:
            if self.is_valid_for_bank(mention, bank):
                mention_analysis = self.create_mention_analysis(mention, bank)
                mention_analyses.append(mention_analysis)
        return mention_analyses

    def is_valid_for_bank(self, mention, bank):
        try:
            categories = mention.categories
        except AttributeError:
            categories = None
        return (categories is not None) and (bank in categories)

    def create_mention_analysis(self, mention, bank):
        mentions_analysis = MentionAnalysis()
        mentions_analysis.mention_id = mention.id
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

        mentions_analysis.numerator = (TITLE_WEIGHT if mentions_analysis.title_mentioned else 0) + (SUBTITLE_WEIGHT if mentions_analysis.subtitle_mentioned and mentions_analysis.subtitle_used else 0)
        if mentions_analysis.subtitle_used:
            mentions_analysis.denominator = TITLE_WEIGHT + SUBTITLE_WEIGHT
        else:
            mentions_analysis.denominator = TITLE_WEIGHT

        if mentions_analysis.sentiment_enum == Sentiment.POSITIVE or mentions_analysis.sentiment_enum == Sentiment.NEUTRAL:
            sign = 1
        elif mentions_analysis.sentiment_enum == Sentiment.NEGATIVE:
            sign = -1

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
