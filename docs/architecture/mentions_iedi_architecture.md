# Arquitetura: Mentions + IEDI Calculations

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 2.0

---

## Visão Geral

Este documento descreve a arquitetura de armazenamento e processamento de menções no sistema IEDI, com foco na separação entre **dados brutos** (mentions) e **cálculos IEDI específicos por banco** (analysis_mentions).

A arquitetura foi projetada para suportar menções que citam **múltiplos bancos**, permitindo que cada banco tenha seu próprio cálculo IEDI independente.

---

## Problema Resolvido

### Cenário

Uma menção pode citar múltiplos bancos simultaneamente:

> **Título**: "Banco do Brasil e Itaú lideram ranking de crédito no Brasil"  
> **Veículo**: Valor Econômico  
> **Data**: 15/11/2024

### Desafio

Cada banco mencionado deve ter seu próprio **cálculo IEDI**, pois:

1. **Verificação de Título**: O banco está mencionado no título? (BB: sim, Itaú: sim)
2. **Verificação de Subtítulo**: O banco está no subtítulo? (BB: sim, Itaú: não)
3. **Numerador**: Quantidade de verificações positivas (BB: 2, Itaú: 1)
4. **Score IEDI**: Cálculo final (BB: 85.5, Itaú: 82.3)

### Solução Anterior (Incorreta)

A tabela `mentions` continha campos de cálculo IEDI, mas só permitia armazenar **um único conjunto de valores**:

```sql
CREATE TABLE mentions (
    id STRING,
    title STRING,
    iedi_score FLOAT64,      -- ❌ De qual banco? BB ou Itaú?
    numerator INT64,         -- ❌ Ambíguo!
    title_verified BOOL      -- ❌ Ambíguo!
);
```

**Problema**: Impossível armazenar cálculos IEDI diferentes para cada banco na mesma menção.

### Solução Atual (Correta)

Separar **dados brutos** (mentions) de **cálculos IEDI** (analysis_mentions):

```sql
-- Tabela 1: Dados brutos (uma menção)
CREATE TABLE mentions (
    id STRING,
    brandwatch_id STRING,
    title STRING,
    domain STRING
    -- SEM campos de cálculo IEDI
);

-- Tabela 2: Cálculos IEDI (um registro por banco)
CREATE TABLE analysis_mentions (
    analysis_id STRING,
    mention_id STRING,
    bank_id STRING,
    iedi_score FLOAT64,      -- ✅ Específico para este banco
    numerator INT64,         -- ✅ Específico para este banco
    title_verified INT64,    -- ✅ Específico para este banco
    PRIMARY KEY (analysis_id, mention_id, bank_id)
);
```

**Benefício**: Permite múltiplos registros por menção, um para cada banco detectado.

---

## Arquitetura de Dados

### Diagrama Entidade-Relacionamento

```
┌─────────────┐       ┌──────────────────────┐       ┌─────────────┐
│  analyses   │       │  analysis_mentions   │       │  mentions   │
├─────────────┤       ├──────────────────────┤       ├─────────────┤
│ id (PK)     │───┐   │ analysis_id (PK,FK)  │   ┌───│ id (PK)     │
│ name        │   └──→│ mention_id (PK,FK)   │←──┘   │ brandwatch_id│
│ start_date  │       │ bank_id (PK,FK)      │       │ title       │
│ end_date    │       │ iedi_score           │       │ domain      │
└─────────────┘       │ numerator            │       │ sentiment   │
                      │ denominator          │       │ published_date│
┌─────────────┐       │ title_verified       │       │ reach_group │
│   banks     │       │ subtitle_verified    │       └─────────────┘
├─────────────┤       │ *_outlet_verified    │
│ id (PK)     │───┐   │ created_at           │
│ name        │   └──→│                      │
│ variations  │       └──────────────────────┘
└─────────────┘
```

### Relacionamentos

| Tabela | Cardinalidade | Descrição |
|--------|---------------|-----------|
| `analyses` ↔ `analysis_mentions` | 1:N | Uma análise tem muitos relacionamentos |
| `mentions` ↔ `analysis_mentions` | 1:N | Uma menção pode estar em múltiplas análises |
| `banks` ↔ `analysis_mentions` | 1:N | Um banco tem muitos relacionamentos |
| `analysis_mentions` | N:N:N | Relacionamento ternário (análise + menção + banco) |

