from app.infra.brandwatch_client import BrandwatchClient
from app.utils.date_utils import DateUtils
from datetime import datetime
from typing import Dict, List, Optional
from time import sleep

class BrandwatchService:

    def fetch(
        self,
        start_date: datetime,
        end_date: datetime,
        query_name: str,
        parent_categories: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        page_type: Optional[str] = "news"
    ) -> List[Dict]:
        """
        Busca mentions da Brandwatch com filtros aplicados na API.
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            query_name: Nome da query Brandwatch
            parent_categories: Lista de categorias pai (ex: ["Bancos"])
            categories: Lista de categorias específicas (ex: ["Banco do Brasil", "Itaú"])
            page_type: Tipo de página (padrão: "news")
        
        Returns:
            Lista de mentions filtradas
        """
        client = BrandwatchClient()
        all_mentions = []
        max_retries = 5  # Maximum number of retries
        retry_delay = 10  # Initial delay in seconds

        # Construir kwargs com filtros
        kwargs = {
            "startDate": DateUtils.to_iso_format(start_date),
            "endDate": DateUtils.to_iso_format(end_date),
            "pageSize": 5000,
            "iter_by_page": True
        }

        # Adicionar filtro de tipo de página
        if page_type:
            kwargs["pageType"] = page_type

        # Adicionar filtro de categoria pai
        if parent_categories:
            kwargs["parentCategory"] = parent_categories

        # Adicionar filtro de categorias específicas
        if categories:
            kwargs["category"] = categories

        try:
            page_count = 0  # Track the number of pages fetched
            for page in client.queries.iter_mentions(
                name=query_name,
                **kwargs  # Passa filtros para a API
            ):
                retries = 0
                while retries < max_retries:
                    try:
                        if page:
                            all_mentions.extend(page)
                            page_count += 1
                            print(f"Fetched page {page_count} with {len(page)} mentions.")  # Log progress
                        break  # Exit retry loop if successful
                    except Exception as e:
                        if "rate limit exceeded" in str(e).lower():
                            retries += 1
                            wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                            print(f"Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                            sleep(wait_time)
                        else:
                            raise  # Raise other exceptions immediately

            print(f"Total pages fetched: {page_count}")
            print(f"Total mentions fetched: {len(all_mentions)}")
            return all_mentions

        except Exception as e:
            raise RuntimeError(f"Failed to fetch mentions: {e}")
