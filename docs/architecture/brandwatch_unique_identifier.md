# Identificador Único de Menções Brandwatch

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0

---

## Problema Identificado

O campo `id` retornado pela Brandwatch API **não é um identificador único** confiável para menções. Testes e observações práticas revelaram que o mesmo `id` pode aparecer em menções diferentes, tornando-o inadequado como chave primária ou identificador único.

---

## Solução Implementada

### Identificador Único Real: URL

O **identificador único real** de uma menção Brandwatch é a **URL da publicação**. Cada menção possui uma URL única que identifica univocamente aquela publicação específica.

### Campos de URL na Brandwatch API

A Brandwatch API pode retornar a URL em **dois campos diferentes**:

| Campo | Descrição | Quando é preenchido |
|-------|-----------|---------------------|
| `url` | URL principal da menção | Sempre (na maioria dos casos) |
| `originalUrl` | URL original antes de redirecionamentos | Quando a menção é um redirecionamento |

### Lógica de Extração

Para garantir que sempre capturamos o identificador único, implementamos a seguinte lógica:

```python
def extract_unique_url(mention_data: dict) -> str:
    """
    Extrai URL única da menção Brandwatch.
    
    Brandwatch pode retornar a URL em dois campos:
    - 'url': URL principal
    - 'originalUrl': URL original (redirecionamentos)
    
    Args:
        mention_data: Dados brutos da menção Brandwatch
    
    Returns:
        URL única (primeiro campo preenchido)
    
    Raises:
        ValueError: Se nenhum campo de URL estiver preenchido
    """
    url = mention_data.get('url') or mention_data.get('originalUrl')
    
    if not url:
        raise ValueError(
            f"Menção sem URL: {mention_data.get('id')} - "
            "Campos 'url' e 'originalUrl' vazios"
        )
    
    return url
```

**Ordem de prioridade**:
1. Verificar campo `url`
2. Se vazio, verificar campo `originalUrl`
3. Se ambos vazios, lançar erro

---

## Alterações Implementadas

### 1. Modelo `Mention`

**Antes**:
```python
class Mention(Base):
    id = Column(String(36), primary_key=True)
    brandwatch_id = Column(String(255), unique=True, nullable=True)
    url = Column(String(500), nullable=True)
```

**Depois**:
```python
class Mention(Base):
    id = Column(String(36), primary_key=True)
    
    # Identificador único da Brandwatch (URL da menção)
    url = Column(String(500), unique=True, nullable=False)  # Identificador único
    brandwatch_id = Column(String(255), nullable=True)      # ID Brandwatch (não único)
    original_url = Column(String(500), nullable=True)       # URL original (backup)
```

**Mudanças**:
- `url`: Agora é `unique=True` e `nullable=False` (identificador único)
- `brandwatch_id`: Agora é `nullable=True` e **não é único** (apenas referência)
- `original_url`: Novo campo para armazenar URL original quando disponível

### 2. Script SQL

**Antes**:
```sql
CREATE TABLE iedi.mentions (
  id STRING(36) NOT NULL,
  brandwatch_id STRING(255),
  url STRING(500),
  ...
  PRIMARY KEY (id)
);

CREATE UNIQUE INDEX idx_mentions_brandwatch_id 
ON iedi.mentions(brandwatch_id);
```

**Depois**:
```sql
CREATE TABLE iedi.mentions (
  id STRING(36) NOT NULL,
  url STRING(500) NOT NULL,               -- Identificador único
  brandwatch_id STRING(255),              -- ID Brandwatch (não único)
  original_url STRING(500),               -- URL original (backup)
  ...
  PRIMARY KEY (id)
);

-- Índice único na URL (identificador real)
CREATE UNIQUE INDEX idx_mentions_url 
ON iedi.mentions(url);

-- Índice não-único no brandwatch_id (pode ser útil mas não é único)
CREATE INDEX idx_mentions_brandwatch_id 
ON iedi.mentions(brandwatch_id);
```

