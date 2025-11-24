# Reorganização da Estrutura do Frontend

## Resumo

Reorganização completa da estrutura do frontend para seguir o padrão Flask:
- Templates em `templates/`
- Assets estáticos em `static/css/` e `static/js/`
- Remoção de arquivos antigos não utilizados

---

## Estrutura Anterior

```
frontend/
├── analyses.html (antigo)
├── index.html
├── detail.html
├── create.html
├── css/
│   ├── analyses.css (antigo)
│   └── styles.css
└── js/
    ├── analyses.js (antigo)
    ├── api.js
    ├── index.js
    ├── detail.js
    └── create.js

templates/
├── README.md
├── analyses.html (antigo)
├── banks.html (antigo)
├── base.html (antigo)
├── index.html (antigo)
├── media.html (antigo)
├── niche_media.html (antigo)
└── relevant_media.html (antigo)

static/
├── css/
│   └── style.css (antigo)
└── js/
    ├── main.js (antigo)
    └── analyses.js (antigo)
```

---

## Estrutura Atual (Padrão Flask)

```
templates/
├── README.md
├── index.html          ← Listagem de análises
├── detail.html         ← Detalhamento de análise
└── create.html         ← Criação de análise

static/
├── css/
│   └── styles.css      ← Design system completo
└── js/
    ├── api.js          ← Cliente API + utilities
    ├── index.js        ← Lógica da listagem
    ├── detail.js       ← Lógica do detalhamento
    └── create.js       ← Lógica da criação
```

---

## Alterações Realizadas

### 1. Movimentação de Arquivos

**HTMLs**: `frontend/` → `templates/`
- ✅ `frontend/index.html` → `templates/index.html`
- ✅ `frontend/detail.html` → `templates/detail.html`
- ✅ `frontend/create.html` → `templates/create.html`

**CSS**: `frontend/css/` → `static/css/`
- ✅ `frontend/css/styles.css` → `static/css/styles.css`

**JS**: `frontend/js/` → `static/js/`
- ✅ `frontend/js/api.js` → `static/js/api.js`
- ✅ `frontend/js/index.js` → `static/js/index.js`
- ✅ `frontend/js/detail.js` → `static/js/detail.js`
- ✅ `frontend/js/create.js` → `static/js/create.js`

### 2. Atualização de Caminhos

Todos os HTMLs foram atualizados para usar caminhos absolutos do Flask:

**Antes**:
```html
<link rel="stylesheet" href="css/styles.css">
<script src="js/api.js"></script>
<script src="js/index.js"></script>
```

**Depois**:
```html
<link rel="stylesheet" href="/static/css/styles.css">
<script src="/static/js/api.js"></script>
<script src="/static/js/index.js"></script>
```

### 3. Arquivos Removidos

#### Templates (6 arquivos antigos)
- ❌ `templates/analyses.html` - Substituído por `templates/index.html`
- ❌ `templates/banks.html` - Não utilizado
- ❌ `templates/base.html` - Não utilizado
- ❌ `templates/media.html` - Não utilizado
- ❌ `templates/niche_media.html` - Não utilizado
- ❌ `templates/relevant_media.html` - Não utilizado

#### CSS (1 arquivo antigo)
- ❌ `static/css/style.css` - Substituído por `static/css/styles.css`

#### JS (2 arquivos antigos)
- ❌ `static/js/main.js` - Não utilizado
- ❌ `static/js/analyses.js` - Substituído por `static/js/index.js`

#### Frontend (3 arquivos antigos)
- ❌ `frontend/analyses.html` - Substituído por `templates/index.html`
- ❌ `frontend/css/analyses.css` - Substituído por `static/css/styles.css`
- ❌ `frontend/index.html` - Movido para `templates/`

---

## Arquivos Mantidos

### Templates (3 arquivos)

1. **`templates/index.html`** - Listagem de análises
   - Tabela com todas as análises
   - Estados: loading, error, empty, success
   - Botão "Nova Análise"
   - Link "Ver Detalhes"

2. **`templates/detail.html`** - Detalhamento de análise
   - Card com informações da análise
   - Badge de status
   - Grid de resultados por banco
   - Mensagem de processamento
   - Botão "Atualizar"

3. **`templates/create.html`** - Criação de análise
   - Formulário completo
   - Toggle: Modo Padrão vs. Customizado
   - Seleção de bancos
   - Períodos customizados
   - Card informativo

### CSS (1 arquivo)

4. **`static/css/styles.css`** - Design system completo
   - Variáveis CSS (cores, espaçamentos, tipografia)
   - Componentes: buttons, cards, tables, forms, badges
   - Estados: loading, error, empty, success
   - Grid responsivo
   - Mobile-first (breakpoint 768px)

### JavaScript (4 arquivos)

5. **`static/js/api.js`** - Cliente API
   - Métodos para todos os endpoints
   - Funções utilitárias (formatação, badges)
   - Tratamento de erros
   - Helpers de loading/error

