# Metodologia de Cálculo do IEDI - Versão 2.0

## Índice de Exposição Digital na Imprensa (IEDI)

O IEDI é um índice que mede a exposição de bancos na imprensa digital brasileira, considerando tanto a quantidade quanto a qualidade das menções.

---

## Mudanças da Versão 2.0

Esta versão atualiza a metodologia original para refletir as limitações atuais de dados e implementação:

**Removido**:
- ❌ **Porta-vozes**: Removido do cálculo (peso 20) até que seja estabelecida uma lista completa e atualizada de porta-vozes dos bancos
- ❌ **Imagens**: Removido do cálculo (peso 20) até que seja implementado um sistema de reconhecimento de logotipos/marcas dos bancos em imagens

**Modificado**:
- ✏️ **Subtítulo**: Agora é verificado **condicionalmente** - apenas quando `snippet ≠ fullText` (detalhes abaixo)

---

## Variáveis do IEDI v2.0

O IEDI é calculado com base em **4 variáveis binárias** (0 ou 1) para cada menção:

| Variável | Peso | Descrição |
|----------|------|-----------|
| **Qualificação** | - | Sentimento da menção (positivo/negativo/neutro) |
| **Título** | 100 | Banco mencionado no título da matéria |
| **Subtítulo** | 80 | Banco mencionado no primeiro parágrafo (condicional) |
| **Veículo Relevante** | 95 | Matéria publicada em veículo da lista relevante |
| **Veículo de Nicho** | 54 | Matéria publicada em veículo especializado |
| **Grupo de Alcance** | 20-91 | Classificação por acessos mensais do veículo |

---

## Grupos de Alcance

Os veículos são classificados em 4 grupos baseados em **acessos mensais**:

| Grupo | Acessos Mensais | Peso |
|-------|-----------------|------|
| **A** | > 29.000.000 | 91 |
| **B** | 11.000.001 - 29.000.000 | 85 |
| **C** | 500.000 - 11.000.000 | 24 |
| **D** | 0 - 500.000 | 20 |

---

## Cálculo do IEDI por Menção

### Fórmula Base

Para cada menção, o IEDI é calculado da seguinte forma:

```
IEDI_Mencao = (Numerador / Denominador) × Sinal
```

Onde:
- **Numerador**: Soma dos pesos das variáveis verificadas
- **Denominador**: Soma dos pesos máximos possíveis (varia por grupo)
- **Sinal**: +1 para menções positivas, -1 para negativas

### Numerador

O numerador é a soma dos pesos de todas as variáveis que foram verificadas:

```python
numerador = 0

# 1. Título (sempre verificado)
if banco_mencionado_no_titulo:
    numerador += 100

# 2. Subtítulo (verificação condicional)
if snippet != fullText:  # Apenas se forem diferentes
    if banco_mencionado_no_primeiro_paragrafo:
        numerador += 80

# 3. Grupo de Alcance (sempre verificado)
if grupo == "A":
    numerador += 91
elif grupo == "B":
    numerador += 85
elif grupo == "C":
    numerador += 24
elif grupo == "D":
    numerador += 20

# 4. Veículo Relevante (sempre verificado)
if veiculo_na_lista_relevante:
    numerador += 95

# 5. Veículo de Nicho (sempre verificado)
if veiculo_na_lista_nicho:
    numerador += 54
```

### Denominador

O denominador varia dependendo do **Grupo de Alcance** e se a **verificação de subtítulo foi realizada**:

#### Grupo A (> 29M acessos)

```python
# Veículo de Nicho NÃO é incluído no denominador para Grupo A
if snippet != fullText:
    denominador = 100 + 80 + 91 + 95 = 366
else:
    denominador = 100 + 91 + 95 = 286
```

#### Grupos B, C, D

```python
# Veículo de Nicho É incluído no denominador
if snippet != fullText:
    denominador = 100 + 80 + peso_grupo + 95 + 54
else:
    denominador = 100 + peso_grupo + 95 + 54
```

**Tabela de Denominadores**:

| Grupo | Com Subtítulo | Sem Subtítulo |
|-------|---------------|---------------|
| **A** | 366 | 286 |
| **B** | 414 | 334 |
| **C** | 353 | 273 |
| **D** | 349 | 269 |

### Sinal (Qualificação)

O sinal é determinado pelo **sentimento** da menção:

```python
if sentiment == "positive":
    sinal = +1
elif sentiment == "negative":
    sinal = -1
else:  # neutral
    sinal = 0  # Menções neutras não contribuem para o IEDI
```

### Conversão para Escala 0-10

O resultado da fórmula base está na escala **-1 a 1**. Para converter para **0 a 10**:

```python
iedi_mencao_0_10 = ((iedi_mencao + 1) / 2) × 10
```

**Exemplo**:
- IEDI = 0.5 → `((0.5 + 1) / 2) × 10 = 7.5`
- IEDI = -0.3 → `((-0.3 + 1) / 2) × 10 = 3.5`

---

## Lógica Condicional do Subtítulo

