# SQL Scripts - IEDI BigQuery Schema

Scripts SQL para criação do schema e tabelas do sistema IEDI no Google BigQuery.

## Ordem de Execução

Execute os scripts na ordem numérica:

### Criação do Schema e Tabelas

1. `01_create_schema.sql` - Cria o schema `iedi`
2. `02_create_table_banks.sql` - Cria tabela de bancos
3. `03_create_table_media_outlets.sql` - Cria tabela de veículos de mídia (unificada)
4. `04_create_table_analyses.sql` - Cria tabela de análises
5. `05_create_table_bank_periods.sql` - Cria tabela de períodos por banco
6. `06_create_table_mentions.sql` - Cria tabela de menções (sem analysis_id)
7. `07_create_table_analysis_mentions.sql` - Cria tabela de relacionamento N:N
8. `08_create_table_iedi_results.sql` - Cria tabela de resultados IEDI

### Inserção de Dados Iniciais

9. `09_insert_banks.sql` - Insere 4 bancos (BB, Bradesco, Itaú, Santander)
10. `10_insert_media_outlets.sql` - Insere 62 veículos (40 relevant + 22 niche)

### Migrações Opcionais

11. `11_migrate_unify_media_outlets.sql` - Unificação de veículos (se vindo de schema antigo)
12. `12_migrate_mentions_schema.sql` - Refatoração de menções (se vindo de schema antigo)

## Como Executar

### Opção 1: BigQuery Console

1. Acesse o [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Selecione seu projeto
3. Clique em "Compose new query"
4. Cole o conteúdo de cada arquivo SQL
5. Execute na ordem

### Opção 2: bq CLI

```bash
export PROJECT_ID=your-gcp-project-id

bq query --project_id=$PROJECT_ID < 01_create_schema.sql
bq query --project_id=$PROJECT_ID < 02_create_table_banks.sql
bq query --project_id=$PROJECT_ID < 03_create_table_media_outlets.sql
bq query --project_id=$PROJECT_ID < 04_create_table_analyses.sql
bq query --project_id=$PROJECT_ID < 05_create_table_bank_periods.sql
bq query --project_id=$PROJECT_ID < 06_create_table_mentions.sql
bq query --project_id=$PROJECT_ID < 07_create_table_iedi_results.sql

bq query --project_id=$PROJECT_ID < 08_insert_banks.sql
bq query --project_id=$PROJECT_ID < 09_insert_media_outlets.sql
```

### Opção 3: Python (SQLAlchemy)

```python
from app.models import Base
from app.infra.bq_sa import engine

Base.metadata.create_all(engine)
```

## Estrutura do Schema

```
iedi/
├── banks                    (Bancos)
├── media_outlets            (Veículos de mídia - relevant + niche)
├── analyses                 (Análises)
├── bank_periods             (Períodos por banco)
├── mentions                 (Menções da Brandwatch - sem analysis_id)
├── analysis_mentions        (Relacionamento N:N entre analyses e mentions)
└── iedi_results             (Resultados IEDI agregados)
```

## Relacionamentos

```
analyses (1) ──→ (N) bank_periods
analyses (1) ──→ (N) analysis_mentions ──→ (N) mentions  (N:N)
analyses (1) ──→ (N) iedi_results

bank_periods (N) ──→ (1) banks
iedi_results (N) ──→ (1) banks
analysis_mentions (N) ──→ (1) banks
analysis_mentions (N) ──→ (1) mentions

mentions: Dados brutos independentes (sem FK)
```

## Tipos de Dados BigQuery

| Tipo Python | Tipo BigQuery | Exemplo |
|-------------|---------------|---------|
| `int` | `INT64` | 123 |
| `str` | `STRING` | "texto" |
| `float` | `FLOAT64` | 3.14 |
| `bool` | `BOOL` | TRUE/FALSE |
| `datetime` | `TIMESTAMP` | 2025-01-01 00:00:00 UTC |
| `list[str]` | `ARRAY<STRING>` | ["item1", "item2"] |

## Media Outlets (Tabela Unificada)

A tabela `media_outlets` unifica veículos relevantes e de nicho:

- **is_niche = FALSE**: Veículos relevantes (40 outlets)
- **is_niche = TRUE**: Veículos de nicho (22 outlets)
- **monthly_visitors**: Apenas para niche (NULL para relevant)

## Observações

- Todas as tabelas usam `INT64` para IDs (auto-increment gerenciado pela aplicação)
- Timestamps são armazenados em UTC
- Arrays são nativos do BigQuery (`ARRAY<STRING>`)
- Schema `iedi` está configurado para região `us`

## Limpeza

Para remover todas as tabelas e o schema:

```sql
DROP SCHEMA iedi CASCADE;
```

⚠️ **ATENÇÃO**: Este comando remove TODOS os dados permanentemente!
