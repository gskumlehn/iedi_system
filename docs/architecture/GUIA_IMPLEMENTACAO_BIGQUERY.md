# Guia de Implementação - Sistema IEDI com BigQuery

## Status Atual

✅ **Concluído**:
- Documentação completa do cálculo IEDI
- Mapeamento Brandwatch → Variáveis IEDI
- Models SQLAlchemy para BigQuery (8 entidades)
- Infraestrutura de conexão BigQuery
- Exemplo de Repository (BancoRepository)
- Análise da arquitetura bb-monitor

📋 **Pendente**:
- Repositories restantes (6)
- Services (4)
- Controllers (6)
- Templates HTML atualizados
- app.py refatorado

---

## Arquitetura Implementada

```
app_new/
├── models/              ✅ 8 models SQLAlchemy
│   ├── banco.py
│   ├── porta_voz.py
│   ├── veiculo_relevante.py
│   ├── veiculo_nicho.py
│   ├── analise.py
│   ├── periodo_banco.py
│   ├── mencao.py
│   └── resultado_iedi.py
├── infra/               ✅ Conexão BigQuery
│   └── bq_sa.py
├── repositories/        ⚠️  1 de 7 completo
│   └── banco_repository.py
├── services/            ❌ Pendente
├── controllers/         ❌ Pendente
├── enums/               ❌ Pendente
└── constants/           ❌ Pendente
```

---

## Próximos Passos

### 1. Completar Repositories

Criar os repositories restantes seguindo o padrão de `BancoRepository`:

**Arquivos a criar**:
- `porta_voz_repository.py`
- `veiculo_repository.py` (para relevantes e nicho)
- `analise_repository.py`
- `mencao_repository.py`
- `resultado_iedi_repository.py`
- `periodo_banco_repository.py`

**Padrão**:
```python
from app_new.models.{model} import {Model}
from app_new.infra.bq_sa import get_session

class {Model}Repository:
    @staticmethod
    def save(entity: {Model}) -> {Model}:
        with get_session() as session:
            session.add(entity)
            session.flush()
            session.refresh(entity)
            return entity
    
    @staticmethod
    def find_by_id(id: int) -> Optional[{Model}]:
        with get_session() as session:
            return session.query({Model}).filter({Model}.id == id).first()
    
    # ... outros métodos conforme necessidade
```

### 2. Criar Services

**IEDICalculatorService** (`services/iedi_calculator_service.py`):
- Método `calcular_iedi_mencao(mencao_data, banco, portavozes, veiculos_relevantes, veiculos_nicho)`
- Retorna: `{"nota": float, "variaveis": dict}`
- Implementa a lógica do `CALCULO_IEDI.md`

**BrandwatchService** (`services/brandwatch_service.py`):
- Método `fetch_mentions(query_name, start_date, end_date, category_detail=None)`
- Integração com API Brandwatch
- Retorna lista de menções

**AnaliseService** (`services/analise_service.py`):
- Método `criar_analise(nome, query_name, data_inicio, data_fim, bancos, periodo_personalizado)`
- Método `executar_analise(analise_id)`
- Orquestra: Brandwatch → Cálculo IEDI → Salvamento

**ResultadoService** (`services/resultado_service.py`):
- Método `gerar_ranking(analise_id)`
- Método `calcular_metricas(analise_id, banco_id)`
- Agregação e balizamento

### 3. Criar Controllers

**AnaliseController** (`controllers/analise_controller.py`):
```python
from flask import Blueprint, request, jsonify, render_template
from app_new.services.analise_service import AnaliseService

analise_bp = Blueprint("analise", __name__)
analise_service = AnaliseService()

@analise_bp.get("/")
def index():
    return render_template("analises.html")

@analise_bp.post("/criar")
def criar():
    data = request.json
    resultado = analise_service.criar_analise(
        nome=data["nome"],
        query_name=data["query_name"],
        data_inicio=data["data_inicio"],
        data_fim=data["data_fim"],
        bancos=data["bancos"],
        periodo_personalizado=data.get("periodo_personalizado", False)
    )
    return jsonify(resultado), 201

@analise_bp.post("/<int:analise_id>/executar")
def executar(analise_id):
    resultado = analise_service.executar_analise(analise_id)
    return jsonify(resultado), 200
```

**Outros controllers**:
- `banco_controller.py`
- `porta_voz_controller.py`
- `veiculo_controller.py`
- `resultado_controller.py`
- `root_controller.py` (home, dashboard)

### 4. Atualizar Templates

**Nova tela de criação de análise** (`templates/criar_analise.html`):
```html
<form id="formAnalise">
    <input type="text" name="nome" placeholder="Nome da Análise" required>
    <input type="text" name="query_name" placeholder="Nome da Query Brandwatch" required>
    
    <label>
        <input type="checkbox" id="periodoPersonalizado">
        Período personalizado por banco
    </label>
    
    <div id="periodoUnico">
        <input type="datetime-local" name="data_inicio" required>
        <input type="datetime-local" name="data_fim" required>
    </div>
    
    <div id="periodosPorBanco" style="display:none">
        <!-- Para cada banco -->
        <div class="banco-periodo">
            <h4>Banco do Brasil</h4>
            <input type="text" name="category_detail_bb" placeholder="Category Detail">
            <input type="datetime-local" name="data_inicio_bb">
            <input type="datetime-local" name="data_fim_bb">
        </div>
        <!-- Repetir para outros bancos -->
    </div>
    
    <button type="submit">Criar e Executar Análise</button>
</form>
```