### Por que a verificação é condicional?

A Brandwatch fornece dois campos relacionados ao texto da menção:

1. **`snippet`**: "Snippet of the mention text that best matches the query" [1]
2. **`title`**: "Title of the mention, as determined by Brandwatch" [1]

Segundo a documentação oficial da Brandwatch [1], o `snippet` é um **trecho do texto da menção que melhor corresponde à query de busca**, não necessariamente o primeiro parágrafo ou subtítulo.

### Problema Identificado

Em muitos casos, especialmente para **imprensa digital paga** (paywalls), o texto completo da notícia não está disponível para a Brandwatch. Nesses casos:

- O `snippet` pode ser uma fração pequena do texto
- O `snippet` pode não ser o início da matéria
- Não há garantia de que o `snippet` representa o subtítulo/primeiro parágrafo

### Solução Implementada

Para garantir que estamos de fato analisando o **subtítulo/primeiro parágrafo** e não apenas um trecho aleatório que corresponde à query:

```python
# Verificar se snippet é diferente de fullText
if snippet != fullText:
    # Neste caso, temos acesso ao texto completo
    # Podemos extrair o primeiro parágrafo com segurança
    primeiro_paragrafo = extrair_primeiro_paragrafo(fullText)
    
    if banco_mencionado_em(primeiro_paragrafo):
        verificacao_subtitulo = 1
        numerador += 80
        denominador += 80  # Adiciona peso ao denominador também
    else:
        verificacao_subtitulo = 0
        denominador += 80  # Peso ainda conta no denominador
else:
    # snippet == fullText significa que não temos texto completo
    # NÃO fazemos a verificação de subtítulo
    # NÃO adicionamos o peso ao denominador
    verificacao_subtitulo = None  # Não aplicável
```

### Impacto no Cálculo

**Caso 1: Texto completo disponível** (`snippet ≠ fullText`)
```
Denominador inclui peso do subtítulo (80)
Numerador pode incluir 80 se banco for mencionado
```

**Caso 2: Apenas snippet disponível** (`snippet == fullText`)
```
Denominador NÃO inclui peso do subtítulo
Numerador NÃO pode incluir 80
Cálculo permanece proporcional e justo
```

### Extração do Primeiro Parágrafo

Quando `snippet ≠ fullText`, o primeiro parágrafo é extraído do `fullText`:

```python
def extrair_primeiro_paragrafo(fullText: str) -> str:
    """
    Extrai o primeiro parágrafo do texto completo.
    
    Considera como parágrafo:
    - Texto até a primeira quebra dupla de linha (\n\n)
    - Ou os primeiros 300 caracteres se não houver quebra
    """
    paragrafos = fullText.split('\n\n')
    
    if len(paragrafos) > 1:
        return paragrafos[0].strip()
    else:
        # Sem quebras duplas, pega os primeiros 300 caracteres
        return fullText[:300].strip()
```

---

## Agregação por Período

### IEDI Médio

Para cada banco, calculamos a **média aritmética** dos IEDIs de todas as menções no período:

```python
iedi_medio = sum(iedi_mencoes) / total_mencoes
```

### Balizamento por Positividade

O **IEDI Final** é o IEDI Médio ajustado pela **proporção de menções positivas**:

```python
proporcao_positivas = volume_positivo / volume_total

iedi_final = iedi_medio × proporcao_positivas
```

**Justificativa**: Este balizamento penaliza bancos com muitas menções negativas, mesmo que tenham alta exposição. Um banco com 100 menções mas 90% negativas terá IEDI Final muito menor que um banco com 50 menções e 80% positivas.

### Métricas Complementares

Além do IEDI Final, calculamos:

| Métrica | Fórmula | Descrição |
|---------|---------|-----------|
| **Volume Total** | `count(mencoes)` | Total de menções no período |
| **Volume Positivo** | `count(sentiment == "positive")` | Menções positivas |
| **Volume Negativo** | `count(sentiment == "negative")` | Menções negativas |
| **Volume Neutro** | `count(sentiment == "neutral")` | Menções neutras |
| **Positividade** | `(volume_positivo / volume_total) × 100` | % de menções positivas |
| **Negatividade** | `(volume_negativo / volume_total) × 100` | % de menções negativas |

---

## Exemplo Completo

### Cenário: Menção do Banco do Brasil

**Dados da Menção**:
- **Título**: "Banco do Brasil anuncia lucro recorde no trimestre"
- **Snippet**: "O Banco do Brasil divulgou ontem seus resultados..."
- **FullText**: "O Banco do Brasil divulgou ontem seus resultados trimestrais, superando as expectativas do mercado. A instituição registrou lucro líquido de R$ 8,2 bilhões..."
- **Domínio**: valor.globo.com (Valor Econômico)
- **Acessos Mensais**: 14.000.000 (Grupo C)
- **Sentimento**: positive

**Verificações**:

1. **Título**: ✅ "Banco do Brasil" está no título → +100
2. **Subtítulo**: 
   - `snippet ≠ fullText`? ✅ Sim (são diferentes)
   - "Banco do Brasil" no primeiro parágrafo? ✅ Sim → +80
