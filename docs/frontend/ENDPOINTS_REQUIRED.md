# Endpoints Necessários para Frontend de Análises

## Resumo

Este documento lista todos os endpoints necessários para o frontend de análises IEDI.

---

## Endpoints

### 1. Listar Análises

**Endpoint**: `GET /api/analyses`

**Descrição**: Retorna lista de todas as análises criadas

**Response**:
```json
{
  "analyses": [
    {
      "id": "uuid",
      "name": "Análise Outubro 2024",
      "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
      "status": "COMPLETED",
      "is_custom_dates": false,
      "created_at": "2024-10-01T00:00:00Z"
    }
  ]
}
```

**Repository Method Needed**:
```python
@staticmethod
def find_all():
    """Busca todas as análises ordenadas por data de criação (mais recente primeiro)"""
    with get_session() as session:
        return session.query(Analysis).order_by(Analysis.created_at.desc()).all()
```

---

### 2. Buscar Análise por ID

**Endpoint**: `GET /api/analyses/<analysis_id>`

**Descrição**: Retorna detalhes de uma análise específica

**Response**:
```json
{
  "analysis": {
    "id": "uuid",
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "status": "COMPLETED",
    "is_custom_dates": false,
    "created_at": "2024-10-01T00:00:00Z"
  }
}
```

**Repository Method Needed**:
```python
@staticmethod
def find_by_id(analysis_id: str):
    """Busca análise por ID"""
    with get_session() as session:
        return session.query(Analysis).filter(Analysis.id == analysis_id).first()
```

---

### 3. Buscar BankAnalysis de uma Análise

**Endpoint**: `GET /api/analyses/<analysis_id>/banks`

**Descrição**: Retorna todos os BankAnalysis de uma análise

**Response**:
```json
{
  "bank_analyses": [
    {
      "id": "uuid",
      "analysis_id": "uuid",
      "bank_name": "BANCO_DO_BRASIL",
      "start_date": "2024-10-01T00:00:00Z",
      "end_date": "2024-10-31T23:59:59Z",
      "total_mentions": 150,
      "positive_volume": 120.0,
      "negative_volume": 30.0,
      "iedi_mean": 7.5,
      "iedi_score": 6.8
    }
  ]
}
```

**Repository Method**: Já existe `BankAnalysisRepository.find_by_analysis_id()`

---

### 4. Criar Análise

**Endpoint**: `POST /api/analyses`

**Descrição**: Cria nova análise

**Request Body** (Modo Padrão):
```json
{
  "name": "Análise Outubro 2024",
  "query": "OPERAÇÃO BB :: MONITORAMENTO",
  "bank_names": ["Banco do Brasil", "Itaú"],
  "start_date": "2024-10-01T00:00:00",
  "end_date": "2024-10-31T23:59:59"
}
```

**Request Body** (Modo Customizado):
```json
{
  "name": "Análise Customizada",
  "query": "OPERAÇÃO BB :: MONITORAMENTO",
  "custom_bank_dates": [
    {
      "bank_name": "Banco do Brasil",
      "start_date": "2024-10-01T00:00:00",
      "end_date": "2024-10-31T23:59:59"
    },
    {
      "bank_name": "Itaú",
      "start_date": "2024-09-01T00:00:00",
      "end_date": "2024-09-30T23:59:59"
    }
  ]
}
```

**Response**:
```json
{
  "message": "Análise criada com sucesso.",
  "analysis": {
    "id": "uuid",
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "status": "PENDING",
    "is_custom_dates": false
  }
}
```

**Service Method**: Já existe `AnalysisService.save()`

---

### 5. Listar Bancos Disponíveis

**Endpoint**: `GET /api/banks`

**Descrição**: Retorna lista de todos os bancos cadastrados

**Response**:
```json
{
  "banks": [
    {
      "id": "uuid",
      "name": "BANCO_DO_BRASIL",
      "display_name": "Banco do Brasil",
      "variations": ["Banco do Brasil", "BB", "Banco do Brasil S.A."]
    }
  ]
}
```