---

## Tabelas

### 1. `mentions` - Dados Brutos

Armazena menções **únicas** da Brandwatch API, identificadas por `brandwatch_id`.

#### Schema SQL

```sql
CREATE TABLE iedi.mentions (
  -- Identificadores
  id STRING(36) PRIMARY KEY,
  brandwatch_id STRING(255) UNIQUE,
  
  -- Dados brutos da Brandwatch
  categories ARRAY<STRING>,           -- Bancos detectados (raw)
  sentiment STRING(50) NOT NULL,      -- positive, negative, neutral
  title STRING,
  snippet STRING,
  full_text STRING,
  url STRING(500),
  domain STRING(255),
  published_date TIMESTAMP,
  
  -- Metadados do veículo
  media_outlet_id STRING(36),         -- FK para media_outlets
  monthly_visitors INT64 DEFAULT 0,
  reach_group STRING(10) NOT NULL,    -- A, B, C, D
  
  -- Timestamps
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP
);
```

#### Modelo Python

```python
class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(String(36), primary_key=True)
    brandwatch_id = Column(String(255), unique=True)
    categories = Column(ARRAY(String))  # Lista de bancos (raw)
    sentiment = Column(String(50))
    title = Column(Text)
    domain = Column(String(255))
    published_date = Column(TIMESTAMP)
    media_outlet_id = Column(String(36))
    monthly_visitors = Column(Integer)
    reach_group = Column(String(10))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
```

#### Características

- ✅ Armazena **apenas dados brutos** da Brandwatch
- ✅ **Sem** cálculos IEDI
- ✅ **Sem** `analysis_id` (menção é reutilizável)
- ✅ **Sem** `bank_id` (menção pode citar múltiplos bancos)
- ✅ Identificada por `brandwatch_id` único

### 2. `analysis_mentions` - Relacionamento + Cálculos IEDI

Conecta análises, menções e bancos, armazenando cálculos IEDI específicos para cada combinação.

#### Schema SQL

```sql
CREATE TABLE iedi.analysis_mentions (
  -- Chave primária composta
  analysis_id STRING(36) NOT NULL,
  mention_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  
  -- Cálculos IEDI específicos
  iedi_score FLOAT64,
  iedi_normalized FLOAT64,
  numerator INT64,
  denominator INT64,
  
  -- Flags de verificação
  title_verified INT64 DEFAULT 0,
  subtitle_verified INT64 DEFAULT 0,
  relevant_outlet_verified INT64 DEFAULT 0,
  niche_outlet_verified INT64 DEFAULT 0,
  
  -- Timestamp
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  
  PRIMARY KEY (analysis_id, mention_id, bank_id),
  FOREIGN KEY (analysis_id) REFERENCES analyses(id),
  FOREIGN KEY (mention_id) REFERENCES mentions(id),
  FOREIGN KEY (bank_id) REFERENCES banks(id)
);
```

#### Modelo Python

```python
class AnalysisMention(Base):
    __tablename__ = "analysis_mentions"
    
    analysis_id = Column(String(36), primary_key=True)
    mention_id = Column(String(36), primary_key=True)
    bank_id = Column(String(36), primary_key=True)
    
    # Cálculos IEDI
    iedi_score = Column(Float)
    iedi_normalized = Column(Float)
    numerator = Column(Integer)
    denominator = Column(Integer)
    
    # Flags de verificação
    title_verified = Column(Integer, default=0)
    subtitle_verified = Column(Integer, default=0)
    relevant_outlet_verified = Column(Integer, default=0)
    niche_outlet_verified = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP)
```

#### Características

- ✅ Relacionamento **N:N** entre análises, menções e bancos
- ✅ Armazena **cálculos IEDI específicos** para cada banco
- ✅ Uma menção pode ter **múltiplos registros** (um por banco)
- ✅ Permite reutilizar menções em diferentes análises

---

## Exemplo Prático

### Cenário: Menção com 2 Bancos