3. **Grupo C**: 14M acessos → +24
4. **Veículo Relevante**: Valor Econômico está na lista → +95
5. **Veículo de Nicho**: Valor Econômico está na lista de nicho → +54

**Cálculo**:

```python
# Numerador
numerador = 100 + 80 + 24 + 95 + 54 = 353

# Denominador (Grupo C com subtítulo)
denominador = 100 + 80 + 24 + 95 + 54 = 353

# IEDI (-1 a 1)
iedi = (353 / 353) × (+1) = 1.0

# IEDI (0 a 10)
iedi_0_10 = ((1.0 + 1) / 2) × 10 = 10.0
```

**Resultado**: Esta menção recebe **IEDI = 10.0** (máximo possível), pois atende a todos os critérios com sentimento positivo.

### Cenário 2: Menção Negativa sem Texto Completo

**Dados da Menção**:
- **Título**: "Bancos enfrentam críticas por tarifas abusivas"
- **Snippet**: "Bancos enfrentam críticas por tarifas abusivas" (mesmo que fullText)
- **FullText**: "Bancos enfrentam críticas por tarifas abusivas" (paywall bloqueou)
- **Domínio**: folha.uol.com.br (Folha de S.Paulo)
- **Acessos Mensais**: 150.000.000 (Grupo A)
- **Sentimento**: negative

**Verificações**:

1. **Título**: ❌ "Banco do Brasil" não está no título (menciona "Bancos" genericamente) → 0
2. **Subtítulo**: 
   - `snippet == fullText`? ✅ Sim (são iguais - paywall)
   - Verificação NÃO é realizada (peso não entra no denominador)
3. **Grupo A**: 150M acessos → +91
4. **Veículo Relevante**: Folha de S.Paulo está na lista → +95
5. **Veículo de Nicho**: ❌ Não está na lista de nicho → 0

**Cálculo**:

```python
# Numerador
numerador = 0 + 91 + 95 + 0 = 186

# Denominador (Grupo A SEM subtítulo - paywall)
denominador = 100 + 91 + 95 = 286

# IEDI (-1 a 1)
iedi = (186 / 286) × (-1) = -0.65

# IEDI (0 a 10)
iedi_0_10 = ((-0.65 + 1) / 2) × 10 = 1.75
```

**Resultado**: Esta menção recebe **IEDI = 1.75**, refletindo:
- Menção negativa (sinal negativo)
- Banco não citado no título
- Veículo de alto alcance mas não especializado
- Texto completo indisponível (sem penalização adicional)

---

## Ranking Comparativo

Após calcular o IEDI Final de cada banco, geramos um **ranking** ordenado:

```python
ranking = sorted(resultados, key=lambda x: x.iedi_final, reverse=True)

for posicao, banco in enumerate(ranking, start=1):
    print(f"{posicao}º - {banco.name}: {banco.iedi_final:.2f}")
```

**Exemplo de Ranking**:

| Posição | Banco | IEDI Final | Volume | Positividade |
|---------|-------|------------|--------|--------------|
| 1º | Itaú | 7.85 | 245 | 82% |
| 2º | Banco do Brasil | 7.42 | 312 | 75% |
| 3º | Bradesco | 6.91 | 198 | 71% |
| 4º | Santander | 6.23 | 176 | 68% |

---

## Comparação v1.0 vs v2.0

| Aspecto | v1.0 | v2.0 |
|---------|------|------|
| **Porta-vozes** | Incluído (peso 20) | ❌ Removido |
| **Imagens** | Incluído (peso 20) | ❌ Removido |
| **Subtítulo** | Sempre verificado | ✅ Condicional (`snippet ≠ fullText`) |
| **Denominador Grupo A** | 406 (sem subtítulo) / 486 (com) | 286 (sem subtítulo) / 366 (com) |
| **Denominador Grupo B** | 460 (sem subtítulo) / 540 (com) | 334 (sem subtítulo) / 414 (com) |
| **Denominador Grupo C** | 399 (sem subtítulo) / 479 (com) | 273 (sem subtítulo) / 353 (com) |
| **Denominador Grupo D** | 395 (sem subtítulo) / 475 (com) | 269 (sem subtítulo) / 349 (com) |

### Impacto das Mudanças

**Remoção de Porta-vozes e Imagens**:
- Reduz denominador em 40 pontos
- Simplifica implementação
- Mantém proporcionalidade do cálculo
- Permite implementação imediata sem dependências externas

**Subtítulo Condicional**:
- Garante precisão da análise
- Evita falsos positivos de paywalls
- Mantém justiça comparativa entre menções
- Denominador se ajusta automaticamente

---

## Referências

[1] Brandwatch. (2024). *Mention Field Definitions*. Brandwatch Developer Documentation. https://developers.brandwatch.com/docs/mention-metadata-field-definitions

---

**Desenvolvido por**: Manus AI  
**Data**: 13/11/2024  
**Versão**: 2.0
