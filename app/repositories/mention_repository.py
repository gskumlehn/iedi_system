from app.infra.bq_sa import get_session
from app.models.mention import Mention
from sqlalchemy.orm import joinedload
from app.infra.csv_storage import CSVStorage
from datetime import datetime
import uuid
from typing import List

class MentionRepository:
    
    # ========================================
    # MÉTODOS ORIGINAIS (BANCO DE DADOS)
    # Comentados para melhorar performance
    # ========================================
    
    # @staticmethod
    # def save(mention: Mention) -> Mention:
    #     with get_session() as session:
    #         session.add(mention)
    #         session.commit()
    #         session.refresh(mention)
    #         return mention
    
    # @staticmethod
    # def update(mention: Mention) -> Mention | None:
    #     with get_session() as session:
    #         merged = session.merge(mention)
    #         session.commit()
    #         session.refresh(merged)
    #         return merged
    
    # @staticmethod
    # def find_by_url(url: str) -> Mention:
    #     with get_session() as session:
    #         return session.query(Mention).options(joinedload('*')).filter(Mention.url == url).first()
    
    # ========================================
    # NOVOS MÉTODOS (CSV COM PANDAS)
    # ========================================
    
    # Armazenamento temporário em memória para batch save
    _batch_mentions = []
    _current_analysis_id = None
    
    @classmethod
    def set_analysis_context(cls, analysis_id: str):
        """Define o contexto da análise atual para salvar no CSV correto"""
        cls._current_analysis_id = analysis_id
        cls._batch_mentions = []
    
    @classmethod
    def save(cls, mention: Mention) -> Mention:
        """
        Salva mention em memória para processamento em lote.
        """
        if not cls._current_analysis_id:
            raise ValueError("Analysis context não definido. Chame set_analysis_context() primeiro.")

        # Converter mention para dict
        mention_dict = {
            'url': mention.url,
            'title': mention.title,
            'snippet': mention.snippet,
            'full_text': mention.full_text,
            'domain': mention.domain,
            'published_date': mention.published_date.isoformat() if mention.published_date else None,
            'sentiment': mention.sentiment,
            'categories': ','.join(mention.categories) if mention.categories else '',
            'monthly_visitors': mention.monthly_visitors
        }
        
        # Adicionar ao batch
        cls._batch_mentions.append(mention_dict)
        
        return mention
    
    @classmethod
    def update(cls, mention: Mention) -> Mention | None:
        """
        Atualiza mention (mesmo comportamento de save para CSV).
        """
        mention.updated_at = datetime.utcnow()
        return cls.save(mention)
    
    @classmethod
    def find_by_url(cls, url: str) -> Mention | None:
        """
        Busca mention por URL no batch em memória.
        Retorna None se não encontrar (para evitar leitura de CSV).
        """
        for mention_dict in cls._batch_mentions:
            if mention_dict['url'] == url:
                # Reconstruir objeto Mention
                mention = Mention(
                    id=mention_dict['id'],
                    url=mention_dict['url'],
                    title=mention_dict['title'],
                    snippet=mention_dict['snippet'],
                    full_text=mention_dict['full_text'],
                    domain=mention_dict['domain'],
                    published_date=datetime.fromisoformat(mention_dict['published_date']) if mention_dict['published_date'] else None,
                    sentiment=mention_dict['sentiment'],
                    categories=mention_dict['categories'].split(',') if mention_dict['categories'] else [],
                    monthly_visitors=mention_dict['monthly_visitors'],
                    created_at=datetime.fromisoformat(mention_dict['created_at']) if mention_dict['created_at'] else None,
                    updated_at=datetime.fromisoformat(mention_dict['updated_at']) if mention_dict['updated_at'] else None
                )
                return mention
        
        # Não encontrado no batch (evitar leitura de CSV para performance)
        return None
    
    @classmethod
    def flush_batch(cls):
        """
        Salva todas as mentions em memória para um arquivo CSV.
        """
        if not cls._current_analysis_id:
            print("[MentionRepository] Analysis context não definido. Nada para salvar.")
            return
        
        if not cls._batch_mentions:
            print(f"[MentionRepository] Nenhuma mention para salvar (analysis_id={cls._current_analysis_id})")
            return
        
        # Salvar em CSV
        CSVStorage.save_mentions(cls._batch_mentions, cls._current_analysis_id)
        
        # Limpar batch
        print(f"[MentionRepository] Batch flushed: {len(cls._batch_mentions)} mentions")
        cls._batch_mentions = []

    @classmethod
    def bulk_save(cls, mentions: List[Mention]):
        """
        Save a list of mentions in memory for batch processing.
        """
        if not cls._current_analysis_id:
            raise ValueError("Analysis context not defined. Call set_analysis_context() first.")

        for mention in mentions:
            mention_dict = {
                'url': mention.url,
                'title': mention.title,
                'snippet': mention.snippet,
                'full_text': mention.full_text,
                'domain': mention.domain,
                'published_date': mention.published_date.isoformat() if mention.published_date else None,
                'sentiment': mention.sentiment,
                'categories': ','.join(mention.categories) if mention.categories else '',
                'monthly_visitors': mention.monthly_visitors
            }
            cls._batch_mentions.append(mention_dict)
