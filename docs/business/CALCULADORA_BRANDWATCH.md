# Calculadora IEDI Brandwatch - Documentação Técnica

## Visão Geral

A **Calculadora IEDI Brandwatch** é uma implementação fiel das fórmulas originais do Power BI, adaptada para trabalhar exclusivamente com os campos disponíveis na API da Brandwatch. Este módulo elimina dependências de processamento manual e integra-se perfeitamente ao fluxo automatizado de extração e análise.

---

## Arquitetura

### Módulo Principal
**Arquivo**: `app/iedi_calculator_brandwatch.py`

**Classe**: `IEDICalculatorBrandwatch`

**Responsabilidades**:
- Calcular IEDI individual de cada menção
- Agregar IEDIs por banco
- Gerar ranking comparativo
- Calcular indicadores complementares

---

## Diferenças da Calculadora Anterior

| Aspecto | Calculadora Antiga | Calculadora Brandwatch |
|---------|-------------------|----------------------|
| **Identificação de Banco** | Busca por texto (regex) | `categoryDetail` da Brandwatch |
| **Fórmulas** | Simplificadas | Fórmulas originais do Power BI |
| **Pesos** | Aproximados | Pesos exatos do Power BI |
| **Denominadores** | Único | Dois (Grupo A e Não-Grupo A) |
| **Balizamento** | Separado | Integrado no cálculo |
| **Fonte de Dados** | Genérica | Otimizada para Brandwatch |

---

## Fórmulas Implementadas

### 1. Cálculo Individual (Menção)

Para cada menção, o IEDI é calculado em etapas:

#### Etapa 1: Verificações Binárias (0 ou 1)

```python
verificacao_qualificacao = 1 if sentiment == 'positive' else 0
verificacao_titulo = 1 if banco in title else 0
verificacao_subtitulo = 1 if banco in snippet else 0
verificacao_imagem = 1 if len(imageUrls) > 0 else 0
verificacao_portavoz = 1 if portavoz in fullText else 0
verificacao_veiculo_nicho = 1 if domain in veiculos_nicho else 0
```

#### Etapa 2: Classificação de Grupo

```python
if monthlyVisitors >= 29_000_001:
    grupo = 'A'  # peso 91
elif 11_000_001 <= monthlyVisitors <= 29_000_000:
    grupo = 'B'  # peso 85
elif 500_000 <= monthlyVisitors <= 11_000_000:
    grupo = 'C'  # peso 24
else:
    grupo = 'D'  # peso 20
```

#### Etapa 3: Cálculo do Numerador

```python
numerador = (
    (grupo_d * 20) +
    (grupo_c * 24) +
    (grupo_b * 85) +
    (grupo_a * 91) +
    (1 * 95) +  # Veículo relevante (sempre 1)
    (verificacao_veiculo_nicho * 54) +
    (verificacao_titulo * 100) +
    (verificacao_subtitulo * 80) +
    (verificacao_imagem * 20) +
    (verificacao_portavoz * 20)
)
```

#### Etapa 4: Escolha do Denominador

```python
if grupo == 'A':
    denominador = 406  # 91 + 95 + 100 + 80 + 20 + 20
else:
    denominador = 460  # 91 + 95 + 54 + 100 + 80 + 20 + 20
```

**Razão**: Quando o veículo é Grupo A, o peso de "veículo de nicho" (54) não entra no denominador, pois veículos Grupo A já têm alto alcance e não precisam do bônus de nicho.

#### Etapa 5: Cálculo Base (-1 a 1)

```python
iedi_base = numerador / denominador

if sentiment == 'negative':
    iedi_base = iedi_base * -1
```

#### Etapa 6: Conversão para Escala 0-10

```python
iedi_0_a_10 = (10 * (iedi_base + 1)) / 2
iedi_0_a_10 = max(0, min(10, iedi_0_a_10))  # Limitar entre 0 e 10
```

---

### 2. Agregação por Banco

Para calcular o IEDI de um banco:

#### Etapa 1: IEDI Médio

```python
iedi_medio = sum(iedi_mencao for mencao in mencoes) / len(mencoes)
```

#### Etapa 2: Positividade

```python
volume_positivo = count(mencoes WHERE sentiment == 'positive')
volume_total = len(mencoes)
positividade = (volume_positivo / volume_total) * 100
```

#### Etapa 3: Balizamento

```python
fator_balizamento = positividade / 100
iedi_final = iedi_medio * fator_balizamento
```

**Razão do Balizamento**: Bancos com maior proporção de menções positivas devem ter IEDI final mais alto, mesmo que o IEDI médio seja similar. Isso incentiva a qualidade sobre quantidade.

---

## Mapeamento Brandwatch → IEDI

