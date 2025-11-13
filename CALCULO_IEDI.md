# Cálculo do IEDI - Índice de Exposição Digital na Imprensa

## Visão Geral

O **IEDI** é um índice que mede a qualidade da exposição de um banco na imprensa digital, considerando múltiplas variáveis que indicam relevância, alcance e posicionamento da menção.

O cálculo é feito em **duas etapas**:
1. **IEDI por Menção**: Cada notícia recebe uma nota de 0 a 10
2. **IEDI Agregado**: As notas são agregadas por banco e balizadas pela positividade

---

## Etapa 1: Cálculo do IEDI por Menção

Cada menção (notícia) da Brandwatch recebe uma nota individual baseada em **6 verificações binárias** e **1 classificação de alcance**.

### Fórmula Base

```
IEDI_Base = Numerador / Denominador
```

Onde:
- **Numerador** = Soma dos pesos das variáveis presentes
- **Denominador** = Soma máxima possível de pesos (depende do grupo de alcance)

### Variáveis e Pesos

| Variável | Peso | Verificação |
|----------|------|-------------|
| **Grupo de Alcance** | 20-91 | Baseado em acessos mensais do veículo |
| **Veículo Relevante** | 95 | Veículo está na lista de relevantes |
| **Veículo de Nicho** | 54 | Veículo está na lista de nicho |
| **Título** | 100 | Nome do banco aparece no título |
| **Subtítulo/1º Parágrafo** | 80 | Nome do banco no snippet |
| **Imagem** | 20 | Menção possui imagem |
| **Porta-voz** | 20 | Porta-voz do banco é mencionado |

### Classificação de Alcance

Baseado no campo `monthlyVisitors` da Brandwatch:

| Grupo | Acessos Mensais | Peso |
|-------|----------------|------|
| **A** | ≥ 29.000.001 | 91 |
| **B** | 11.000.001 - 29.000.000 | 85 |
| **C** | 500.000 - 11.000.000 | 24 |
| **D** | 0 - 500.000 | 20 |

### Denominadores

O denominador varia conforme o grupo de alcance:

**Grupo A**:
```
Denominador = 91 + 95 + 100 + 80 + 20 + 20 = 406
```
*(Não inclui peso de nicho pois Grupo A já tem peso máximo de alcance)*

**Grupos B, C e D**:
```
Denominador = 91 + 95 + 54 + 100 + 80 + 20 + 20 = 460
```
*(Inclui peso de nicho para compensar menor alcance)*

### Aplicação de Sinal

O IEDI Base é multiplicado por **-1** se a menção for **negativa**:

```python
if sentiment == "negative":
    IEDI_Base = IEDI_Base * -1
```

Isso resulta em um valor entre **-1 e 1**.

### Conversão para Escala 0-10

```
IEDI_Mencao = (10 * IEDI_Base + 1) / 2
```

Esta fórmula converte:
- **-1** → **0** (pior nota)
- **0** → **5** (neutro)
- **1** → **10** (melhor nota)

### Exemplo de Cálculo

**Menção Positiva do Banco do Brasil**:
- Veículo: G1 (Grupo A, 313M acessos mensais)
- Título: "Banco do Brasil anuncia lucro recorde"
- Snippet: "O Banco do Brasil divulgou..."
- Imagem: Sim
- Porta-voz: "Tarciana Medeiros, presidente do BB"
- Sentiment: positive

**Cálculo**:
```
Numerador = 91 (Grupo A) + 95 (Relevante) + 100 (Título) + 80 (Subtítulo) + 20 (Imagem) + 20 (Porta-voz)
Numerador = 406

Denominador = 406 (Grupo A)

IEDI_Base = 406 / 406 = 1.0

Como é positiva, mantém o sinal:
IEDI_Base = 1.0

Conversão para 0-10:
IEDI_Mencao = (10 * 1.0 + 1) / 2 = 5.5
```

**Nota Final da Menção: 5.5**

---

## Etapa 2: Agregação por Banco

Após calcular o IEDI de cada menção, agregamos por banco no período da análise.

### IEDI Médio

```
IEDI_Medio = Soma(IEDI_Mencoes) / Total_Mencoes
```

### Métricas Complementares

