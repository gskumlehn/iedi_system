from app.models.mention import Mention
from app.repositories.mention_repository import MentionRepository
from app.services.brandwatch_service import BrandwatchService
from app.utils.date_utils import DateUtils

class MentionService:

    brandwatch_service = BrandwatchService()

    def fetch_and_filter_mentions(self, start_date, end_date, query_name, parent_name, category_names=None):
        mentions_data = self.brandwatch_service.fetch(
            start_date=start_date,
            end_date=end_date,
            query_name=query_name,
            parent_name=parent_name,
            category_names=category_names
        )

        filtered_mentions = []
        for mention_data in mentions_data:
            if self.passes_filter(mention_data, parent_name, category_names):
                mention = self.create_mention(mention_data, parent_name)
                filtered_mentions.append(mention)

        MentionRepository.bulk_save(filtered_mentions)
        return filtered_mentions

    def passes_filter(self, mention_data, parent_name, category_names):
        content_source = mention_data.get('contentSourceName')

        if not (content_source == "News" or content_source == "Online News"):
            return False

        categories = self.extract_categories(mention_data.get('categoryDetails', []), parent_name)
        if not categories:
            return False

        return any(category in category_names for category in categories)

    def extract_categories(self, category_details, parent_name):
        return [
            category['name']
            for category in category_details
            if category.get('parentName') == parent_name
        ]

    def extract_url(self, mention_data):
        return mention_data.get('url') or mention_data.get('originalUrl')

    def create_mention(self, mention_data, parent_name):
        categories = self.extract_categories(mention_data.get('categoryDetails', []), parent_name)
        url = self.extract_url(mention_data)
        published_date = DateUtils.parse_date(mention_data.get('date'))

        # Ensure dailyVisitors is not None before multiplication
        daily_visitors = mention_data.get('dailyVisitors')
        monthly_visitors = (daily_visitors * 30) if daily_visitors is not None else 0

        return Mention(
            url=url,
            title=mention_data.get('title'),
            snippet=mention_data.get('snippet'),
            full_text=mention_data.get('fullText'),
            domain=mention_data.get('domain'),
            published_date=published_date,
            sentiment=mention_data.get('sentiment'),
            categories=categories,
            monthly_visitors=monthly_visitors
        )