**Mudanças**:
- Índice único movido de `brandwatch_id` para `url`
- `brandwatch_id` agora tem índice não-único (apenas para busca)

### 3. Repository `MentionRepository`

**Novos métodos**:

```python
def find_by_url(self, url: str) -> Optional[Mention]:
    """Busca menção por URL (identificador único real)."""
    session = get_session()
    return session.query(Mention).filter(
        Mention.url == url
    ).first()

@staticmethod
def extract_unique_url(mention_data: dict) -> str:
    """Extrai URL única (verificar 'url' e 'originalUrl')."""
    url = mention_data.get('url') or mention_data.get('originalUrl')
    
    if not url:
        raise ValueError(
            f"Menção sem URL: {mention_data.get('id')} - "
            "Campos 'url' e 'originalUrl' vazios"
        )
    
    return url

def find_or_create(self, url: str, **kwargs) -> Mention:
    """Busca menção existente por URL ou cria nova."""
    existing = self.find_by_url(url)
    if existing:
        return existing
    
    kwargs['url'] = url
    return self.create(**kwargs)
```

**Método atualizado**:

```python
def find_by_brandwatch_id(self, brandwatch_id: str) -> Optional[Mention]:
    """
    Busca menção por brandwatch_id (ATENÇÃO: não é identificador único).
    
    Este método existe para compatibilidade, mas o brandwatch_id pode se repetir.
    Use find_by_url() para busca por identificador único.
    """
    # ... implementação
```

### 4. Service `MentionEnrichmentService`

**Antes**:
```python
def enrich(self, mention: Dict) -> Dict:
    enriched = {
        'brandwatch_id': mention['id'],
        'title': mention.get('title'),
        'url': mention.get('url'),
        ...
    }
    return enriched
```

**Depois**:
```python
def enrich(self, mention: Dict) -> Dict:
    # Extrair URL única (verificar 'url' e 'originalUrl')
    unique_url = self._extract_unique_url(mention)
    
    enriched = {
        'url': unique_url,
        'brandwatch_id': mention.get('id'),
        'original_url': mention.get('originalUrl'),
        'title': mention.get('title'),
        ...
    }
    return enriched

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

### 5. Orquestrador `IEDIOrchestrator`

**Antes**:
```python
mention_record = self.mention_repo.find_or_create(
    brandwatch_id=enriched['brandwatch_id'],
    **enriched
)
```

**Depois**:
```python
mention_record = self.mention_repo.find_or_create(
    url=enriched['url'],
    **enriched
)
```

---

## Fluxo de Processamento Atualizado

### 1. Coleta Brandwatch

```python
# Brandwatch retorna menção com 'url' e/ou 'originalUrl'
mention = {
    'id': 'bw_123456',
    'url': 'https://valor.globo.com/financas/noticia/2024/11/15/bb-lucro.ghtml',
    'originalUrl': 'https://valor.globo.com/financas/noticia/2024/11/15/bb-lucro.ghtml',
    'title': 'Banco do Brasil anuncia lucro recorde',
    ...
}
```

### 2. Enriquecimento

```python
# Extrair URL única
unique_url = enrichment_service._extract_unique_url(mention)
# Resultado: 'https://valor.globo.com/financas/noticia/2024/11/15/bb-lucro.ghtml'

enriched = {
    'url': unique_url,
    'brandwatch_id': mention.get('id'),
    'original_url': mention.get('originalUrl'),
    ...
}
```

### 3. Armazenamento

```python
# Buscar menção existente por URL
mention_record = mention_repo.find_by_url(url=unique_url)

if not mention_record:
    # Criar nova menção
    mention_record = mention_repo.create(
        url=unique_url,
        brandwatch_id=mention.get('id'),
        original_url=mention.get('originalUrl'),
        ...
    )