**Repository Method Needed**:
```python
@staticmethod
def find_all():
    """Busca todos os bancos ativos"""
    with get_session() as session:
        return session.query(Bank).filter(Bank.active == True).all()
```

---

## Fluxo de Criação de Análise

### Passo a Passo

```
1. Usuário preenche formulário
   ├─ Nome da análise
   ├─ Query Brandwatch
   ├─ Modo: Padrão ou Customizado
   │
   ├─ Se Modo Padrão:
   │   ├─ Selecionar bancos (múltipla escolha)
   │   ├─ Data início (única para todos)
   │   └─ Data fim (única para todos)
   │
   └─ Se Modo Customizado:
       └─ Para cada banco:
           ├─ Selecionar banco
           ├─ Data início específica
           └─ Data fim específica

2. Frontend envia POST /api/analyses

3. AnalysisController.create_analysis()
   ├─ Recebe dados do request
   ├─ Chama AnalysisService.save()
   └─ Retorna response

4. AnalysisService.save()
   ├─ Valida name e query
   ├─ BankAnalysisService.validate()
   │   ├─ Valida bancos e datas
   │   └─ Retorna lista de BankAnalysis
   ├─ Cria Analysis
   ├─ AnalysisRepository.save(analysis)
   ├─ BankAnalysisService.save_all()
   │   └─ Para cada BankAnalysis:
   │       └─ BankAnalysisRepository.save()
   └─ Inicia thread assíncrona:
       └─ MentionAnalysisService.process_mention_analysis()

5. Frontend redireciona para listagem
   └─ Usuário vê análise com status "PENDING"

6. Processamento assíncrono (thread)
   ├─ Busca mentions na Brandwatch
   ├─ Filtra e salva mentions
   ├─ Calcula IEDI para cada mention
   ├─ Atualiza BankAnalysis com métricas
   └─ Atualiza status da Analysis para "COMPLETED"

7. Usuário atualiza página
   └─ Vê análise com status "COMPLETED" e métricas
```

---

## Validações no Controller

### create_analysis()

```python
# Regras de negócio (já implementadas no AnalysisService):
# 1. name é obrigatório
# 2. query é obrigatório
# 3. Deve fornecer bank_names + start_date + end_date OU custom_bank_dates (não ambos)
# 4. Datas devem estar no formato ISO 8601
# 5. start_date < end_date
# 6. end_date < data atual
# 7. bank_names devem existir no enum BankName
```

### get_analysis()

```python
# Regras de negócio:
# 1. analysis_id deve ser UUID válido
# 2. Análise deve existir (retornar 404 se não encontrada)
```

### get_bank_analyses()

```python
# Regras de negócio:
# 1. analysis_id deve ser UUID válido
# 2. Análise deve existir (retornar 404 se não encontrada)
# 3. Retornar lista vazia se não houver BankAnalysis (não erro)
```

---

## Status da Análise

| Status | Descrição |
|--------|-----------|
| `PENDING` | Análise criada, processamento não iniciado |
| `PROCESSING` | Processamento em andamento |
| `COMPLETED` | Processamento concluído com sucesso |
| `FAILED` | Processamento falhou |

**Nota**: O enum `AnalysisStatus` já existe em `app/enums/analysis_status.py`

---

## Resumo de Métodos Necessários

### AnalysisRepository

- ✅ `save()` - Já existe
- ❌ `find_all()` - **CRIAR**
- ❌ `find_by_id()` - **CRIAR**

### BankAnalysisRepository

- ✅ `save()` - Já existe
- ✅ `update()` - Já existe
- ✅ `find_by_analysis_id()` - Já existe

### BankRepository

- ✅ `find_by_name()` - Já existe
- ❌ `find_all()` - **CRIAR**

---

## Endpoints do Controller

### Existente

- ✅ `POST /api` - Criar análise (renomear para `/api/analyses`)

### A Criar

- ❌ `GET /api/analyses` - Listar análises
- ❌ `GET /api/analyses/<id>` - Buscar análise por ID
- ❌ `GET /api/analyses/<id>/banks` - Buscar BankAnalysis de uma análise
- ❌ `GET /api/banks` - Listar bancos disponíveis
