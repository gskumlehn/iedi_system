# Validação do Teste End-to-End - Análise IEDI

## Resumo

Este documento valida o teste `test_outubro_bb_real_flow.py` que segue o **fluxo real** do sistema IEDI.

---

## Diferenças entre Teste Anterior e Novo Teste

| Aspecto | Teste Anterior (Incorreto) | Novo Teste (Correto) |
|---------|----------------------------|----------------------|
| **Entry Point** | `AnalysisRepository.create()` | `AnalysisService.save()` |
| **Criação de BankAnalysis** | Manual via `BankPeriodRepository.create()` | Automático via `BankAnalysisService` |
| **Nome da Entidade** | `BankPeriod` | `BankAnalysis` |
| **Processamento** | Manual via `IEDIOrchestrator.process_analysis()` | Automático via thread assíncrona |
| **Detecção de Banco** | Mock de `BankDetectionService` | Real via `mention.categories` |
| **Cálculo IEDI** | Via `IEDICalculationService` | Via `MentionAnalysisService` |
| **Aguardar Resultado** | Síncrono (retorno imediato) | Assíncrono (aguardar thread) |

---

## Fluxo do Novo Teste

### 1. Validações Iniciais

```python
# Variáveis de ambiente
BW_PROJECT, BW_EMAIL, BW_PASSWORD

# Banco no banco de dados
BankRepository.find_by_name(BankName.BANCO_DO_BRASIL)
```

### 2. Criação da Análise

```python
analysis = AnalysisService().save(
    name="Análise Outubro 2024 - Banco do Brasil",
    query="OPERAÇÃO BB :: MONITORAMENTO",
    bank_names=["Banco do Brasil"],
    start_date="2024-10-01T00:00:00",
    end_date="2024-10-31T23:59:59"
)
```

**O que acontece internamente**:
1. `AnalysisService.save()` valida name e query
2. `BankAnalysisService.validate()` valida bancos e datas
3. Cria objeto `Analysis` e salva no banco
4. Para cada banco em `bank_names`:
   - Cria `BankAnalysis` com `analysis_id`, `bank_name`, `start_date`, `end_date`
   - Salva no banco via `BankAnalysisRepository.save()`
5. Inicia thread assíncrona:
   ```python
   threading.Thread(
       target=self.mention_analysis_service.process_mention_analysis,
       args=(analysis, validated_bank_analyses)
   ).start()
   ```

### 3. Processamento Assíncrono (Thread)

**Executado em paralelo**:

```
MentionAnalysisService.process_mention_analysis()
  ↓
  Se is_custom_dates=False (nosso caso):
    process_standard_dates()
      ↓
      1. Buscar mentions UMA VEZ:
         MentionService.fetch_and_filter_mentions()
           ↓
           BrandwatchService.fetch()
             ↓
             BrandwatchClient.queries.get_mentions()
               ↓
               Retorna lista de dicts
           ↓
           Filtrar contentSource == "News"
           ↓
           Para cada mention_data:
             - Extrair categories de categoryDetails
             - Salvar/atualizar Mention no banco
           ↓
           Retornar lista de objetos Mention
      
      2. Para cada BankAnalysis:
         process_mentions(mentions, bank_name)
           ↓
           Buscar objeto Bank
           ↓
           Para cada Mention:
             - Verificar se bank in mention.categories
             - Se válida:
               * create_mention_analysis(mention, bank)
                 - Classificar reach_group
                 - Verificar title_mentioned
                 - Verificar subtitle_mentioned
                 - Classificar veículos
                 - Calcular numerador
                 - Calcular denominador
                 - Calcular iedi_score e iedi_normalized
               * Adicionar à lista
           ↓
           MentionAnalysisRepository.bulk_save(mention_analyses)
           ↓
           Retornar lista de MentionAnalysis
         
         compute_and_persist_bank_metrics(bank_analysis, mention_analyses)
           ↓
           Contar positive/negative
           ↓
           Calcular iedi_mean (média de iedi_normalized)
           ↓
           Calcular iedi_final (iedi_mean × positivity_ratio)
           ↓
           Atualizar BankAnalysis:
             - total_mentions
             - positive_volume
             - negative_volume
             - iedi_mean
             - iedi_score
           ↓
           BankAnalysisRepository.update(bank_analysis)
```

