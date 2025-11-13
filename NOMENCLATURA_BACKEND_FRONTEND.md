# Guia de Nomenclatura - Backend (Inglês) / Frontend (Português)

## Princípio

**Backend** (models, repositories, services, controllers, métodos, variáveis): **INGLÊS**  
**Frontend** (HTML, mensagens JS, validações, labels): **PORTUGUÊS**

---

## Tabela de Mapeamento

### Models e Tabelas

| Português (OLD) | Inglês (NEW) | Tabela BigQuery |
|-----------------|--------------|-----------------|
| Banco | Bank | `banks` |
| PortaVoz | Spokesperson | `spokespersons` |
| VeiculoRelevante | RelevantMediaOutlet | `relevant_media_outlets` |
| VeiculoNicho | NicheMediaOutlet | `niche_media_outlets` |
| Analise | Analysis | `analyses` |
| PeriodoBanco | BankPeriod | `bank_periods` |
| Mencao | Mention | `mentions` |
| ResultadoIEDI | IEDIResult | `iedi_results` |

### Campos/Colunas

| Português (OLD) | Inglês (NEW) | Tipo |
|-----------------|--------------|------|
| nome | name | String |
| variacoes | variations | JSON |
| ativo | active | Boolean |
| banco_id | bank_id | Integer |
| cargo | position | String |
| dominio | domain | String |
| categoria | category | String |
| data_inicio | start_date | DateTime |
| data_fim | end_date | DateTime |
| periodo_personalizado | custom_period | Boolean |
| query_name | query_name | String |
| status | status | String |
| total_mencoes | total_mentions | Integer |
| mensagem_erro | error_message | Text |
| titulo | title | Text |
| snippet | snippet | Text |
| url | url | Text |
| sentimento | sentiment | String |
| category_detail | category_detail | String |
| acessos_mensais | monthly_visitors | Integer |
| data_mencao | mention_date | DateTime |
| nota | score | Float |
| grupo_alcance | reach_group | String |
| variaveis | variables | JSON |
| iedi_medio | average_iedi | Float |
| iedi_final | final_iedi | Float |
| volume_total | total_volume | Integer |
| volume_positivo | positive_volume | Integer |
| volume_negativo | negative_volume | Integer |
| volume_neutro | neutral_volume | Integer |
| positividade | positivity | Float |
| negatividade | negativity | Float |
| proporcao_positivas | positive_ratio | Float |

### Repositories

| Português (OLD) | Inglês (NEW) |
|-----------------|--------------|
| BancoRepository | BankRepository |
| PortaVozRepository | SpokespersonRepository |
| VeiculoRepository | MediaOutletRepository |
| AnaliseRepository | AnalysisRepository |
| MencaoRepository | MentionRepository |
| ResultadoIEDIRepository | IEDIResultRepository |

### Services

| Português (OLD) | Inglês (NEW) |
|-----------------|--------------|
| IEDICalculatorService | IEDICalculatorService |
| BrandwatchService | BrandwatchService |
| AnaliseService | AnalysisService |
| ResultadoService | ResultService |

### Controllers

| Português (OLD) | Inglês (NEW) |
|-----------------|--------------|
| BancoController | BankController |
| PortaVozController | SpokespersonController |
| VeiculoController | MediaOutletController |
| AnaliseController | AnalysisController |
| ResultadoController | ResultController |

### Métodos

| Português (OLD) | Inglês (NEW) | Descrição |
|-----------------|--------------|-----------|
| salvar() | save() | Salvar entidade |
| buscar_por_id() | find_by_id() | Buscar por ID |
| buscar_por_nome() | find_by_name() | Buscar por nome |
| listar_todos() | find_all() | Listar todos |
| atualizar() | update() | Atualizar |
| deletar() | delete() | Deletar |
| contar() | count() | Contar |
| criar_analise() | create_analysis() | Criar análise |
| executar_analise() | execute_analysis() | Executar análise |
| calcular_iedi() | calculate_iedi() | Calcular IEDI |
| gerar_ranking() | generate_ranking() | Gerar ranking |

---

## Exemplos de Uso

### Backend (Inglês)

**Model**:
```python
class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    variations = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)
```

**Repository**:
```python
class BankRepository:
    @staticmethod
    def find_by_name(name: str) -> Optional[Bank]:
        with get_session() as session:
            return session.query(Bank).filter(Bank.name == name).first()
```

**Service**:
```python
class AnalysisService:
    def create_analysis(self, name: str, query_name: str, 
                       start_date: datetime, end_date: datetime) -> Analysis:
        analysis = Analysis()
        analysis.name = name
        analysis.query_name = query_name
        analysis.start_date = start_date
        analysis.end_date = end_date
        return AnalysisRepository.save(analysis)
```

