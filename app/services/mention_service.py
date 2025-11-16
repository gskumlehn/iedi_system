from typing import Dict
from urllib.parse import urlparse
import logging

from app.models.mention import Mention
from app.repositories.mention_repository import MentionRepository
from app.repositories.media_outlet_repository import MediaOutletRepository

logger = logging.getLogger(__name__)


class MentionService:
    def process_mention(self, mention_data: Dict) -> Mention:
        unique_url = MentionRepository.extract_unique_url(mention_data)
        
        existing = MentionRepository.find_by_url(unique_url)
        if existing:
            logger.info(f"Menção já existe: {existing.id} - {unique_url}")
            return existing
        
        enriched_data = self._enrich_mention_data(mention_data, unique_url)
        
        mention = MentionRepository.create(**enriched_data)
        logger.info(f"Menção criada: {mention.id} - {unique_url}")
        return mention

    def _enrich_mention_data(self, mention_data: Dict, unique_url: str) -> Dict:
        domain = self._extract_domain(unique_url)
        
        media_outlet = None
        if domain:
            media_outlet = MediaOutletRepository.find_by_domain(domain)
        
        enriched = {
            'url': unique_url,
            'brandwatch_id': mention_data.get('id'),
            'original_url': mention_data.get('originalUrl'),
            'title': mention_data.get('title'),
            'snippet': mention_data.get('snippet'),
            'full_text': mention_data.get('fullText'),
            'domain': domain,
            'published_date': mention_data.get('date'),
            'sentiment': mention_data.get('sentiment', 'neutral'),
            'media_outlet_id': media_outlet.id if media_outlet else None,
            'monthly_visitors': media_outlet.monthly_visitors if media_outlet else 0,
            'reach_group': self._determine_reach_group(media_outlet)
        }
        
        return enriched

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.warning(f"Erro ao extrair domínio de {url}: {e}")
            return ''

    def _determine_reach_group(self, media_outlet) -> str:
        if not media_outlet:
            return 'D'
        
        visitors = media_outlet.monthly_visitors
        
        if visitors > 29_000_000:
            return 'A'
        elif visitors > 11_000_000:
            return 'B'
        elif visitors >= 500_000:
            return 'C'
        else:
            return 'D'
