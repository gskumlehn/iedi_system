# Fórmulas IEDI - Extraídas do Power BI

## Estrutura do Cálculo IEDI

O cálculo do IEDI segue uma estrutura hierárquica de variáveis e pesos, culminando em um índice final de -1 a 1, que é então convertido para escala de 0 a 10.

---

## 1. Variáveis Binárias (Verificações)

Cada menção é avaliada em 6 variáveis binárias (0 ou 1):

### 1.1 Verificacao Qualificacao
- **Valor**: 1 se sentimento = "Positivas", 0 caso contrário
- **Significado**: Indica se a menção é positiva ou negativa

### 1.2 Verificacao Titulo
- **Valor**: 1 se banco aparece no título, 0 caso contrário
- **Campo Brandwatch**: `title`

### 1.3 Verificacao Subtitulo
- **Valor**: 1 se banco aparece no subtítulo/snippet, 0 caso contrário
- **Campo Brandwatch**: `snippet`

### 1.4 Verificacao Imagem
- **Valor**: 1 se menção possui imagem, 0 caso contrário
- **Campo Brandwatch**: `imageUrls` (se não vazio)

### 1.5 Verificacao Portavoz
- **Valor**: 1 se porta-voz do banco é mencionado, 0 caso contrário
- **Lógica**: Buscar nomes de porta-vozes cadastrados no texto

### 1.6 Verificacao Veiculo de Nicho
- **Valor**: 1 se veículo é de nicho, 0 caso contrário
- **Lógica**: Verificar se `domain` está na lista de veículos de nicho

---

## 2. Grupos de Alcance

Classificação por volume de visitas mensais do veículo:

### Grupo A
- **Critério**: `monthlyVisitors` > 29.000.000
- **Peso**: 91

### Grupo B
- **Critério**: 11.000.001 <= `monthlyVisitors` <= 29.000.000
- **Peso**: 85

### Grupo C
- **Critério**: 500.000 <= `monthlyVisitors` <= 11.000.000
- **Peso**: 24

### Grupo D
- **Critério**: `monthlyVisitors` < 500.000
- **Peso**: 20

**Nota**: Apenas um grupo é 1, os demais são 0 para cada menção.

---

## 3. Pesos das Variáveis

### Para Menções Positivas:

| Variável | Peso |
|----------|------|
| Grupo de Alcance (A/B/C/D) | 91/85/24/20 |
| Veículo Relevante (sempre 1) | 95 |
| Veículo de Nicho | 54 |
| Título | 100 |
| Subtítulo | 80 |
| Imagem | 20 |
| Porta-voz | 20 |

### Para Menções Negativas:
Os mesmos pesos, mas multiplicados por -1.

---

## 4. Fórmulas de Cálculo

### 4.1 Positiva e Grupo A

```
Numerador = (
    (Grupo_D * 20) +
    (Grupo_C * 24) +
    (Grupo_B * 85) +
    (Grupo_A * 91) +
    (1 * 95) +  // Veículo relevante
    (Verificacao_Veiculo_Nicho * 54) +
    (Verificacao_Titulo * 100) +
    (Verificacao_Subtitulo * 80) +
    (Verificacao_Imagem * 20) +
    (Verificacao_Portavoz * 20)
)

Denominador = (91 + 95 + 100 + 80 + 20 + 20) = 406

Resultado = Numerador / Denominador
```

### 4.2 Positiva e NÃO Grupo A

```
Numerador = (
    (Grupo_D * 20) +
    (Grupo_C * 24) +
    (Grupo_B * 85) +
    (Grupo_A * 91) +
    (1 * 95) +
    (Verificacao_Veiculo_Nicho * 54) +
    (Verificacao_Titulo * 100) +
    (Verificacao_Subtitulo * 80) +
    (Verificacao_Imagem * 20) +
    (Verificacao_Portavoz * 20)
)

Denominador = (91 + 95 + 54 + 100 + 80 + 20 + 20) = 460

Resultado = Numerador / Denominador
```

**Diferença**: Quando não é Grupo A, o denominador inclui o peso do veículo de nicho (54).

### 4.3 Negativa e Grupo A

```
Numerador = -1 * (
    (Grupo_D * 20) +
    (Grupo_C * 24) +
    (Grupo_B * 85) +
    (Grupo_A * 91) +
    (1 * 95) +
    (Verificacao_Veiculo_Nicho * 54) +
    (Verificacao_Titulo * 100) +
    (Verificacao_Subtitulo * 80) +
    (Verificacao_Imagem * 20) +
    (Verificacao_Portavoz * 20)
)

Denominador = (91 + 95 + 100 + 80 + 20 + 20) = 406

Resultado = Numerador / Denominador
```

### 4.4 Negativa e NÃO Grupo A

```
Numerador = -1 * (
    (Grupo_D * 20) +
    (Grupo_C * 24) +
    (Grupo_B * 85) +
    (Grupo_A * 91) +
    (1 * 95) +
    (Verificacao_Veiculo_Nicho * 54) +
    (Verificacao_Titulo * 100) +
    (Verificacao_Subtitulo * 80) +
    (Verificacao_Imagem * 20) +
    (Verificacao_Portavoz * 20)
)

Denominador = (91 + 95 + 54 + 100 + 80 + 20 + 20) = 460

Resultado = Numerador / Denominador
```

