# Relatórios IEDI

Este diretório contém os relatórios gerados pelo Sistema IEDI (Índice de Exposição e Desempenho de Imagem).

---

## 📊 Relatórios Disponíveis

### 1. Relatório IEDI - Banco do Brasil

**Arquivos**:
- `RELATORIO_IEDI_BANCO_DO_BRASIL.md` - Versão Markdown (26 KB)
- `RELATORIO_IEDI_BANCO_DO_BRASIL.pdf` - Versão PDF (419 KB)

**Período de Análise**: 12 a 19 de novembro de 2025 (7 dias)

**Conteúdo**:
- Sumário executivo com principais conclusões
- Contexto e metodologia IEDI
- Performance comparativa com Itaú, Bradesco e Santander
- Análise de temas e narrativas dominantes
- Análise de veículos e alcance
- Análise de sentimento
- Diagnóstico SWOT (Forças, Fraquezas, Oportunidades, Ameaças)
- Recomendações estratégicas (curto, médio e longo prazo)

**Principais Resultados**:
- **Posição**: 4º lugar no ranking IEDI
- **IEDI Score**: 4,87 pontos
- **Volume**: 5.909 menções
- **Sentimento**: 81,9% positivo
- **Gap vs. Líder**: 0,33 pontos (6,3%)

**Temas Dominantes**:
1. Abono salarial PIS/PASEP (33% das menções)
2. Resultados financeiros do 3º trimestre (13,3%)
3. COP30 e sustentabilidade (7,0%)
4. Crédito imobiliário (3,4%)

---

### 2. Anexo Técnico - Código para Gráficos

**Arquivos**:
- `ANEXO_TECNICO_GRAFICOS.md` - Versão Markdown (37 KB)
- `ANEXO_TECNICO_GRAFICOS.pdf` - Versão PDF (454 KB)

**Conteúdo**:
- Código Python completo para reproduzir todos os gráficos
- 10 tipos de visualizações diferentes
- Instruções de instalação e configuração
- Exemplos de customização
- Troubleshooting

**Gráficos Incluídos**:
1. **Ranking IEDI Comparativo** - Barras horizontais e comparação Score vs Mean
2. **Volume de Menções** - Barras empilhadas e Share of Voice
3. **Distribuição de Sentimento** - Barras agrupadas e breakdown 100%
4. **Top 20 Veículos** - Barras horizontais e distribuição por tipo
5. **Nuvem de Palavras** - WordCloud e Top 30 keywords
6. **Evolução Temporal** - Séries temporais de volume e sentimento
7. **Análise Temática** - Distribuição por tema e gráfico de pizza
8. **Matriz de Posicionamento** - Scatter plot e Bubble chart
9. **Heatmap** - Sentimento por tema
10. **Radar Chart** - Comparação multidimensional

**Bibliotecas Utilizadas**:
- Pandas 2.1.0
- Matplotlib 3.8.0
- Seaborn 0.12.2
- WordCloud 1.9.2
- Plotly 5.17.0
- NumPy 1.24.3

---

## 📁 Estrutura de Dados

Os relatórios são baseados em dados extraídos de:

1. **Brandwatch API**
   - Query: "BB | Monitoramento | + Lagos"
   - Categoria: Análise de Resultado - Bancos
   - Total de menções: 18.013 (todos os bancos)

2. **CSVs Persistidos**
   - `data/mentions_[analysis_id].csv` - Menções brutas
   - `data/mention_analysis_[analysis_id].csv` - Análises IEDI individuais

3. **JSON Agregado**
   - `iedi_report_data.json` - Dados consolidados para relatório

---

## 🎯 Metodologia IEDI

O **Índice de Exposição e Desempenho de Imagem (IEDI)** quantifica a exposição midiática considerando:

### Componentes de Pontuação

| Componente | Peso | Critério |
|------------|------|----------|
| **Alcance Alto** | 100 | > 1 milhão de visitantes/mês |
| **Alcance Médio** | 80 | 100 mil - 1 milhão |
| **Alcance Baixo** | 24 | < 100 mil |
| **Veículo Relevante** | 95 | Mainstream (G1, Folha, Estadão) |
| **Veículo de Nicho** | 54 | Especializado (InfoMoney, Valor) |
| **Título Mencionado** | 40 | Banco citado no título |
| **Subtítulo Usado** | 20 | Banco citado no subtítulo |

### Fórmula de Cálculo

```
IEDI Score = (Numerador / Denominador) × Multiplicador de Sentimento × 10

Onde:
Numerador = Pontos de Alcance + Pontos de Veículo + Pontos de Destaque
Denominador = Máximo Possível (353 pontos)
Multiplicador de Sentimento = +1 (positivo), 0 (neutro), -1 (negativo)
```

### Escala

- **0-3**: Exposição baixa ou percepção negativa
- **3-6**: Exposição moderada com percepção mista
- **6-8**: Boa exposição com percepção positiva
- **8-10**: Excelente exposição com percepção muito positiva

---

## 📈 Como Usar os Relatórios

### Para Análise Estratégica

1. **Leia o Sumário Executivo** para entender os principais achados
2. **Revise a Seção 2 (Performance Comparativa)** para contexto competitivo
3. **Analise a Seção 3 (Temas e Narrativas)** para entender o que está sendo dito
4. **Consulte a Seção 7 (Diagnóstico)** para identificar forças e fraquezas
5. **Implemente as Recomendações da Seção 8** de acordo com prioridades

### Para Geração de Gráficos

1. **Instale as dependências** listadas no Anexo Técnico
2. **Carregue os dados** dos CSVs e JSON
3. **Execute as funções** de cada gráfico individualmente
4. **Customize** cores, tamanhos e estilos conforme necessário
5. **Use o script master** `generate_all_charts()` para gerar todos de uma vez

---

## 🔄 Atualizações

### Versão 1.0 (25 de novembro de 2025)

- ✅ Relatório completo do Banco do Brasil
- ✅ Análise comparativa com 3 concorrentes
- ✅ 18.013 menções analisadas
- ✅ 10 tipos de visualizações
- ✅ Código Python completo
- ✅ Recomendações estratégicas

### Próximas Versões

- [ ] Relatórios individuais para Itaú, Bradesco e Santander
- [ ] Dashboard interativo com Plotly/Dash
- [ ] Análise de séries temporais (múltiplos períodos)
- [ ] Integração com BigQuery para dados históricos
- [ ] Alertas automáticos de mudanças de sentimento

---

## 📞 Contato

Para dúvidas ou sugestões sobre os relatórios:

- **Repositório**: [gskumlehn/iedi_system](https://github.com/gskumlehn/iedi_system)
- **Issues**: Abra uma issue no GitHub
- **Documentação**: Consulte `/docs` para documentação técnica completa

---

## 📄 Licença

Este relatório e código são parte do Sistema IEDI e seguem a mesma licença do projeto principal.

---

**Última atualização**: 25 de novembro de 2025  
**Versão**: 1.0  
**Analista**: Sistema IEDI
