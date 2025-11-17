# SQL Migrations - Sistema IEDI

Scripts SQL para criação e população do banco de dados BigQuery.

## Estrutura

```
sql/
├── 01_create_dataset.sql              # Criar dataset 'iedi'
├── 02_create_table_banks.sql          # Tabela de bancos
├── 03_create_table_media_outlets.sql  # Tabela de veículos de mídia
├── 04_create_table_analyses.sql       # Tabela de análises
├── 05_create_table_mentions.sql       # Tabela de menções
├── 06_create_table_analysis_mentions.sql  # Relacionamento análise-menção-banco
├── 07_create_table_iedi_results.sql   # Tabela de resultados IEDI
├── 08_insert_banks.sql                # Inserir 4 bancos
├── 09_insert_media_outlets.sql        # Inserir 62 veículos de mídia
├── run_migrations.py                  # Script automatizado ⭐
└── README.md                          # Este arquivo
```

## Método Recomendado: Script Automatizado

### Pré-requisitos

1. **Service Account do Google Cloud**

Crie um service account com permissões de BigQuery:

- Acesse [Google Cloud Console](https://console.cloud.google.com)
- Navegue para **IAM & Admin** → **Service Accounts**
- Crie service account com permissões:
  * `BigQuery Admin`
  * `BigQuery Data Editor`
  * `BigQuery Job User`
- Baixe a chave JSON

2. **Variáveis de Ambiente**

```bash
export GOOGLE_CLOUD_PROJECT_ID=seu-projeto-id
export GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/service-account.json
```

3. **Dependências Python**

```bash
pip install google-cloud-bigquery
```

### Executar Migrations

```bash
python sql/run_migrations.py
```

O script irá:
1. Conectar ao BigQuery usando service account
2. Listar todos os arquivos SQL
3. Solicitar confirmação
4. Executar na ordem correta
5. Exibir resumo de execução

### Saída Esperada

```
================================================================================
MIGRATIONS BIGQUERY - Sistema IEDI
================================================================================

Conectando ao BigQuery...
✓ Conectado ao projeto: seu-projeto-id

Encontrados 9 arquivos SQL:
  - 01_create_dataset.sql
  - 02_create_table_banks.sql
  - 03_create_table_media_outlets.sql
  - 04_create_table_analyses.sql
  - 05_create_table_mentions.sql
  - 06_create_table_analysis_mentions.sql
  - 07_create_table_iedi_results.sql
  - 08_insert_banks.sql
  - 09_insert_media_outlets.sql
  ...

Pressione ENTER para continuar ou Ctrl+C para cancelar...

================================================================================
Executando: 01_create_dataset.sql
================================================================================
✓ 01_create_dataset.sql executado com sucesso

...

================================================================================
RESUMO
================================================================================
Total de arquivos: 9
Executados com sucesso: 9
Erros: 0

✓ Todas as migrations foram executadas com sucesso!
```

## Métodos Alternativos

### Opção 2: BigQuery Console (Manual)

1. Acesse [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Selecione seu projeto
3. Clique em "Compose new query"
4. Cole o conteúdo de cada arquivo SQL
5. Execute na ordem numérica

### Opção 3: bq CLI

```bash
export PROJECT_ID=seu-projeto-id

bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 01_create_dataset.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 02_create_table_banks.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 03_create_table_media_outlets.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 04_create_table_analyses.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 05_create_table_mentions.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 06_create_table_analysis_mentions.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 07_create_table_iedi_results.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 08_insert_banks.sql
bq query --project_id=$PROJECT_ID --use_legacy_sql=false < 09_insert_media_outlets.sql
```

## Ordem de Execução

**IMPORTANTE**: Execute na ordem correta para respeitar dependências:

1. **Dataset** (01) - Criar namespace `iedi`
2. **Tabelas** (02-07) - Criar estrutura
3. **Inserts** (08-09) - Popular dados iniciais

## Estrutura do Schema

```
iedi/
├── banks                    (Bancos)
├── media_outlets            (Veículos de mídia)
├── analyses                 (Análises)
├── mentions                 (Menções da Brandwatch)
├── analysis_mentions        (Relacionamento N:N)
└── iedi_results             (Resultados IEDI)
```

## Relacionamentos

```
analyses (1) ──→ (N) analysis_mentions ──→ (N) mentions  (N:N)
analyses (1) ──→ (N) iedi_results

iedi_results (N) ──→ (1) banks
analysis_mentions (N) ──→ (1) banks
analysis_mentions (N) ──→ (1) mentions

mentions: Dados brutos independentes
```

## Tipos de Dados BigQuery

| Tipo Python | Tipo BigQuery | Exemplo |
|-------------|---------------|---------|
| `str` | `STRING(tamanho)` | "texto" |
| `int` | `INT64` | 123 |
| `float` | `FLOAT64` | 3.14 |
| `bool` | `BOOL` | TRUE/FALSE |
| `datetime` | `TIMESTAMP` | 2025-01-01 00:00:00 UTC |
| `list[str]` | `ARRAY<STRING>` | ["item1", "item2"] |

## Troubleshooting

### Erro: "GOOGLE_CLOUD_PROJECT_ID não definido"

```bash
export GOOGLE_CLOUD_PROJECT_ID=seu-projeto-id
```

### Erro: "Arquivo de credenciais não encontrado"

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/caminho/completo/service-account.json
```

### Erro: "Permission denied"

Service account precisa das permissões:
- `BigQuery Admin`
- `BigQuery Data Editor`
- `BigQuery Job User`

### Erro: "Dataset already exists"

Normal se executar múltiplas vezes. Scripts usam `CREATE TABLE IF NOT EXISTS`.

## Verificar Resultados

### Via Console BigQuery

1. Acesse [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Navegue para seu projeto
3. Verifique dataset `iedi`
4. Explore as tabelas criadas

### Via Python

```python
from google.cloud import bigquery

client = bigquery.Client(project='seu-projeto-id')

# Listar tabelas
tables = client.list_tables('iedi')
for table in tables:
    print(f"- {table.table_id}")

# Contar registros
query = "SELECT COUNT(*) as total FROM iedi.banks"
result = client.query(query).result()
for row in result:
    print(f"Total de bancos: {row.total}")
```

### Via bq CLI

```bash
# Listar tabelas
bq ls iedi

# Contar registros
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM iedi.banks"
```

## Rollback

Para remover tudo e recomeçar:

```bash
# Via bq CLI
bq rm -r -f -d iedi

# Ou via Python
from google.cloud import bigquery
client = bigquery.Client(project='seu-projeto-id')
client.delete_dataset('iedi', delete_contents=True, not_found_ok=True)
```

Depois execute `python sql/run_migrations.py` novamente.

## Observações

- IDs usam UUID (STRING(36)) - BigQuery não suporta AUTO_INCREMENT
- Timestamps armazenados em UTC
- Arrays nativos do BigQuery (`ARRAY<STRING>`)
- BigQuery gerencia índices automaticamente
- Sem PRIMARY KEY ou FOREIGN KEY constraints (não suportados)
