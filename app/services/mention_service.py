from typing import Dict, Optional
from datetime import datetime
import logging

from app.repositories.mention_repository import MentionRepository
from app.repositories.media_outlet_repository import MediaOutletRepository
from app.models.mention import Mention
from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup

logger = logging.getLogger(__name__)


class MentionService:
    """
    Service para gerenciar menções.
    Centraliza regras de negócio relacionadas a menções.
    """

    def __init__(
        self,
        mention_repo: MentionRepository,
        media_outlet_repo: MediaOutletRepository
    ):
        self.mention_repo = mention_repo
        self.media_outlet_repo = media_outlet_repo

    def process_mention(self, mention_data: Dict) -> Mention:
        """
        Processa menção da Brandwatch: extrai URL, enriquece e armazena.
        
        Args:
            mention_data: Dados brutos da Brandwatch API
        
        Returns:
            Mention: Menção processada e armazenada
        """
        # Extrair URL única
        unique_url = self.mention_repo.extract_unique_url(mention_data)
        
        # Buscar menção existente
        existing = self.mention_repo.find_by_url(unique_url)
        if existing:
            logger.debug(f"Menção já existe: {unique_url}")
            return existing
        
        # Enriquecer dados
        enriched_data = self._enrich_mention_data(mention_data, unique_url)
        
        # Criar nova menção
        mention = self.mention_repo.create(**enriched_data)
        logger.info(f"Menção criada: {mention.id} - {unique_url}")
        
        return mention

    def _enrich_mention_data(self, mention_data: Dict, unique_url: str) -> Dict:
        """Enriquece dados brutos da Brandwatch com metadados."""
        domain = mention_data.get('domain')
        media_outlet = None
        
        if domain:
            media_outlet = self.media_outlet_repo.find_by_domain(domain)
        
        sentiment = self._normalize_sentiment(mention_data.get('sentiment'))
        first_paragraph = self._extract_first_paragraph(
            mention_data.get('snippet'),
            mention_data.get('fullText')
        )
        
        return {
            'url': unique_url,
            'brandwatch_id': mention_data.get('id'),
            'original_url': mention_data.get('originalUrl'),
            'title': mention_data.get('title'),
            'snippet': mention_data.get('snippet'),
            'full_text': mention_data.get('fullText'),
            'domain': domain,
            'published_date': self._parse_date(mention_data.get('publishedDate')),
            'categories': [],  # Será preenchido pelo BankDetectionService
            'sentiment': sentiment,
            'media_outlet_id': media_outlet.id if media_outlet else None,
            'monthly_visitors': media_outlet.monthly_visitors if media_outlet else 0,
            'reach_group': media_outlet.reach_group if media_outlet else ReachGroup.D,
        }

    def _normalize_sentiment(self, sentiment: str) -> Sentiment:
        """Normaliza sentimento da Brandwatch para enum."""
        if not sentiment:
            return Sentiment.NEUTRAL
        
        sentiment_map = {
            'positive': Sentiment.POSITIVE,
            'negative': Sentiment.NEGATIVE,
            'neutral': Sentiment.NEUTRAL
        }
        return sentiment_map.get(sentiment.lower(), Sentiment.NEUTRAL)

    def _extract_first_paragraph(
        self,
        snippet: Optional[str],
        full_text: Optional[str]
    ) -> Optional[str]:
        """Extrai primeiro parágrafo do texto completo."""
        if not full_text or snippet == full_text:
            return None
        
        paragraphs = full_text.split('\n\n')
        if len(paragraphs) > 1:
            return paragraphs[0].strip()
        
        return full_text[:300].strip() if len(full_text) > 300 else None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parseia data ISO 8601 da Brandwatch."""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Erro ao parsear data: {date_str} - {e}")
            return None
