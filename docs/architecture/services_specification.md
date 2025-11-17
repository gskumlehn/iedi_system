# Especificações Técnicas dos Services IEDI

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0

---

## Visão Geral

Este documento especifica os **services** necessários para implementar o fluxo completo de processamento IEDI. Cada service é responsável por uma etapa específica do processamento, com interfaces bem definidas, tratamento de erros e logging estruturado.

---

## 1. BrandwatchService

### Responsabilidade

Comunicação com a Brandwatch API para coleta de menções de imprensa digital.

### Localização

`app/services/brandwatch_service.py`

### Interface

```python
class BrandwatchService:
    """Service para integração com Brandwatch API."""
    
    def __init__(self, api_key: str, project_id: str):
        """
        Inicializa o service com credenciais.
        
        Args:
            api_key: Chave de autenticação Brandwatch
            project_id: ID do projeto Brandwatch
        """
        pass
    
    def extract_mentions(
        self,
        start_date: datetime,
        end_date: datetime,
        query_name: str,
        media_type: str = 'News',
        language: str = 'pt',
        page_size: int = 5000
    ) -> List[Dict]:
        """
        Extrai menções da Brandwatch API.
        
        Args:
            start_date: Data inicial do período
            end_date: Data final do período
            query_name: Nome da query configurada na Brandwatch
            media_type: Tipo de mídia (default: 'News')
            language: Idioma das menções (default: 'pt')
            page_size: Tamanho da página (max: 5000)
        
        Returns:
            Lista de menções brutas (JSON)
        
        Raises:
            AuthenticationError: Credenciais inválidas
            RateLimitError: Rate limit atingido
            BrandwatchAPIError: Erro genérico da API
        """
        pass
    
    def is_authenticated(self) -> bool:
        """
        Verifica se as credenciais são válidas.
        
        Returns:
            True se autenticado, False caso contrário
        """
        pass
```

### Implementação

```python
from bcr_api import BrandwatchClient
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BrandwatchService:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.client = BrandwatchClient(
            api_key=api_key,
            project_id=project_id
        )
    
    def extract_mentions(
        self,
        start_date: datetime,
        end_date: datetime,
        query_name: str,
        media_type: str = 'News',
        language: str = 'pt',
        page_size: int = 5000
    ) -> List[Dict]:
        logger.info(f"Iniciando extração de menções: {start_date} - {end_date}")
        
        # Verificar autenticação
        if not self.is_authenticated():
            raise AuthenticationError("Falha na autenticação Brandwatch")
        
        all_mentions = []
        page = 1
        
        while True:
            try:
                response = self.client.get_mentions(
                    query_name=query_name,
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    page_size=page_size,
                    fields=[
                        'id', 'title', 'snippet', 'fullText', 'url', 'domain',
                        'publishedDate', 'sentiment', 'mediaType', 'language'
                    ]
                )
            except Exception as e:
                logger.error(f"Erro ao buscar menções (página {page}): {e}")
                raise BrandwatchAPIError(f"Erro na API: {e}")
            
            if not response.get('results'):
                break
            
            # Filtrar por mediaType e language
            filtered = [
                m for m in response['results']
                if m.get('mediaType') == media_type and m.get('language') == language
            ]
            
            all_mentions.extend(filtered)
            
            logger.info(f"Página {page}: {len(filtered)} menções filtradas")
            
            page += 1
            
            # Limite de segurança (100 páginas = 500k menções)
            if page > 100:
                logger.warning("Limite de páginas atingido (100)")
                break
        
        logger.info(f"Total de menções extraídas: {len(all_mentions)}")
        return all_mentions
    
    def is_authenticated(self) -> bool:
        try:
            self.client.test_connection()
            return True
        except Exception:
            return False
```

### Testes

```python
import pytest
from datetime import datetime
from app.services.brandwatch_service import BrandwatchService

def test_extract_mentions_success():
    service = BrandwatchService(api_key='test_key', project_id='test_project')
    
    mentions = service.extract_mentions(
        start_date=datetime(2024, 11, 1),
        end_date=datetime(2024, 11, 30),
        query_name='Bancos Brasil'
    )
    
    assert isinstance(mentions, list)
    assert len(mentions) > 0
    assert 'id' in mentions[0]
    assert 'title' in mentions[0]

def test_authentication_failure():
    service = BrandwatchService(api_key='invalid_key', project_id='invalid_project')
    
    with pytest.raises(AuthenticationError):
        service.extract_mentions(
            start_date=datetime(2024, 11, 1),
            end_date=datetime(2024, 11, 30),
            query_name='Bancos Brasil'
        )
```

