# Refatoração de Services - Arquitetura IEDI

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0

---

## Mudanças Implementadas

### 1. Criação do MentionService

**Motivação**: Centralizar regras de negócio relacionadas a menções, removendo acesso direto a repositories dos services de análise.

**Responsabilidades**:
- Processar menções da Brandwatch (extração de URL, enriquecimento, armazenamento)
- Gerenciar cache e reutilização de menções
- Normalizar dados brutos da Brandwatch

**Localização**: `app/services/mention_service.py`

**Interface**:

```python
class MentionService:
    def __init__(
        self,
        mention_repo: MentionRepository,
        media_outlet_repo: MediaOutletRepository
    ):
        pass

    def process_mention(self, mention_data: Dict) -> Mention:
        """Processa menção: extrai URL, enriquece e armazena."""
        pass
```

**Fluxo**:
1. Extrai URL única (verifica `url` e `originalUrl`)
2. Busca menção existente por URL
3. Se não existe: enriquece dados e cria nova menção
4. Retorna menção (nova ou existente)

---

### 2. Refatoração do BankDetectionService

**Mudança**: Detecção de bancos agora usa `categoryDetails` da Brandwatch com grupo específico.

**Problema anterior**: Tentava detectar bancos em todas as categorias, incluindo categorias não relacionadas (Tecnologia, Política, etc.).

**Solução**: Filtrar apenas categorias do grupo "Bancos" em `categoryDetails`.

**Estrutura esperada da Brandwatch**:

```json
{
  "categoryDetails": [
    {
      "name": "Banco do Brasil",
      "group": "Bancos"
    },
    {
      "name": "Tecnologia",
      "group": "Temas"
    }
  ]
}
```

**Lógica de detecção**:

1. **Fonte primária**: `categoryDetails` com `group == "Bancos"`
2. **Fallback**: Busca no texto (título + snippet) se `categoryDetails` vazio

**Localização**: `app/services/bank_detection_service.py`

**Interface**:

```python
class BankDetectionService:
    BANK_CATEGORY_GROUP = "Bancos"

    def __init__(self, bank_repo: BankRepository):
        pass

    def detect_banks(self, mention_data: Dict) -> List[Bank]:
        """Detecta bancos usando categoryDetails."""
        pass
```

---

### 3. Refatoração do IEDIOrchestrator

**Mudanças**:
- Removido acesso direto a `MentionRepository`
- Usa `MentionService` para processar menções
- Simplificado fluxo de processamento

**Antes**:

```python
class IEDIOrchestrator:
    def __init__(
        self,
        brandwatch_service,
        enrichment_service,
        detection_service,
        calculation_service,
        aggregation_service,
        mention_repo,  # ← Acesso direto ao repository
        analysis_mention_repo,
        ...
    ):
        pass
```

**Depois**:

```python
class IEDIOrchestrator:
    def __init__(
        self,
        brandwatch_service,
        mention_service,  # ← Service em vez de repository
        bank_detection_service,
        iedi_calculation_service,
        iedi_aggregation_service,
        analysis_mention_repo,
        ...
    ):
        pass
```

**Fluxo simplificado**:

```python
def _process_single_mention(self, analysis_id: str, mention_data: Dict):
    # 1. Processar menção (MentionService)
    mention = self.mention_service.process_mention(mention_data)
    
    # 2. Detectar bancos (BankDetectionService)
    detected_banks = self.bank_detection.detect_banks(mention_data)
    
    # 3. Calcular IEDI para cada banco
    for bank in detected_banks:
        iedi_result = self.iedi_calculation.calculate_iedi(
            mention_data=mention_data,
            bank=bank
        )
        
        # 4. Armazenar relacionamento
        self.analysis_mention_repo.create(
            analysis_id=analysis_id,
            mention_id=mention.id,
            bank_id=bank.id,
            **iedi_result
        )
```

---

## Arquitetura Atualizada

### Separação de Responsabilidades

| Camada | Componente | Responsabilidade |
|--------|------------|------------------|
| **Orchestration** | IEDIOrchestrator | Coordena fluxo completo |
| **Business Logic** | MentionService | Regras de negócio de menções |
| **Business Logic** | BankDetectionService | Detecção de bancos via categoryDetails |
| **Business Logic** | IEDICalculationService | Cálculo do índice IEDI |
| **Business Logic** | IEDIAggregationService | Agregação e balizamento |
| **Data Access** | MentionRepository | Acesso a dados de menções |
| **Data Access** | BankRepository | Acesso a dados de bancos |

### Fluxo de Dados

```
Brandwatch API
    ↓
BrandwatchService (Coleta)
    ↓
MentionService (Processar menção)
    ├→ MentionRepository (Armazenar)
    └→ MediaOutletRepository (Enriquecer)
    ↓
BankDetectionService (Detectar bancos)
    └→ BankRepository (Buscar bancos)
    ↓
IEDICalculationService (Calcular IEDI)
    ↓
AnalysisMentionRepository (Armazenar IEDI)
    ↓
IEDIAggregationService (Agregar)
    ↓
Ranking Final
```

---

## Detecção de Bancos via categoryDetails

### Configuração Brandwatch

No Brandwatch, criar **grupo de categorias** chamado "Bancos" com as seguintes categorias:

| Categoria | Grupo |
|-----------|-------|
| Banco do Brasil | Bancos |
| Itaú | Bancos |
| Bradesco | Bancos |
| Santander | Bancos |

### Exemplo de Resposta da API

```json
{
  "id": "bw_123456",
  "title": "Banco do Brasil e Itaú lideram ranking",
  "categoryDetails": [
    {
      "name": "Banco do Brasil",
      "group": "Bancos"
    },
    {
      "name": "Itaú",
      "group": "Bancos"
    },
    {
      "name": "Economia",
      "group": "Temas"
    }
  ]
}
```

### Lógica de Filtragem

```python
def _detect_from_categories(self, mention_data: Dict) -> List[Bank]:
    category_details = mention_data.get('categoryDetails', [])
    detected_banks = []
    
    for category in category_details:
        # Filtrar apenas grupo "Bancos"
        if category.get('group') != self.BANK_CATEGORY_GROUP:
            continue
        
        category_name = category.get('name', '').lower()
        
        # Mapear nome da categoria para banco
        for bank in banks:
            if self._matches_bank(category_name, bank):
                detected_banks.append(bank)
                break
    
    return detected_banks
```

**Resultado**: `[Banco do Brasil, Itaú]` (ignora "Economia")

---

## Vantagens da Refatoração

### 1. Separação de Responsabilidades

Services de análise não acessam repositories diretamente. MentionService centraliza regras de negócio.

### 2. Reutilização de Código

Lógica de processamento de menções centralizada em um único service.

### 3. Testabilidade

Cada service pode ser testado isoladamente com mocks.

### 4. Precisão na Detecção

Uso de `categoryDetails` elimina falsos positivos de categorias não relacionadas.

### 5. Manutenibilidade

Mudanças em regras de negócio de menções ficam isoladas em MentionService.

---

## Arquivos Criados

```
app/services/
├── mention_service.py           # Novo service de menções
├── bank_detection_service.py    # Refatorado para usar categoryDetails
└── iedi_orchestrator.py         # Refatorado para usar MentionService
```

---

## Próximos Passos

1. Implementar `BrandwatchService`
2. Implementar `IEDICalculationService`
3. Implementar `IEDIAggregationService`
4. Criar testes unitários para cada service
5. Configurar grupo "Bancos" no Brandwatch

---

**Desenvolvido por**: Manus AI  
**Data**: 15 de novembro de 2025
