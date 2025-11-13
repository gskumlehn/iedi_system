# Mapeamento Brandwatch → Variáveis IEDI

## Visão Geral

Este documento descreve de forma direta como os campos da API da Brandwatch são mapeados para as variáveis usadas no cálculo do IEDI.

---

## Campos da Brandwatch Utilizados

### 1. **sentiment**
- **Tipo**: String
- **Valores**: `"positive"`, `"negative"`, `"neutral"`
- **Uso no IEDI**: 
  - **Verificação de Qualificação**: `sentiment == "positive"` → variável = 1
  - **Sinal do IEDI**: Se `negative`, multiplica IEDI_Base por -1
  - **Balizamento**: Conta menções positivas para proporção

**Mapeamento**:
```python
verificacao_qualificacao = 1 if sentiment == "positive" else 0
```

---

### 2. **title**
- **Tipo**: String (Text)
- **Conteúdo**: Título da notícia
- **Uso no IEDI**:
  - **Verificação de Título**: Verifica se nome do banco aparece no título
  - **Peso**: 100 pontos

**Mapeamento**:
```python
banco_no_titulo = any(variacao.lower() in title.lower() for variacao in banco.variacoes)
verificacao_titulo = 1 if banco_no_titulo else 0
```

---

### 3. **snippet**
- **Tipo**: String (Text)
- **Conteúdo**: Trecho inicial da notícia (subtítulo ou 1º parágrafo)
- **Uso no IEDI**:
  - **Verificação de Subtítulo**: Verifica se nome do banco aparece no snippet
  - **Peso**: 80 pontos

**Mapeamento**:
```python
banco_no_snippet = any(variacao.lower() in snippet.lower() for variacao in banco.variacoes)
verificacao_subtitulo = 1 if banco_no_snippet else 0
```

---

### 4. **fullText**
- **Tipo**: String (Text)
- **Conteúdo**: Texto completo da notícia
- **Uso no IEDI**:
  - **Verificação de Porta-voz**: Verifica se algum porta-voz do banco é mencionado
  - **Peso**: 20 pontos

**Mapeamento**:
```python
portavozes = get_portavozes_banco(banco_id)
portavoz_mencionado = any(pv.nome.lower() in fullText.lower() for pv in portavozes)
verificacao_portavoz = 1 if portavoz_mencionado else 0
```

---

### 5. **imageUrls**
- **Tipo**: Array de Strings (URLs)
- **Conteúdo**: Lista de URLs de imagens na notícia
- **Uso no IEDI**:
  - **Verificação de Imagem**: Verifica se a menção possui pelo menos uma imagem
  - **Peso**: 20 pontos

**Mapeamento**:
```python
verificacao_imagem = 1 if len(imageUrls) > 0 else 0
```

---

### 6. **domain**
- **Tipo**: String
- **Conteúdo**: Domínio do veículo (ex: "g1.globo.com")
- **Uso no IEDI**:
  - **Verificação de Veículo Relevante**: Verifica se está na lista de veículos relevantes (peso 95)
  - **Verificação de Veículo de Nicho**: Verifica se está na lista de veículos de nicho (peso 54)

**Mapeamento**:
```python
veiculo_relevante = domain in lista_veiculos_relevantes
verificacao_veiculo_relevante = 1 if veiculo_relevante else 0

veiculo_nicho = domain in lista_veiculos_nicho
verificacao_veiculo_nicho = 1 if veiculo_nicho else 0
```

---

### 7. **monthlyVisitors**
- **Tipo**: Integer
- **Conteúdo**: Número de acessos mensais do veículo
- **Uso no IEDI**:
  - **Classificação de Grupo de Alcance**: Define o peso do alcance (20-91 pontos)
  - **Escolha do Denominador**: Grupo A usa 406, demais usam 460

**Mapeamento**:
```python
if monthlyVisitors >= 29_000_001:
    grupo_alcance = "A"
    peso_alcance = 91
    denominador = 406
elif monthlyVisitors >= 11_000_001:
    grupo_alcance = "B"
    peso_alcance = 85
    denominador = 460
elif monthlyVisitors >= 500_000:
    grupo_alcance = "C"
    peso_alcance = 24
    denominador = 460
else:
    grupo_alcance = "D"
    peso_alcance = 20
    denominador = 460
```

---

### 8. **categoryDetail**
- **Tipo**: String
- **Conteúdo**: Categoria detalhada da menção (configurada na query da Brandwatch)
- **Uso no IEDI**:
  - **Identificação do Banco**: Usado para segregar menções por banco
  - **Essencial**: Permite usar uma query geral para todos os bancos

**Mapeamento**:
```python
# Na query da Brandwatch, configure categoryDetail para retornar o nome do banco
# Exemplo: categoryDetail = "Banco do Brasil" para menções do BB

banco = get_banco_by_category_detail(categoryDetail)
```

**Configuração na Brandwatch**:
- A query deve ter regras que atribuem `categoryDetail` baseado no conteúdo
- Exemplo de regra: Se menção contém "Banco do Brasil" OU "BB" → categoryDetail = "Banco do Brasil"

