# Revisão Completa do Fluxo do Frontend

## Resumo

Revisão completa do fluxo do frontend para garantir que:
1. ✅ Bancos sejam carregados da API corretamente
2. ✅ Dados sejam submetidos no formato esperado pelo `AnalysisService.save()`
3. ✅ Enum names sejam usados ao invés de display names
4. ✅ Redirecionamentos usem rotas Flask (`/`, `/create`, `/detail`)

---

## Fluxo de Criação de Análise

### 1. Entry Point: `AnalysisService.save()`

**Arquivo**: `app/services/analysis_service.py`

**Assinatura**:
```python
def save(self, name=None, query=None, bank_names=None, start_date=None, end_date=None, custom_bank_dates=None):
```

**Parâmetros**:
- `name` (str): Nome da análise (obrigatório)
- `query` (str): Nome da query Brandwatch (obrigatório)
- **Modo Padrão**:
  - `bank_names` (list[str]): Lista de enum names (ex: `["BANCO_DO_BRASIL", "ITAU"]`)
  - `start_date` (str): Data início ISO 8601 (ex: `"2024-10-01T00:00:00"`)
  - `end_date` (str): Data fim ISO 8601 (ex: `"2024-10-31T23:59:59"`)
- **Modo Customizado**:
  - `custom_bank_dates` (list[dict]): Lista de objetos com:
    ```python
    {
        "bank_name": "BANCO_DO_BRASIL",  # Enum name
        "start_date": "2024-10-01T00:00:00",
        "end_date": "2024-10-31T23:59:59"
    }
    ```

**Validações** (em `BankAnalysisService.validate()`):
- ✅ Deve fornecer **OU** `bank_names + start_date + end_date` **OU** `custom_bank_dates`
- ✅ Não pode fornecer ambos
- ✅ Datas devem estar no formato ISO 8601
- ✅ `start_date` < `end_date`
- ✅ `end_date` < data atual
- ✅ `bank_names` devem existir no enum `BankName`

---

## Enum BankName

**Arquivo**: `app/enums/bank_name.py`

**Valores**:
```python
class BankName(Enum):
    BANCO_DO_BRASIL = "Banco do Brasil"
    BRADESCO = "Bradesco"
    ITAU = "Itaú"
    SANTANDER = "Santander"
```

**Importante**:
- **Enum name** (ex: `BANCO_DO_BRASIL`) é usado para submissão
- **Enum value** (ex: `"Banco do Brasil"`) é usado para exibição

---

## API Endpoints

### 1. GET /api/banks

**Resposta**:
```json
{
  "banks": [
    {
      "id": "uuid",
      "name": "BANCO_DO_BRASIL",        // Enum name (para submissão)
      "display_name": "Banco do Brasil", // Enum value (para exibição)
      "variations": ["BB", "Banco do Brasil S.A."]
    }
  ]
}
```

### 2. POST /api/analyses

**Request (Modo Padrão)**:
```json
{
  "name": "Análise Outubro 2024",
  "query": "OPERAÇÃO BB :: MONITORAMENTO",
  "bank_names": ["BANCO_DO_BRASIL", "ITAU"],
  "start_date": "2024-10-01T00:00:00",
  "end_date": "2024-10-31T23:59:59"
}
```

**Request (Modo Customizado)**:
```json
{
  "name": "Análise Customizada",
  "query": "OPERAÇÃO BB :: MONITORAMENTO",
  "custom_bank_dates": [
    {
      "bank_name": "BANCO_DO_BRASIL",
      "start_date": "2024-10-01T00:00:00",
      "end_date": "2024-10-31T23:59:59"
    },
    {
      "bank_name": "ITAU",
      "start_date": "2024-10-15T00:00:00",
      "end_date": "2024-11-15T23:59:59"
    }
  ]
}
```

---

## Frontend: create.js

### Correções Realizadas

#### 1. Renderização de Checkboxes

**Antes** (INCORRETO):
```javascript
checkbox.value = bank.display_name || bank.name;  // "Banco do Brasil"
```

**Depois** (CORRETO):
```javascript
checkbox.value = bank.name;  // "BANCO_DO_BRASIL"
```

#### 2. Select de Bancos Customizados

**Antes** (INCORRETO):
```javascript
<option value="${bank.display_name || bank.name}">
```

**Depois** (CORRETO):
```javascript
<option value="${bank.name}">
```

#### 3. Redirecionamento Após Criação

**Antes** (INCORRETO):
```javascript
window.location.href = 'index.html';
```

**Depois** (CORRETO):
```javascript
window.location.href = '/';
```

### Fluxo de Submissão

#### Modo Padrão

1. Usuário seleciona bancos via checkboxes
2. Usuário define data início e fim
3. JavaScript coleta:
   ```javascript
   {
     name: "Análise Outubro",
     query: "OPERAÇÃO BB",
     bank_names: ["BANCO_DO_BRASIL", "ITAU"],  // Enum names
     start_date: "2024-10-01T00:00:00",
     end_date: "2024-10-31T23:59:59"
   }
   ```