---

## 2. MentionEnrichmentService

### Responsabilidade

Enriquecer menções brutas com metadados de veículos de mídia e extrair primeiro parágrafo.

### Localização

`app/services/mention_enrichment_service.py`

### Interface

```python
class MentionEnrichmentService:
    """Service para enriquecimento de menções."""
    
    def __init__(self, media_outlet_repo: MediaOutletRepository):
        """
        Inicializa o service com repository de veículos.
        
        Args:
            media_outlet_repo: Repository de media_outlets
        """
        pass
    
    def enrich(self, mention: Dict) -> Dict:
        """
        Enriquece menção bruta com metadados.
        
        Args:
            mention: Menção bruta da Brandwatch
        
        Returns:
            Menção enriquecida com metadados
        
        Raises:
            ValueError: Dados inválidos na menção
        """
        pass
    
    def extract_first_paragraph(self, full_text: str) -> Optional[str]:
        """
        Extrai o primeiro parágrafo do texto completo.
        
        Args:
            full_text: Texto completo da menção
        
        Returns:
            Primeiro parágrafo ou None se não disponível
        """
        pass
    
    @staticmethod
    def extract_unique_url(mention: Dict) -> str:
        """
        Extrai URL única da menção Brandwatch.
        
        Brandwatch pode retornar a URL em dois campos:
        - 'url': URL principal
        - 'originalUrl': URL original (redirecionamentos)
        
        Args:
            mention: Dados brutos da menção Brandwatch
        
        Returns:
            URL única (primeiro campo preenchido)
        
        Raises:
            ValueError: Se nenhum campo de URL estiver preenchido
        """
        pass
```

### Implementação

```python
from typing import Dict, Optional
from datetime import datetime
import logging

from app.repositories.media_outlet_repository import MediaOutletRepository
from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup

logger = logging.getLogger(__name__)

class MentionEnrichmentService:
    def __init__(self, media_outlet_repo: MediaOutletRepository):
        self.media_outlet_repo = media_outlet_repo
        self._media_outlets_cache = {}
    
    def enrich(self, mention: Dict) -> Dict:
        logger.debug(f"Enriquecendo menção: {mention.get('id')}")
        
        # Validar campos obrigatórios
        required_fields = ['id', 'title', 'domain', 'sentiment']
        for field in required_fields:
            if field not in mention:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Extrair URL única (verificar 'url' e 'originalUrl')
        unique_url = self._extract_unique_url(mention)
        
        # Buscar veículo de mídia
        media_outlet = self._get_media_outlet(mention['domain'])
        
        # Normalizar sentimento
        sentiment = self._normalize_sentiment(mention['sentiment'])
        
        # Extrair primeiro parágrafo
        first_paragraph = None
        if mention.get('snippet') != mention.get('fullText'):
            first_paragraph = self.extract_first_paragraph(mention.get('fullText'))
        
        # Construir menção enriquecida
        enriched = {
            # Dados originais
            'url': unique_url,
            'brandwatch_id': mention.get('id'),
            'original_url': mention.get('originalUrl'),
            'title': mention.get('title'),
            'snippet': mention.get('snippet'),
            'full_text': mention.get('fullText'),
            'domain': mention['domain'],
            'published_date': self._parse_date(mention.get('publishedDate')),
            
            # Sentimento normalizado
            'sentiment': sentiment,
            
            # Metadados do veículo
            'media_outlet_id': media_outlet['id'] if media_outlet else None,
            'monthly_visitors': media_outlet['monthly_visitors'] if media_outlet else 0,
            'reach_group': media_outlet['reach_group'] if media_outlet else ReachGroup.D,
            'is_relevant_outlet': media_outlet['is_relevant'] if media_outlet else False,
            'is_niche_outlet': media_outlet['is_niche'] if media_outlet else False,
            
            # Primeiro parágrafo
            'first_paragraph': first_paragraph
        }
        
        return enriched
    
    def extract_first_paragraph(self, full_text: str) -> Optional[str]:
        if not full_text:
            return None
        
        # Dividir por quebras duplas
        paragraphs = full_text.split('\n\n')
        
        if len(paragraphs) > 1:
            return paragraphs[0].strip()
        else:
            # Sem quebras duplas, pega os primeiros 300 caracteres
            return full_text[:300].strip()
    
    def _get_media_outlet(self, domain: str) -> Optional[Dict]:
        # Cache para evitar queries repetidas
        if domain not in self._media_outlets_cache:
            media_outlet = self.media_outlet_repo.find_by_domain(domain)
            
            if media_outlet:
                self._media_outlets_cache[domain] = {
                    'id': media_outlet.id,
                    'monthly_visitors': media_outlet.monthly_visitors,
                    'reach_group': media_outlet.reach_group,
                    'is_relevant': media_outlet.is_relevant,
                    'is_niche': media_outlet.is_niche
                }
            else:
                logger.warning(f"Veículo não cadastrado: {domain}")
                self._media_outlets_cache[domain] = None
        
        return self._media_outlets_cache[domain]
    
    def _normalize_sentiment(self, sentiment: str) -> Sentiment:
        sentiment_map = {
            'positive': Sentiment.POSITIVE,
            'negative': Sentiment.NEGATIVE,
            'neutral': Sentiment.NEUTRAL
        }
        return sentiment_map.get(sentiment.lower(), Sentiment.NEUTRAL)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Erro ao parsear data: {date_str} - {e}")
            return None
    
    def _extract_unique_url(self, mention: dict) -> str:
        """Extrai URL única (verificar 'url' e 'originalUrl')."""
        url = mention.get('url') or mention.get('originalUrl')
        
        if not url:
            raise ValueError(
                f"Menção sem URL: {mention.get('id')} - "
                "Campos 'url' e 'originalUrl' vazios"
            )
        
        return url
```