---

### 9. **url**
- **Tipo**: String (URL)
- **Conteúdo**: URL completa da notícia
- **Uso no IEDI**:
  - **Identificação única**: Usado como referência da menção
  - **Rastreabilidade**: Permite acessar a notícia original

**Mapeamento**:
```python
mencao.url = url  # Armazenado para referência
```

---

### 10. **publishedDate** (ou campo de data)
- **Tipo**: DateTime
- **Conteúdo**: Data e hora de publicação da notícia
- **Uso no IEDI**:
  - **Filtragem por Período**: Seleciona menções dentro do intervalo da análise

**Mapeamento**:
```python
# Filtro na query Brandwatch
mencoes = fetch_mentions(
    startDate=data_inicio,
    endDate=data_fim
)
```

---

## Resumo do Mapeamento

| Campo Brandwatch | Variável IEDI | Peso | Tipo de Verificação |
|------------------|---------------|------|---------------------|
| `sentiment` | Qualificação | - | Sinal do IEDI |
| `title` | Título | 100 | Presença do banco |
| `snippet` | Subtítulo | 80 | Presença do banco |
| `fullText` | Porta-voz | 20 | Presença de porta-voz |
| `imageUrls` | Imagem | 20 | Existência de imagem |
| `domain` | Veículo Relevante | 95 | Presença na lista |
| `domain` | Veículo de Nicho | 54 | Presença na lista |
| `monthlyVisitors` | Grupo de Alcance | 20-91 | Classificação por faixa |
| `categoryDetail` | Identificação | - | Segregação por banco |
| `url` | Referência | - | Rastreabilidade |
| `publishedDate` | Período | - | Filtragem temporal |

---

## Fluxo de Dados

```
Brandwatch API
    ↓
Fetch Mentions (startDate, endDate, mediaType=News)
    ↓
Para cada Mention:
    ├─ sentiment → Qualificação + Sinal
    ├─ title → Verificação Título
    ├─ snippet → Verificação Subtítulo
    ├─ fullText → Verificação Porta-voz
    ├─ imageUrls → Verificação Imagem
    ├─ domain → Verificação Veículo Relevante/Nicho
    ├─ monthlyVisitors → Classificação Grupo Alcance
    └─ categoryDetail → Identificação do Banco
    ↓
Calcular IEDI da Menção
    ↓
Agregar por Banco
    ↓
Aplicar Balizamento
    ↓
Gerar Ranking
```

---

## Exemplo Completo

**Menção da Brandwatch**:
```json
{
  "title": "Banco do Brasil anuncia lucro recorde no 1º trimestre",
  "snippet": "O Banco do Brasil (BB) divulgou nesta quinta-feira...",
  "fullText": "...Tarciana Medeiros, presidente do Banco do Brasil...",
  "url": "https://g1.globo.com/economia/noticia/...",
  "domain": "g1.globo.com",
  "sentiment": "positive",
  "imageUrls": ["https://s2.glbimg.com/..."],
  "monthlyVisitors": 313000000,
  "categoryDetail": "Banco do Brasil",
  "publishedDate": "2025-05-13T10:30:00Z"
}
```

**Processamento IEDI**:
```python
# 1. Identificação
banco = "Banco do Brasil" (via categoryDetail)

# 2. Verificações
verificacao_titulo = 1  # "Banco do Brasil" no title
verificacao_subtitulo = 1  # "Banco do Brasil" e "BB" no snippet
verificacao_imagem = 1  # imageUrls tem 1 item
verificacao_portavoz = 1  # "Tarciana Medeiros" no fullText
verificacao_veiculo_relevante = 1  # g1.globo.com está na lista
verificacao_veiculo_nicho = 0  # g1.globo.com não é nicho

# 3. Classificação de Alcance
monthlyVisitors = 313000000 → Grupo A
peso_alcance = 91
denominador = 406

# 4. Cálculo
numerador = 91 + 95 + 100 + 80 + 20 + 20 = 406
iedi_base = 406 / 406 = 1.0

# 5. Sinal
sentiment = "positive" → mantém sinal positivo
iedi_base = 1.0

# 6. Conversão
iedi_mencao = (10 * 1.0 + 1) / 2 = 5.5
```

**Resultado**: Menção recebe nota **5.5**

---

## Observações Importantes

### categoryDetail
- **Crítico**: Este campo é a chave para segregar menções por banco
- **Configuração**: Deve ser configurado na query da Brandwatch
- **Alternativa**: Se não disponível, usar busca por texto (menos preciso)

### monthlyVisitors
- **Fonte**: Dados de tráfego do veículo (SimilarWeb, Comscore, etc.)
- **Atualização**: Brandwatch atualiza periodicamente
- **Fallback**: Se não disponível, classificar como Grupo D

### Listas de Veículos
- **Relevantes**: 41 veículos principais de imprensa
- **Nicho**: 22 veículos especializados em economia/negócios
- **Manutenção**: Listas devem ser atualizadas periodicamente

---

**Desenvolvido por**: Manus AI  
**Data**: 12/11/2024  
**Versão**: 4.0
