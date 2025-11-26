from typing import List, Optional, Dict, Any
from datetime import datetime
from app.infra.bq_sa import get_session
from app.models.mention_analysis import MentionAnalysis
from sqlalchemy.orm import joinedload
from app.infra.csv_storage import CSVStorage

class MentionAnalysisRepository:
    
    # ========================================
    # MÉTODOS ORIGINAIS (BANCO DE DADOS)
    # Comentados para melhorar performance
    # ========================================
    
    # @staticmethod
    # def create(analysis_id: str, mention_id: str, bank_id: str, **kwargs) -> MentionAnalysis:
    #     with get_session() as session:
    #         mention_analysis = MentionAnalysis(
    #             analysis_id=analysis_id,
    #             mention_id=mention_id,
    #             bank_id=bank_id,
    #             created_at=datetime.now(),
    #             **kwargs
    #         )
    #         session.add(mention_analysis)
    #         session.commit()
    #         session.refresh(mention_analysis)
    #         return mention_analysis
    
    # @staticmethod
    # def find_by_mention(mention_id: str) -> List[MentionAnalysis]:
    #     with get_session() as session:
    #         return session.query(MentionAnalysis).options(joinedload('*')).filter(
    #             MentionAnalysis.mention_id == mention_id
    #         ).all()
    
    # @staticmethod
    # def update_iedi_scores(analysis_id: str, mention_id: str, bank_id: str,
    #                       iedi_score: float, numerator: int, denominator: int, **kwargs) -> Optional[MentionAnalysis]:
    #     with get_session() as session:
    #         mention_analysis = session.query(MentionAnalysis).filter(
    #             MentionAnalysis.analysis_id == analysis_id,
    #             MentionAnalysis.mention_id == mention_id,
    #             MentionAnalysis.bank_id == bank_id
    #         ).first()
    #
    #         if not mention_analysis:
    #             return None
    #
    #         mention_analysis.iedi_score = iedi_score
    #         mention_analysis.numerator = numerator
    #         mention_analysis.denominator = denominator
    #
    #         for key, value in kwargs.items():
    #             if hasattr(mention_analysis, key):
    #                 setattr(mention_analysis, key, value)
    #
    #         session.commit()
    #         session.refresh(mention_analysis)
    #         return mention_analysis
    
    # @staticmethod
    # def bulk_save(mention_analyses: List[MentionAnalysis]):
    #    with get_session() as session:
    #         session.add_all(mention_analyses)
    #         session.commit()
    
    # @staticmethod
    # def find_by_bank_name(bank_name):
    #     """Busca todos os MentionAnalysis de um banco"""
    #     with get_session() as session:
    #         return session.query(MentionAnalysis).filter(
    #             MentionAnalysis._bank_name == bank_name.name
    #         ).all()
    
    # @staticmethod
    # def find_by_mention_id_and_bank_name(mention_id: str, bank_name: str) -> Optional[MentionAnalysis]:
    #     with get_session() as session:
    #         return session.query(MentionAnalysis).filter(
    #             MentionAnalysis.mention_id == mention_id,
    #             MentionAnalysis._bank_name == bank_name
    #         ).first()
    
    # @staticmethod
    # def update(existing_analysis: MentionAnalysis, new_analysis: MentionAnalysis):
    #     with get_session() as session:
    #         for attr in vars(new_analysis):
    #             if hasattr(existing_analysis, attr):
    #                 setattr(existing_analysis, attr, getattr(new_analysis, attr))
    #         session.commit()
    
    # @staticmethod
    # def save(analysis: MentionAnalysis):
    #     with get_session() as session:
    #         session.add(analysis)
    #         session.commit()
    
    # ========================================
    # NOVOS MÉTODOS (CSV COM PANDAS)
    # ========================================
    
    # Armazenamento temporário em memória para batch save
    _batch_mention_analyses = []
    _current_analysis_id = None
    
    @classmethod
    def set_analysis_context(cls, analysis_id: str):
        """Define o contexto da análise atual para salvar no CSV correto"""
        cls._current_analysis_id = analysis_id
        cls._batch_mention_analyses = []
    
    @classmethod
    def create(cls, analysis_id: str, mention_url: str, bank_id: str, **kwargs) -> MentionAnalysis:
        """
        Cria mention_analysis (não usado no fluxo atual, mas mantido para compatibilidade).
        """
        mention_analysis = MentionAnalysis(
            analysis_id=analysis_id,
            mention_url=mention_url,
            bank_id=bank_id,
            **kwargs
        )
        return cls.save(mention_analysis)
    
    @classmethod
    def save(cls, analysis: MentionAnalysis) -> MentionAnalysis:
        """
        Salva mention_analysis em batch (memória).
        Chame flush_batch() para persistir em CSV.
        """
        if not cls._current_analysis_id:
            raise ValueError("Analysis context não definido. Chame set_analysis_context() primeiro.")
        
        # Converter mention_analysis para dict
        analysis_dict = {
            'mention_url': analysis.mention_url,
            'bank_name': analysis.bank_name.name if hasattr(analysis.bank_name, 'name') else str(analysis.bank_name),
            'sentiment': analysis.sentiment.name if hasattr(analysis.sentiment, 'name') else str(analysis.sentiment) if analysis.sentiment else None,
            'reach_group': analysis.reach_group.name if hasattr(analysis.reach_group, 'name') else str(analysis.reach_group) if analysis.reach_group else None,
            'niche_vehicle': analysis.niche_vehicle,
            'title_mentioned': analysis.title_mentioned,
            'subtitle_used': analysis.subtitle_used,
            'subtitle_mentioned': analysis.subtitle_mentioned,
            'iedi_score': analysis.iedi_score
        }
        
        cls._batch_mention_analyses.append(analysis_dict)
        
        return analysis
    
    @classmethod
    def bulk_save(cls, mention_analyses: List[Dict[str, Any]]):
        """
        Save a list of mention analyses in memory for batch processing.
        """
        if not cls._current_analysis_id:
            raise ValueError("Analysis context not defined. Call set_analysis_context() first.")

        cls._batch_mention_analyses.extend(mention_analyses)

    @classmethod
    def update(cls, existing_analysis: MentionAnalysis, new_analysis: MentionAnalysis):
        new_analysis.updated_at = datetime.utcnow()
        return cls.save(new_analysis)
    
    @classmethod
    def find_by_mention(cls, mention_url: str) -> List[MentionAnalysis]:
        results = []
        for analysis_dict in cls._batch_mention_analyses:
            if analysis_dict.get('mention_url') == mention_url:
                analysis = MentionAnalysis(
                    mention_url=analysis_dict.get('mention_url'),
                    bank_name=analysis_dict.get('bank_name'),
                    sentiment=analysis_dict.get('sentiment'),
                    reach_group=analysis_dict.get('reach_group'),
                    niche_vehicle=analysis_dict.get('niche_vehicle'),
                    title_mentioned=analysis_dict.get('title_mentioned'),
                    subtitle_used=analysis_dict.get('subtitle_used'),
                    subtitle_mentioned=analysis_dict.get('subtitle_mentioned'),
                    iedi_score=analysis_dict.get('iedi_score'),
                )
                results.append(analysis)
        
        return results
    
    @classmethod
    def find_by_bank_name(cls, bank_name):
        """
        Busca todos os MentionAnalysis de um banco no batch em memória.
        """
        bank_name_str = bank_name.name if hasattr(bank_name, 'name') else str(bank_name)
        
        results = []
        for analysis_dict in cls._batch_mention_analyses:
            if analysis_dict.get('bank_name') == bank_name_str:
                # Reconstruir objeto MentionAnalysis (simplificado)
                analysis = MentionAnalysis(
                    mention_url=analysis_dict.get('mention_url'),
                    bank_name=analysis_dict.get('bank_name'),
                    sentiment=analysis_dict.get('sentiment'),
                    reach_group=analysis_dict.get('reach_group'),
                    niche_vehicle=analysis_dict.get('niche_vehicle'),
                    title_mentioned=analysis_dict.get('title_mentioned'),
                    subtitle_used=analysis_dict.get('subtitle_used'),
                    subtitle_mentioned=analysis_dict.get('subtitle_mentioned'),
                    iedi_score=analysis_dict.get('iedi_score'),
                    created_at=datetime.fromisoformat(analysis_dict['created_at']) if analysis_dict.get('created_at') else None,
                    updated_at=datetime.fromisoformat(analysis_dict['updated_at']) if analysis_dict.get('updated_at') else None
                )
                results.append(analysis)
        
        return results
    
    @classmethod
    def find_by_mention_id_and_bank_name(cls, mention_url: str, bank_name: str) -> Optional[MentionAnalysis]:
        """
        Busca mention_analysis por mention_id e bank_name no batch em memória.
        """
        bank_name_str = bank_name.name if hasattr(bank_name, 'name') else str(bank_name)
        for analysis_dict in cls._batch_mention_analyses:
            if analysis_dict.get('mention_url') == mention_url and analysis_dict.get('bank_name') == bank_name_str:
                # Reconstruir objeto MentionAnalysis (simplificado)
                analysis = MentionAnalysis(
                    mention_url=analysis_dict.get('mention_url'),
                    bank_name=analysis_dict.get('bank_name'),
                    sentiment=analysis_dict.get('sentiment'),
                    reach_group=analysis_dict.get('reach_group'),
                    niche_vehicle=analysis_dict.get('niche_vehicle'),
                    title_mentioned=analysis_dict.get('title_mentioned'),
                    subtitle_used=analysis_dict.get('subtitle_used'),
                    subtitle_mentioned=analysis_dict.get('subtitle_mentioned'),
                    iedi_score=analysis_dict.get('iedi_score'),
                    created_at=datetime.fromisoformat(analysis_dict['created_at']) if analysis_dict.get('created_at') else None,
                    updated_at=datetime.fromisoformat(analysis_dict['updated_at']) if analysis_dict.get('updated_at') else None
                )
                return analysis
        
        return None
    
    @classmethod
    def update_iedi_scores(cls, analysis_id: str, mention_id: str, bank_id: str,
                          iedi_score: float, numerator: int, denominator: int, **kwargs) -> Optional[MentionAnalysis]:
        """
        Atualiza IEDI scores (não implementado para CSV - usar save diretamente).
        """
        # Não implementado para CSV (usar save diretamente)
        return None
    
    @classmethod
    def flush_batch(cls):
        """
        Persiste batch de mention_analyses em CSV.
        """
        if not cls._current_analysis_id:
            print("[MentionAnalysisRepository] Analysis context não definido. Nada para salvar.")
            return
        
        if not cls._batch_mention_analyses:
            print(f"[MentionAnalysisRepository] Nenhuma mention_analysis no batch (analysis_id={cls._current_analysis_id})")
            return
        
        # Salvar em CSV
        CSVStorage.save_mention_analyses(cls._batch_mention_analyses, cls._current_analysis_id)
        
        # Limpar batch
        print(f"[MentionAnalysisRepository] Batch flushed: {len(cls._batch_mention_analyses)} mention_analyses")
        cls._batch_mention_analyses = []
