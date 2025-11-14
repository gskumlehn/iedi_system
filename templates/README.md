# Templates - Interface Web IEDI

Esta pasta contém os templates HTML da interface web do sistema IEDI, servidos pelo Flask.

## Estrutura

### Base Template
- **base.html** - Template base com sidebar, navegação e layout geral

### Páginas
- **index.html** - Dashboard com estatísticas gerais
- **bancos.html** - Gerenciamento de bancos (CRUD completo)
- **veiculos_relevantes.html** - Gerenciamento de veículos relevantes (CRUD completo)
- **veiculos_nicho.html** - Gerenciamento de veículos de nicho (CRUD completo)
- **analises.html** - Visualização de análises IEDI e histórico

## Tecnologias

- **HTML5** - Estrutura semântica
- **CSS3** - Estilização via `/static/css/style.css`
- **JavaScript Vanilla** - Interatividade e comunicação com APIs REST
- **Jinja2** - Template engine do Flask

## Funcionalidades

### Dashboard (index.html)
- Cards com estatísticas em tempo real
- Integração com APIs REST para contagem de registros

### CRUD Pages
Todas as páginas de gerenciamento incluem:
- Listagem com tabelas responsivas
- Modal para criar/editar registros
- Confirmação de exclusão
- Toast notifications para feedback
- Loading states
- Empty states

### APIs REST
As páginas consomem as seguintes APIs (definidas em `app.py`):

- `GET /api/bancos` - Listar bancos
- `POST /api/bancos` - Criar banco
- `PUT /api/bancos/:id` - Atualizar banco
- `DELETE /api/bancos/:id` - Excluir banco

- `GET /api/veiculos-relevantes` - Listar veículos relevantes
- `POST /api/veiculos-relevantes` - Criar veículo relevante
- `PUT /api/veiculos-relevantes/:id` - Atualizar veículo relevante
- `DELETE /api/veiculos-relevantes/:id` - Excluir veículo relevante

- `GET /api/veiculos-nicho` - Listar veículos de nicho
- `POST /api/veiculos-nicho` - Criar veículo de nicho
- `PUT /api/veiculos-nicho/:id` - Atualizar veículo de nicho
- `DELETE /api/veiculos-nicho/:id` - Excluir veículo de nicho

- `GET /api/analises` - Listar análises
- `GET /api/analises/:id` - Obter detalhes de análise

## Design System

### Cores
- **Primary**: #2563eb (azul)
- **Success**: #10b981 (verde)
- **Danger**: #ef4444 (vermelho)
- **Warning**: #f59e0b (amarelo)

### Tipografia
- **Fonte**: Inter (Google Fonts)
- **Tamanhos**: 0.75rem - 2rem

### Componentes
- Cards
- Buttons (primary, secondary, danger)
- Tables
- Modals
- Forms
- Badges
- Toast notifications
- Loading states
- Empty states

## Navegação

A navegação é feita através da sidebar no `base.html`:
- Dashboard (/)
- Bancos (/bancos)
- Veículos Relevantes (/veiculos-relevantes)
- Veículos de Nicho (/veiculos-nicho)
- Análises (/analises)