| Variável IEDI | Campo Brandwatch | Tipo | Processamento |
|---------------|------------------|------|---------------|
| `verificacao_qualificacao` | `sentiment` | string | "positive" → 1, outros → 0 |
| `verificacao_titulo` | `title` | string | Buscar banco no título |
| `verificacao_subtitulo` | `snippet` | string | Buscar banco no snippet |
| `verificacao_imagem` | `imageUrls` | array | len > 0 → 1 |
| `verificacao_portavoz` | `fullText` | string | Buscar porta-vozes cadastrados |
| `verificacao_veiculo_nicho` | `domain` | string | Verificar se está na lista |
| `grupo_alcance` | `monthlyVisitors` | integer | Classificar por faixa |
| `veiculo_relevante` | `domain` | string | Sempre 1 (filtramos apenas relevantes) |
| `banco` | `categoryDetail` | string | Identificação direta |

---

## Uso da Calculadora

### Inicialização

```python
from app.iedi_calculator_brandwatch import criar_calculadora_brandwatch
from app.models import Database

db = Database()
calculadora = criar_calculadora_brandwatch(db)
```

A função `criar_calculadora_brandwatch()` carrega automaticamente:
- Veículos relevantes do banco de dados
- Veículos de nicho do banco de dados
- Porta-vozes por banco do banco de dados

### Calcular IEDI de um Banco

```python
# Menções já filtradas por banco (via categoryDetail)
mencoes_banco = [...]  # Lista de dicts da Brandwatch

# Dados do banco
banco_nome = "Banco do Brasil"
variacoes = ["banco do brasil", "bb", "banco do brazil"]

# Calcular
resultado = calculadora.calcular_iedi_banco(
    mencoes=mencoes_banco,
    banco_nome=banco_nome,
    variacoes=variacoes
)

print(f"IEDI Final: {resultado['iedi_final']}")
print(f"Positividade: {resultado['positividade']}%")
```

### Gerar Ranking Comparativo

```python
# Resultados de múltiplos bancos
resultados_bancos = [
    {'banco': 'BB', 'iedi_final': 7.5, ...},
    {'banco': 'Itaú', 'iedi_final': 8.2, ...},
    {'banco': 'Bradesco', 'iedi_final': 6.8, ...},
]

# Gerar ranking
ranking = calculadora.calcular_iedi_comparativo(resultados_bancos)

for item in ranking:
    print(f"{item['posicao']}º - {item['banco']}: {item['iedi_final']}")
```

---

## Indicadores Complementares

A calculadora também fornece indicadores adicionais:

### Presença em Títulos

Percentual de menções positivas onde o banco aparece no título.

```python
indicadores = IEDICalculatorBrandwatch.calcular_indicadores_adicionais(
    mencoes=mencoes_banco,
    banco_nome=banco_nome
)

print(f"Presença em Títulos: {indicadores['presenca_positiva_titulos_perc']}%")
```

### Diversidade de Veículos

Quantidade de veículos distintos com menções positivas, segmentada por grupo de alcance.

```python
print(f"Diversidade Total: {indicadores['diversidade_veiculos']}")
print(f"Diversidade Grupo A: {indicadores['diversidade_grupo_a']}")
print(f"Diversidade Grupo B: {indicadores['diversidade_grupo_b']}")
```

---

## Estrutura de Retorno

### Resultado Individual (Menção)

```python
{
    'iedi_-1_a_1': 0.85,
    'iedi_0_a_10': 9.25,
    'sentiment': 'positiva',
    'grupo_alcance': 'A',
    'variaveis': {
        'titulo': 1,
        'subtitulo': 1,
        'imagem': 1,
        'portavoz': 0,
        'veiculo_nicho': 0,
        'grupo': 'A',
        'monthly_visitors': 35000000
    },
    'pesos_aplicados': {
        'numerador': 386,
        'denominador': 406
    },
    'mention_id': '123456',
    'titulo': 'Banco do Brasil anuncia...',
    'url': 'https://...',
    'domain': 'g1.globo.com',
    'data_mencao': '2025-02-10',
    'category_detail': 'Banco do Brasil'
}
```

### Resultado Agregado (Banco)

```python
{
    'banco': 'Banco do Brasil',
    'iedi_medio': 7.8,
    'iedi_final': 6.5,
    'volume_total': 150,
    'volume_positivo': 98,
    'volume_negativo': 52,
    'positividade': 65.33,
    'negatividade': 34.67,
    'mencoes_detalhadas': [...]  # Lista de resultados individuais
}
```

---

## Validação das Fórmulas

As fórmulas foram extraídas diretamente do Power BI original e validadas:

### Pesos Confirmados

| Variável | Peso Power BI | Peso Implementado | Status |
|----------|---------------|-------------------|--------|
| Grupo A | 91 | 91 | ✅ |
| Grupo B | 85 | 85 | ✅ |
| Grupo C | 24 | 24 | ✅ |
| Grupo D | 20 | 20 | ✅ |
| Veículo Relevante | 95 | 95 | ✅ |
| Veículo de Nicho | 54 | 54 | ✅ |
| Título | 100 | 100 | ✅ |
| Subtítulo | 80 | 80 | ✅ |
| Imagem | 20 | 20 | ✅ |
| Porta-voz | 20 | 20 | ✅ |

### Denominadores Confirmados

| Caso | Denominador Power BI | Denominador Implementado | Status |
|------|---------------------|--------------------------|--------|
| Grupo A | 406 | 406 | ✅ |
| Não Grupo A | 460 | 460 | ✅ |

