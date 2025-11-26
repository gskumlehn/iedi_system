# Especificações dos Gráficos - Relatório IEDI 3T25

## Sumário

Este documento especifica a estrutura de dados e as especificações visuais para reproduzir todos os gráficos e tabelas do Relatório IEDI 3T25, baseado no formato do relatório Brivia 4T24.

---

## 1. Dados Consolidados

**Arquivo Principal**: `DADOS_CONSOLIDADOS_RELATORIO_IEDI_3T25.json`

### Estrutura do JSON

```json
{
  "metadata": {
    "titulo": "Relatório IEDI - 3T25",
    "periodo": "4T24 a 3T25",
    "bancos": ["Banco do Brasil", "Itaú", "Bradesco", "Santander"],
    "metodologia": "IEDI Mean (sem balizamento por positividade)",
    "data_geracao": "2025-11-26"
  },
  "dados_brutos": { ... },
  "graficos": { ... },
  "resumo_executivo": { ... }
}
```

---

## 2. Gráfico 1: Ranking IEDI + Linha do Tempo BB

### 2.1 Descrição

Gráfico combinado mostrando:
- **Esquerda**: Ranking IEDI 3T25 (barras verticais com logos dos bancos)
- **Direita**: Linha do tempo BB (4T24 a 3T25) com IEDI, Positividade e Negatividade

### 2.2 Fonte de Dados

**JSON**: `grafico_1_ranking_linha_tempo.json`  
**CSVs**:
- `grafico_1_ranking_3t25.csv`
- `grafico_1_linha_tempo_bb.csv`

### 2.3 Dados do Ranking 3T25

| Posição | Banco | IEDI Mean | Positividade | Negatividade |
|---------|-------|-----------|--------------|--------------|
| 1º | Santander | 5.78 | 22.0% | 16.0% |
| 2º | Bradesco | 5.76 | 20.6% | 17.4% |
| 3º | Banco do Brasil | 5.62 | 16.3% | 18.1% |
| 4º | Itaú | 5.59 | 17.2% | 13.7% |
| --- | **Média do Setor** | **5.69** | **19.1%** | **16.3%** |

### 2.4 Dados da Linha do Tempo BB

| Trimestre | IEDI Mean | Positividade | Negatividade |
|-----------|-----------|--------------|--------------|
| 4T24 | 5.72 | 16.8% | 18.8% |
| 1T25 | 5.63 | 13.8% | 17.7% |
| 2T25 | 5.27 | 14.5% | 29.9% |
| 3T25 | 5.62 | 16.3% | 18.1% |

### 2.5 Especificações Visuais

**Tipo**: Barras verticais (ranking) + Gráfico de barras com linhas sobrepostas (linha do tempo)