### 4. Aguardar Processamento

```python
def wait_for_processing(analysis_id, max_wait=300, check_interval=5):
    while elapsed < max_wait:
        bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis_id)
        
        if bank_analyses:
            has_metrics = any(ba.total_mentions > 0 for ba in bank_analyses)
            if has_metrics:
                return True
        
        time.sleep(check_interval)
        elapsed += check_interval
    
    return False
```

**Lógica**:
- Verifica a cada 5 segundos se `BankAnalysis` tem `total_mentions > 0`
- Timeout de 5 minutos (300s)
- Se timeout, processamento falhou ou ainda está em andamento

### 5. Verificar Resultados

```python
bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis.id)

for ba in bank_analyses:
    print(f"Banco: {ba.bank_name.value}")
    print(f"Total: {ba.total_mentions}")
    print(f"Positivas: {ba.positive_volume}")
    print(f"Negativas: {ba.negative_volume}")
    print(f"IEDI Médio: {ba.iedi_mean}")
    print(f"IEDI Final: {ba.iedi_score}")
```

---

## Métodos Adicionados aos Repositories

### BankAnalysisRepository

```python
@staticmethod
def find_by_analysis_id(analysis_id: str):
    """Busca todos os BankAnalysis de uma análise"""
    with get_session() as session:
        return session.query(BankAnalysis).filter(
            BankAnalysis.analysis_id == analysis_id
        ).all()
```

### MentionAnalysisRepository

```python
@staticmethod
def find_by_bank_name(bank_name):
    """Busca todos os MentionAnalysis de um banco"""
    with get_session() as session:
        return session.query(MentionAnalysis).filter(
            MentionAnalysis.bank_name == bank_name.name
        ).all()
```

---

## Pré-requisitos para o Teste Funcionar

### 1. Variáveis de Ambiente

```bash
BW_PROJECT=<project_id>
BW_EMAIL=<username>
BW_PASSWORD=<password>
```

### 2. Banco no Banco de Dados

```sql
-- Executar sql/09_insert_banks.sql
INSERT INTO iedi.bank (id, name, variations) VALUES
  ('uuid-bb', 'BANCO_DO_BRASIL', '["Banco do Brasil", "BB", "Banco do Brasil S.A."]');
```

### 3. Media Outlets Cadastrados

```sql
-- Executar sql/10_insert_media_outlets.sql
-- Precisa ter veículos relevantes e de nicho cadastrados
```

### 4. Categorias na Brandwatch

**CRÍTICO**: Mentions precisam ter `categoryDetails` com o nome do banco.

Exemplo de mention válida:
```json
{
  "id": "123456789",
  "title": "Banco do Brasil anuncia lucro recorde",
  "categoryDetails": [
    {"name": "Banco do Brasil"},
    {"name": "Notícias"}
  ],
  "contentSource": "News",
  "sentiment": "positive",
  ...
}
```

**Se a mention não tiver a categoria "Banco do Brasil", ela será IGNORADA** pelo método `is_valid_for_bank()`:

```python
def is_valid_for_bank(self, mention, bank):
    categories = mention.categories  # Lista de objetos Bank
    return (categories is not None) and (bank in categories)
```

---

## Possíveis Problemas e Soluções

### Problema 1: Timeout no Processamento

**Sintoma**: `wait_for_processing()` retorna `False` após 5 minutos

**Causas Possíveis**:
1. Erro na conexão com Brandwatch
2. Query não encontrada
3. Nenhuma mention com categoria do banco
4. Erro no processamento (exception na thread)

**Solução**:
- Verificar logs da aplicação
- Testar conexão Brandwatch manualmente
- Verificar se query existe e tem mentions
- Verificar se mentions têm `categoryDetails` correto

