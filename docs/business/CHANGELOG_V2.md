# Changelog - Sistema IEDI v2.0

## Versão 2.0 - Análise de Resultados com Períodos Diferentes

### Data: 12/11/2024

### Resumo
Implementação de funcionalidade para análise IEDI de divulgação de resultados trimestrais, permitindo que cada banco tenha um período de coleta diferente, baseado na data de divulgação de seus resultados.

---

## Principais Mudanças

### 1. Schema do Banco de Dados

#### Tabela `analises` - Campos Adicionados
- `periodo_referencia` TEXT - Identificação do período (ex: "1T2025", "4T2024")
- `tipo` TEXT - Tipo de análise: "mensal" ou "resultados"
- Campos `data_inicio` e `data_fim` agora são opcionais

#### Nova Tabela `periodos_banco`
```sql
CREATE TABLE periodos_banco (
    id INTEGER PRIMARY KEY,
    analise_id INTEGER,
    banco_id INTEGER,
    data_divulgacao DATE,
    data_inicio DATE,
    data_fim DATE,
    dias_coleta INTEGER DEFAULT 2,
    total_mencoes INTEGER DEFAULT 0,
    FOREIGN KEY (analise_id) REFERENCES analises(id),
    FOREIGN KEY (banco_id) REFERENCES bancos(id)
)
```

#### Tabela `mencoes` - Campo Adicionado
- `category_detail` TEXT - Campo da Brandwatch que identifica o banco

---

### 2. Novos Métodos no models.py

#### Gerenciamento de Períodos
- `create_periodo_banco()` - Cria período de coleta para um banco
- `get_periodos_banco()` - Lista períodos de uma análise
- `update_periodo_banco_mencoes()` - Atualiza total de menções
- `get_periodo_banco()` - Busca período específico de um banco

#### Análises Modificadas
- `create_analise()` - Agora aceita `periodo_referencia` e `tipo`

---

### 3. Brandwatch Service - Novos Métodos

#### Filtragem por CategoryDetail
- `filter_by_category_detail()` - Filtra menções por banco usando categoryDetail
- `get_unique_category_details()` - Lista valores únicos de categoryDetail

---

### 4. Nova Interface Web

#### Página: `/analise-resultados`
Interface completa para análise de resultados com:
- Configuração de período de referência (ex: "1T2025")
- Input de data de divulgação para cada banco
- Input de dias de coleta para cada banco (padrão: 2 dias)
- Cálculo automático do período (divulgação + dias)
- Visualização de períodos diferentes por banco

#### Menu Atualizado
- "Análise Mensal" (antiga "Executar Análise")
- "Análise Resultados" (nova funcionalidade)

---

### 5. Nova API REST

#### Endpoint: `POST /api/analises/executar-resultados`

**Request:**
```json
{
  "periodo_referencia": "1T2025",
  "query_name": "query_geral_bancos",
  "bancos": [
    {
      "banco_id": 1,
      "banco_nome": "Banco do Brasil",
      "data_divulgacao": "2025-02-10",
      "dias_coleta": 2
    },
    {
      "banco_id": 2,
      "banco_nome": "Itaú",
      "data_divulgacao": "2025-02-12",
      "dias_coleta": 2
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "analise_id": 15,
  "periodo_referencia": "1T2025",
  "total_mencoes": 450,
  "periodos": [
    {
      "banco_id": 1,
      "banco_nome": "Banco do Brasil",
      "data_divulgacao": "2025-02-10",
      "data_inicio": "2025-02-10",
      "data_fim": "2025-02-12",
      "total_mencoes": 230
    }
  ],
  "resultados": [
    {
      "banco": "Banco do Brasil",
      "iedi_final": 85.5,
      "iedi_medio": 78.2,
      "volume_total": 230,
      "positividade": 65.5
    }
  ]
}
```

---

## Fluxo de Uso

### Análise de Resultados Trimestrais

1. **Configurar Brandwatch**
   - Definir query geral com todos os bancos
   - Configurar categoryDetail para identificar cada banco

