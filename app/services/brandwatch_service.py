from app.infra.brandwatch_client import BrandwatchClient
from app.utils.date_utils import DateUtils
from datetime import datetime
from typing import Dict, List

class BrandwatchService:

    def fetch(
        self,
        start_date: datetime,
        end_date: datetime,
        query_name: str
    ) -> List[Dict]:
        client = BrandwatchClient()

        try:
            mentions = client.queries.get_mentions(
                query_name=query_name,
                start_date=DateUtils.to_iso_format(start_date),
                end_date=DateUtils.to_iso_format(end_date),
                page_size=5000
            )

            return mentions

        except Exception as e:
            raise RuntimeError(f"Failed to fetch mentions: {e}")