### Problema 2: BankAnalysis Criado mas sem Métricas

**Sintoma**: `BankAnalysis.total_mentions == 0`

**Causas Possíveis**:
1. Mentions não têm categoria do banco
2. Filtro `contentSource == "News"` eliminou todas
3. Período sem mentions

**Solução**:
- Verificar `categoryDetails` das mentions na Brandwatch
- Verificar se há mentions no período
- Testar busca de mentions manualmente

### Problema 3: IEDI Calculado Incorretamente

**Sintoma**: Valores de IEDI não fazem sentido

**Causas Possíveis**:
1. Media outlets não cadastrados
2. Variações do banco incorretas
3. Erro na fórmula de cálculo

**Solução**:
- Verificar se domínios estão em `media_outlets`
- Verificar variações do banco em `banks`
- Validar cálculo manualmente para uma mention

---

## Validação Manual do Cálculo IEDI

Para validar se o cálculo está correto, escolha uma mention e calcule manualmente:

### Exemplo de Mention

```
Título: "Banco do Brasil anuncia lucro recorde"
Domínio: g1.globo.com
Monthly Visitors: 50.000.000
Sentiment: positive
Snippet: "O Banco do Brasil anunciou..."
Full Text: "O Banco do Brasil anunciou lucro recorde..."
```

### Cálculo Manual

1. **Reach Group**: 50M > 10M → **A**
2. **Title Mentioned**: "Banco do Brasil" in título → **True**
3. **Subtitle Used**: snippet == full_text → **False**
4. **Subtitle Mentioned**: N/A (subtitle não usado)
5. **Relevant Vehicle**: g1.globo.com in relevant_domains → **True**
6. **Niche Vehicle**: g1.globo.com in niche_domains → **False**

**Numerador**:
```
title_pts = 95 (title_mentioned)
subtitle_pts = 0 (subtitle não usado)
reach_weight = 100 (grupo A)
relevant_pts = 95 (relevant_vehicle)
niche_pts = 0 (não é niche)

numerator = 95 + 0 + 100 + 95 + 0 = 290
```

**Denominador** (subtitle não usado + reach_group A):
```
denominator = 95 (title) + 100 (reach A) + 95 (relevant) = 290
```

**IEDI Score**:
```
sign = +1 (positive)
iedi_score = (290 / 290) × 1 = 1.0
iedi_normalized = ((1.0 + 1) / 2) × 10 = 10.0
```

**Resultado Esperado**: `iedi_normalized = 10.0` (máximo)

---

## Checklist de Validação

Antes de executar o teste:

- [ ] Variáveis de ambiente configuradas (BW_PROJECT, BW_EMAIL, BW_PASSWORD)
- [ ] Banco "Banco do Brasil" cadastrado no banco de dados
- [ ] Media outlets cadastrados (relevantes e de nicho)
- [ ] Mentions na Brandwatch têm `categoryDetails` com "Banco do Brasil"
- [ ] Query "OPERAÇÃO BB :: MONITORAMENTO" existe na Brandwatch
- [ ] Período 2024-10-01 a 2024-10-31 tem mentions

Após executar o teste:

- [ ] Analysis criada com sucesso
- [ ] BankAnalysis criado com `analysis_id` correto
- [ ] Processamento assíncrono concluído (total_mentions > 0)
- [ ] Métricas calculadas (iedi_mean, iedi_score)
- [ ] MentionAnalysis criados para mentions válidas
- [ ] Resultados salvos em arquivo JSON

---

## Conclusão

O novo teste segue **exatamente** o fluxo real do sistema:

1. ✅ Usa `AnalysisService.save()` como entry point
2. ✅ Cria `BankAnalysis` automaticamente
3. ✅ Processa mentions em thread assíncrona
4. ✅ Detecta banco via `mention.categories`
5. ✅ Calcula IEDI via `MentionAnalysisService`
6. ✅ Aguarda processamento assíncrono
7. ✅ Valida resultados finais

Este é o **teste correto** para validar o sistema IEDI.
