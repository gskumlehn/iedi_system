from typing import Dict
import logging
import re

from app.models.bank import Bank
from app.enums.reach_group import ReachGroup
from app.enums.sentiment import Sentiment

logger = logging.getLogger(__name__)


class IEDICalculationService:
    WEIGHTS = {
        'title': 100,
        'subtitle': 80,
        'relevant_outlet': 95,
        'niche_outlet': 54,
        'reach_group': {
            ReachGroup.A: 91,
            ReachGroup.B: 85,
            ReachGroup.C: 24,
            ReachGroup.D: 20
        }
    }

    def calculate_iedi(self, mention_data: Dict, bank: Bank) -> Dict:
        title_verified = self._check_title(mention_data, bank)
        subtitle_verified = self._check_subtitle(mention_data, bank)
        
        reach_group = self._get_reach_group(mention_data)
        relevant_outlet_verified = self._check_relevant_outlet(mention_data)
        niche_outlet_verified = self._check_niche_outlet(mention_data)
        
        numerator = self._calculate_numerator(
            title_verified=title_verified,
            subtitle_verified=subtitle_verified,
            reach_group=reach_group,
            relevant_outlet_verified=relevant_outlet_verified,
            niche_outlet_verified=niche_outlet_verified
        )
        
        denominator = self._calculate_denominator(
            reach_group=reach_group,
            has_subtitle=self._should_check_subtitle(mention_data)
        )
        
        sentiment = self._get_sentiment(mention_data)
        sign = self._get_sign(sentiment)
        
        iedi_score = (numerator / denominator) * sign if denominator > 0 else 0
        iedi_normalized = (iedi_score + 1) * 5
        
        return {
            'iedi_score': round(iedi_score, 4),
            'iedi_normalized': round(iedi_normalized, 2),
            'numerator': numerator,
            'denominator': denominator,
            'title_verified': 1 if title_verified else 0,
            'subtitle_verified': 1 if subtitle_verified else 0,
            'relevant_outlet_verified': 1 if relevant_outlet_verified else 0,
            'niche_outlet_verified': 1 if niche_outlet_verified else 0
        }

    def _check_title(self, mention_data: Dict, bank: Bank) -> bool:
        title = mention_data.get('title', '').lower()
        if not title:
            return False
        
        bank_name = bank.name.value.lower()
        pattern = r'\b' + re.escape(bank_name) + r'\b'
        return bool(re.search(pattern, title, re.IGNORECASE))

    def _check_subtitle(self, mention_data: Dict, bank: Bank) -> bool:
        if not self._should_check_subtitle(mention_data):
            return False
        
        snippet = mention_data.get('snippet', '').lower()
        if not snippet:
            return False
        
        bank_name = bank.name.value.lower()
        pattern = r'\b' + re.escape(bank_name) + r'\b'
        return bool(re.search(pattern, snippet, re.IGNORECASE))

    def _should_check_subtitle(self, mention_data: Dict) -> bool:
        snippet = mention_data.get('snippet', '')
        full_text = mention_data.get('fullText', '')
        return snippet != full_text

    def _get_reach_group(self, mention_data: Dict) -> ReachGroup:
        monthly_visitors = mention_data.get('monthlyVisitors', 0)
        
        if monthly_visitors > 29_000_000:
            return ReachGroup.A
        elif monthly_visitors > 11_000_000:
            return ReachGroup.B
        elif monthly_visitors >= 500_000:
            return ReachGroup.C
        else:
            return ReachGroup.D

    def _check_relevant_outlet(self, mention_data: Dict) -> bool:
        return not mention_data.get('isNiche', False)

    def _check_niche_outlet(self, mention_data: Dict) -> bool:
        return mention_data.get('isNiche', False)

    def _calculate_numerator(
        self,
        title_verified: bool,
        subtitle_verified: bool,
        reach_group: ReachGroup,
        relevant_outlet_verified: bool,
        niche_outlet_verified: bool
    ) -> int:
        numerator = 0
        
        if title_verified:
            numerator += self.WEIGHTS['title']
        
        if subtitle_verified:
            numerator += self.WEIGHTS['subtitle']
        
        numerator += self.WEIGHTS['reach_group'][reach_group]
        
        if relevant_outlet_verified:
            numerator += self.WEIGHTS['relevant_outlet']
        
        if niche_outlet_verified:
            numerator += self.WEIGHTS['niche_outlet']
        
        return numerator

    def _calculate_denominator(self, reach_group: ReachGroup, has_subtitle: bool) -> int:
        denominator = self.WEIGHTS['title']
        
        if has_subtitle:
            denominator += self.WEIGHTS['subtitle']
        
        denominator += self.WEIGHTS['reach_group'][reach_group]
        denominator += self.WEIGHTS['relevant_outlet']
        
        if reach_group != ReachGroup.A:
            denominator += self.WEIGHTS['niche_outlet']
        
        return denominator

    def _get_sentiment(self, mention_data: Dict) -> Sentiment:
        sentiment_str = mention_data.get('sentiment', 'neutral').lower()
        
        if sentiment_str == 'positive':
            return Sentiment.POSITIVE
        elif sentiment_str == 'negative':
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL

    def _get_sign(self, sentiment: Sentiment) -> int:
        if sentiment == Sentiment.POSITIVE:
            return 1
        elif sentiment == Sentiment.NEGATIVE:
            return -1
        else:
            return 0