### 5. Refatorar app.py

```python
from flask import Flask
from app_new.controllers.analise_controller import analise_bp
from app_new.controllers.banco_controller import banco_bp
from app_new.controllers.porta_voz_controller import porta_voz_bp
from app_new.controllers.veiculo_controller import veiculo_bp
from app_new.controllers.resultado_controller import resultado_bp
from app_new.controllers.root_controller import root_bp
from app_new.infra.bq_sa import init_schema, create_tables

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(root_bp, url_prefix="/")
app.register_blueprint(analise_bp, url_prefix="/analises")
app.register_blueprint(banco_bp, url_prefix="/bancos")
app.register_blueprint(porta_voz_bp, url_prefix="/porta-vozes")
app.register_blueprint(veiculo_bp, url_prefix="/veiculos")
app.register_blueprint(resultado_bp, url_prefix="/resultados")

# Inicializar BigQuery
with app.app_context():
    init_schema()
    create_tables()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

### 6. Configurar BigQuery

**Arquivo `.env`**:
```bash
# BigQuery
BQ_PROJECT=seu-projeto-gcp
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Brandwatch
BRANDWATCH_API_KEY=sua-chave
BRANDWATCH_PROJECT_ID=seu-projeto-id
```

**Criar service account no GCP**:
1. Acesse Google Cloud Console
2. IAM & Admin → Service Accounts
3. Create Service Account
4. Adicionar roles: BigQuery Admin
5. Create Key (JSON)
6. Salvar JSON e configurar caminho no `.env`

### 7. Atualizar requirements.txt

```txt
Flask==3.0.0
sqlalchemy==1.4.49
sqlalchemy-bigquery==1.10.0
google-cloud-bigquery==3.25.0
google-cloud-bigquery-storage==2.24.0
bcr-api==1.0.0
python-dotenv==1.0.0
```

### 8. Atualizar docker-compose.yml

```yaml
version: '3.8'

services:
  iedi-system:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./credentials.json:/app/credentials.json:ro
    environment:
      - BQ_PROJECT=${BQ_PROJECT}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
      - BRANDWATCH_API_KEY=${BRANDWATCH_API_KEY}
      - BRANDWATCH_PROJECT_ID=${BRANDWATCH_PROJECT_ID}
    restart: unless-stopped
```

---

## Estrutura de Dados Simplificada

### Análise com Período Único

```json
{
  "nome": "Análise Mensal Abril 2025",
  "query_name": "Query Geral Bancos",
  "data_inicio": "2025-04-01T00:00:00",
  "data_fim": "2025-04-30T23:59:59",
  "periodo_personalizado": false,
  "bancos": [
    {"id": 1, "category_detail": "Banco do Brasil"},
    {"id": 2, "category_detail": "Itaú"},
    {"id": 3, "category_detail": "Bradesco"},
    {"id": 4, "category_detail": "Santander"}
  ]
}
```

### Análise com Período Personalizado

```json
{
  "nome": "Resultados 1T2025",
  "query_name": "Query Geral Bancos",
  "periodo_personalizado": true,
  "bancos": [
    {
      "id": 1,
      "category_detail": "Banco do Brasil",
      "data_inicio": "2025-05-13T00:00:00",
      "data_fim": "2025-05-15T23:59:59"
    },
    {
      "id": 2,
      "category_detail": "Itaú",
      "data_inicio": "2025-05-14T00:00:00",
      "data_fim": "2025-05-16T23:59:59"
    }
  ]
}
```

---

## Vantagens da Nova Estrutura

✅ **Flexibilidade Total**: Qualquer período, qualquer banco  
✅ **Simplicidade**: Sem distinção mensal/resultados  
✅ **Escalabilidade**: BigQuery suporta grande volume  
✅ **Manutenibilidade**: Arquitetura em camadas  
✅ **Rastreabilidade**: Cada menção com detalhes completos  
✅ **Comparabilidade**: Mesma metodologia para todos os períodos  

---

## Estimativa de Esforço

| Tarefa | Tempo Estimado |
|--------|----------------|
| Repositories restantes | 2h |
| Services | 4h |
| Controllers | 3h |
| Templates | 3h |
| Testes | 2h |
| **Total** | **14h** |

---

## Suporte

Para completar a implementação, consulte:
- `CALCULO_IEDI.md` - Lógica de cálculo
- `MAPEAMENTO_BRANDWATCH_IEDI.md` - Campos da API
- `ANALISE_BB_MONITOR.md` - Padrões de arquitetura
- Código do `bb-monitor` em `/home/ubuntu/bb-monitor`

---

**Desenvolvido por**: Manus AI  
**Data**: 12/11/2024  
**Versão**: 4.0