---

## 3. BankDetectionService

### Responsabilidade

Detectar quais bancos foram mencionados em cada menção.

### Localização

`app/services/bank_detection_service.py`

### Interface

```python
class BankDetectionService:
    """Service para detecção de bancos em menções."""
    
    def __init__(self, bank_repo: BankRepository):
        """
        Inicializa o service com repository de bancos.
        
        Args:
            bank_repo: Repository de banks
        """
        pass
    
    def detect_banks(self, mention: Dict) -> List[Dict]:
        """
        Detecta bancos mencionados.
        
        Args:
            mention: Menção enriquecida
        
        Returns:
            Lista de bancos detectados com flags de localização
        """
        pass
```

### Implementação

```python
from typing import Dict, List
import logging
import re

from app.repositories.bank_repository import BankRepository

logger = logging.getLogger(__name__)

class BankDetectionService:
    def __init__(self, bank_repo: BankRepository):
        self.bank_repo = bank_repo
        self._banks_cache = None
    
    def detect_banks(self, mention: Dict) -> List[Dict]:
        logger.debug(f"Detectando bancos em: {mention.get('title')}")
        
        # Carregar bancos (cache)
        if self._banks_cache is None:
            self._banks_cache = self.bank_repo.find_all()
        
        detected_banks = []
        
        # 1. Detectar no título
        for bank in self._banks_cache:
            found_in_title = self._search_bank_in_text(
                bank=bank,
                text=mention.get('title', '')
            )
            
            if found_in_title:
                detected_banks.append({
                    'bank_id': bank.id,
                    'bank_name': bank.name,
                    'found_in_title': True,
                    'found_in_first_paragraph': False
                })
        
        # 2. Verificar primeiro parágrafo (se disponível)
        if mention.get('first_paragraph'):
            for detection in detected_banks:
                bank = next(b for b in self._banks_cache if b.id == detection['bank_id'])
                
                found_in_paragraph = self._search_bank_in_text(
                    bank=bank,
                    text=mention['first_paragraph']
                )
                
                detection['found_in_first_paragraph'] = found_in_paragraph
        
        # 3. Se não encontrou no título, buscar no texto completo
        if not detected_banks and mention.get('full_text'):
            for bank in self._banks_cache:
                found_in_text = self._search_bank_in_text(
                    bank=bank,
                    text=mention['full_text']
                )
                
                if found_in_text:
                    detected_banks.append({
                        'bank_id': bank.id,
                        'bank_name': bank.name,
                        'found_in_title': False,
                        'found_in_first_paragraph': False
                    })
        
        logger.info(f"Bancos detectados: {len(detected_banks)}")
        return detected_banks
    
    def _search_bank_in_text(self, bank, text: str) -> bool:
        """Busca banco no texto (nome principal + variações)."""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Verificar nome principal
        if self._match_word_boundary(bank.name, text_lower):
            return True
        
        # Verificar variações
        for variation in bank.variations:
            if self._match_word_boundary(variation, text_lower):
                return True
        
        return False
    
    def _match_word_boundary(self, word: str, text: str) -> bool:
        """Verifica se a palavra está no texto com word boundaries."""
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        return bool(re.search(pattern, text))
```