- **Volume Total**: Quantidade total de menções
- **Volume Positivo**: Menções com sentiment = "positive"
- **Volume Negativo**: Menções com sentiment = "negative"
- **Volume Neutro**: Menções com sentiment = "neutral"
- **Positividade**: `(Volume_Positivo / Volume_Total) * 100`
- **Negatividade**: `(Volume_Negativo / Volume_Total) * 100`

### Balizamento

O IEDI Final é **balizando pela positividade**:

```
Proporcao_Positivas = Volume_Positivo / Volume_Total

IEDI_Final = IEDI_Medio * Proporcao_Positivas
```

**Lógica**: Um banco com muitas menções negativas terá seu IEDI reduzido, mesmo que as menções positivas sejam de alta qualidade.

### Exemplo de Agregação

**Banco do Brasil - Abril 2025**:
- 150 menções totais
- 120 positivas
- 20 negativas
- 10 neutras
- IEDI Médio: 6.8

**Cálculo**:
```
Proporcao_Positivas = 120 / 150 = 0.80

IEDI_Final = 6.8 * 0.80 = 5.44
```

**IEDI Final do BB: 5.44**

---

## Agregação por Período

### Análise com Período Único

Quando `periodo_personalizado = False`:
- Todos os bancos usam o mesmo `data_inicio` e `data_fim` da análise
- Menções são filtradas por:
  - `data_mencao >= data_inicio`
  - `data_mencao <= data_fim`
  - `categoryDetail` = nome do banco

### Análise com Período Personalizado

Quando `periodo_personalizado = True`:
- Cada banco pode ter `data_inicio` e `data_fim` diferentes
- Períodos são armazenados na tabela `periodos_banco`
- Útil para análises de resultados trimestrais onde cada banco divulga em datas diferentes

**Exemplo**:
```
Análise: "Resultados 1T2025"
- Banco do Brasil: 13/05/2025 00:00 - 15/05/2025 23:59 (2 dias após divulgação)
- Itaú: 14/05/2025 00:00 - 16/05/2025 23:59
- Bradesco: 15/05/2025 00:00 - 17/05/2025 23:59
- Santander: 16/05/2025 00:00 - 18/05/2025 23:59
```

Cada banco é analisado no seu período específico, mas o IEDI Final é comparável pois a metodologia de cálculo é a mesma.

---

## Ranking Comparativo

Após calcular o IEDI Final de todos os bancos:

1. **Ordenar** por IEDI Final (decrescente)
2. **Atribuir posições**: 1º, 2º, 3º, 4º
3. **Calcular média do setor**: `Média = Soma(IEDIs) / 4`
4. **Comparar** cada banco com a média

**Indicadores**:
- 🟢 **Acima da média**: IEDI > Média
- 🔴 **Abaixo da média**: IEDI < Média

---

## Rastreabilidade

Cada menção armazena:
- **nota**: IEDI da menção (0-10)
- **variaveis**: JSON com detalhes das verificações

Exemplo de `variaveis`:
```json
{
  "verificacao_titulo": 1,
  "verificacao_subtitulo": 1,
  "verificacao_imagem": 1,
  "verificacao_portavoz": 1,
  "verificacao_veiculo_nicho": 0,
  "grupo_alcance": "A",
  "peso_alcance": 91,
  "numerador": 406,
  "denominador": 406,
  "iedi_base": 1.0
}
```

Isso permite auditoria completa do cálculo.

---

## Resumo da Metodologia

1. **Coleta**: Extrair menções da Brandwatch no período definido
2. **Filtragem**: Apenas menções de imprensa (mediaType = News)
3. **Identificação**: Usar `categoryDetail` para identificar o banco
4. **Cálculo Individual**: Aplicar fórmula para cada menção
5. **Agregação**: Calcular IEDI Médio por banco
6. **Balizamento**: Aplicar proporção de menções positivas
7. **Ranking**: Ordenar e comparar bancos

---

## Vantagens da Metodologia

✅ **Objetiva**: Baseada em variáveis mensuráveis  
✅ **Comparável**: Mesma fórmula para todos os bancos  
✅ **Flexível**: Funciona para qualquer período  
✅ **Rastreável**: Cada nota pode ser auditada  
✅ **Balanceada**: Considera qualidade E quantidade  
✅ **Justa**: Balizamento evita distorções por volume

---

**Desenvolvido por**: Manus AI  
**Data**: 12/11/2024  
**Versão**: 4.0