---

## 5. IEDI (-1 a 1)

```python
if Verificacao_Qualificacao == True and Grupo_A == 1:
    IEDI = Positiva_e_Grupo_A
elif Verificacao_Qualificacao == True and Grupo_A == 0:
    IEDI = Positiva_e_Nao_Grupo_A
elif Verificacao_Qualificacao == False and Grupo_A == 1:
    IEDI = Negativa_e_Grupo_A
elif Verificacao_Qualificacao == False and Grupo_A == 0:
    IEDI = Negativa_e_Nao_Grupo_A
else:
    IEDI = 0
```

**Resultado**: Valor entre -1 e 1 para cada menção.

---

## 6. Bônus (Resposta do Banco)

Se houver resposta ou posicionamento do banco na menção:

```python
if Resposta_BB == 1 and Verificacao_Qualificacao == False:
    # Menção negativa com resposta: minimiza impacto negativo
    Bonus = IEDI * 0.15 * -1
elif Resposta_BB == 1 and Verificacao_Qualificacao == True:
    # Menção positiva com resposta: amplifica impacto positivo
    Bonus = IEDI * 0.15
else:
    Bonus = 0

IEDI_com_Bonus = IEDI + Bonus
```

---

## 7. IEDI (0 a 10)

Conversão da escala -1 a 1 para 0 a 10:

```python
IEDI_0_a_10 = (10 * (IEDI + 1)) / 2
```

Com bônus:

```python
IEDI_com_Bonus_0_a_10 = (10 * (IEDI_com_Bonus + 1)) / 2

# Limitar ao máximo de 10
if IEDI_com_Bonus_0_a_10 > 10:
    IEDI_com_Bonus_0_a_10 = 10
```

---

## 8. Agregação por Banco

Para calcular o IEDI de um banco em um período:

1. **Calcular IEDI individual** de cada menção
2. **Média dos IEDIs** de todas as menções do banco
3. **Aplicar balizamento** (proporção de menções positivas)

### Balizamento

```python
Positividade = (Mencoes_Positivas / Total_Mencoes) * 100

# Fator de balizamento (quanto maior a positividade, maior o IEDI final)
IEDI_Final = IEDI_Medio * (Positividade / 100)
```

---

## 9. Indicadores Complementares

### Volume Positivo
```python
Volume_Positivo = COUNT(mencoes WHERE sentiment = "Positivas")
```

### Volume Negativo
```python
Volume_Negativo = COUNT(mencoes WHERE sentiment = "Negativas")
```

### Positividade %
```python
Positividade = (Volume_Positivo / Total_Mencoes) * 100
```

### Negatividade %
```python
Negatividade = (Volume_Negativo / Total_Mencoes) * 100
```

### Presença Positiva em Títulos
```python
Presenca_Titulos = COUNT(mencoes WHERE sentiment = "Positivas" AND Verificacao_Titulo = 1)
Presenca_Titulos_Perc = (Presenca_Titulos / Volume_Positivo) * 100
```

### Diversidade de Veículos Relevantes
```python
Diversidade = COUNT(DISTINCT domain WHERE sentiment = "Positivas" AND veiculo_relevante = 1)
```

### Diversidade por Grupo
```python
Diversidade_Grupo_A = COUNT(DISTINCT domain WHERE sentiment = "Positivas" AND Grupo_A = 1)
Diversidade_Grupo_B = COUNT(DISTINCT domain WHERE sentiment = "Positivas" AND Grupo_B = 1)
Diversidade_Grupo_C = COUNT(DISTINCT domain WHERE sentiment = "Positivas" AND Grupo_C = 1)
Diversidade_Grupo_D = COUNT(DISTINCT domain WHERE sentiment = "Positivas" AND Grupo_D = 1)
```

---

## 10. Mapeamento Brandwatch → IEDI

| Variável IEDI | Campo Brandwatch | Processamento |
|---------------|------------------|---------------|
| Verificacao_Qualificacao | `sentiment` | "positive" → 1, outros → 0 |
| Verificacao_Titulo | `title` | Buscar nome do banco no título |
| Verificacao_Subtitulo | `snippet` | Buscar nome do banco no snippet |
| Verificacao_Imagem | `imageUrls` | len(imageUrls) > 0 → 1 |
| Verificacao_Portavoz | `fullText` | Buscar porta-vozes cadastrados |
| Verificacao_Veiculo_Nicho | `domain` | Verificar se está na lista de nichos |
| Grupo_A/B/C/D | `monthlyVisitors` | Classificar por faixa de visitas |
| Veiculo_Relevante | `domain` | Verificar se está na lista de relevantes |

---

## Notas Importantes

1. **Veículo Relevante**: No Power BI, sempre vale 1 (peso 95). No nosso sistema, filtramos apenas veículos relevantes, então sempre será 1.

2. **Denominadores Diferentes**: 
   - Grupo A: 406 (não inclui peso de nicho)
   - Não Grupo A: 460 (inclui peso de nicho)

3. **Bônus**: Implementação opcional. Requer identificação de resposta do banco na menção.

4. **Escala Final**: O IEDI final está na escala 0-10, mas o cálculo intermediário usa -1 a 1.

5. **Balizamento**: Fundamental para comparar bancos com volumes diferentes de menções.