---

## 4. IEDICalculationService

### Responsabilidade

Calcular índice IEDI para cada combinação de menção e banco.

### Localização

`app/services/iedi_calculation_service.py`

### Interface

```python
class IEDICalculationService:
    """Service para cálculo do índice IEDI."""
    
    def calculate_iedi(self, mention: Dict, bank_detection: Dict) -> Dict:
        """
        Calcula IEDI para uma menção e banco específicos.
        
        Args:
            mention: Menção enriquecida
            bank_detection: Banco detectado com flags
        
        Returns:
            Resultado do cálculo IEDI
        
        Raises:
            ValueError: Dados inválidos
        """
        pass
```

### Implementação

```python
from typing import Dict
import logging

from app.enums.sentiment import Sentiment
from app.enums.reach_group import ReachGroup

logger = logging.getLogger(__name__)

class IEDICalculationService:
    # Pesos das variáveis
    WEIGHT_TITLE = 100
    WEIGHT_SUBTITLE = 80
    WEIGHT_RELEVANT_OUTLET = 95
    WEIGHT_NICHE_OUTLET = 54
    
    # Pesos por grupo de alcance
    REACH_WEIGHTS = {
        ReachGroup.A: 91,
        ReachGroup.B: 85,
        ReachGroup.C: 24,
        ReachGroup.D: 20
    }
    
    # Denominadores por grupo (com e sem subtítulo)
    DENOMINATORS = {
        ReachGroup.A: {'with_subtitle': 366, 'without_subtitle': 286},
        ReachGroup.B: {'with_subtitle': 414, 'without_subtitle': 334},
        ReachGroup.C: {'with_subtitle': 353, 'without_subtitle': 273},
        ReachGroup.D: {'with_subtitle': 349, 'without_subtitle': 269}
    }
    
    def calculate_iedi(self, mention: Dict, bank_detection: Dict) -> Dict:
        logger.debug(f"Calculando IEDI: {mention.get('title')} - {bank_detection.get('bank_name')}")
        
        # 1. Verificações binárias
        title_verified = 1 if bank_detection['found_in_title'] else 0
        
        # Subtítulo (condicional)
        if mention.get('first_paragraph') is not None:
            subtitle_verified = 1 if bank_detection['found_in_first_paragraph'] else 0
            include_subtitle = True
        else:
            subtitle_verified = 0
            include_subtitle = False
        
        relevant_outlet_verified = 1 if mention.get('is_relevant_outlet') else 0
        niche_outlet_verified = 1 if mention.get('is_niche_outlet') else 0
        
        # 2. Calcular numerador
        numerator = 0
        
        if title_verified:
            numerator += self.WEIGHT_TITLE
        
        if include_subtitle and subtitle_verified:
            numerator += self.WEIGHT_SUBTITLE
        
        numerator += self.REACH_WEIGHTS[mention['reach_group']]
        
        if relevant_outlet_verified:
            numerator += self.WEIGHT_RELEVANT_OUTLET
        
        if niche_outlet_verified:
            numerator += self.WEIGHT_NICHE_OUTLET
        
        # 3. Calcular denominador
        if include_subtitle:
            denominator = self.DENOMINATORS[mention['reach_group']]['with_subtitle']
        else:
            denominator = self.DENOMINATORS[mention['reach_group']]['without_subtitle']
        
        # 4. Calcular sinal (sentimento)
        if mention['sentiment'] == Sentiment.POSITIVE:
            sign = +1
        elif mention['sentiment'] == Sentiment.NEGATIVE:
            sign = -1
        else:  # NEUTRAL
            sign = 0
        
        # 5. Calcular IEDI
        if sign == 0:
            iedi_score = 0.0
        else:
            iedi_score = (numerator / denominator) * sign
        
        # 6. IEDI normalizado (0 a 1)
        iedi_normalized = (iedi_score + 1) / 2
        
        result = {
            'iedi_score': round(iedi_score, 4),
            'iedi_normalized': round(iedi_normalized, 4),
            'numerator': numerator,
            'denominator': denominator,
            'title_verified': title_verified,
            'subtitle_verified': subtitle_verified,
            'relevant_outlet_verified': relevant_outlet_verified,
            'niche_outlet_verified': niche_outlet_verified
        }
        
        logger.debug(f"IEDI calculado: {result['iedi_score']}")
        return result
```

