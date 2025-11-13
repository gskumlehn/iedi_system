# Mapeamento Brandwatch → IEDI v2.0

## Campos da API Brandwatch Utilizados no Cálculo do IEDI

Este documento mapeia diretamente os campos da API da Brandwatch para as variáveis do IEDI v2.0.

---

## Tabela de Mapeamento

| Campo Brandwatch | Variável IEDI | Uso | Peso |
|------------------|---------------|-----|------|
| `sentiment` | Qualificação | Determina o sinal (+1/-1) | - |
| `title` | Título | Verifica menção no título | 100 |
| `snippet` | Subtítulo (condicional) | Comparação com fullText | 80 |
| `fullText` | Subtítulo (condicional) | Extração do 1º parágrafo | 80 |
| `domain` | Veículo Relevante | Verifica se está na lista | 95 |
| `domain` | Veículo de Nicho | Verifica se está na lista | 54 |
| `monthlyVisitors` | Grupo de Alcance | Classifica em A/B/C/D | 20-91 |
| `categoryDetail` | Identificação do Banco | Segregação por banco | - |

---

## Detalhamento por Campo

### 1. `sentiment` - Qualificação

**Tipo**: String  
**Valores possíveis**: `"positive"`, `"negative"`, `"neutral"`

**Uso no IEDI**:
```python
if sentiment == "positive":
    sinal = +1
elif sentiment == "negative":
    sinal = -1
else:  # neutral
    sinal = 0  # Menção não contribui para o IEDI
```

**Observações**:
- Determina se a menção é favorável ou desfavorável ao banco
- Menções neutras não contribuem para o IEDI (sinal = 0)
- O sentimento é aplicado como multiplicador no cálculo final

---

### 2. `title` - Título

**Tipo**: String  
**Definição**: "Title of the mention, as determined by Brandwatch" [1]

**Uso no IEDI**:
```python
def verificar_titulo(title: str, banco: Bank) -> int:
    """
    Verifica se o banco é mencionado no título.
    
    Args:
        title: Título da menção
        banco: Objeto Bank com name e variations
    
    Returns:
        100 se banco mencionado, 0 caso contrário
    """
    title_lower = title.lower()
    
    # Verifica nome principal
    if banco.name.lower() in title_lower:
        return 100
    
    # Verifica variações
    for variacao in banco.variations:
        if variacao.lower() in title_lower:
            return 100
    
    return 0
```

**Peso**: 100 pontos

---

### 3. `snippet` e `fullText` - Subtítulo (Condicional)

**Tipo**: String  
**Definições**:
- `snippet`: "Snippet of the mention text that best matches the query" [1]
- `fullText`: Texto completo da menção (não documentado explicitamente, mas disponível na API)

**Uso no IEDI**:
```python
def verificar_subtitulo(snippet: str, fullText: str, banco: Bank) -> tuple[int, bool]:
    """
    Verifica se o banco é mencionado no primeiro parágrafo.
    APENAS se snippet ≠ fullText (texto completo disponível).
    
    Args:
        snippet: Snippet da menção
        fullText: Texto completo da menção
        banco: Objeto Bank com name e variations
    
    Returns:
        (pontos, verificacao_realizada)
        - (80, True) se banco mencionado e verificação realizada
        - (0, True) se banco não mencionado mas verificação realizada
        - (0, False) se verificação não foi realizada (paywall)
    """
    # Verificar se temos texto completo
    if snippet == fullText:
        # Paywall ou texto curto - não verificar
        return (0, False)
    
    # Extrair primeiro parágrafo
    primeiro_paragrafo = extrair_primeiro_paragrafo(fullText)
    
    # Verificar menção do banco
    paragrafo_lower = primeiro_paragrafo.lower()
    
    # Verifica nome principal
    if banco.name.lower() in paragrafo_lower:
        return (80, True)
    
    # Verifica variações
    for variacao in banco.variations:
        if variacao.lower() in paragrafo_lower:
            return (80, True)
    
    return (0, True)


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

**Peso**: 80 pontos (apenas quando `snippet ≠ fullText`)

**Observações**:
- A verificação só é realizada quando `snippet ≠ fullText`
- Quando `snippet == fullText`, assume-se paywall ou texto muito curto
- O peso de 80 **só é adicionado ao denominador** quando a verificação é realizada
- Isso mantém a proporcionalidade do cálculo

---

### 4. `domain` - Veículo Relevante

**Tipo**: String  
**Definição**: "Domain name of the website from which the mention originated" [1]

**Uso no IEDI**:
```python
def verificar_veiculo_relevante(domain: str, veiculos_relevantes: List[RelevantMediaOutlet]) -> int:
    """
    Verifica se o domínio está na lista de veículos relevantes.
    
    Args:
        domain: Domínio da menção (ex: "valor.globo.com")
        veiculos_relevantes: Lista de veículos relevantes
    
    Returns:
        95 se veículo relevante, 0 caso contrário
    """
    for veiculo in veiculos_relevantes:
        if domain.endswith(veiculo.domain) or veiculo.domain in domain:
            return 95
    
    return 0
