# Análise: Refatoração Schema Mentions + Analysis_Mentions

**Data**: 15 de novembro de 2025  
**Objetivo**: Separar dados brutos de menções dos cálculos IEDI específicos por banco

---

## Problema Identificado

### Schema Atual (Incorreto)

#### Tabela `mentions`
```sql
CREATE TABLE iedi.mentions (
    id STRING(36) PRIMARY KEY,
    brandwatch_id STRING(255),
    categories ARRAY<STRING>,        -- Bancos detectados
    title TEXT,
    domain STRING(255),
    published_date TIMESTAMP,
    -- ❌ PROBLEMA: Campos de cálculo IEDI na tabela de menções
    iedi_score FLOAT64,              -- Específico por BANCO
    iedi_normalized FLOAT64,         -- Específico por BANCO
    numerator INT64,                 -- Específico por BANCO
    denominator INT64,               -- Específico por BANCO
    title_verified INT64,            -- Específico por BANCO
    subtitle_verified INT64,         -- Específico por BANCO
    relevant_outlet_verified INT64,  -- Específico por BANCO
    niche_outlet_verified INT64      -- Específico por BANCO
);
```

**Problema**: Uma menção pode citar **múltiplos bancos** (ex: "BB e Itaú anunciam parceria"). Cada banco terá um **cálculo IEDI diferente**, mas atualmente só podemos armazenar **um único conjunto de valores**.

#### Tabela `analysis_mentions`
```sql
CREATE TABLE iedi.analysis_mentions (
    analysis_id STRING(36),
    mention_id STRING(36),
    bank_id STRING(36),
    created_at TIMESTAMP,
    PRIMARY KEY (analysis_id, mention_id, bank_id)
);
```

**Problema**: Apenas relaciona análise → menção → banco, mas **não armazena os cálculos IEDI** específicos daquela combinação.

---

## Solução Proposta

### Novo Schema (Correto)

#### 1. Tabela `mentions` - Dados Brutos APENAS

```sql
CREATE TABLE iedi.mentions (
    id STRING(36) PRIMARY KEY,
    brandwatch_id STRING(255) UNIQUE,
    
    -- Dados brutos da Brandwatch (não processados)
    categories ARRAY<STRING>,        -- Bancos detectados (raw)
    sentiment STRING(50),            -- Sentimento (raw)
    title TEXT,
    snippet TEXT,
    full_text TEXT,
    domain STRING(255),
    url STRING(500),
    published_date TIMESTAMP,
    
    -- Metadados do veículo (copiados de media_outlets)
    media_outlet_id STRING(36),      -- FK para media_outlets
    monthly_visitors INT64,
    reach_group STRING(10),          -- A, B, C, D
    
    -- Timestamps
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Características**:
- ✅ Apenas dados **brutos** da Brandwatch
- ✅ **Sem** cálculos IEDI
- ✅ **Sem** analysis_id (menção é reutilizável)
- ✅ **Sem** bank_id (menção pode citar múltiplos bancos)
- ✅ Identificada por `brandwatch_id` único

#### 2. Tabela `analysis_mentions` - Relacionamento + Cálculos IEDI

```sql
CREATE TABLE iedi.analysis_mentions (
    analysis_id STRING(36),
    mention_id STRING(36),
    bank_id STRING(36),
    
    -- ✅ CÁLCULOS IEDI ESPECÍFICOS PARA ESTE BANCO NESTA ANÁLISE
    iedi_score FLOAT64,
    iedi_normalized FLOAT64,
    numerator INT64,
    denominator INT64,
    
    -- Flags de verificação (específicas por banco)
    title_verified INT64 DEFAULT 0,
    subtitle_verified INT64 DEFAULT 0,
    relevant_outlet_verified INT64 DEFAULT 0,
    niche_outlet_verified INT64 DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP,
    
    PRIMARY KEY (analysis_id, mention_id, bank_id),
    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    FOREIGN KEY (mention_id) REFERENCES mentions(id),
    FOREIGN KEY (bank_id) REFERENCES banks(id)
);
```

**Características**:
- ✅ Relacionamento N:N entre análises, menções e bancos
- ✅ Armazena **cálculos IEDI específicos** para cada banco
- ✅ Uma menção pode ter **múltiplos registros** (um por banco detectado)
- ✅ Permite reutilizar menções em diferentes análises

---

## Exemplo Prático

### Cenário: Menção com 2 Bancos

**Título**: "Banco do Brasil e Itaú lideram ranking de crédito"  
**Domain**: valor.globo.com  
**Brandwatch ID**: bw_123456  
**Categories**: ["Banco do Brasil", "Itaú"]

### Dados Armazenados

#### Tabela `mentions` (1 registro)
```sql
INSERT INTO iedi.mentions VALUES (
    'uuid-mention-1',           -- id
    'bw_123456',                -- brandwatch_id
    ['Banco do Brasil', 'Itaú'], -- categories (raw)
    'positive',                 -- sentiment
    'Banco do Brasil e Itaú lideram ranking...',  -- title
    'valor.globo.com',          -- domain
    '2024-11-15 10:00:00',      -- published_date
    'uuid-valor',               -- media_outlet_id
    5000000,                    -- monthly_visitors
    'A',                        -- reach_group
    CURRENT_TIMESTAMP()         -- created_at
);
```

#### Tabela `analysis_mentions` (2 registros - um por banco)

**Análise ID**: uuid-analysis-nov2024

```sql
-- Registro 1: Banco do Brasil
INSERT INTO iedi.analysis_mentions VALUES (
    'uuid-analysis-nov2024',    -- analysis_id
    'uuid-mention-1',           -- mention_id
    'uuid-bb',                  -- bank_id (Banco do Brasil)
    85.5,                       -- iedi_score (calculado para BB)
    0.855,                      -- iedi_normalized
    5,                          -- numerator
    100,                        -- denominator
    1,                          -- title_verified (BB está no título)
    0,                          -- subtitle_verified
    1,                          -- relevant_outlet_verified (Valor é relevante)
    0,                          -- niche_outlet_verified
    CURRENT_TIMESTAMP()
);