---

## 5. IEDIAggregationService

### Responsabilidade

Agregar resultados IEDI por banco e aplicar balizamento.

### Localização

`app/services/iedi_aggregation_service.py`

### Interface

```python
class IEDIAggregationService:
    """Service para agregação de resultados IEDI."""
    
    def __init__(self, analysis_mention_repo: AnalysisMentionRepository):
        """
        Inicializa o service com repository.
        
        Args:
            analysis_mention_repo: Repository de analysis_mentions
        """
        pass
    
    def aggregate_by_period(self, analysis_id: str) -> List[Dict]:
        """
        Agrega resultados IEDI por banco.
        
        Args:
            analysis_id: UUID da análise
        
        Returns:
            Lista de métricas agregadas por banco
        """
        pass
```

### Implementação

```python
from typing import List, Dict
import logging

from app.repositories.mention_repository import AnalysisMentionRepository

logger = logging.getLogger(__name__)

class IEDIAggregationService:
    def __init__(self, analysis_mention_repo: AnalysisMentionRepository):
        self.analysis_mention_repo = analysis_mention_repo
    
    def aggregate_by_period(self, analysis_id: str) -> List[Dict]:
        logger.info(f"Agregando resultados para análise: {analysis_id}")
        
        # 1. Buscar todos os relacionamentos
        analysis_mentions = self.analysis_mention_repo.find_by_analysis(analysis_id)
        
        if not analysis_mentions:
            logger.warning("Nenhum relacionamento encontrado")
            return []
        
        # 2. Agrupar por banco
        mentions_by_bank = {}
        for am in analysis_mentions:
            if am.bank_id not in mentions_by_bank:
                mentions_by_bank[am.bank_id] = []
            mentions_by_bank[am.bank_id].append(am)
        
        # 3. Calcular métricas por banco
        results = []
        for bank_id, mentions in mentions_by_bank.items():
            metrics = self._calculate_metrics(bank_id, mentions)
            results.append(metrics)
        
        logger.info(f"Agregação concluída: {len(results)} bancos")
        return results
    
    def _calculate_metrics(self, bank_id: str, mentions: List) -> Dict:
        # Volume total
        volume_total = len(mentions)
        
        # Volume por sentimento
        volume_positive = sum(1 for m in mentions if m.sentiment == 'positive')
        volume_negative = sum(1 for m in mentions if m.sentiment == 'negative')
        volume_neutral = sum(1 for m in mentions if m.sentiment == 'neutral')
        
        # IEDI médio (apenas positivas e negativas)
        non_neutral = [m for m in mentions if m.sentiment != 'neutral']
        
        if non_neutral:
            iedi_medio = sum(m.iedi_score for m in non_neutral) / len(non_neutral)
        else:
            iedi_medio = 0.0
        
        # Proporção de positivas
        proporcao_positivas = volume_positive / volume_total if volume_total > 0 else 0
        
        # IEDI final (balizamento)
        iedi_final = iedi_medio * proporcao_positivas
        
        # Positividade e negatividade (%)
        positividade = (volume_positive / volume_total) * 100 if volume_total > 0 else 0
        negatividade = (volume_negative / volume_total) * 100 if volume_total > 0 else 0
        
        return {
            'bank_id': bank_id,
            'volume_total': volume_total,
            'volume_positive': volume_positive,
            'volume_negative': volume_negative,
            'volume_neutral': volume_neutral,
            'iedi_medio': round(iedi_medio, 4),
            'proporcao_positivas': round(proporcao_positivas, 4),
            'iedi_final': round(iedi_final, 4),
            'positividade': round(positividade, 2),
            'negatividade': round(negatividade, 2)
        }
```

