# Sistema IEDI - Índice de Exposição Digital na Imprensa

Sistema web completo para calcular e gerenciar o Índice de Exposição Digital na Imprensa (IEDI) de bancos, com interface de administração para configurar porta-vozes, veículos relevantes e de nicho.

## Características

- **Backend**: Python + Flask + SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript puro
- **Banco de Dados**: SQLite com persistência via Docker volumes
- **Containerização**: Docker + Docker Compose
- **Interface Responsiva**: Design moderno e intuitivo

## Funcionalidades

### Gerenciamento
- ✅ Cadastro e gerenciamento de bancos
- ✅ Cadastro e gerenciamento de porta-vozes por banco
- ✅ Cadastro de veículos relevantes da imprensa
- ✅ Cadastro de veículos de nicho (especializados)
- ✅ Configuração de pesos e parâmetros do IEDI

### Análise IEDI
- ✅ Cálculo automático do IEDI baseado na metodologia oficial
- ✅ Identificação automática de bancos em menções
- ✅ Classificação por sentimento (positivo, negativo, neutro)
- ✅ Classificação por alcance (grupos A, B, C, D)
- ✅ Balizamento por volume de menções positivas
- ✅ Histórico de análises realizadas
- ✅ Visualização detalhada de resultados

### Dashboard
- 📊 Estatísticas gerais do sistema
- 📈 Ranking IEDI dos bancos
- 📰 Histórico de análises
- 🎯 Métricas de positividade e negatividade

## Estrutura do Projeto

```
iedi_system/
├── app/
│   ├── models.py           # Modelos do banco de dados SQLite
│   └── iedi_calculator.py  # Lógica de cálculo do IEDI
├── static/
│   ├── css/
│   │   └── style.css       # Estilos CSS
│   └── js/
│       └── main.js         # JavaScript principal
├── templates/
│   ├── base.html           # Template base
│   ├── index.html          # Dashboard
│   ├── bancos.html         # Gerenciamento de bancos
│   ├── porta_vozes.html    # Gerenciamento de porta-vozes
│   ├── veiculos.html       # Gerenciamento de veículos
│   ├── configuracoes.html  # Configurações do sistema
│   ├── analises.html       # Lista de análises
│   └── analise_detalhes.html # Detalhes de uma análise
├── data/
│   └── iedi.db            # Banco de dados SQLite (criado automaticamente)
├── app.py                 # Aplicação Flask principal
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## Instalação e Uso

### Opção 1: Docker (Recomendado)

1. **Certifique-se de ter Docker e Docker Compose instalados**

2. **Clone ou extraia o projeto**
   ```bash
   cd iedi_system
   ```

3. **Inicie o sistema com Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Acesse o sistema**
   ```
   http://localhost:5000
   ```

5. **Para parar o sistema**
   ```bash
   docker-compose down
   ```

6. **Para ver logs**
   ```bash
   docker-compose logs -f
   ```

### Opção 2: Execução Local (sem Docker)

1. **Instale Python 3.11+**

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**
   ```bash
   python app.py
   ```

4. **Acesse o sistema**
   ```
   http://localhost:5000
   ```

## Persistência de Dados

O banco de dados SQLite é armazenado em `/app/data/iedi.db` dentro do container e mapeado para `./data/iedi.db` no host através de um volume Docker.

**Importante**: O diretório `./data` no host persiste os dados mesmo quando o container é removido. Para backup, basta copiar o arquivo `data/iedi.db`.

## Primeiros Passos

1. **Acesse o Dashboard** em `http://localhost:5000`

2. **Carregue Dados Iniciais**
   - Clique no botão "🌱 Carregar Dados Iniciais"
   - Isso criará bancos e veículos de exemplo

3. **Configure os Bancos**
   - Acesse "Bancos" no menu lateral
   - Adicione ou edite os bancos que deseja monitorar
   - Configure as variações de nome de cada banco

4. **Configure Porta-vozes**
   - Acesse "Porta-vozes" no menu lateral
   - Adicione os porta-vozes de cada banco

5. **Configure Veículos**
   - Acesse "Veículos" no menu lateral
   - Gerencie veículos relevantes e de nicho

6. **Ajuste Configurações**
   - Acesse "Configurações" no menu lateral
   - Ajuste pesos e parâmetros do IEDI conforme necessário

## Integração com Brandwatch

Para executar uma análise IEDI, você precisa:

1. **Extrair menções da Brandwatch** usando o script de extração fornecido separadamente

2. **Enviar as menções para o endpoint da API**:
   ```bash
   POST /api/analises/executar
   Content-Type: application/json

   {
     "data_inicio": "2025-01-01",
     "data_fim": "2025-01-31",
     "mencoes": [
       {
         "id": "123",
         "title": "Banco anuncia resultados",
         "snippet": "O Banco do Brasil divulgou...",
         "url": "https://...",
         "domain": "g1.globo.com",
         "sentiment": "positive",
         "monthlyVisitors": 50000000,
         "date": "2025-01-15T10:00:00Z",
         "contentSourceName": "News"
       },
       ...
     ]
   }
   ```

3. **Visualize os resultados** na página de Análises

## API Endpoints

### Bancos
- `GET /api/bancos` - Listar bancos
- `POST /api/bancos` - Criar banco
- `PUT /api/bancos/:id` - Atualizar banco
- `DELETE /api/bancos/:id` - Excluir banco

### Porta-vozes
- `GET /api/porta-vozes` - Listar porta-vozes
- `POST /api/porta-vozes` - Criar porta-voz
- `PUT /api/porta-vozes/:id` - Atualizar porta-voz
- `DELETE /api/porta-vozes/:id` - Excluir porta-voz

### Veículos
- `GET /api/veiculos-relevantes` - Listar veículos relevantes
- `POST /api/veiculos-relevantes` - Criar veículo relevante
- `GET /api/veiculos-nicho` - Listar veículos de nicho
- `POST /api/veiculos-nicho` - Criar veículo de nicho

### Análises
- `GET /api/analises` - Listar análises
- `GET /api/analises/:id` - Detalhes de uma análise
- `POST /api/analises/executar` - Executar nova análise
- `GET /api/analises/:id/mencoes` - Menções de uma análise

### Configurações
- `GET /api/configuracoes` - Obter configurações
- `PUT /api/configuracoes` - Atualizar configurações

## Metodologia IEDI

O sistema implementa a metodologia oficial do IEDI com as seguintes variáveis:

### Variáveis Principais
- **Título** (peso 100): Banco mencionado no título
- **Veículo Relevante** (peso 95): Publicação em veículo de grande alcance
- **Subtítulo/1º Parágrafo** (peso 80): Banco mencionado no início do texto
- **Veículo de Nicho** (peso 54): Publicação em veículo especializado
- **Imagem** (peso 20): Presença de imagem na matéria
- **Porta-voz** (peso 20): Citação de porta-voz do banco

### Classificação por Alcance
- **Grupo A** (peso 91): > 29 milhões de visitas/mês
- **Grupo B** (peso 85): 11-29 milhões de visitas/mês
- **Grupo C** (peso 24): 500 mil - 11 milhões de visitas/mês
- **Grupo D** (peso 20): < 500 mil visitas/mês

### Cálculo
1. Nota base = soma ponderada das variáveis presentes
2. Ajuste por sentimento (negativo inverte o sinal)
3. Bônus de resposta (15%) para menções negativas com resposta oficial
4. IEDI final = balizamento por proporção de menções positivas

## Backup e Restauração

### Backup
```bash
# Copiar banco de dados
cp data/iedi.db backup_iedi_$(date +%Y%m%d).db
```

### Restauração
```bash
# Restaurar backup
cp backup_iedi_20250112.db data/iedi.db

# Reiniciar container
docker-compose restart
```

## Troubleshooting

### Container não inicia
```bash
# Ver logs
docker-compose logs -f

# Verificar portas
netstat -an | grep 5000
```

### Banco de dados corrompido
```bash
# Parar container
docker-compose down

# Remover banco
rm data/iedi.db

# Reiniciar (criará novo banco)
docker-compose up -d
```

### Permissões de arquivo
```bash
# Ajustar permissões do diretório data
chmod -R 755 data/
```

## Tecnologias Utilizadas

- **Python 3.11**: Linguagem principal
- **Flask 3.0**: Framework web
- **SQLite**: Banco de dados
- **Docker**: Containerização
- **HTML5/CSS3/JS**: Interface web

## Suporte

Para dúvidas ou problemas, consulte a documentação da metodologia IEDI ou entre em contato com o desenvolvedor.

## Licença

Este sistema foi desenvolvido para uso interno e análise de exposição na imprensa.