**Cores**:
- **Barras IEDI**: Azul royal (#4169E1)
- **Linha Positividade**: Verde (#00C853)
- **Linha Negatividade**: Vermelho (#FF5252)
- **Logos dos bancos**: Cores oficiais de cada banco

**Layout**:
- Eixo Y (esquerda): IEDI Mean (0-10)
- Eixo Y (direita): Percentual (0-100%)
- Eixo X: Trimestres (4T24, 1T25, 2T25, 3T25)
- Legenda: Superior direito

**Elementos**:
- Logos dos bancos acima das barras do ranking
- Valores numéricos exibidos nas barras
- Linha pontilhada para média do setor

---

## 3. Gráfico 2: Quadro Comparativo de Indicadores

### 3.1 Descrição

Tabela comparativa mostrando 6 indicadores principais para os 4 bancos no 3T25.

### 3.2 Fonte de Dados

**JSON**: `quadro_comparativo_indicadores_3t25.json`  
**CSV**: `quadro_comparativo_indicadores_3t25.csv`

### 3.3 Dados da Tabela

| Banco | IEDI | Vol Positivo | Vol Pos Título | Positividade | Presença Pos Título | Média Variáveis |
|-------|------|--------------|----------------|--------------|---------------------|-----------------|
| **Santander** | **5.78** | **472** | **70** | **22.0%** | **14.8%** | **0.2** |
| **Bradesco** | **5.76** | **586** | **83** | **20.6%** | **14.2%** | **0.2** |
| **Banco do Brasil** | **5.62** | **966** | **191** | **16.3%** | **19.8%** | **0.3** |
| **Itaú** | **5.59** | **1,229** | **99** | **17.2%** | **8.1%** | **0.1** |
| **Média 3T25** | **5.69** | **813** | **111** | **19.1%** | **14.2%** | **0.2** |

### 3.4 Especificações Visuais

**Tipo**: Tabela com cores alternadas

**Cores**:
- **Cabeçalho**: Azul escuro (#1a2b4a) com texto branco
- **Linhas ímpares**: Branco (#FFFFFF)
- **Linhas pares**: Cinza claro (#F5F5F5)
- **Linha de média**: Cinza médio (#E0E0E0) com texto em negrito
- **Valores acima da média**: Verde claro (#E8F5E9)
- **Valores abaixo da média**: Vermelho claro (#FFEBEE)

**Formatação**:
- IEDI: 2 casas decimais
- Volumes: Números inteiros com separador de milhares
- Percentuais: 1 casa decimal + símbolo %
- Média de Variáveis: 1 casa decimal

---

## 4. Gráfico 3: Comparativos Históricos (BB vs. Concorrentes)

### 4.1 Descrição

Três gráficos de linhas comparando a evolução do IEDI Mean do BB com cada concorrente ao longo de 4 trimestres (4T24 a 3T25).

### 4.2 Fonte de Dados

**JSON**: `graficos_comparativos_historicos.json`  
**CSVs**:
- `grafico_comparativo_bb_vs_itaú.csv`
- `grafico_comparativo_bb_vs_bradesco.csv`
- `grafico_comparativo_bb_vs_santander.csv`

### 4.3 Dados dos Gráficos

#### 4.3.1 BB vs. Itaú

| Trimestre | BB IEDI | Itaú IEDI | Média Setor |
|-----------|---------|-----------|-------------|
| 4T24 | 5.72 | 5.81 | 5.70 |
| 1T25 | 5.63 | 5.85 | 5.76 |
| 2T25 | 5.27 | 6.02 | 5.69 |
| 3T25 | 5.62 | 5.59 | 5.69 |

#### 4.3.2 BB vs. Bradesco

| Trimestre | BB IEDI | Bradesco IEDI | Média Setor |
|-----------|---------|---------------|-------------|
| 4T24 | 5.72 | 5.52 | 5.70 |
| 1T25 | 5.63 | 5.74 | 5.76 |
| 2T25 | 5.27 | 5.69 | 5.69 |
| 3T25 | 5.62 | 5.76 | 5.69 |

#### 4.3.3 BB vs. Santander

| Trimestre | BB IEDI | Santander IEDI | Média Setor |
|-----------|---------|----------------|-------------|
| 4T24 | 5.72 | 5.72 | 5.70 |
| 1T25 | 5.63 | 5.81 | 5.76 |
| 2T25 | 5.27 | 5.79 | 5.69 |
| 3T25 | 5.62 | 5.78 | 5.69 |

### 4.4 Especificações Visuais

**Tipo**: Gráficos de linhas múltiplas

**Cores**:
- **Linha BB**: Amarelo (#FFDD00) ou Azul BB (#003087)
- **Linha Concorrente**: Cor oficial do banco
  - Itaú: Laranja (#EC7000)
  - Bradesco: Vermelho (#CC092F)
  - Santander: Vermelho (#EC0000)
- **Linha Média Setor**: Cinza pontilhado (#9E9E9E)

**Layout**:
- Eixo Y: IEDI Mean (escala 5.0 a 6.5 para melhor visualização)
- Eixo X: Trimestres (4T24, 1T25, 2T25, 3T25)
- Legenda: Superior direito
- Grid: Linhas horizontais cinza claro

**Elementos**:
- Marcadores circulares nos pontos de dados
- Valores numéricos exibidos nos pontos
- Logos dos bancos no canto superior esquerdo de cada gráfico

---

## 5. Paleta de Cores Padrão

### 5.1 Cores dos Bancos

| Banco | Cor Principal | Cor Secundária | Hex |
|-------|---------------|----------------|-----|
| **Banco do Brasil** | Amarelo | Azul | #FFDD00 / #003087 |
| **Itaú** | Laranja | - | #EC7000 |
| **Bradesco** | Vermelho | - | #CC092F |
| **Santander** | Vermelho | - | #EC0000 |

### 5.2 Cores de Sentimento

| Sentimento | Cor | Hex |
|------------|-----|-----|
| **Positivo** | Verde | #00A859 |
| **Negativo** | Vermelho | #D32F2F |
| **Neutro** | Cinza | #9E9E9E |

### 5.3 Cores de Grupos de Alcance

| Grupo | Descrição | Cor | Hex |
|-------|-----------|-----|-----|
| **A** | ≥ 50M visitantes/mês | Azul escuro | #1565C0 |
| **B** | ≥ 15M visitantes/mês | Azul médio | #1976D2 |
| **C** | ≥ 500k visitantes/mês | Azul claro | #42A5F5 |
| **D** | < 500k visitantes/mês | Cinza azulado | #90CAF9 |

### 5.4 Cores de Fundo

| Elemento | Cor | Hex |
|----------|-----|-----|
| **Fundo principal** | Azul escuro | #1a2b4a |
| **Fundo secundário** | Azul royal | #4169E1 |
| **Fundo claro** | Branco | #FFFFFF |
| **Fundo alternado** | Cinza claro | #F5F5F5 |

---

## 6. Tipografia

### 6.1 Fontes

| Elemento | Fonte | Peso | Tamanho |
|----------|-------|------|---------|
| **Título principal** | Sans-serif | Bold | 32-36pt |
| **Subtítulos** | Sans-serif | Medium | 24-28pt |
| **Corpo de texto** | Sans-serif | Regular | 12-14pt |
| **Legendas** | Sans-serif | Regular | 10-12pt |
| **Valores numéricos** | Sans-serif | Bold | 14-16pt |

### 6.2 Recomendações

- **Fonte principal**: Arial, Helvetica, ou similar sans-serif
- **Fonte de dados**: Monospace para valores numéricos em tabelas
- **Alinhamento**: Esquerda para texto, direita para números, centro para cabeçalhos

---

## 7. Dimensões e Layout

### 7.1 Gráficos

| Tipo | Largura | Altura | Proporção |
|------|---------|--------|-----------|
| **Gráfico de barras** | 1200px | 600px | 2:1 |
| **Gráfico de linhas** | 1000px | 500px | 2:1 |
| **Tabela** | 100% | Auto | - |

### 7.2 Margens e Espaçamento

| Elemento | Valor |
|----------|-------|
| **Margem externa** | 40px |
| **Margem interna** | 20px |
| **Espaçamento entre gráficos** | 60px |
| **Espaçamento entre linhas (tabela)** | 8px |
| **Padding de células (tabela)** | 12px |

---

## 8. Exportação e Formatos

### 8.1 Formatos Suportados

| Formato | Uso | Resolução |
|---------|-----|-----------|
| **PNG** | Imagens de alta qualidade | 300 DPI |
| **SVG** | Gráficos vetoriais | Vetorial |
| **PDF** | Relatório completo | 300 DPI |
| **CSV** | Dados brutos | - |
| **JSON** | Dados estruturados | - |

### 8.2 Nomenclatura de Arquivos

```
grafico_[numero]_[descricao].[formato]

Exemplos:
- grafico_1_ranking_linha_tempo.png
- grafico_2_quadro_comparativo.png
- grafico_3_comparativo_bb_vs_itau.png
```

---

## 9. Bibliotecas Recomendadas

### 9.1 Python

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
```

**Configuração de estilo**:
```python
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12
```

### 9.2 JavaScript

```javascript
// Chart.js
import Chart from 'chart.js/auto';

// D3.js
import * as d3 from 'd3';

// Plotly.js
import Plotly from 'plotly.js-dist';
```

---

## 10. Checklist de Implementação

### 10.1 Gráfico 1: Ranking + Linha do Tempo

- [ ] Carregar dados de `grafico_1_ranking_linha_tempo.json`
- [ ] Criar gráfico de barras verticais para ranking
- [ ] Adicionar logos dos bancos
- [ ] Criar gráfico de barras com linhas sobrepostas para linha do tempo
- [ ] Adicionar legenda e eixos
- [ ] Aplicar cores e estilos
- [ ] Exportar em PNG (300 DPI)

### 10.2 Gráfico 2: Quadro Comparativo

- [ ] Carregar dados de `quadro_comparativo_indicadores_3t25.json`
- [ ] Criar tabela HTML ou LaTeX
- [ ] Aplicar cores alternadas
- [ ] Destacar valores acima/abaixo da média
- [ ] Formatar números e percentuais
- [ ] Exportar em PNG ou incluir no PDF

### 10.3 Gráfico 3: Comparativos Históricos

- [ ] Carregar dados de `graficos_comparativos_historicos.json`
- [ ] Criar 3 gráficos de linhas (BB vs. cada concorrente)
- [ ] Adicionar linha de média do setor
- [ ] Adicionar logos dos bancos
- [ ] Aplicar cores oficiais
- [ ] Adicionar marcadores e valores
- [ ] Exportar cada gráfico em PNG (300 DPI)

---

## 11. Exemplos de Código

### 11.1 Gráfico de Ranking (Python + Matplotlib)

```python
import matplotlib.pyplot as plt
import pandas as pd
import json

# Carregar dados
with open('grafico_1_ranking_3t25.csv', 'r') as f:
    df = pd.read_csv(f)

# Filtrar apenas bancos (sem média)
df_bancos = df[df['posicao'].notna()]

# Criar gráfico
fig, ax = plt.subplots(figsize=(10, 6))

# Barras
bars = ax.bar(df_bancos['banco'], df_bancos['iedi_mean'], color='#4169E1')

# Adicionar valores nas barras
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

# Linha de média
media = df[df['banco'] == 'Média do Setor']['iedi_mean'].values[0]
ax.axhline(y=media, color='#9E9E9E', linestyle='--', linewidth=2, label=f'Média: {media:.2f}')

# Configurações
ax.set_ylabel('IEDI Mean', fontsize=14, fontweight='bold')
ax.set_title('Ranking IEDI - 3T25', fontsize=16, fontweight='bold')
ax.set_ylim(0, 7)
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('grafico_1_ranking.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 11.2 Gráfico de Linha do Tempo (Python + Matplotlib)

```python
import matplotlib.pyplot as plt
import pandas as pd

# Carregar dados
df = pd.read_csv('grafico_1_linha_tempo_bb.csv')

# Criar gráfico
fig, ax1 = plt.subplots(figsize=(12, 6))

# Eixo Y1: IEDI
ax1.bar(df['trimestre'], df['iedi_mean'], color='#4169E1', alpha=0.7, label='IEDI Mean')
ax1.set_ylabel('IEDI Mean', fontsize=14, fontweight='bold', color='#4169E1')
ax1.set_ylim(0, 7)
ax1.tick_params(axis='y', labelcolor='#4169E1')

# Eixo Y2: Positividade e Negatividade
ax2 = ax1.twinx()
ax2.plot(df['trimestre'], df['positividade'], color='#00C853', marker='o', linewidth=2, label='Positividade')
ax2.plot(df['trimestre'], df['negatividade'], color='#FF5252', marker='o', linewidth=2, label='Negatividade')
ax2.set_ylabel('Percentual (%)', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 100)

# Configurações
ax1.set_xlabel('Trimestre', fontsize=14, fontweight='bold')
ax1.set_title('Linha do Tempo BB - IEDI, Positividade e Negatividade', fontsize=16, fontweight='bold')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax1.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('grafico_1_linha_tempo.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

## 12. Observações Importantes

### 12.1 Diferenças vs. Relatório Brivia Original

| Aspecto | Brivia (4T24) | Nosso (3T25) |
|---------|---------------|--------------|
| **Escala IEDI** | 7-10 | 5-6 |
| **Metodologia** | IEDI balizado | IEDI Mean (sem balizamento) |
| **Período** | 24 horas | 7 dias |
| **Bancos** | 5 (com Caixa) | 4 (sem Caixa) |

### 12.2 Notas Técnicas

1. **IEDI Mean**: Calculado como média dos valores `iedi_normalized` (escala 0-10) sem multiplicação por positividade
2. **Positividade**: Percentual de menções positivas sobre total de menções
3. **Negatividade**: Percentual de menções negativas sobre total de menções
4. **Neutralidade**: Percentual de menções neutras sobre total de menções (não exibida nos gráficos principais)
5. **Média do Setor**: Média aritmética simples dos IEDI dos 4 bancos

### 12.3 Limitações Atuais

- ❌ Não temos dados de porta-vozes mencionados
- ❌ Não temos dados de diversidade de jornalistas
- ❌ Não temos dados de imagens/logos nas matérias
- ❌ Não temos dados de replicações
- ⚠️ Alguns veículos podem estar mal classificados (ex: UOL como Grupo C ao invés de A)

---

## 13. Próximos Passos

1. **Implementar gráficos** usando as especificações acima
2. **Validar dados** com stakeholders
3. **Ajustar classificação de veículos** (especialmente UOL)
4. **Adicionar análises qualitativas** (nuvens de palavras, temas principais)
5. **Criar dashboard interativo** (opcional)
6. **Automatizar geração** de relatórios trimestrais

---

## 14. Contato e Suporte

Para dúvidas ou sugestões sobre as especificações, consulte:
- **Repositório**: [gskumlehn/iedi_system](https://github.com/gskumlehn/iedi_system)
- **Documentação**: `/docs/business/METODOLOGIA_IEDI.md`
- **Dados**: `/data/` (CSVs de mentions e mention_analysis)

---

**Versão**: 1.0  
**Data**: 26 de novembro de 2025  
**Autor**: Manus AI