```

**Peso**: 95 pontos

**Veículos Relevantes** (41 no total):
- Agência Brasil, Band, BandNews, BBC Brasil, Bloomberg, Bloomberg Línea
- Brasil 247, Carta Capital, CNN Brasil, Correio Braziliense
- E-Investidor, Época Negócios, Estadão, Exame
- Folha de S. Paulo, Forbes Brasil, G1, Globo News, Globo Rural
- InfoMoney, IstoÉ, IstoÉ Dinheiro, Jovem Pan
- Metrópoles, Money Times, O Antagonista, O Globo
- Poder 360, R7, Reuters, Revista Piauí
- Safras & Mercado, Seu Dinheiro, Terra, CNBC
- TV Globo, UOL, Valor Econômico, Valor Investe, Veja

---

### 5. `domain` - Veículo de Nicho

**Tipo**: String

**Uso no IEDI**:
```python
def verificar_veiculo_nicho(domain: str, veiculos_nicho: List[NicheMediaOutlet]) -> int:
    """
    Verifica se o domínio está na lista de veículos de nicho.
    
    Args:
        domain: Domínio da menção
        veiculos_nicho: Lista de veículos de nicho
    
    Returns:
        54 se veículo de nicho, 0 caso contrário
    """
    for veiculo in veiculos_nicho:
        if domain.endswith(veiculo.domain) or veiculo.domain in domain:
            return 54
    
    return 0
```

**Peso**: 54 pontos

**Veículos de Nicho** (22 no total):
- Agência Pública, Agência Spotlight, AzMina, Capital Digital
- Congresso em Foco, Época Negócios, Forbes Brasil
- Globo News, Globo Rural, InfoMoney, Investing.com
- IstoÉ Dinheiro, Le Monde Diplomatique Brasil, MoneyTimes
- Pequenas Empresas Grandes Negócios, Poder 360
- Repórter Brasil, Seu Dinheiro, The Brazilian Report
- The Intercept, Valor Econômico, Valor Investe

**Observação**: Alguns veículos aparecem em ambas as listas (relevante e nicho), recebendo ambos os pesos.

---

### 6. `monthlyVisitors` - Grupo de Alcance

**Tipo**: Integer  
**Definição**: "Total number of unique visitors who have been to the website that month" [1]

**Uso no IEDI**:
```python
def classificar_grupo_alcance(monthly_visitors: int) -> tuple[str, int]:
    """
    Classifica o veículo em grupo de alcance baseado em acessos mensais.
    
    Args:
        monthly_visitors: Número de visitantes únicos mensais
    
    Returns:
        (grupo, peso)
    """
    if monthly_visitors > 29_000_000:
        return ("A", 91)
    elif monthly_visitors > 11_000_000:
        return ("B", 85)
    elif monthly_visitors >= 500_000:
        return ("C", 24)
    else:
        return ("D", 20)
```

**Pesos por Grupo**:
| Grupo | Acessos Mensais | Peso |
|-------|-----------------|------|
| A | > 29.000.000 | 91 |
| B | 11.000.001 - 29.000.000 | 85 |
| C | 500.000 - 11.000.000 | 24 |
| D | 0 - 500.000 | 20 |

**Observação**: O Grupo A tem tratamento especial no denominador (não inclui peso de veículo de nicho).

---

### 7. `categoryDetail` - Identificação do Banco

**Tipo**: String (array de objetos na verdade)  
**Definição**: "Array of the details for each of the categories that is applied to the mention" [1]

**Estrutura**:
```json
{
  "categoryDetails": [
    {
      "id": 123,
      "name": "Banco do Brasil",
      "parentId": 100,
      "parentName": "Bancos"
    }
  ]
}
```

**Uso no IEDI**:
```python
def identificar_banco(category_details: List[dict], bancos: List[Bank]) -> Optional[Bank]:
    """
    Identifica qual banco é referenciado pela categoria da menção.
    
    Args:
        category_details: Array de categoryDetails da Brandwatch
        bancos: Lista de bancos cadastrados
    
    Returns:
        Objeto Bank correspondente ou None
    """
    if not category_details:
        return None
    
    # Pegar o nome da primeira categoria
    category_name = category_details[0]["name"]
    
    # Buscar banco correspondente
    for banco in bancos:
        if banco.name.lower() == category_name.lower():
            return banco
        
        # Verificar variações
        for variacao in banco.variations:
            if variacao.lower() == category_name.lower():
                return banco
    
    return None
