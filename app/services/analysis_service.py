from datetime import datetime
from typing import Dict, List
from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository, BankPeriodRepository
from app.repositories.bank_repository import BankRepository
from app.repositories.iedi_result_repository import IEDIResultRepository
from app.repositories.media_outlet_repository import NicheMediaOutletRepository, RelevantMediaOutletRepository
from app.repositories.mention_repository import MentionRepository
from app.services.iedi_calculator_service import IEDICalculatorService

class AnalysisService:

    def __init__(self):
        self.analysis_repo = AnalysisRepository()
        self.bank_period_repo = BankPeriodRepository()
        self.bank_repo = BankRepository()
        self.mention_repo = MentionRepository()
        self.iedi_result_repo = IEDIResultRepository()
        self.relevant_outlet_repo = RelevantMediaOutletRepository()
        self.niche_outlet_repo = NicheMediaOutletRepository()
        self.calculator = IEDICalculatorService()

    def create_analysis(self, name: str, query: str, custom_period: bool, 
                       bank_periods: List[Dict]) -> Dict:
        analysis = self.analysis_repo.create(name=name, query=query, custom_period=custom_period)
        
        for bp in bank_periods:
            self.bank_period_repo.create(
                analysis_id=analysis.id,
                bank_id=bp["bank_id"],
                category_detail=bp["category_detail"],
                start_date=datetime.fromisoformat(bp["start_date"]),
                end_date=datetime.fromisoformat(bp["end_date"])
            )
        
        return self._analysis_to_dict(analysis)

    def get_all_analyses(self) -> List[Dict]:
        analyses = self.analysis_repo.find_all()
        return [self._analysis_to_dict(a) for a in analyses]

    def get_analysis_results(self, analysis_id: int) -> Dict:
        analysis = self.analysis_repo.find_by_id(analysis_id)
        if not analysis:
            return None
        
        results = self.iedi_result_repo.find_by_analysis(analysis_id)
        return {
            "analysis": self._analysis_to_dict(analysis),
            "results": [self._result_to_dict(r) for r in results]
        }

    def process_mentions(self, analysis_id: int, mentions_by_bank: Dict[int, List[Dict]]) -> Dict:
        relevant_outlets = self.relevant_outlet_repo.find_all_active()
        niche_outlets = self.niche_outlet_repo.find_all_active()
        
        results = []
        for bank_id, mentions in mentions_by_bank.items():
            bank = self.bank_repo.find_by_id(bank_id)
            if not bank:
                continue
            
            calculated_mentions = []
            for mention in mentions:
                calc_result = self.calculator.calculate_mention(
                    mention, bank, relevant_outlets, niche_outlets
                )
                
                self.mention_repo.create(
                    analysis_id=analysis_id,
                    bank_id=bank_id,
                    brandwatch_id=mention.get("id"),
                    category_detail=mention.get("categoryDetail"),
                    sentiment=calc_result["sentiment"],
                    title=mention.get("title"),
                    snippet=mention.get("snippet"),
                    full_text=mention.get("fullText"),
                    domain=mention.get("domain"),
                    monthly_visitors=mention.get("monthlyVisitors"),
                    reach_group=calc_result["reach_group"],
                    published_date=datetime.fromisoformat(mention.get("publishedDate")),
                    iedi_score=calc_result["iedi_score"],
                    iedi_normalized=calc_result["iedi_normalized"],
                    numerator=calc_result["numerator"],
                    denominator=calc_result["denominator"],
                    title_verified=calc_result["title_verified"],
                    subtitle_verified=calc_result["subtitle_verified"],
                    relevant_outlet_verified=calc_result["relevant_outlet_verified"],
                    niche_outlet_verified=calc_result["niche_outlet_verified"]
                )
                
                calculated_mentions.append(calc_result)
            
            aggregated = self.calculator.aggregate_results(calculated_mentions)
            
            iedi_result = self.iedi_result_repo.create(
                analysis_id=analysis_id,
                bank_id=bank_id,
                total_volume=aggregated["total_volume"],
                positive_volume=aggregated["positive_volume"],
                negative_volume=aggregated["negative_volume"],
                neutral_volume=aggregated["neutral_volume"],
                average_iedi=aggregated["average_iedi"],
                final_iedi=aggregated["final_iedi"],
                positivity_rate=aggregated["positivity_rate"],
                negativity_rate=aggregated["negativity_rate"]
            )
            
            results.append(self._result_to_dict(iedi_result))
        
        return {"results": results}

    def _analysis_to_dict(self, analysis: Analysis) -> Dict:
        return {
            "id": analysis.id,
            "name": analysis.name,
            "query": analysis.query,
            "custom_period": analysis.custom_period,
            "created_at": analysis.created_at.isoformat()
        }

    def _result_to_dict(self, result) -> Dict:
        return {
            "id": result.id,
            "analysis_id": result.analysis_id,
            "bank_id": result.bank_id,
            "total_volume": result.total_volume,
            "positive_volume": result.positive_volume,
            "negative_volume": result.negative_volume,
            "neutral_volume": result.neutral_volume,
            "average_iedi": result.average_iedi,
            "final_iedi": result.final_iedi,
            "positivity_rate": result.positivity_rate,
            "negativity_rate": result.negativity_rate
        }