-- Registro 2: Itaú
INSERT INTO iedi.analysis_mentions VALUES (
    'uuid-analysis-nov2024',    -- analysis_id
    'uuid-mention-1',           -- mention_id (MESMA menção)
    'uuid-itau',                -- bank_id (Itaú)
    82.3,                       -- iedi_score (calculado para Itaú)
    0.823,                      -- iedi_normalized
    4,                          -- numerator
    100,                        -- denominator
    1,                          -- title_verified (Itaú está no título)
    0,                          -- subtitle_verified
    1,                          -- relevant_outlet_verified
    0,                          -- niche_outlet_verified
    CURRENT_TIMESTAMP()
);
```

---

## Campos a Mover

### De `mentions` para `analysis_mentions`

| Campo | Tipo | Motivo |
|-------|------|--------|
| `iedi_score` | FLOAT64 | Específico por banco |
| `iedi_normalized` | FLOAT64 | Específico por banco |
| `numerator` | INT64 | Específico por banco |
| `denominator` | INT64 | Específico por banco |
| `title_verified` | INT64 | Específico por banco |
| `subtitle_verified` | INT64 | Específico por banco |
| `relevant_outlet_verified` | INT64 | Específico por banco |
| `niche_outlet_verified` | INT64 | Específico por banco |

### Campos que Permanecem em `mentions`

| Campo | Tipo | Motivo |
|-------|------|--------|
| `id` | STRING(36) | Chave primária |
| `brandwatch_id` | STRING(255) | Identificador único Brandwatch |
| `categories` | ARRAY<STRING> | Dados brutos (lista de bancos) |
| `sentiment` | STRING(50) | Dado bruto |
| `title` | TEXT | Dado bruto |
| `snippet` | TEXT | Dado bruto |
| `full_text` | TEXT | Dado bruto |
| `domain` | STRING(255) | Dado bruto |
| `url` | STRING(500) | Dado bruto |
| `published_date` | TIMESTAMP | Dado bruto |
| `media_outlet_id` | STRING(36) | FK para media_outlets |
| `monthly_visitors` | INT64 | Metadado do veículo |
| `reach_group` | STRING(10) | Metadado do veículo |
| `created_at` | TIMESTAMP | Auditoria |

---

## Benefícios da Nova Arquitetura

### 1. **Suporte a Múltiplos Bancos por Menção**

**Antes** (Incorreto):
```python
# ❌ Menção cita BB e Itaú, mas só podemos armazenar 1 cálculo IEDI
mention = Mention(
    brandwatch_id='bw_123',
    categories=['Banco do Brasil', 'Itaú'],
    iedi_score=85.5,  # De qual banco? BB ou Itaú?
    numerator=5       # Ambíguo!
)
```

**Depois** (Correto):
```python
# ✅ Menção armazena apenas dados brutos
mention = Mention(
    brandwatch_id='bw_123',
    categories=['Banco do Brasil', 'Itaú']  # Raw data
)

# ✅ Cálculos IEDI separados por banco
analysis_mention_bb = AnalysisMention(
    mention_id=mention.id,
    bank_id='uuid-bb',
    iedi_score=85.5,  # Específico para BB
    numerator=5
)

analysis_mention_itau = AnalysisMention(
    mention_id=mention.id,
    bank_id='uuid-itau',
    iedi_score=82.3,  # Específico para Itaú
    numerator=4
)
```

### 2. **Reutilização de Menções em Múltiplas Análises**

```python
# Análise Mensal (Novembro 2024)
analysis_nov = Analysis(name='Novembro 2024', start_date='2024-11-01')

