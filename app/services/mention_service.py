from app.models.mention import Mention
from app.repositories.mention_repository import MentionRepository
from app.services.brandwatch_service import BrandwatchService
from app.utils.date_utils import DateUtils
from typing import List, Optional

class MentionService:

    brandwatch_service = BrandwatchService()

    def fetch_and_filter_mentions(
        self,
        start_date,
        end_date,
        query_name,
        bank_names: Optional[List[str]] = None
    ):
        """
        Busca mentions da Brandwatch já filtradas por categoria.
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            query_name: Nome da query Brandwatch
            bank_names: Lista de nomes de bancos (enum names) para filtrar
        
        Returns:
            Lista de mentions filtradas e salvas
        """
        # Converter bank_names para categorias Brandwatch
        categories = None
        if bank_names:
            # Mapear enum names para nomes de categorias Brandwatch
            categories = [self._map_bank_to_category(bank) for bank in bank_names]

        # Buscar mentions com filtros aplicados na API
        mentions_data = self.brandwatch_service.fetch(
            start_date=start_date,
            end_date=end_date,
            query_name=query_name,
            parent_categories=["Bancos"],  # Filtrar apenas categoria pai "Bancos"
            categories=categories,          # Filtrar por bancos específicos (se fornecido)
            page_type="news"                # Filtrar apenas notícias
        )

        # Salvar mentions (sem filtro adicional)
        filtered_mentions = []
        for mention_data in mentions_data:
            mention = self.save_or_update(mention_data)
            filtered_mentions.append(mention)

        return filtered_mentions

    def _map_bank_to_category(self, bank_name: str) -> str:
        """
        Mapeia enum name do banco para nome da categoria Brandwatch.
        
        Args:
            bank_name: Enum name (ex: "BANCO_DO_BRASIL")
        
        Returns:
            Nome da categoria Brandwatch (ex: "Banco do Brasil")
        """
        # Mapeamento de enum names para categorias Brandwatch
        mapping = {
            "BANCO_DO_BRASIL": "Banco do Brasil",
            "ITAU": "Itaú",
            "BRADESCO": "Bradesco",
            "SANTANDER": "Santander"
        }
        return mapping.get(bank_name, bank_name)

    def extract_categories(self, category_details):
        parent_category_name = "Análise de Resultado - Bancos"
        return [
            category['name']
            for category in category_details
            if category.get('parentName') == parent_category_name
        ]

    def extract_url(self, mention_data):
        return mention_data.get('url') or mention_data.get('originalUrl')

    def save_or_update(self, mention_data):
        categories = self.extract_categories(mention_data.get('categoryDetails', []))
        url = self.extract_url(mention_data)

        existing_mention = MentionRepository.find_by_url(url)
        if existing_mention:
            return self.update(existing_mention, mention_data, categories)

        return self.save(mention_data, categories)

    def save(self, mention_data, categories):
        url = self.extract_url(mention_data)
        published_date = DateUtils.parse_date(mention_data.get('date'))
        mention = Mention(
            url=url,
            title=mention_data.get('title'),
            snippet=mention_data.get('snippet'),
            full_text=mention_data.get('fullText'),
            domain=mention_data.get('domain'),
            published_date=published_date,
            sentiment=mention_data.get('sentiment'),
            categories=categories,
            monthly_visitors=mention_data.get('dailyVisitors', 0) * 30
        )

        MentionRepository.save(mention)
        return mention

    def update(self, existing_mention, mention_data, categories):
        existing_mention.title = mention_data.get('title')
        existing_mention.snippet = mention_data.get('snippet')
        existing_mention.full_text = mention_data.get('fullText')
        existing_mention.published_date = DateUtils.parse_date(mention_data.get('date'))
        existing_mention.sentiment = mention_data.get('sentiment')
        existing_mention.categories = categories
        existing_mention.monthly_visitors = mention_data.get('monthlyVisitors', 0)

        MentionRepository.update(existing_mention)
        return existing_mention
