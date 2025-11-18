# BrandwatchService - Guia Técnico

## Visão Geral

O `BrandwatchService` é responsável por toda interação com a API do Brandwatch através da biblioteca `bcr-api`. Ele abstrai a complexidade de autenticação, paginação e extração de mentions.

## Arquitetura

```
BrandwatchService
├── BWProject (autenticação e projeto)
└── BWQueries (gerenciamento de queries e mentions)
```

## Configuração

### Variáveis de Ambiente (.env)

```env
BRANDWATCH_USERNAME=seu_email@exemplo.com
BRANDWATCH_PASSWORD=sua_senha
BRANDWATCH_PROJECT_ID=12345
```

### Instalação de Dependências

```bash
pip install bcr-api
```

## Uso Básico

### 1. Inicialização

```python
from app.services.brandwatch_service import BrandwatchService

service = BrandwatchService()
```

### 2. Testar Conexão

```python
if service.test_connection():
    print("Conexão estabelecida!")
else:
    print("Falha na conexão")
```

### 3. Listar Queries Disponíveis

```python
queries = service.list_queries()

for query in queries:
    print(f"Query: {query['name']} (ID: {query['id']})")
```

### 4. Extrair Mentions

```python
from datetime import datetime

mentions = service.extract_mentions(
    query_name="Nome da Query",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31)
)

print(f"Total de mentions: {len(mentions)}")
```

## Métodos Disponíveis

### `extract_mentions()`

Extrai mentions de uma query específica.

**Parâmetros:**
- `query_name` (str): Nome da query no Brandwatch
- `start_date` (datetime): Data de início da coleta
- `end_date` (datetime): Data final da coleta
- `max_pages` (int, opcional): Número máximo de páginas (None = todas)
- `page_size` (int, opcional): Mentions por página (padrão: 5000)
- `**filters`: Filtros adicionais

**Retorno:**
- Lista de dicionários com dados das mentions

**Exemplo:**
```python
mentions = service.extract_mentions(
    query_name="Banco do Brasil",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    max_pages=10,  # Limitar a 10 páginas
    page_size=1000,  # 1000 mentions por página
    sentiment="positive"  # Filtrar apenas sentimento positivo
)
```

### `list_queries()`

Lista todas as queries disponíveis no projeto.

**Retorno:**
- Lista de dicionários com informações das queries

**Exemplo:**
```python
queries = service.list_queries()
for query in queries:
    print(f"{query['id']}: {query['name']}")
```

### `test_connection()`

Testa conexão com Brandwatch API.

**Retorno:**
- `True` se conexão bem-sucedida, `False` caso contrário

**Exemplo:**
```python
if service.test_connection():
    print("Conectado!")
```

## Filtros Disponíveis

O método `extract_mentions()` aceita diversos filtros opcionais:

### Filtros de Conteúdo

- `search` (str): Busca por texto específico
- `language` (str): Filtrar por idioma (ex: "pt", "en")
- `sentiment` (str ou list): Filtrar por sentimento ("positive", "negative", "neutral")

### Filtros de Fonte

- `domain` (str): Filtrar por domínio (ex: "globo.com")
- `pageType` (str ou list): Tipo de página ("blog", "news", "forum", etc.)
- `siteGroup` (list): Filtrar por grupo de sites (requer IDs)

### Filtros de Autor

- `author` (str): Filtrar por autor
- `authorGroup` (list): Filtrar por grupo de autores (requer IDs)

### Filtros de Engajamento

- `twitterRetweetsMin` (int): Mínimo de retweets
- `twitterRetweetsMax` (int): Máximo de retweets
- `facebookSharesMin` (int): Mínimo de compartilhamentos Facebook
- `facebookSharesMax` (int): Máximo de compartilhamentos Facebook

### Filtros de Localização

- `location` (str): Filtrar por localização
- `locationGroup` (list): Filtrar por grupo de localizações (requer IDs)

### Filtros de Classificação

- `tag` (list): Filtrar por tags (requer IDs)
- `category` (list): Filtrar por categorias (requer IDs)
- `starred` (bool): Apenas mentions marcadas como favoritas

### Exemplo com Múltiplos Filtros

```python
mentions = service.extract_mentions(
    query_name="Banco do Brasil",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    language="pt",
    sentiment=["positive", "neutral"],
    pageType="news",
    domain="globo.com"
)
```

## Estrutura de uma Mention

Cada mention retornada é um dicionário com os seguintes campos principais:

