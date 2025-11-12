"""
Serviço de integração com Brandwatch API
Adaptado para funcionar dentro do sistema IEDI
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from bcr_api.bwproject import BWProject
    from bcr_api.bwresources import BWQueries
    BRANDWATCH_AVAILABLE = True
except ImportError:
    BRANDWATCH_AVAILABLE = False
    logger.warning("bcr_api não está instalado. Funcionalidade Brandwatch desabilitada.")


class BrandwatchService:
    """Serviço para extrair menções da Brandwatch"""
    
    def __init__(self, email: str, password: str, project: str):
        if not BRANDWATCH_AVAILABLE:
            raise ImportError("bcr_api não está instalado. Instale com: pip install bcr-api")
        
        self.email = email
        self.password = password
        self.project = project
        self._bw_project = None
    
    def get_project(self) -> BWProject:
        """Obtém ou cria conexão com projeto Brandwatch"""
        if self._bw_project is None:
            self._bw_project = BWProject(
                project=self.project,
                username=self.email,
                password=self.password
            )
        return self._bw_project
    
    def extract_mentions(
        self,
        query_name: str,
        start_date: str,
        end_date: str,
        pagesize: int = 5000
    ) -> List[Dict]:
        """
        Extrai menções da Brandwatch para uma query específica
        
        Args:
            query_name: Nome da query na Brandwatch
            start_date: Data inicial no formato ISO (YYYY-MM-DDTHH:MM:SSZ)
            end_date: Data final no formato ISO (YYYY-MM-DDTHH:MM:SSZ)
            pagesize: Tamanho da página (máx 5000)
        
        Returns:
            Lista de menções (dicionários)
        """
        try:
            proj = self.get_project()
            queries = BWQueries(proj)
            
            all_mentions = []
            
            for page in queries.iter_mentions(
                name=query_name,
                startDate=start_date,
                endDate=end_date,
                pagesize=pagesize,
                iter_by_page=True
            ):
                if page:
                    all_mentions.extend(page)
                    logger.info(f"Extraídas {len(page)} menções. Total: {len(all_mentions)}")
            
            logger.info(f"Extração concluída. Total de menções: {len(all_mentions)}")
            return all_mentions
        
        except Exception as e:
            logger.error(f"Erro ao extrair menções da Brandwatch: {str(e)}")
            raise
    
    def extract_mentions_by_date_range(
        self,
        query_name: str,
        start_date_str: str,
        end_date_str: str
    ) -> List[Dict]:
        """
        Extrai menções para um intervalo de datas (formato YYYY-MM-DD)
        
        Args:
            query_name: Nome da query
            start_date_str: Data inicial (YYYY-MM-DD)
            end_date_str: Data final (YYYY-MM-DD)
        
        Returns:
            Lista de menções
        """
        try:
            # Converter datas para datetime UTC
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Adicionar timezone UTC
            start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # Converter para formato ISO da Brandwatch
            start_iso = start_dt.isoformat().replace("+00:00", "Z")
            end_iso = end_dt.isoformat().replace("+00:00", "Z")
            
            logger.info(f"Extraindo menções de {start_iso} até {end_iso}")
            
            return self.extract_mentions(query_name, start_iso, end_iso)
        
        except ValueError as e:
            logger.error(f"Formato de data inválido: {str(e)}")
            raise ValueError("Formato de data deve ser YYYY-MM-DD")
    
    def extract_last_days(
        self,
        query_name: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Extrai menções dos últimos N dias
        
        Args:
            query_name: Nome da query
            days: Número de dias para buscar
        
        Returns:
            Lista de menções
        """
        now_utc = datetime.now(timezone.utc).replace(microsecond=0)
        start_dt = now_utc - timedelta(days=days)
        
        start_iso = start_dt.isoformat().replace("+00:00", "Z")
        end_iso = now_utc.isoformat().replace("+00:00", "Z")
        
        logger.info(f"Extraindo menções dos últimos {days} dias")
        
        return self.extract_mentions(query_name, start_iso, end_iso)
    
    @staticmethod
    def filter_news_mentions(mentions: List[Dict]) -> List[Dict]:
        """
        Filtra apenas menções de imprensa (News)
        
        Args:
            mentions: Lista de menções
        
        Returns:
            Lista filtrada apenas com menções de imprensa
        """
        news_mentions = [
            m for m in mentions
            if m.get('contentSourceName') == 'News' or
               'news' in str(m.get('contentSource', '')).lower()
        ]
        
        logger.info(f"Filtradas {len(news_mentions)} menções de imprensa de {len(mentions)} totais")
        
        return news_mentions


def create_brandwatch_service(config: Dict) -> Optional[BrandwatchService]:
    """
    Factory para criar BrandwatchService a partir de configuração
    
    Args:
        config: Dicionário com email, password, project
    
    Returns:
        BrandwatchService ou None se não disponível
    """
    if not BRANDWATCH_AVAILABLE:
        logger.warning("Brandwatch API não disponível")
        return None
    
    try:
        return BrandwatchService(
            email=config['email'],
            password=config['password'],
            project=config['project']
        )
    except Exception as e:
        logger.error(f"Erro ao criar BrandwatchService: {str(e)}")
        return None
