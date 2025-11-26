import pandas as pd
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
from app.repositories.mention_repository import MentionRepository
from app.services.bank_analysis_service import BankAnalysisService

class MentionAnalysisService:

    brandwatch_service = BrandwatchService()
    mention_service = MentionService()
    bank_analysis_service = BankAnalysisService()

    def process_mention_analysis(self, analysis, bank_analyses, parent_name):
        MentionRepository.set_analysis_context(analysis.id)
        MentionAnalysisRepository.set_analysis_context(analysis.id)
        
        try:
            if analysis.is_custom_dates:
                self.process_custom_dates(analysis, bank_analyses, parent_name)
            else:
                self.process_standard_dates(analysis, bank_analyses, parent_name)
        finally:
            MentionRepository.flush_batch()
            MentionAnalysisRepository.flush_batch()

    def process_standard_dates(self, analysis, bank_analyses, parent_name):
        results = {}
        if bank_analyses:
            start_date = bank_analyses[0].start_date
            end_date = bank_analyses[0].end_date
            category_names = [bank.bank_name.value for bank in bank_analyses]
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
                category_names=[bank_analysis.bank_name.value]
            )

            processed = self.process_mentions(mentions, bank_analysis.bank_name)
            results[bank_analysis.bank_name.value] = processed

            self.bank_analysis_service.compute_and_persist_bank_metrics(bank_analysis, processed)
        return results

    def process_mentions(self, mentions, bank_name):
        bank = BankRepository.find_by_name(bank_name)
        df_mention_analyses = self.create_mention_analysis_bulk(mentions, bank)
        mention_analyses_dicts = df_mention_analyses.to_dict(orient='records')
        MentionAnalysisRepository.bulk_save(mention_analyses_dicts)
        return df_mention_analyses

    def is_valid_for_bank(self, mention, bank):
        return bank.name.value in mention.categories

    def create_mention_analysis(self, mention, bank):
        mentions_analysis = MentionAnalysis()
        mentions_analysis.mention_url = mention.url
        mentions_analysis.bank_name = bank.name
        mentions_analysis.sentiment = Sentiment.from_string(mention.sentiment) if mention.sentiment else None
        mentions_analysis.reach_group = self.classify_reach_group(mention.monthly_visitors)
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
        relevant_domains = [media_outlet.domain for media_outlet in MediaOutletRepository.find_by_niche(False)]
        niche_domains = [media_outlet.domain for media_outlet in MediaOutletRepository.find_by_niche(True)]
        relevant_vehicle = mention.domain in relevant_domains
        niche_vehicle = mention.domain in niche_domains
        mentions_analysis.niche_vehicle = niche_vehicle
        reach_group = mentions_analysis.reach_group if mentions_analysis.reach_group else ReachGroup.D
        reach_weight = REACH_GROUP_WEIGHTS.get(reach_group.name, 0)
        title_pts = TITLE_WEIGHT if mentions_analysis.title_mentioned else 0
        subtitle_pts = SUBTITLE_WEIGHT if (mentions_analysis.subtitle_mentioned and mentions_analysis.subtitle_used) else 0
        relevant_pts = RELEVANT_OUTLET_WEIGHT if relevant_vehicle else 0
        niche_pts = NICHE_OUTLET_WEIGHT if niche_vehicle else 0
        mentions_analysis.numerator = title_pts + subtitle_pts + reach_weight + relevant_pts + niche_pts
        if reach_group == ReachGroup.A:
            if mentions_analysis.subtitle_used:
                mentions_analysis.denominator = TITLE_WEIGHT + SUBTITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT
            else:
                mentions_analysis.denominator = TITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT
        else:
            if mentions_analysis.subtitle_used:
                mentions_analysis.denominator = TITLE_WEIGHT + SUBTITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT
            else:
                mentions_analysis.denominator = TITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT
        sentiment = mentions_analysis.sentiment if mentions_analysis.sentiment else Sentiment.NEUTRAL
        if sentiment == Sentiment.NEGATIVE:
            sign = -1
        else:
            sign = 1
        if mentions_analysis.numerator is not None and mentions_analysis.denominator:
            raw_score = (mentions_analysis.numerator / mentions_analysis.denominator) * sign
            raw_normalized = ((raw_score + 1) / 2) * 10
        else:
            raw_score = 0
            raw_normalized = 0
        mentions_analysis.iedi_score = round(raw_score, 2)
        mentions_analysis.iedi_normalized = round(raw_normalized, 2)
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

    def create_mention_analysis_bulk(self, mentions, bank):
        df = pd.DataFrame([{
            'mention_url': mention.url,
            'title': mention.title,
            'snippet': mention.snippet,
            'full_text': mention.full_text,
            'domain': mention.domain,
            'published_date': mention.published_date,
            'sentiment': mention.sentiment,
            'categories': mention.categories,
            'monthly_visitors': mention.monthly_visitors or 0
        } for mention in mentions])
        df['bank_name'] = bank.name.value
        df['sentiment'] = df['sentiment'].apply(lambda s: Sentiment.from_string(s) if s else None)
        df['reach_group'] = df['monthly_visitors'].apply(self.classify_reach_group)
        df['title_mentioned'] = df['title'].apply(
            lambda title: any(v.lower() in title.lower() for v in bank.variations if v)
        )
        df['subtitle_used'] = df['snippet'] != df['full_text']
        df['subtitle_mentioned'] = df.apply(
            lambda row: any(
                v.lower() in self.extract_first_paragraph(row['full_text']).lower()
                for v in bank.variations if v
            ) if row['subtitle_used'] else False,
            axis=1
        )
        relevant_domains = [media_outlet.domain for media_outlet in MediaOutletRepository.find_by_niche(False)]
        niche_domains = [media_outlet.domain for media_outlet in MediaOutletRepository.find_by_niche(True)]
        df['relevant_vehicle'] = df['domain'].isin(relevant_domains)
        df['niche_vehicle'] = df['domain'].isin(niche_domains)
        df['numerator'] = (
            df['title_mentioned'].fillna(0).astype(int) * TITLE_WEIGHT +
            df['subtitle_mentioned'].fillna(0).astype(int) * df['subtitle_used'].fillna(0).astype(int) * SUBTITLE_WEIGHT +
            df['reach_group'].apply(lambda rg: REACH_GROUP_WEIGHTS.get(rg.name, 0) if rg else 0) +
            df['relevant_vehicle'].fillna(0).astype(int) * RELEVANT_OUTLET_WEIGHT +
            df['niche_vehicle'].fillna(0).astype(int) * NICHE_OUTLET_WEIGHT
        )
        def calculate_denominator(row):
            reach_weight = REACH_GROUP_WEIGHTS.get(row['reach_group'].name, 0) if row['reach_group'] else 0
            if row['reach_group'] == ReachGroup.A:
                if row['subtitle_used']:
                    return TITLE_WEIGHT + SUBTITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT
                else:
                    return TITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT
            else:
                if row['subtitle_used']:
                    return TITLE_WEIGHT + SUBTITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT
                else:
                    return TITLE_WEIGHT + reach_weight + RELEVANT_OUTLET_WEIGHT + NICHE_OUTLET_WEIGHT
        df['denominator'] = df.apply(calculate_denominator, axis=1)
        df['iedi_score'] = df.apply(
            lambda row: round(max(-1, min(1, (row['numerator'] / row['denominator']) * (-1 if row['sentiment'] == Sentiment.NEGATIVE else 1))), 2)
            if row['denominator'] > 0 else 0,
            axis=1
        )
        df['iedi_normalized'] = df['iedi_score'].apply(lambda score: round(((score + 1) / 2) * 10, 2))
        return df