```python
{
    'id': 123456789,                    # ID único da mention
    'url': 'https://...',               # URL da mention
    'originalUrl': 'https://...',       # URL original (antes de redirecionamentos)
    'title': 'Título da notícia',      # Título
    'snippet': 'Texto da mention...',  # Conteúdo/snippet
    'date': '2024-10-15T10:30:00Z',    # Data de publicação
    'domain': 'globo.com',             # Domínio
    'author': 'Nome do Autor',         # Autor
    'language': 'pt',                  # Idioma
    'sentiment': 'positive',           # Sentimento
    'pageType': 'news',                # Tipo de página
    'reach': 1000000,                  # Alcance estimado
    'twitterRetweets': 50,             # Número de retweets
    'facebookShares': 100,             # Compartilhamentos Facebook
    'tags': [...],                     # Tags aplicadas
    'categories': [...],               # Categorias aplicadas
    # ... outros campos
}
```

## Paginação

O `BrandwatchService` gerencia paginação automaticamente:

- **Padrão**: Coleta TODAS as mentions (sem limite de páginas)
- **Com limite**: Use `max_pages` para limitar
- **Tamanho de página**: Padrão 5000, ajustável via `page_size`

### Exemplo de Paginação Controlada

```python
# Coletar apenas primeiras 5 páginas (25.000 mentions)
mentions = service.extract_mentions(
    query_name="Banco do Brasil",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    max_pages=5,
    page_size=5000
)
```

## Tratamento de Erros

### ValueError

Lançado quando credenciais não estão configuradas:

```python
try:
    service.test_connection()
except ValueError as e:
    print(f"Credenciais faltando: {e}")
```

### RuntimeError

Lançado quando query não é encontrada:

```python
try:
    mentions = service.extract_mentions(
        query_name="Query Inexistente",
        start_date=datetime(2024, 10, 1),
        end_date=datetime(2024, 10, 31)
    )
except RuntimeError as e:
    print(f"Query não encontrada: {e}")
```

### KeyError

Lançado quando filtro é inválido:

```python
try:
    mentions = service.extract_mentions(
        query_name="Banco do Brasil",
        start_date=datetime(2024, 10, 1),
        end_date=datetime(2024, 10, 31),
        filtro_invalido="valor"
    )
except KeyError as e:
    print(f"Filtro inválido: {e}")
```

## Logging

O serviço usa Python logging para rastreabilidade:

```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Logs automáticos:
# INFO: Cliente Brandwatch conectado com sucesso
# INFO: Extraindo menções: Banco do Brasil (2024-10-01 - 2024-10-31)
# INFO: Total de menções extraídas: 1234
```

## Performance

### Recomendações

1. **Use `max_pages` para testes**: Evite coletar milhares de mentions em testes
2. **Ajuste `page_size`**: Páginas menores = mais requisições, mas menos memória
3. **Filtre no Brandwatch**: Use filtros para reduzir volume de dados
4. **Cache de conexão**: A instância `BWProject` é reutilizada (lazy loading)

### Exemplo de Teste Rápido

```python
# Coletar apenas 1 página para teste
mentions = service.extract_mentions(
    query_name="Banco do Brasil",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    max_pages=1,  # Apenas 1 página
    page_size=100  # Apenas 100 mentions
)
```

## Integração com IEDI

### Fluxo Completo

```python
from app.services.brandwatch_service import BrandwatchService
from datetime import datetime

# 1. Inicializar serviço
service = BrandwatchService()

# 2. Extrair mentions
mentions = service.extract_mentions(
    query_name="Bancos Brasileiros",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31)
)

# 3. Processar cada mention
for mention in mentions:
    # Extrair URL única
    url = mention.get('url') or mention.get('originalUrl')
    
    # Detectar bancos mencionados
    # Calcular IEDI
    # Salvar no banco de dados
    pass
```

## Próximos Passos

1. **Configurar credenciais reais** no `.env`
2. **Testar conexão** com `test_connection()`
3. **Listar queries** disponíveis com `list_queries()`
4. **Extrair mentions de teste** (1 página) para validar estrutura
5. **Implementar fluxo completo** de processamento IEDI

## Referências

- [Repositório bcr-api](https://github.com/BrandwatchLtd/bcr-api)
- [Notebook de exemplos](https://github.com/BrandwatchLtd/bcr-api/blob/master/DEMO.ipynb)
- [Documentação Brandwatch API](https://developers.brandwatch.com/)