**Dados da Menção:**
- **Título**: "Banco do Brasil e Itaú lideram ranking de crédito"
- **Veículo**: Valor Econômico (valor.globo.com)
- **Data**: 15/11/2024 10:00
- **Brandwatch ID**: bw_123456
- **Categories**: ["Banco do Brasil", "Itaú"]

### Armazenamento

#### Tabela `mentions` (1 registro)

| id | brandwatch_id | title | domain | categories | reach_group |
|----|---------------|-------|--------|------------|-------------|
| uuid-m1 | bw_123456 | Banco do Brasil e Itaú lideram... | valor.globo.com | ["Banco do Brasil", "Itaú"] | A |

#### Tabela `analysis_mentions` (2 registros)

**Análise**: Novembro 2024 (uuid-a1)

| analysis_id | mention_id | bank_id | iedi_score | numerator | title_verified | subtitle_verified |
|-------------|------------|---------|------------|-----------|----------------|-------------------|
| uuid-a1 | uuid-m1 | uuid-bb | 85.5 | 5 | 1 | 1 |
| uuid-a1 | uuid-m1 | uuid-itau | 82.3 | 4 | 1 | 0 |

**Interpretação:**
- **Banco do Brasil**: Score 85.5 (título verificado + subtítulo verificado)
- **Itaú**: Score 82.3 (apenas título verificado, subtítulo não)

### Queries

#### Buscar IEDI Score do Banco do Brasil

```sql
SELECT 
    m.title,
    m.domain,
    am.iedi_score,
    am.numerator,
    am.denominator
FROM iedi.mentions m
JOIN iedi.analysis_mentions am ON m.id = am.mention_id
WHERE am.analysis_id = 'uuid-a1'
  AND am.bank_id = 'uuid-bb'
ORDER BY am.iedi_score DESC;
```

#### Comparar Scores de Diferentes Bancos na Mesma Menção

```sql
SELECT 
    m.title,
    b.name AS bank_name,
    am.iedi_score,
    am.title_verified,
    am.subtitle_verified
FROM iedi.mentions m
JOIN iedi.analysis_mentions am ON m.id = am.mention_id
JOIN iedi.banks b ON b.id = am.bank_id
WHERE m.id = 'uuid-m1'
ORDER BY am.iedi_score DESC;
```

**Resultado:**

| title | bank_name | iedi_score | title_verified | subtitle_verified |
|-------|-----------|------------|----------------|-------------------|
| BB e Itaú lideram... | Banco do Brasil | 85.5 | 1 | 1 |
| BB e Itaú lideram... | Itaú | 82.3 | 1 | 0 |

---

## Fluxo de Processamento

### 1. Coleta de Menções (Brandwatch API)

```python
# Buscar menções da Brandwatch API
brandwatch_mentions = brandwatch_api.get_mentions(
    category='Banco do Brasil',
    start_date='2024-11-01',
    end_date='2024-11-30'
)

for bw_mention in brandwatch_mentions:
    # 1. Criar/buscar menção (dados brutos)
    mention = mention_repo.find_or_create(
        brandwatch_id=bw_mention['id'],
        title=bw_mention['title'],
        snippet=bw_mention['snippet'],
        domain=bw_mention['domain'],
        published_date=bw_mention['published_date'],
        categories=bw_mention['categories'],  # Lista de bancos
        sentiment=bw_mention['sentiment']
    )
```

### 2. Detecção de Bancos

```python
# Detectar quais bancos foram mencionados
detected_banks = detect_banks_in_mention(mention)

# Exemplo: ['Banco do Brasil', 'Itaú']
```

### 3. Cálculo IEDI por Banco

```python
for bank_name in detected_banks:
    bank = bank_repo.find_by_name(bank_name)
    
    # Calcular IEDI específico para este banco
    iedi_result = calculate_iedi(mention, bank)
    # {
    #     'score': 85.5,
    #     'numerator': 5,
    #     'denominator': 100,
    #     'title_verified': 1,
    #     'subtitle_verified': 1,
    #     'relevant_outlet_verified': 1,
    #     'niche_outlet_verified': 0
    # }
    
    # Criar relacionamento com cálculos IEDI
    analysis_mention_repo.create(
        analysis_id=analysis.id,
        mention_id=mention.id,
        bank_id=bank.id,
        iedi_score=iedi_result['score'],
        numerator=iedi_result['numerator'],
        denominator=iedi_result['denominator'],
        title_verified=iedi_result['title_verified'],
        subtitle_verified=iedi_result['subtitle_verified'],
        relevant_outlet_verified=iedi_result['relevant_outlet_verified'],
        niche_outlet_verified=iedi_result['niche_outlet_verified']
    )
```