2. **Acessar "Análise Resultados"**
   - Definir período de referência (ex: "1T2025")
   - Para cada banco:
     - Definir data de divulgação
     - Definir dias de coleta (padrão: 2)

3. **Executar Análise**
   - Sistema extrai menções da query geral
   - Filtra por período de cada banco
   - Filtra por categoryDetail de cada banco
   - Calcula IEDI individual
   - Aplica balizamento final
   - Gera ranking comparativo

4. **Visualizar Resultados**
   - Ranking IEDI final
   - Períodos específicos de cada banco
   - Detalhes de menções por banco

---

## Compatibilidade

### Análises Antigas
- Análises mensais continuam funcionando normalmente
- Página "Análise Mensal" mantém funcionalidade original
- Banco de dados é retrocompatível

### Migração
- Não é necessária migração de dados
- Novas tabelas são criadas automaticamente
- Análises antigas permanecem com `tipo='mensal'`

---

## Vantagens da Nova Abordagem

### 1. Query Única
- Uma única configuração na Brandwatch
- Mais eficiente e fácil de manter
- Todos os bancos em uma query

### 2. Segregação Automática
- categoryDetail já identifica o banco
- Não depende de identificação por texto
- Mais preciso e confiável

### 3. Flexibilidade de Períodos
- Cada banco tem seu período específico
- Respeita datas reais de divulgação
- Período configurável por análise

### 4. Comparabilidade
- Balizamento normaliza diferenças
- Ranking justo mesmo com períodos diferentes
- Mantém metodologia IEDI original

---

## Exemplos de Uso

### Exemplo 1: Resultados 1T2025

**Cenário:**
- BB divulga em 10/02/2025
- Itaú divulga em 12/02/2025
- Bradesco divulga em 15/02/2025
- Santander divulga em 18/02/2025

**Configuração:**
```
Período de Referência: 1T2025
Query: "resultados_bancos_geral"

Banco do Brasil:
  Data Divulgação: 10/02/2025
  Dias Coleta: 2
  Período: 10/02 a 12/02

Itaú:
  Data Divulgação: 12/02/2025
  Dias Coleta: 2
  Período: 12/02 a 14/02

Bradesco:
  Data Divulgação: 15/02/2025
  Dias Coleta: 2
  Período: 15/02 a 17/02

Santander:
  Data Divulgação: 18/02/2025
  Dias Coleta: 2
  Período: 18/02 a 20/02
```

**Resultado:**
- Sistema coleta menções de cada banco no seu período específico
- Filtra por categoryDetail para garantir precisão
- Calcula IEDI considerando proporção de positivas
- Gera ranking comparativo normalizado

---

## Limitações e Considerações

### 1. CategoryDetail Obrigatório
- A query na Brandwatch DEVE ter categoryDetail configurado
- Cada menção deve estar categorizada com o nome do banco
- Sem categoryDetail, a segregação não funciona

### 2. Períodos Não Sobrepostos
- Recomenda-se que os períodos não se sobreponham
- Períodos sobrepostos podem gerar duplicação de análise

### 3. Volume Mínimo
- Bancos com volume muito baixo podem ter IEDI distorcido
- Recomenda-se pelo menos 10 menções por banco

---

## Próximos Passos (Roadmap)

### Melhorias Futuras
- [ ] Agendamento automático de análises
- [ ] Notificações por email ao concluir
- [ ] Comparação entre trimestres
- [ ] Exportação de relatórios em PDF
- [ ] Dashboard com gráficos de evolução
- [ ] API para integração externa

---

## Suporte Técnico

### Documentação
- `README.md` - Documentação geral
- `README_INTEGRACAO.md` - Integração Brandwatch
- `ANALISE_ALTERACOES.md` - Plano de alterações

### Contato
Para dúvidas ou problemas, consulte a documentação ou entre em contato com o desenvolvedor.

---

## Créditos

**Desenvolvido por:** Manus AI  
**Data:** 12/11/2024  
**Versão:** 2.0  
**Metodologia:** IEDI (Índice de Exposição Digital na Imprensa)
