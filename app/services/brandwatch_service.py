from datetime import datetime
from typing import Dict, List
import logging
import os

logger = logging.getLogger(__name__)


class BrandwatchService:
    def __init__(self):
        self.username = os.getenv('BRANDWATCH_USERNAME')
        self.password = os.getenv('BRANDWATCH_PASSWORD')
        self.project_id = os.getenv('BRANDWATCH_PROJECT_ID')
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from bcr_api import Client
            except ImportError:
                raise ImportError("Biblioteca bcr-api não instalada. Execute: pip install bcr-api")
            
            try:
                self._client = Client(
                    username=self.username,
                    password=self.password,
                    project=int(self.project_id)
                )
                logger.info("Cliente Brandwatch conectado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao conectar Brandwatch: {e}")
                raise
        
        return self._client

    def extract_mentions(
        self,
        start_date: datetime,
        end_date: datetime,
        query_name: str
    ) -> List[Dict]:
        client = self._get_client()
        
        logger.info(
            f"Extraindo menções: {query_name} "
            f"({start_date.date()} - {end_date.date()})"
        )
        
        try:
            mentions = client.get_mentions(
                query_name=query_name,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                page_size=5000
            )
            
            logger.info(f"Total de menções extraídas: {len(mentions)}")
            return mentions
            
        except Exception as e:
            logger.error(f"Erro ao extrair menções: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            client = self._get_client()
            return True
        except Exception as e:
            logger.error(f"Teste de conexão falhou: {e}")
            return False
