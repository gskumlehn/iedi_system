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

        parent_category_filter = [parent_name]
        category_filter = {parent_name: category_names} if category_names else {}

        try:
            page_count = 0
            for page in client.queries.iter_mentions(
                name=query_name,
                startDate=DateUtils.to_iso_format(start_date),
                endDate=DateUtils.to_iso_format(end_date),
                pageSize=5000,
                iter_by_page=True,
                params={
                    "parentCategory": parent_category_filter,
                    "category": category_filter
                }
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
                        if "rate limit exceeded" in str(e).lower():
                            retries += 1
                            wait_time = retry_delay * (2 ** (retries - 1))
                            print(f"Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                            sleep(wait_time)
                        else:
                            raise

            print(f"Total pages fetched: {page_count}")
            return all_mentions

        except Exception as e:
            raise RuntimeError(f"Failed to fetch mentions: {e}")