### 4. Reutilização em Múltiplas Análises

```python
# Análise Mensal (Novembro 2024)
analysis_nov = analysis_repo.create(
    name='Novembro 2024',
    start_date='2024-11-01',
    end_date='2024-11-30'
)

# Análise Trimestral (Q4 2024)
analysis_q4 = analysis_repo.create(
    name='Q4 2024',
    start_date='2024-10-01',
    end_date='2024-12-31'
)

# Buscar menções do período (reutilizar existentes)
mentions = mention_repo.find_by_date_range(
    start_date='2024-11-01',
    end_date='2024-11-30'
)

# Para cada análise, criar relacionamentos
for analysis in [analysis_nov, analysis_q4]:
    for mention in mentions:
        for bank in detect_banks_in_mention(mention):
            iedi_result = calculate_iedi(mention, bank)
            
            analysis_mention_repo.create(
                analysis_id=analysis.id,
                mention_id=mention.id,
                bank_id=bank.id,
                **iedi_result  # Mesmo cálculo IEDI
            )
```

**Benefício**: Menção armazenada **uma única vez**, mas usada em **múltiplas análises** com os mesmos cálculos IEDI.

---

## Repositories

### MentionRepository

Gerencia menções (dados brutos da Brandwatch).

#### Métodos Principais

| Método | Descrição | Retorno |
|--------|-----------|---------|
| `create(**kwargs)` | Criar nova menção | Mention |
| `find_by_brandwatch_id(brandwatch_id)` | Buscar por ID Brandwatch | Mention ou None |
| `find_or_create(brandwatch_id, **kwargs)` | Buscar ou criar se não existir | Mention |
| `find_by_domain(domain)` | Buscar por veículo | List[Mention] |
| `find_by_date_range(start, end)` | Buscar por período | List[Mention] |
| `update(mention_id, **kwargs)` | Atualizar dados brutos | Mention ou None |

#### Exemplo de Uso

```python
# Buscar ou criar menção
mention = mention_repo.find_or_create(
    brandwatch_id='bw_123456',
    title='BB e Itaú lideram ranking',
    domain='valor.globo.com',
    published_date=datetime(2024, 11, 15, 10, 0),
    categories=['Banco do Brasil', 'Itaú'],
    sentiment='positive',
    reach_group='A',
    monthly_visitors=5000000
)
```

### AnalysisMentionRepository

Gerencia relacionamentos análise-menção-banco + cálculos IEDI.

#### Métodos Principais

| Método | Descrição | Retorno |
|--------|-----------|---------|
| `create(analysis_id, mention_id, bank_id, **kwargs)` | Criar relacionamento com IEDI | AnalysisMention |
| `find_by_analysis(analysis_id)` | Buscar todos relacionamentos de uma análise | List[AnalysisMention] |
| `find_by_analysis_and_bank(analysis_id, bank_id)` | Filtrar por banco específico | List[AnalysisMention] |
| `find_by_mention(mention_id)` | Ver em quais análises uma menção foi usada | List[AnalysisMention] |
| `find_by_key(analysis_id, mention_id, bank_id)` | Buscar por chave primária composta | AnalysisMention ou None |
| `update_iedi_scores(analysis_id, mention_id, bank_id, ...)` | Atualizar cálculos IEDI | AnalysisMention ou None |

#### Exemplo de Uso

```python
# Criar relacionamento com cálculos IEDI
analysis_mention = analysis_mention_repo.create(
    analysis_id='uuid-analysis-nov2024',
    mention_id='uuid-mention-1',
    bank_id='uuid-bb',
    iedi_score=85.5,
    iedi_normalized=0.855,
    numerator=5,
    denominator=100,
    title_verified=1,
    subtitle_verified=1,
    relevant_outlet_verified=1,
    niche_outlet_verified=0
)

# Buscar menções do Banco do Brasil em uma análise
bb_mentions = analysis_mention_repo.find_by_analysis_and_bank(
    analysis_id='uuid-analysis-nov2024',
    bank_id='uuid-bb'
)
```

