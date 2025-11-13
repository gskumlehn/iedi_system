from typing import Dict, List, Tuple
from app.constants.weights import (NICHE_OUTLET_WEIGHT, REACH_GROUP_THRESHOLDS,
                                     REACH_GROUP_WEIGHTS, RELEVANT_OUTLET_WEIGHT,
                                     SUBTITLE_WEIGHT, TITLE_WEIGHT)
from app.enums.reach_group import ReachGroup
from app.enums.sentiment import Sentiment
from app.models.bank import Bank
from app.models.media_outlet import NicheMediaOutlet, RelevantMediaOutlet

class IEDICalculatorService:

    def calculate_mention(self, mention: Dict, bank: Bank, 
                         relevant_outlets: List[RelevantMediaOutlet],
                         niche_outlets: List[NicheMediaOutlet]) -> Dict:
        title_points, title_verified = self._verify_title(mention.get("title", ""), bank)
        subtitle_points, subtitle_verified = self._verify_subtitle(
            mention.get("snippet", ""),
            mention.get("fullText", ""),
            bank
        )
        reach_group, reach_points = self._classify_reach_group(mention.get("monthlyVisitors", 0))
        relevant_points = self._verify_relevant_outlet(mention.get("domain", ""), relevant_outlets)
        niche_points = self._verify_niche_outlet(mention.get("domain", ""), niche_outlets)
        
        numerator = title_points + subtitle_points + reach_points + relevant_points + niche_points
        denominator = TITLE_WEIGHT + reach_points + RELEVANT_OUTLET_WEIGHT
        
        if subtitle_verified:
            denominator += SUBTITLE_WEIGHT
        if reach_group != ReachGroup.A:
            denominator += NICHE_OUTLET_WEIGHT
        
        sentiment = mention.get("sentiment", Sentiment.NEUTRAL)
        sign = 1 if sentiment == Sentiment.POSITIVE else (-1 if sentiment == Sentiment.NEGATIVE else 0)
        
        iedi_normalized = (numerator / denominator) * sign if denominator > 0 and sign != 0 else 0.0
        iedi_score = ((iedi_normalized + 1) / 2) * 10
        
        return {
            "iedi_score": round(iedi_score, 2),
            "iedi_normalized": round(iedi_normalized, 4),
            "sentiment": sentiment,
            "reach_group": reach_group,
            "numerator": numerator,
            "denominator": denominator,
            "title_verified": title_verified,
            "subtitle_verified": subtitle_verified,
            "relevant_outlet_verified": relevant_points > 0,
            "niche_outlet_verified": niche_points > 0
        }

    def aggregate_results(self, mentions: List[Dict]) -> Dict:
        if not mentions:
            return self._empty_result()
        
        positive = sum(1 for m in mentions if m["sentiment"] == Sentiment.POSITIVE)
        negative = sum(1 for m in mentions if m["sentiment"] == Sentiment.NEGATIVE)
        neutral = sum(1 for m in mentions if m["sentiment"] == Sentiment.NEUTRAL)
        total = len(mentions)
        
        avg_iedi = sum(m["iedi_score"] for m in mentions) / total
        final_iedi = avg_iedi * (positive / total) if total > 0 else 0.0
        
        return {
            "total_volume": total,
            "positive_volume": positive,
            "negative_volume": negative,
            "neutral_volume": neutral,
            "average_iedi": round(avg_iedi, 2),
            "final_iedi": round(final_iedi, 2),
            "positivity_rate": round((positive / total * 100), 2) if total > 0 else 0.0,
            "negativity_rate": round((negative / total * 100), 2) if total > 0 else 0.0
        }

    def _verify_title(self, title: str, bank: Bank) -> Tuple[int, bool]:
        if self._check_bank_mention(title, bank):
            return (TITLE_WEIGHT, True)
        return (0, False)

    def _verify_subtitle(self, snippet: str, full_text: str, bank: Bank) -> Tuple[int, bool]:
        if snippet == full_text:
            return (0, False)
        first_paragraph = self._extract_first_paragraph(full_text)
        if self._check_bank_mention(first_paragraph, bank):
            return (SUBTITLE_WEIGHT, True)
        return (0, True)

    def _verify_relevant_outlet(self, domain: str, outlets: List[RelevantMediaOutlet]) -> int:
        domain_lower = domain.lower()
        for outlet in outlets:
            if outlet.domain.lower() in domain_lower:
                return RELEVANT_OUTLET_WEIGHT
        return 0

    def _verify_niche_outlet(self, domain: str, outlets: List[NicheMediaOutlet]) -> int:
        domain_lower = domain.lower()
        for outlet in outlets:
            if outlet.domain.lower() in domain_lower:
                return NICHE_OUTLET_WEIGHT
        return 0

    def _classify_reach_group(self, monthly_visitors: int) -> Tuple[str, int]:
        if monthly_visitors > REACH_GROUP_THRESHOLDS["A"]:
            return (ReachGroup.A, REACH_GROUP_WEIGHTS["A"])
        elif monthly_visitors > REACH_GROUP_THRESHOLDS["B"]:
            return (ReachGroup.B, REACH_GROUP_WEIGHTS["B"])
        elif monthly_visitors >= REACH_GROUP_THRESHOLDS["C"]:
            return (ReachGroup.C, REACH_GROUP_WEIGHTS["C"])
        return (ReachGroup.D, REACH_GROUP_WEIGHTS["D"])

    def _check_bank_mention(self, text: str, bank: Bank) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        if bank.name.lower() in text_lower:
            return True
        return any(v.lower() in text_lower for v in bank.variations)

    def _extract_first_paragraph(self, full_text: str) -> str:
        if not full_text:
            return ""
        paragraphs = full_text.split('\n\n')
        if len(paragraphs) > 1 and paragraphs[0].strip():
            return paragraphs[0].strip()
        return full_text[:300].strip()

    def _empty_result(self) -> Dict:
        return {
            "total_volume": 0,
            "positive_volume": 0,
            "negative_volume": 0,
            "neutral_volume": 0,
            "average_iedi": 0.0,
            "final_iedi": 0.0,
            "positivity_rate": 0.0,
            "negativity_rate": 0.0
        }