**Controller**:
```python
@analysis_bp.post("/create")
def create():
    data = request.json
    analysis = analysis_service.create_analysis(
        name=data["name"],
        query_name=data["query_name"],
        start_date=data["start_date"],
        end_date=data["end_date"]
    )
    return jsonify({
        "success": True,
        "message": "Análise criada com sucesso!",  # ← Português no retorno
        "data": {
            "id": analysis.id,
            "name": analysis.name
        }
    }), 201
```

### Frontend (Português)

**HTML**:
```html
<form id="formAnalise">
    <label for="nome">Nome da Análise:</label>
    <input type="text" id="nome" name="name" required>
    
    <label for="query">Nome da Query Brandwatch:</label>
    <input type="text" id="query" name="query_name" required>
    
    <label>
        <input type="checkbox" id="periodoPersonalizado" name="custom_period">
        Período personalizado por banco
    </label>
    
    <button type="submit">Criar Análise</button>
</form>
```

**JavaScript**:
```javascript
// Mensagens em português
const messages = {
    success: "Análise criada com sucesso!",
    error: "Erro ao criar análise. Tente novamente.",
    required: "Este campo é obrigatório",
    invalidDate: "Data inválida"
};

// Validação
if (!form.name.value) {
    showError("Nome da análise é obrigatório");
    return;
}

// Requisição (campos em inglês)
fetch("/api/analyses/create", {
    method: "POST",
    body: JSON.stringify({
        name: form.name.value,
        query_name: form.query_name.value,
        start_date: form.start_date.value,
        end_date: form.end_date.value,
        custom_period: form.custom_period.checked
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        showSuccess(data.message);  // ← Mensagem em português do backend
    }
});
```

---

## Regras de Ouro

### ✅ Backend (INGLÊS)

1. **Nomes de classes**: PascalCase em inglês
   - `Bank`, `Spokesperson`, `Analysis`

2. **Nomes de métodos**: snake_case em inglês
   - `find_by_id()`, `create_analysis()`, `calculate_iedi()`

3. **Nomes de variáveis**: snake_case em inglês
   - `bank_id`, `start_date`, `total_mentions`

4. **Nomes de tabelas**: snake_case plural em inglês
   - `banks`, `spokespersons`, `analyses`

5. **Nomes de colunas**: snake_case em inglês
   - `name`, `active`, `created_at`

6. **Comentários de código**: Inglês
   ```python
   # Find bank by ID
   def find_by_id(bank_id: int) -> Optional[Bank]:
       ...
   ```

### ✅ Frontend (PORTUGUÊS)

1. **Labels de formulário**: Português
   ```html
   <label>Nome do Banco:</label>
   ```

2. **Placeholders**: Português
   ```html
   <input placeholder="Digite o nome do banco">
   ```

3. **Mensagens de validação**: Português
   ```javascript
   if (!name) {
       alert("Nome é obrigatório");
   }
   ```

4. **Mensagens de sucesso/erro**: Português
   ```javascript
   showSuccess("Banco cadastrado com sucesso!");
   showError("Erro ao cadastrar banco");
   ```

5. **Títulos e textos**: Português
   ```html
   <h1>Cadastro de Bancos</h1>
   <p>Preencha os dados abaixo</p>
   ```

6. **Botões**: Português
   ```html
   <button>Salvar</button>
   <button>Cancelar</button>
   ```

### ⚠️ Comunicação Backend ↔ Frontend

**Campos de dados**: INGLÊS (mesmo no JSON)
```json
{
    "name": "Banco do Brasil",
    "variations": ["BB", "Banco do Brasil"],
    "active": true
}
```

**Mensagens de retorno**: PORTUGUÊS
```json
{
    "success": true,
    "message": "Banco cadastrado com sucesso!",
    "data": { ... }
}
```

---

## Checklist de Implementação

### Backend
- [ ] Models com nomes em inglês
- [ ] Tabelas BigQuery com nomes em inglês
- [ ] Colunas com nomes em inglês
- [ ] Repositories com métodos em inglês
- [ ] Services com métodos em inglês
- [ ] Controllers com métodos em inglês
- [ ] Variáveis internas em inglês
- [ ] Comentários de código em inglês
- [ ] Mensagens de retorno em português

### Frontend
- [ ] Labels em português
- [ ] Placeholders em português
- [ ] Mensagens de validação em português
- [ ] Mensagens de sucesso/erro em português
- [ ] Títulos e textos em português
- [ ] Botões em português
- [ ] Campos de formulário com `name` em inglês
- [ ] Requisições AJAX com campos em inglês

---

## Vantagens da Abordagem

✅ **Código Profissional**: Backend em inglês é padrão internacional  
✅ **Manutenibilidade**: Desenvolvedores de qualquer país entendem o backend  
✅ **UX em Português**: Usuários brasileiros têm interface nativa  
✅ **Separação Clara**: Backend técnico vs Frontend de negócio  
✅ **Escalabilidade**: Fácil adicionar outros idiomas no frontend  
✅ **Documentação**: Código auto-documentado em inglês  

---

**Desenvolvido por**: Manus AI  
**Data**: 13/11/2024  
**Versão**: 5.0