```

**Observações**:
- Este campo é configurado na **query da Brandwatch**
- Permite segregação automática de menções por banco
- Essencial para análises com query unificada (todos os bancos em uma query)

---

## Campos Removidos da v1.0

### ❌ `imageUrls` - Imagens

**Motivo da Remoção**: Não há sistema de reconhecimento de logotipos/marcas dos bancos implementado.

**Código Original** (não usar):
```python
# NÃO IMPLEMENTAR
def verificar_imagem(image_urls: List[str]) -> int:
    # Requer sistema de reconhecimento de imagem
    pass
```

**Peso Removido**: 20 pontos

---

### ❌ Porta-vozes (campo não existe na Brandwatch)

**Motivo da Remoção**: Não há lista completa e atualizada de porta-vozes dos bancos.

**Código Original** (não usar):
```python
# NÃO IMPLEMENTAR
def verificar_portavoz(fullText: str, portavozes: List[Spokesperson]) -> int:
    # Requer lista atualizada de porta-vozes
    pass
```

**Peso Removido**: 20 pontos

---

## Exemplo Completo de Processamento

```python
def calcular_iedi_mencao(mencao: dict, banco: Bank, 
                         veiculos_relevantes: List[RelevantMediaOutlet],
                         veiculos_nicho: List[NicheMediaOutlet]) -> dict:
    """
    Calcula o IEDI de uma menção individual.
    
    Args:
        mencao: Dados da menção da Brandwatch
        banco: Banco sendo analisado
        veiculos_relevantes: Lista de veículos relevantes
        veiculos_nicho: Lista de veículos de nicho
    
    Returns:
        Dict com resultado do cálculo
    """
    # 1. Extrair campos
    sentiment = mencao["sentiment"]
    title = mencao["title"]
    snippet = mencao["snippet"]
    fullText = mencao.get("fullText", snippet)  # Fallback para snippet
    domain = mencao["domain"]
    monthly_visitors = mencao["monthlyVisitors"]
    
    # 2. Verificações
    titulo_pts = verificar_titulo(title, banco)
    subtitulo_pts, subtitulo_verificado = verificar_subtitulo(snippet, fullText, banco)
    veiculo_relevante_pts = verificar_veiculo_relevante(domain, veiculos_relevantes)
    veiculo_nicho_pts = verificar_veiculo_nicho(domain, veiculos_nicho)
    grupo, grupo_pts = classificar_grupo_alcance(monthly_visitors)
    
    # 3. Calcular numerador
    numerador = titulo_pts + subtitulo_pts + grupo_pts + veiculo_relevante_pts + veiculo_nicho_pts
    
    # 4. Calcular denominador
    if grupo == "A":
        # Grupo A não inclui veículo de nicho no denominador
        denominador = 100 + grupo_pts + veiculo_relevante_pts
    else:
        denominador = 100 + grupo_pts + veiculo_relevante_pts + veiculo_nicho_pts
    
    # Adicionar subtítulo ao denominador se verificação foi realizada
    if subtitulo_verificado:
        denominador += 80
    
    # 5. Aplicar sinal
    if sentiment == "positive":
        sinal = 1
    elif sentiment == "negative":
        sinal = -1
    else:
        sinal = 0
    
    # 6. Calcular IEDI (-1 a 1)
    if denominador > 0:
        iedi = (numerador / denominador) * sinal
    else:
        iedi = 0
    
    # 7. Converter para escala 0-10
    iedi_0_10 = ((iedi + 1) / 2) * 10
    
    # 8. Retornar resultado
    return {
        "score": round(iedi_0_10, 2),
        "sentiment": sentiment,
        "reach_group": grupo,
        "variables": {
            "title": titulo_pts > 0,
            "subtitle": subtitulo_pts > 0 if subtitulo_verificado else None,
            "relevant_outlet": veiculo_relevante_pts > 0,
            "niche_outlet": veiculo_nicho_pts > 0,
            "reach_group": grupo
        }
    }
```

---

## Configuração da Query Brandwatch

Para que o sistema funcione corretamente, a query na Brandwatch deve:

1. **Incluir todos os bancos** em uma única query
2. **Configurar categoryDetail** para cada banco:
   - Criar categoria "Banco do Brasil" para menções do BB
   - Criar categoria "Itaú" para menções do Itaú
   - Criar categoria "Bradesco" para menções do Bradesco
   - Criar categoria "Santander" para menções do Santander

3. **Filtrar por tipo de fonte**: `contentSourceName == "News"`

4. **Incluir campos necessários** na extração:
   - `sentiment`
   - `title`
   - `snippet`
   - `fullText` (se disponível)
   - `domain`
   - `monthlyVisitors`
   - `categoryDetails`

---

## Referências

[1] Brandwatch. (2024). *Mention Field Definitions*. Brandwatch Developer Documentation. https://developers.brandwatch.com/docs/mention-metadata-field-definitions

---

**Desenvolvido por**: Manus AI  
**Data**: 13/11/2024  
**Versão**: 2.0
