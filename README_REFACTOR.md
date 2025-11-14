# Sistema IEDI - Refatoração Completa

## ✨ O que mudou

O sistema foi completamente refatorado seguindo a arquitetura do **bb-monitor**, com separação clara de responsabilidades e uso de blueprints Flask.

### Estrutura Anterior (app.py monolítico)
```
app.py (500+ linhas)
├── Rotas HTML
├── APIs REST
├── Lógica de negócio
└── Dados hardcoded
```

### Nova Estrutura (Clean Architecture)
```
iedi_system/
├── wsgi.py                    # Entry point
├── app/
│   ├── __init__.py           # Factory pattern (create_app)
│   ├── controllers/          # Blueprints (rotas)
│   │   ├── root_controller.py
│   │   ├── bank_controller.py
│   │   ├── media_controller.py
│   │   └── analysis_controller.py
│   ├── repositories/         # Acesso a dados
│   │   └── bank_repository.py
│   ├── models/               # Modelos SQLAlchemy
│   │   └── bank.py
│   └── infra/                # Infraestrutura
│       └── mysql_sa.py       # Conexão MySQL
├── templates/                # HTML (Jinja2)
├── static/                   # CSS/JS
└── sql/                      # Scripts SQL
```

---

## 🎯 Melhorias Implementadas

### 1. **Blueprints Flask**
Rotas organizadas por funcionalidade:
- `/` → Dashboard (root_controller)
- `/bancos/*` → CRUD Bancos (bank_controller)
- `/veiculos/*` → CRUD Veículos (media_controller)
- `/analises/*` → Análises IEDI (analysis_controller)

### 2. **Repository Pattern**
Acesso a dados centralizado e testável:
```python
# Antes
db.get_bancos()

# Depois
BankRepository.list_all()
```

### 3. **SQLAlchemy + MySQL**
- Models com tipagem forte
- Migrations automáticas
- Connection pooling
- Context managers

### 4. **Gunicorn + ProxyFix**
- Pronto para produção com nginx
- Workers e threads configuráveis
- Proxy headers corretos

### 5. **Dados no Banco**
- ❌ Removido dados hardcoded
- ✅ Scripts SQL em `/sql/`
- ✅ Inserts para bancos e veículos

---

## 🚀 Como Rodar

### 1. Configurar Banco de Dados

Execute os scripts SQL na ordem:
```bash
mysql -u root -p iedi < sql/01_create_database.sql
mysql -u root -p iedi < sql/02_create_banks_table.sql
# ... (todos os scripts)
```

### 2. Configurar Variáveis de Ambiente

Crie arquivo `.env`:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=iedi
```

### 3. Rodar com Docker

```bash
docker-compose up --build
```

Acesse: `http://localhost:8080`

### 4. Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python wsgi.py
```

---

## 📋 Rotas da API

### Bancos
- `GET /bancos/api` - Listar bancos
- `POST /bancos/api` - Criar banco
- `PUT /bancos/api/:id` - Atualizar banco
- `DELETE /bancos/api/:id` - Excluir banco

### Veículos Relevantes
- `GET /veiculos/api/relevantes` - Listar
- `POST /veiculos/api/relevantes` - Criar
- `PUT /veiculos/api/relevantes/:id` - Atualizar
- `DELETE /veiculos/api/relevantes/:id` - Excluir

### Veículos de Nicho
- `GET /veiculos/api/nicho` - Listar
- `POST /veiculos/api/nicho` - Criar
- `PUT /veiculos/api/nicho/:id` - Atualizar
- `DELETE /veiculos/api/nicho/:id` - Excluir

### Análises
- `GET /analises/api` - Listar análises
- `GET /analises/api/:id` - Detalhes da análise
- `GET /analises/api/:id/mencoes` - Menções da análise

---

## 🔧 Tecnologias

- **Backend:** Flask 3.0 + SQLAlchemy 2.0
- **Database:** MySQL/MariaDB
- **Frontend:** HTML5 + CSS3 + JavaScript Vanilla
- **Server:** Gunicorn + nginx (via ProxyFix)
- **Container:** Docker + docker-compose

---

## 📚 Documentação

- `docs/architecture/` - Diretrizes técnicas agnósticas
- `docs/business/` - Metodologia IEDI e mapeamento Brandwatch
- `templates/README.md` - Documentação da interface web
- `ENV_VARS.md` - Variáveis de ambiente necessárias

---

## 🎨 Frontend

Interface HTML/CSS/JS puro servida pelo Flask:
- Design system profissional (cores, tipografia)
- Sidebar com navegação
- Tabelas responsivas
- Modais para CRUD
- Toast notifications
- Loading e empty states

---

## ✅ Checklist de Deploy

- [ ] Executar todos os scripts SQL
- [ ] Configurar variáveis de ambiente (.env)
- [ ] Build da imagem Docker
- [ ] Configurar nginx (se necessário)
- [ ] Testar todas as rotas
- [ ] Verificar logs do Gunicorn

---

## 📝 Notas

- O arquivo `app.py.backup` contém o código antigo (referência)
- Dados hardcoded foram removidos (use inserts SQL)
- Sistema pronto para nginx com ProxyFix
- Estrutura baseada no bb-monitor (padrão da organização)