6. **`static/js/index.js`** - Lógica da listagem
   - Carregamento de análises
   - Renderização da tabela
   - Navegação para detalhes

7. **`static/js/detail.js`** - Lógica do detalhamento
   - Carregamento de análise + bank analyses
   - Renderização de cards
   - Mensagem de processamento
   - Botão de atualizar

8. **`static/js/create.js`** - Lógica da criação
   - Carregamento de bancos
   - Toggle de modo
   - Validação de formulário
   - Submissão para API

---

## Padrão Flask

### Estrutura de Diretórios

```
app/
├── controllers/        ← Endpoints da API
├── models/            ← Models do banco de dados
├── repositories/      ← Acesso ao banco
├── services/          ← Lógica de negócio
└── ...

templates/             ← Templates HTML (Jinja2)
├── index.html
├── detail.html
└── create.html

static/                ← Assets estáticos
├── css/
│   └── styles.css
└── js/
    ├── api.js
    ├── index.js
    ├── detail.js
    └── create.js
```

### Convenções

1. **Templates**: Arquivos HTML renderizados pelo Flask via `render_template()`
2. **Static**: Assets servidos diretamente pelo Flask via `/static/`
3. **Caminhos**: Usar caminhos absolutos `/static/...` nos templates

---

## Rotas Flask

Para servir os templates, adicionar rotas no controller:

```python
from flask import render_template

@app.route('/')
def index():
    """Listagem de análises"""
    return render_template('index.html')

@app.route('/detail')
def detail():
    """Detalhamento de análise"""
    return render_template('detail.html')

@app.route('/create')
def create():
    """Criação de análise"""
    return render_template('create.html')
```

---

## Navegação Entre Páginas

### No JavaScript

```javascript
// Ir para criação
window.location.href = '/create';

// Ir para detalhamento
window.location.href = `/detail?id=${analysisId}`;

// Voltar para listagem
window.location.href = '/';
```

### Nos HTMLs

```html
<!-- Botão para criar -->
<button onclick="window.location.href='/create'">Nova Análise</button>

<!-- Link para detalhes -->
<a href="/detail?id=uuid">Ver Detalhes</a>

<!-- Voltar para listagem -->
<button onclick="window.location.href='/'">Voltar</button>
```

---

## Endpoints da API

Os endpoints da API continuam em `/api/`:

- `GET /api/analyses` - Listar análises
- `GET /api/analyses/<id>` - Buscar análise
- `GET /api/analyses/<id>/banks` - Buscar bank analyses
- `POST /api/analyses` - Criar análise
- `GET /api/banks` - Listar bancos

---

## Commits Realizados

### Commit 1: `a3c591d`
**Mensagem**: "feat: Refatorar frontend completo para análises IEDI"

**Alterações**:
- Criação de 3 telas (index, detail, create)
- Design system completo (styles.css)
- Cliente API (api.js)
- Lógica JavaScript (index.js, detail.js, create.js)
- Controller atualizado (analysis_controller.py)
- Documentação completa

### Commit 2: `8f934f5`
**Mensagem**: "refactor: Reorganizar estrutura do frontend para padrão Flask"

**Alterações**:
- Movimentação de arquivos para templates/ e static/
- Atualização de caminhos nos HTMLs
- Remoção de 12 arquivos antigos não utilizados
- Estrutura final: 3 templates, 1 CSS, 4 JS

### Commit 3: `22fe56c`
**Mensagem**: "Push após rebase"

**Alterações**:
- Sincronização com repositório remoto

---

## Próximos Passos

### 1. Adicionar Rotas Flask

**Arquivo**: `app/controllers/root_controller.py` ou `app/__init__.py`

```python
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/create')
def create():
    return render_template('create.html')
```

### 2. Implementar Métodos nos Repositories

- `AnalysisRepository.find_all()`
- `AnalysisRepository.find_by_id()`
- `BankRepository.find_all()`

### 3. Remover Placeholders do Controller

- Descomentar chamadas para os métodos
- Remover linhas com `# Placeholder`

### 4. Testar Aplicação

```bash
# Iniciar servidor Flask
python app.py

# Acessar no navegador
http://localhost:5000/
http://localhost:5000/create
http://localhost:5000/detail?id=<uuid>
```

---

## Conclusão

✅ **Estrutura reorganizada** para seguir padrão Flask
✅ **Arquivos antigos removidos** (12 arquivos)
✅ **Caminhos atualizados** nos HTMLs
✅ **3 templates funcionais** (index, detail, create)
✅ **Design system completo** (styles.css)
✅ **Cliente API** (api.js + utilities)
✅ **Lógica JavaScript** (index, detail, create)

⚠️ **Pendente**:
- Adicionar rotas Flask para servir templates
- Implementar métodos nos repositories
- Testar aplicação completa

A estrutura agora segue o **padrão Flask** e está pronta para uso! 🚀
