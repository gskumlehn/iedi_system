from app.infra.brandwatch_client import BrandwatchClient
from app.utils.date_utils import DateUtils
from datetime import datetime
from typing import Dict, List
from time import sleep

class BrandwatchService:

    def fetch(
        self,
        start_date: datetime,
        end_date: datetime,
        query_name: str,
        parent_name: str,
        category_names: List[str] = None
    ) -> List[Dict]:
        client = BrandwatchClient()
        all_mentions = []
        max_retries = 5
        retry_delay = 10

        # Construir kwargs com filtros
        kwargs = {
            "startDate": DateUtils.to_iso_format(start_date),
            "endDate": DateUtils.to_iso_format(end_date),
            "pageSize": 5000,
            "iter_by_page": True,
            "pageType": "news"  # Filtrar apenas notícias
        }

        # Adicionar filtro de categoria pai
        if parent_name:
            kwargs["parentCategory"] = [parent_name]

        # Adicionar filtro de categorias específicas
        if category_names:
            kwargs["category"] = {parent_name: category_names}

        try:
            page_count = 0
            for page in client.queries.iter_mentions(
                name=query_name,
                **kwargs  # Passa filtros como kwargs
            ):
                retries = 0
                while retries < max_retries:
                    try:
                        if page:
                            all_mentions.extend(page)
                            page_count += 1
                            print(f"Fetched page {page_count} with {len(page)} mentions.")
                        break
                    except Exception as e:
                        retries += 1
                        wait_time = retry_delay * (2 ** (retries - 1))
                        sleep(wait_time)

            print(f"Total pages fetched: {page_count}")
            return all_mentions

        except Exception as e:
            raise RuntimeError(f"Failed to fetch mentions: {e}")
