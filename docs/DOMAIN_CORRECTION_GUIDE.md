# Guia de Correção de Domains - Media Outlets

## Problema Identificado

Durante análise dos dados de mentions da Brandwatch, identificamos que **91.9% das mentions** não estavam sendo reconhecidas como veículos relevantes/nicho devido a **inconsistência entre domains cadastrados e domains retornados pela API**.

### Causa Raiz

A Brandwatch retorna **domains raiz** (ex: `globo.com`) enquanto tínhamos cadastrado **subdomínios específicos** (ex: `g1.globo.com`, `valor.globo.com`).

### Impacto

| Métrica | Valor | Percentual |
|---------|-------|------------|
| **Total de mentions** | 16.942 | 100% |
| **Mentions reconhecidas** | 1.372 | 8.1% |
| **Mentions NÃO reconhecidas** | 15.570 | **91.9%** |

**Resultado**: Scores IEDI artificialmente **baixos** devido à falta de pontos de veículo relevante/nicho.

---

## Solução Implementada

### 1. SQL de Correção

**Arquivo**: `sql/11_fix_media_outlets_domains.sql`

**Ação**: Atualizar 18 domains de subdomínios para domains raiz.

**Domains Corrigidos**:

| Subdomínio Cadastrado | Domain Raiz Correto | Mentions Afetadas |
|-----------------------|---------------------|-------------------|
| `g1.globo.com` | `globo.com` | 334 |
| `valor.globo.com` | `globo.com` | 334 |
| `valorinveste.globo.com` | `globo.com` | 334 |
| `oglobo.globo.com` | `globo.com` | 334 |
| `epocanegocios.globo.com` | `globo.com` | 334 |
| `g1.globo.com/globonews` | `globo.com` | 334 |
| `g1.globo.com/economia/agronegocios/globo-rural` | `globo.com` | 334 |
| `folha.uol.com.br` | `uol.com.br` | 238 |
| `economia.uol.com.br` | `uol.com.br` | 238 |
| `band.uol.com.br` | `uol.com.br` | 238 |
| `einvestidor.estadao.com.br` | `estadao.com.br` | 124 |
| `pme.estadao.com.br` | `estadao.com.br` | 124 |
| `pro.infomoney.com.br` | `infomoney.com.br` | 178 |
| `veja.abril.com.br` | `abril.com.br` | 27 |
| `vocesa.abril.com.br` | `abril.com.br` | 27 |
| `vocerh.abril.com.br` | `abril.com.br` | 27 |
| `agenciabrasil.ebc.com.br` | `ebc.com.br` | 23 |
| `exame.com/pme` | `exame.com` | 44 |

**Total de mentions afetadas**: 3.626 (21.4% do total)

**Impacto por domain raiz**:

| Domain Raiz | Mentions | Percentual |
|-------------|----------|------------|
| `globo.com` | 2.338 | 13.8% |
| `uol.com.br` | 714 | 4.2% |
| `estadao.com.br` | 248 | 1.5% |
| `infomoney.com.br` | 178 | 1.1% |
| `abril.com.br` | 81 | 0.5% |
| `exame.com` | 44 | 0.3% |
| `ebc.com.br` | 23 | 0.1% |

---

### 2. Endpoint de Recálculo

**Rota**: `POST /api/analyses/<analysis_id>/recalculate`

**Função**: Recalcular scores IEDI após atualização de `media_outlets`.

**Fluxo**:

1. ✅ Valida que análise está com status `COMPLETED`
2. ✅ Carrega mentions do CSV (`data/mentions_{analysis_id}.csv`)
3. ✅ Carrega `media_outlets` atualizados do BigQuery
4. ✅ Recalcula `mention_analysis` (scores individuais)
5. ✅ Recalcula `bank_analysis` (agregados por banco)
6. ✅ Salva CSVs atualizados

**Exemplo de uso**:

```bash
curl -X POST http://localhost:5000/api/analyses/b04351b4-b917-409c-bde8-f1a92c360ecd/recalculate
```

**Resposta de sucesso**:

```json
{
  "message": "Recálculo concluído com sucesso",
  "details": {
    "total_mentions": 16942,
    "mentions_recalculated": 16942,
    "banks_updated": 4,
    "relevant_domains": 41,
    "niche_domains": 22
  }
}
```

---

## Passo a Passo para Aplicar Correção

### 1. Executar SQL no BigQuery

```bash
# Conectar ao BigQuery
bq query --use_legacy_sql=false < sql/11_fix_media_outlets_domains.sql
```

**Ou via Console BigQuery**:

1. Acessar [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Copiar conteúdo de `sql/11_fix_media_outlets_domains.sql`
3. Executar query
4. Verificar resultado da query de validação final

### 2. Recalcular Análise

**Via API**:

```bash
curl -X POST http://localhost:5000/api/analyses/b04351b4-b917-409c-bde8-f1a92c360ecd/recalculate
```

**Via Frontend** (futuro):

1. Acessar detalhes da análise
2. Clicar em "Recalcular Scores"
3. Aguardar confirmação

### 3. Validar Resultados

**Verificar CSVs atualizados**:

```bash
# Comparar antes e depois
head -20 data/mention_analysis_b04351b4-b917-409c-bde8-f1a92c360ecd.csv
head -20 data/bank_analysis_b04351b4-b917-409c-bde8-f1a92c360ecd.csv
```

**Verificar scores IEDI**:

- ✅ Scores devem estar **mais altos** após correção
- ✅ Mentions de `globo.com`, `uol.com.br`, etc. devem ter pontos de veículo relevante
- ✅ Agregados de `bank_analysis` devem refletir novos scores

---

## Verificação de Qualidade

### Antes da Correção

```
Mentions reconhecidas: 1.372 (8.1%)
Mentions NÃO reconhecidas: 15.570 (91.9%)
```

### Após Correção (Esperado)

```
Mentions reconhecidas: 5.000+ (30%+)
Mentions NÃO reconhecidas: 12.000- (70%-)
```

**Nota**: Ainda haverá mentions não reconhecidas (domains regionais, blogs, etc.), mas o impacto será **significativamente reduzido**.

---

## Manutenção Futura

### Ao Adicionar Novos Media Outlets

1. ✅ **Sempre usar domain raiz** (ex: `globo.com` ao invés de `g1.globo.com`)
2. ✅ Verificar domain real retornado pela Brandwatch antes de cadastrar
3. ✅ Testar matching com mentions reais

### Monitoramento

**Query para identificar domains não cadastrados**:

```sql
SELECT
  domain,
  COUNT(*) as mention_count
FROM iedi.mentions
WHERE domain NOT IN (
  SELECT domain FROM iedi.media_outlets
)
GROUP BY domain
ORDER BY mention_count DESC
LIMIT 50;
```

**Executar mensalmente** para identificar novos domains relevantes.

---

## Arquivos Relacionados

- `sql/11_fix_media_outlets_domains.sql` - SQL de correção
- `app/controllers/analysis_controller.py` - Endpoint de recálculo
- `docs/DOMAIN_CORRECTION_GUIDE.md` - Este guia
- `data/mentions_{analysis_id}.csv` - Mentions originais
- `data/mention_analysis_{analysis_id}.csv` - Scores recalculados
- `data/bank_analysis_{analysis_id}.csv` - Agregados recalculados

---

## Contato

Para dúvidas ou problemas, consultar:

- Documentação técnica: `docs/`
- Repositório: https://github.com/gskumlehn/iedi_system
- Logs de recálculo: Console do servidor Flask

---

**Data de criação**: 2025-11-26  
**Última atualização**: 2025-11-26  
**Versão**: 1.0