4. Submete para `/api/analyses`

#### Modo Customizado

1. Usuário clica em "Adicionar Banco"
2. Para cada banco:
   - Seleciona banco no select (enum name)
   - Define data início e fim específicas
3. JavaScript coleta:
   ```javascript
   {
     name: "Análise Customizada",
     query: "OPERAÇÃO BB",
     custom_bank_dates: [
       {
         bank_name: "BANCO_DO_BRASIL",  // Enum name
         start_date: "2024-10-01T00:00:00",
         end_date: "2024-10-31T23:59:59"
       }
     ]
   }
   ```
4. Submete para `/api/analyses`

---

## Frontend: Redirecionamentos

### Rotas Flask

| Rota | Template | Descrição |
|------|----------|-----------|
| `/` | `templates/index.html` | Listagem de análises |
| `/create` | `templates/create.html` | Criação de análise |
| `/detail?id=<uuid>` | `templates/detail.html` | Detalhamento de análise |

### Correções Realizadas

#### index.html

**Antes**:
```html
<button onclick="window.location.href='create.html'">
```

**Depois**:
```html
<button onclick="window.location.href='/create'">
```

#### create.html

**Antes**:
```html
<button onclick="window.location.href='index.html'">
```

**Depois**:
```html
<button onclick="window.location.href='/'">
```

#### detail.html

**Antes**:
```html
<button onclick="window.location.href='index.html'">
```

**Depois**:
```html
<button onclick="window.location.href='/'">
```

#### index.js

**Antes**:
```javascript
window.location.href = `detail.html?id=${analysisId}`;
```

**Depois**:
```javascript
window.location.href = `/detail?id=${analysisId}`;
```

---

## Backend: Correções Realizadas

### 1. BankRepository.find_all()

**Arquivo**: `app/repositories/bank_repository.py`

**Método Adicionado**:
```python
@staticmethod
def find_all():
    """Busca todos os bancos ativos"""
    with get_session() as session:
        banks = session.query(Bank).filter(Bank.active == True).all()
        for bank in banks:
            session.expunge(bank)
            make_transient(bank)
        return banks
```

### 2. AnalysisController - Endpoint /api/banks

**Arquivo**: `app/controllers/analysis_controller.py`

**Antes** (PLACEHOLDER):
```python
# TODO: Implementar BankRepository.find_all()
# banks = BankRepository.find_all()
banks = []  # Placeholder
```

**Depois** (IMPLEMENTADO):
```python
banks = BankRepository.find_all()
```

**Resposta Corrigida**:
```python
return jsonify({
    "banks": [
        {
            "id": b.id,
            "name": b.name.name,  # Enum name (e.g., "BANCO_DO_BRASIL")
            "display_name": b.name.value,  # Enum value (e.g., "Banco do Brasil")
            "variations": b.variations or [],
        }
        for b in banks
    ]
}), 200
```

---

## Fluxo Completo: Criação de Análise

### 1. Usuário Acessa `/create`

1. Flask renderiza `templates/create.html`
2. Browser carrega `static/js/create.js`
3. JavaScript chama `API.getBanks()`
4. API retorna lista de bancos:
   ```json
   {
     "banks": [
       {
         "id": "uuid",
         "name": "BANCO_DO_BRASIL",
         "display_name": "Banco do Brasil",
         "variations": ["BB"]
       }
     ]
   }
   ```

### 2. Renderização de Bancos

**Checkboxes (Modo Padrão)**:
```html
<input type="checkbox" value="BANCO_DO_BRASIL">
<label>Banco do Brasil</label>
```

**Select (Modo Customizado)**:
```html
<option value="BANCO_DO_BRASIL">Banco do Brasil</option>
```

### 3. Submissão

**Modo Padrão**:
1. Usuário seleciona: ☑ Banco do Brasil, ☑ Itaú
2. Usuário define: 01/10/2024 - 31/10/2024
3. JavaScript coleta:
   ```javascript
   {
     name: "Análise Outubro",
     query: "OPERAÇÃO BB",
     bank_names: ["BANCO_DO_BRASIL", "ITAU"],
     start_date: "2024-10-01T00:00:00",
     end_date: "2024-10-31T23:59:59"
   }
   ```
4. POST para `/api/analyses`

**Modo Customizado**:
1. Usuário clica "Adicionar Banco"
2. Seleciona: Banco do Brasil
3. Define: 01/10/2024 - 31/10/2024
4. Clica "Adicionar Banco" novamente
5. Seleciona: Itaú
6. Define: 15/10/2024 - 15/11/2024
7. JavaScript coleta:
   ```javascript
   {
     name: "Análise Customizada",
     query: "OPERAÇÃO BB",
     custom_bank_dates: [
       {
         bank_name: "BANCO_DO_BRASIL",
         start_date: "2024-10-01T00:00:00",
         end_date: "2024-10-31T23:59:59"
       },
       {
         bank_name: "ITAU",
         start_date: "2024-10-15T00:00:00",
         end_date: "2024-11-15T23:59:59"
       }
     ]
   }
   ```