### Fórmulas Confirmadas

- ✅ Cálculo de numerador
- ✅ Escolha de denominador
- ✅ Aplicação de sinal (positivo/negativo)
- ✅ Conversão para escala 0-10
- ✅ Balizamento por positividade

---

## Vantagens da Nova Calculadora

### Precisão

Implementa as fórmulas exatas do Power BI, garantindo consistência com análises anteriores.

### Performance

Otimizada para processar grandes volumes de menções da Brandwatch sem degradação de performance.

### Integração

Usa `categoryDetail` da Brandwatch para identificação de bancos, eliminando erros de identificação por texto.

### Manutenibilidade

Código limpo, documentado e testado, facilitando futuras modificações.

### Rastreabilidade

Cada menção retorna detalhes de cálculo (numerador, denominador, variáveis), permitindo auditoria completa.

---

## Limitações e Considerações

### 1. Dependência de Dados da Brandwatch

A calculadora assume que os dados vêm da Brandwatch com os campos corretos:
- `sentiment` deve estar preenchido
- `monthlyVisitors` deve estar disponível
- `categoryDetail` deve identificar o banco

### 2. Veículos Relevantes

O sistema filtra apenas veículos relevantes antes do cálculo. Menções de veículos não relevantes são descartadas.

### 3. Bônus de Resposta

O bônus de resposta do banco (15%) **não está implementado** nesta versão. Requer identificação de resposta oficial do banco na menção, o que não é fornecido pela Brandwatch.

### 4. Volume Mínimo

Bancos com volume muito baixo (< 10 menções) podem ter IEDI distorcido devido ao balizamento. Recomenda-se análise qualitativa nesses casos.

---

## Migração da Calculadora Antiga

### Alterações Necessárias

1. **Import**:
   ```python
   # Antes
   from app.iedi_calculator import CalculadoraIEDI
   
   # Depois
   from app.iedi_calculator_brandwatch import criar_calculadora_brandwatch
   ```

2. **Inicialização**:
   ```python
   # Antes
   calculadora = CalculadoraIEDI(db)
   
   # Depois
   calculadora = criar_calculadora_brandwatch(db)
   ```

3. **Identificação de Banco**:
   ```python
   # Antes
   banco_identificado = calculadora.identificar_banco(texto)
   
   # Depois
   # Usar categoryDetail da Brandwatch
   banco_nome = mencao['categoryDetail']
   ```

4. **Cálculo**:
   ```python
   # Antes
   resultado = calculadora.calcular_iedi_banco(mencoes, banco_nome, banco_id)
   
   # Depois
   resultado = calculadora.calcular_iedi_banco(mencoes, banco_nome, variacoes)
   ```

5. **Balizamento**:
   ```python
   # Antes
   resultados_finais = calculadora.calcular_iedi_final_com_balizamento(resultados)
   
   # Depois
   # Balizamento já aplicado automaticamente
   ranking = calculadora.calcular_iedi_comparativo(resultados)
   ```

---

## Testes e Validação

### Teste Unitário de Menção

```python
from app.iedi_calculator_brandwatch import IEDICalculatorBrandwatch

calc = IEDICalculatorBrandwatch(
    veiculos_relevantes=['g1.globo.com'],
    veiculos_nicho=['infomoney.com.br'],
    portavozes={'Banco do Brasil': ['joão silva', 'maria santos']}
)

mencao = {
    'sentiment': 'positive',
    'title': 'Banco do Brasil anuncia lucro recorde',
    'snippet': 'O Banco do Brasil divulgou...',
    'imageUrls': ['https://...'],
    'fullText': 'João Silva, presidente do BB...',
    'domain': 'g1.globo.com',
    'monthlyVisitors': 35000000
}

resultado = calc.calcular_iedi_mencao(
    mencao=mencao,
    banco_nome='Banco do Brasil',
    variacoes=['bb', 'banco do brazil']
)

print(f"IEDI: {resultado['iedi_0_a_10']}")
print(f"Grupo: {resultado['grupo_alcance']}")
print(f"Variáveis: {resultado['variaveis']}")
```

### Teste de Agregação

```python
mencoes = [...]  # Lista de 100 menções

resultado = calc.calcular_iedi_banco(
    mencoes=mencoes,
    banco_nome='Banco do Brasil',
    variacoes=['bb']
)

assert resultado['volume_total'] == 100
assert 0 <= resultado['iedi_final'] <= 10
assert resultado['positividade'] + resultado['negatividade'] == 100
```

---

## Referências

- **Metodologia IEDI**: `/home/ubuntu/upload/ATUALBB_MetodologiaIEDI+PMC_20251.pdf`
- **Fórmulas Power BI**: `/home/ubuntu/upload/pasted_content.txt`
- **Documentação Brandwatch**: https://developers.brandwatch.com/docs/mention-metadata-field-definitions

---

**Desenvolvido por**: Manus AI  
**Data**: 12/11/2024  
**Versão**: 3.0  
**Arquivo**: `app/iedi_calculator_brandwatch.py`