---

## Integração dos Services

### Orquestrador Principal

```python
# app/services/iedi_orchestrator.py

from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class IEDIOrchestrator:
    """Orquestrador principal do fluxo de processamento IEDI."""
    
    def __init__(
        self,
        brandwatch_service: BrandwatchService,
        enrichment_service: MentionEnrichmentService,
        detection_service: BankDetectionService,
        calculation_service: IEDICalculationService,
        aggregation_service: IEDIAggregationService,
        mention_repo: MentionRepository,
        analysis_mention_repo: AnalysisMentionRepository,
        iedi_result_repo: IEDIResultRepository
    ):
        self.brandwatch = brandwatch_service
        self.enrichment = enrichment_service
        self.detection = detection_service
        self.calculation = calculation_service
        self.aggregation = aggregation_service
        self.mention_repo = mention_repo
        self.analysis_mention_repo = analysis_mention_repo
        self.iedi_result_repo = iedi_result_repo
    
    def process_analysis(
        self,
        analysis_id: str,
        start_date: datetime,
        end_date: datetime,
        query_name: str
    ) -> Dict:
        """
        Processa análise IEDI completa.
        
        Args:
            analysis_id: UUID da análise
            start_date: Data inicial
            end_date: Data final
            query_name: Nome da query Brandwatch
        
        Returns:
            Resultado do processamento com métricas
        """
        logger.info(f"Iniciando processamento: {analysis_id}")
        
        # 1. Coleta Brandwatch
        logger.info("Etapa 1: Coleta Brandwatch")
        mentions = self.brandwatch.extract_mentions(
            start_date=start_date,
            end_date=end_date,
            query_name=query_name
        )
        
        # 2-5. Processar cada menção
        logger.info(f"Etapa 2-5: Processando {len(mentions)} menções")
        processed_count = 0
        
        for bw_mention in mentions:
            # 2. Enriquecimento
            enriched = self.enrichment.enrich(bw_mention)
            
            # 3. Detecção
            detected_banks = self.detection.detect_banks(enriched)
            
            if not detected_banks:
                continue
            
            # 5. Armazenamento
            mention_record = self.mention_repo.find_or_create(
                url=enriched['url'],
                **enriched
            )
            
            # 4. Cálculo + 5. Armazenamento (por banco)
            for bank in detected_banks:
                iedi_result = self.calculation.calculate_iedi(enriched, bank)
                
                self.analysis_mention_repo.create(
                    analysis_id=analysis_id,
                    mention_id=mention_record.id,
                    bank_id=bank['bank_id'],
                    **iedi_result
                )
            
            processed_count += 1
        
        # 6. Agregação
        logger.info("Etapa 6: Agregação")
        aggregated = self.aggregation.aggregate_by_period(analysis_id)
        
        # 7. Geração de Resultados
        logger.info("Etapa 7: Geração de Resultados")
        for metrics in aggregated:
            self.iedi_result_repo.create(
                bank_id=metrics['bank_id'],
                **metrics
            )
        
        # Gerar ranking
        ranking = self.iedi_result_repo.generate_ranking(analysis_id)
        
        logger.info("Processamento concluído!")
        
        return {
            'analysis_id': analysis_id,
            'total_mentions': len(mentions),
            'processed_mentions': processed_count,
            'banks_detected': len(aggregated),
            'ranking': ranking
        }
```

---

## Próximos Passos

1. ✅ Implementar cada service em `app/services/`
2. ✅ Criar testes unitários em `tests/services/`
3. ✅ Implementar orquestrador em `app/services/iedi_orchestrator.py`
4. ✅ Criar endpoint REST em `app/controllers/analysis_controller.py`
5. ✅ Adicionar documentação de API (Swagger/OpenAPI)

---

**Desenvolvido por**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0