# Análise Trimestral (Q4 2024)
analysis_q4 = Analysis(name='Q4 2024', start_date='2024-10-01')

# MESMA menção, MESMOS cálculos IEDI, análises diferentes
for analysis in [analysis_nov, analysis_q4]:
    AnalysisMention(
        analysis_id=analysis.id,
        mention_id='uuid-mention-1',
        bank_id='uuid-bb',
        iedi_score=85.5,  # Mesmo valor
        numerator=5
    )
```

### 3. **Queries Mais Claras**

```sql
-- Buscar IEDI score do Banco do Brasil em uma análise específica
SELECT 
    m.title,
    m.domain,
    am.iedi_score,
    am.numerator,
    am.denominator
FROM iedi.mentions m
JOIN iedi.analysis_mentions am ON m.id = am.mention_id
WHERE am.analysis_id = 'uuid-analysis-nov2024'
  AND am.bank_id = 'uuid-bb'
ORDER BY am.iedi_score DESC;

-- Comparar IEDI scores de diferentes bancos na mesma menção
SELECT 
    m.title,
    b.name AS bank_name,
    am.iedi_score
FROM iedi.mentions m
JOIN iedi.analysis_mentions am ON m.id = am.mention_id
JOIN iedi.banks b ON b.id = am.bank_id
WHERE m.id = 'uuid-mention-1';
```

---

## Impacto no Código

### Modelos Python

#### Mention (Simplificado)
```python
class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(String(36), primary_key=True)
    brandwatch_id = Column(String(255), unique=True)
    categories = Column(ARRAY(String))  # Raw data
    sentiment = Column(String(50))
    title = Column(Text)
    domain = Column(String(255))
    published_date = Column(TIMESTAMP)
    media_outlet_id = Column(String(36), ForeignKey('media_outlets.id'))
    monthly_visitors = Column(Integer)
    reach_group = Column(String(10))
    
    # SEM campos de cálculo IEDI
```

#### AnalysisMention (Expandido)
```python
class AnalysisMention(Base):
    __tablename__ = "analysis_mentions"
    
    analysis_id = Column(String(36), primary_key=True)
    mention_id = Column(String(36), primary_key=True)
    bank_id = Column(String(36), primary_key=True)
    
    # CÁLCULOS IEDI (movidos de Mention)
    iedi_score = Column(Float)
    iedi_normalized = Column(Float)
    numerator = Column(Integer)
    denominator = Column(Integer)
    title_verified = Column(Integer, default=0)
    subtitle_verified = Column(Integer, default=0)
    relevant_outlet_verified = Column(Integer, default=0)
    niche_outlet_verified = Column(Integer, default=0)
```

### Fluxo de Criação

```python
# 1. Buscar ou criar menção (dados brutos)
mention = session.query(Mention).filter_by(brandwatch_id='bw_123').first()
if not mention:
    mention = Mention(
        id=generate_uuid(),
        brandwatch_id='bw_123',
        categories=['Banco do Brasil', 'Itaú'],
        title='...',
        domain='valor.globo.com',
        published_date=datetime.now()
    )
    session.add(mention)
    session.flush()

# 2. Para cada banco detectado, calcular IEDI e criar relacionamento
for bank_name in mention.categories:
    bank = session.query(Bank).filter_by(name=bank_name).first()
    
    # Calcular IEDI específico para este banco
    iedi_result = calculate_iedi(mention, bank)
    
    # Criar relacionamento com cálculos
    analysis_mention = AnalysisMention(
        analysis_id=analysis.id,
        mention_id=mention.id,
        bank_id=bank.id,
        iedi_score=iedi_result['score'],
        numerator=iedi_result['numerator'],
        denominator=iedi_result['denominator'],
        title_verified=iedi_result['title_verified'],
        # ...
    )
    session.add(analysis_mention)
```

---

## Próximos Passos

1. ✅ Analisar schema atual (CONCLUÍDO)
2. ⏭️ Atualizar modelo `Mention` (remover campos IEDI)
3. ⏭️ Atualizar modelo `AnalysisMention` (adicionar campos IEDI)
4. ⏭️ Atualizar `sql/06_create_table_mentions.sql`
5. ⏭️ Atualizar `sql/07_create_table_analysis_mentions.sql`
6. ⏭️ Atualizar repositories
7. ⏭️ Criar script de migração de dados
8. ⏭️ Documentar nova arquitetura

---

## Referências

- `docs/business/MENTIONS_SCHEMA_REFACTOR.md` - Documentação original da refatoração N:N
- `docs/business/METODOLOGIA_IEDI.md` - Metodologia de cálculo IEDI
- `app/models/mention.py` - Modelo atual (a ser atualizado)
- `app/models/analysis_mention.py` - Modelo atual (a ser expandido)