```

---

## Vantagens da Solução

### 1. Unicidade Garantida

A URL é **garantidamente única** para cada publicação, eliminando o risco de duplicatas ou conflitos de chave primária.

### 2. Reutilização de Menções

Menções podem ser reutilizadas em múltiplas análises sem duplicação:

```python
# Análise de Novembro
mention_nov = mention_repo.find_by_url('https://valor.globo.com/...')

# Análise de Trimestre (reutiliza mesma menção)
mention_tri = mention_repo.find_by_url('https://valor.globo.com/...')

# mention_nov.id == mention_tri.id (mesma menção)
```

### 3. Rastreabilidade

A URL permite rastrear a menção de volta à publicação original na web:

```python
# Acessar publicação original
import webbrowser
webbrowser.open(mention.url)
```

### 4. Compatibilidade com Brandwatch

A solução verifica **ambos os campos** (`url` e `originalUrl`), garantindo compatibilidade com diferentes cenários de retorno da API Brandwatch.

---

## Casos de Uso

### Caso 1: URL Normal

```python
mention = {
    'id': 'bw_123',
    'url': 'https://valor.globo.com/artigo.html',
    'originalUrl': None  # Não preenchido
}

unique_url = extract_unique_url(mention)
# Resultado: 'https://valor.globo.com/artigo.html'
```

### Caso 2: Redirecionamento

```python
mention = {
    'id': 'bw_456',
    'url': 'https://valor.globo.com/artigo-final.html',
    'originalUrl': 'https://valor.globo.com/artigo-original.html'
}

unique_url = extract_unique_url(mention)
# Resultado: 'https://valor.globo.com/artigo-final.html' (prioriza 'url')
```

### Caso 3: Apenas originalUrl

```python
mention = {
    'id': 'bw_789',
    'url': None,  # Não preenchido
    'originalUrl': 'https://valor.globo.com/artigo.html'
}

unique_url = extract_unique_url(mention)
# Resultado: 'https://valor.globo.com/artigo.html' (fallback para 'originalUrl')
```

### Caso 4: Erro (Nenhum campo preenchido)

```python
mention = {
    'id': 'bw_999',
    'url': None,
    'originalUrl': None
}

unique_url = extract_unique_url(mention)
# Resultado: ValueError("Menção sem URL: bw_999 - Campos 'url' e 'originalUrl' vazios")
```

---

## Migração de Dados Existentes

Se já existem menções no banco de dados com `brandwatch_id` como identificador único:

### Passo 1: Verificar Duplicatas

```sql
-- Verificar se há brandwatch_ids duplicados
SELECT brandwatch_id, COUNT(*) as count
FROM iedi.mentions
GROUP BY brandwatch_id
HAVING COUNT(*) > 1;
```

### Passo 2: Atualizar Schema

```sql
-- Remover índice único de brandwatch_id
DROP INDEX idx_mentions_brandwatch_id ON iedi.mentions;

-- Adicionar índice único em url
CREATE UNIQUE INDEX idx_mentions_url ON iedi.mentions(url);

-- Adicionar índice não-único em brandwatch_id
CREATE INDEX idx_mentions_brandwatch_id ON iedi.mentions(brandwatch_id);
```

### Passo 3: Validar Dados

```sql
-- Verificar menções sem URL
SELECT id, brandwatch_id, title
FROM iedi.mentions
WHERE url IS NULL OR url = '';
```

---

## Referências

- **Brandwatch API Documentation**: Mention Field Definitions
- **Modelo Mention**: `app/models/mention.py`
- **Repository**: `app/repositories/mention_repository.py`
- **Service**: `app/services/mention_enrichment_service.py`

---

## Conclusão

A mudança de `brandwatch_id` para `url` como identificador único resolve o problema de duplicatas e garante a integridade dos dados. A solução é **robusta**, **compatível** com a API Brandwatch e **escalável** para grandes volumes de menções.

---

**Desenvolvido por**: Manus AI  
**Data**: 15 de novembro de 2025
