# Correção do BrandwatchService

## Problema Identificado

O `BrandwatchService` estava tentando importar uma classe `Client` que não existe na biblioteca `bcr-api`. A classe correta é `BWProject`.

## Erro Original

```python
from bcr_api import Client  # ❌ INCORRETO - classe não existe
```

**Mensagem de erro:**
```
ImportError: cannot import name 'Client' from 'bcr_api'
```

## Correção Aplicada

### 1. Import Correto

```python
from bcr_api.bwproject import BWProject  # ✅ CORRETO
```

### 2. Inicialização Correta

**Antes:**
```python
self._client = Client(
    username=self.username,
    password=self.password,
    project=int(self.project_id)
)
```

**Depois:**
```python
self._client = BWProject(
    project=int(self.project_id),  # primeiro parâmetro obrigatório
    username=self.username,
    password=self.password
)
```

### 3. Validação de Credenciais

Adicionada validação para fornecer mensagens de erro claras:

```python
if not self.username:
    raise ValueError("BRANDWATCH_USERNAME não configurado no .env")
if not self.password:
    raise ValueError("BRANDWATCH_PASSWORD não configurado no .env")
if not self.project_id:
    raise ValueError("BRANDWATCH_PROJECT_ID não configurado no .env")
```

## Assinatura do BWProject

Segundo a documentação da biblioteca `bcr-api`:

```python
BWProject.__init__(
    self,
    project,                    # obrigatório: ID numérico do projeto
    token=None,                 # opcional: token de autenticação
    token_path='tokens.txt',    # opcional: caminho para arquivo de tokens
    username=None,              # opcional: usuário para autenticação
    password=None,              # opcional: senha para autenticação
    grant_type='api-password',  # opcional: tipo de autenticação
    client_id='brandwatch-api-client',
    client_secret=None,
    apiurl='https://api.brandwatch.com/'
)
```

## Testes Realizados

### 1. Teste de Import
✅ **PASSOU**: `from bcr_api.bwproject import BWProject` funciona corretamente

### 2. Teste de Conexão
✅ **PASSOU**: Validação de credenciais funciona corretamente
⚠️ **BLOQUEADO**: Conexão real requer credenciais válidas no `.env`

## Arquivos Modificados

1. **`app/services/brandwatch_service.py`**
   - Corrigido import de `Client` para `BWProject`
   - Corrigida inicialização com parâmetros corretos
   - Adicionada validação de credenciais

2. **`tests/test_brandwatch_connection.py`** (novo)
   - Teste de conexão com Brandwatch API
   - Validação de configuração de credenciais

3. **`.venv/`** (novo)
   - Ambiente virtual Python 3.11 criado
   - Todas as dependências instaladas via `requirements.txt`

## Próximos Passos

### 1. Configurar Credenciais Reais

Editar arquivo `.env` com credenciais válidas:

```env
BRANDWATCH_USERNAME=seu_email@exemplo.com
BRANDWATCH_PASSWORD=sua_senha_real
BRANDWATCH_PROJECT_ID=12345
```

### 2. Testar Conexão Real

```bash
cd /home/ubuntu/iedi_system
source .venv/bin/activate
python tests/test_brandwatch_connection.py
```

### 3. Investigar API do BWProject

Precisamos entender:
- Como listar queries disponíveis no projeto
- Como extrair mentions de uma query específica
- Quais campos estão disponíveis nas mentions retornadas
- Como filtrar por data

### 4. Implementar Método `extract_mentions`

Atualmente o método usa:
```python
mentions = client.get_mentions(
    query_name=query_name,
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d'),
    page_size=5000
)
```

**Precisamos verificar:**
- Se `get_mentions` é o método correto
- Se os parâmetros estão corretos
- Se existe paginação automática ou manual
- Qual é o formato dos dados retornados

### 5. Criar Teste End-to-End

Após configurar credenciais, executar:
```bash
python tests/test_outubro_bb.py
```

Este teste deve:
1. Conectar ao Brandwatch
2. Extrair mentions de outubro/2024
3. Detectar banco (Banco do Brasil)
4. Calcular IEDI
5. Salvar no BigQuery

## Referências

- **Repositório bcr-api**: https://github.com/BrandwatchLtd/bcr-api
- **Notebook de exemplos**: https://github.com/BrandwatchLtd/bcr-api/blob/master/DEMO.ipynb
- **Documentação Brandwatch API**: https://developers.brandwatch.com/

## Status

✅ **Import corrigido**
✅ **Validação de credenciais implementada**
✅ **Ambiente virtual configurado**
⏳ **Aguardando credenciais reais para testes**