8. POST para `/api/analyses`

### 4. Backend Processing

1. `AnalysisController.create_analysis()` recebe request
2. Chama `AnalysisService.save()`
3. `AnalysisService.validate()` valida `name` e `query`
4. `BankAnalysisService.validate()` valida bancos e datas
5. `AnalysisRepository.save()` salva `Analysis`
6. `BankAnalysisService.save_all()` salva `BankAnalysis` para cada banco
7. Thread assíncrona inicia `MentionAnalysisService.process_mention_analysis()`
8. Retorna resposta:
   ```json
   {
     "message": "Análise criada com sucesso",
     "analysis": {
       "id": "uuid",
       "name": "Análise Outubro",
       "query_name": "OPERAÇÃO BB",
       "status": "PENDING",
       "is_custom_dates": false
     }
   }
   ```

### 5. Redirecionamento

1. JavaScript recebe resposta de sucesso
2. Redireciona para `/`
3. Flask renderiza `templates/index.html`
4. Listagem mostra nova análise com status "PENDING"

---

## Validações

### Frontend (JavaScript)

- ✅ Nome da análise obrigatório
- ✅ Query Brandwatch obrigatória
- ✅ Pelo menos um banco selecionado (modo padrão)
- ✅ Pelo menos um banco adicionado (modo customizado)
- ✅ Datas de início e fim obrigatórias
- ✅ Data início < Data fim
- ✅ Data fim < Data atual

### Backend (Python)

- ✅ `name` obrigatório
- ✅ `query` obrigatório
- ✅ Deve fornecer `bank_names + start_date + end_date` OU `custom_bank_dates`
- ✅ Não pode fornecer ambos
- ✅ Datas no formato ISO 8601
- ✅ `start_date` < `end_date`
- ✅ `end_date` < data atual
- ✅ `bank_names` devem existir no enum `BankName`

---

## Arquivos Alterados

### Backend (3 arquivos)

1. **`app/repositories/bank_repository.py`**
   - ✅ Adicionado método `find_all()`

2. **`app/controllers/analysis_controller.py`**
   - ✅ Removido placeholder do endpoint `/api/banks`
   - ✅ Corrigida estrutura da resposta (enum name vs value)

### Frontend (5 arquivos)

3. **`static/js/create.js`**
   - ✅ Corrigido `checkbox.value` para usar `bank.name` (enum name)
   - ✅ Corrigido `<option value>` para usar `bank.name` (enum name)
   - ✅ Corrigido redirecionamento para `/`

4. **`static/js/index.js`**
   - ✅ Corrigido redirecionamento para `/detail?id=...`

5. **`templates/index.html`**
   - ✅ Corrigidos redirecionamentos para `/create`

6. **`templates/create.html`**
   - ✅ Corrigidos redirecionamentos para `/`

7. **`templates/detail.html`**
   - ✅ Corrigidos redirecionamentos para `/`

---

## Testes Necessários

### 1. Teste de Listagem de Bancos

```bash
curl -X GET http://localhost:5000/api/banks
```

**Resposta Esperada**:
```json
{
  "banks": [
    {
      "id": "uuid",
      "name": "BANCO_DO_BRASIL",
      "display_name": "Banco do Brasil",
      "variations": ["BB", "Banco do Brasil S.A."]
    }
  ]
}
```

### 2. Teste de Criação (Modo Padrão)

```bash
curl -X POST http://localhost:5000/api/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Análise Outubro 2024",
    "query": "OPERAÇÃO BB :: MONITORAMENTO",
    "bank_names": ["BANCO_DO_BRASIL", "ITAU"],
    "start_date": "2024-10-01T00:00:00",
    "end_date": "2024-10-31T23:59:59"
  }'
```

### 3. Teste de Criação (Modo Customizado)

```bash
curl -X POST http://localhost:5000/api/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Análise Customizada",
    "query": "OPERAÇÃO BB :: MONITORAMENTO",
    "custom_bank_dates": [
      {
        "bank_name": "BANCO_DO_BRASIL",
        "start_date": "2024-10-01T00:00:00",
        "end_date": "2024-10-31T23:59:59"
      }
    ]
  }'
```

### 4. Teste de Frontend

1. Acessar `http://localhost:5000/`
2. Clicar em "Nova Análise"
3. Verificar se bancos são carregados
4. Preencher formulário (modo padrão)
5. Submeter
6. Verificar redirecionamento para `/`
7. Verificar se análise aparece na listagem

---

## Conclusão

✅ **Fluxo completo revisado e corrigido**
✅ **Enum names usados para submissão**
✅ **Display names usados para exibição**
✅ **Redirecionamentos usando rotas Flask**
✅ **Endpoint /api/banks implementado**
✅ **Validações frontend e backend alinhadas**

O sistema está pronto para teste completo! 🚀