---

## Benefícios da Arquitetura

### 1. Suporte a Múltiplos Bancos por Menção

**Antes** (Incorreto):
```python
# ❌ Menção cita BB e Itaú, mas só podemos armazenar 1 cálculo IEDI
mention = Mention(
    brandwatch_id='bw_123',
    categories=['Banco do Brasil', 'Itaú'],
    iedi_score=85.5,  # De qual banco?
    numerator=5       # Ambíguo!
)
```

**Depois** (Correto):
```python
# ✅ Menção armazena apenas dados brutos
mention = Mention(
    brandwatch_id='bw_123',
    categories=['Banco do Brasil', 'Itaú']
)

# ✅ Cálculos IEDI separados por banco
AnalysisMention(mention_id=mention.id, bank_id='uuid-bb', iedi_score=85.5)
AnalysisMention(mention_id=mention.id, bank_id='uuid-itau', iedi_score=82.3)
```

### 2. Reutilização de Menções

```python
# MESMA menção usada em múltiplas análises
for analysis in [analysis_nov, analysis_q4, analysis_year]:
    AnalysisMention(
        analysis_id=analysis.id,
        mention_id='uuid-mention-1',
        bank_id='uuid-bb',
        iedi_score=85.5  # Mesmo valor
    )
```

**Economia**: Menção armazenada **1 vez**, usada em **3 análises**.

### 3. Consistência de Dados

```python
# Atualizar sentimento da menção
mention = mention_repo.find_by_brandwatch_id('bw_123')
mention_repo.update(mention.id, sentiment='neutral')

# Todas as análises que usam esta menção verão a atualização
```

### 4. Queries Flexíveis

```sql
-- Top 10 menções com maior IEDI score para Banco do Brasil
SELECT m.title, am.iedi_score
FROM mentions m
JOIN analysis_mentions am ON m.id = am.mention_id
WHERE am.analysis_id = 'uuid-a1' AND am.bank_id = 'uuid-bb'
ORDER BY am.iedi_score DESC
LIMIT 10;
```

---

## Migração de Dados

### Script SQL

Executar `sql/13_migrate_iedi_to_analysis_mentions.sql` para:

1. ✅ Criar backup `mentions_backup`
2. ✅ Migrar campos IEDI de `mentions` para `analysis_mentions`
3. ✅ Criar nova tabela `mentions_new` sem campos IEDI
4. ✅ Remover duplicatas por `brandwatch_id`
5. ⚠️ **Manual**: Validar dados e substituir tabela antiga

### Validação

```sql
-- Verificar contagem de registros
SELECT 
  (SELECT COUNT(*) FROM iedi.mentions_backup) as old_count,
  (SELECT COUNT(DISTINCT brandwatch_id) FROM iedi.mentions) as new_unique_count,
  (SELECT COUNT(*) FROM iedi.analysis_mentions) as relationships_count;

-- Verificar integridade referencial
SELECT am.analysis_id, am.mention_id, am.bank_id
FROM iedi.analysis_mentions am
LEFT JOIN iedi.mentions m ON m.id = am.mention_id
WHERE m.id IS NULL;  -- Deve retornar 0 registros
```

---

## Referências

- `docs/business/MENTIONS_SCHEMA_REFACTOR.md` - Documentação original da refatoração N:N
- `docs/business/METODOLOGIA_IEDI.md` - Metodologia de cálculo IEDI
- `SCHEMA_REFACTOR_ANALYSIS.md` - Análise detalhada da refatoração
- `app/models/mention.py` - Modelo Mention (dados brutos)
- `app/models/analysis_mention.py` - Modelo AnalysisMention (IEDI)
- `app/repositories/mention_repository.py` - Repositories para mentions e analysis_mentions
- `sql/06_create_table_mentions.sql` - Schema SQL de mentions
- `sql/07_create_table_analysis_mentions.sql` - Schema SQL de analysis_mentions

---

**Nota**: Esta arquitetura foi projetada para máxima flexibilidade e reutilização de dados, permitindo que o sistema IEDI escale eficientemente com o crescimento do volume de menções e análises.
