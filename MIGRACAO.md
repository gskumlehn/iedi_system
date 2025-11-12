# Guia de Migração - IEDI System

## Problema

Se você está vendo este erro:

```
ERROR: table analises has no column named periodo_referencia
```

Significa que seu banco de dados foi criado com uma versão anterior do sistema e precisa ser migrado para a v2.0+.

## Solução Rápida

### Opção 1: Migração Automática (Recomendado)

Execute o script de migração que adiciona as colunas faltantes:

```bash
# Parar o sistema
docker-compose down

# Executar migração
python3 migrate_db.py

# Reiniciar o sistema
docker-compose up -d
```

### Opção 2: Recriar Banco de Dados (Perde dados existentes)

Se você não tem análises importantes salvas, pode simplesmente deletar o banco e deixar o sistema recriá-lo:

```bash
# Parar o sistema
docker-compose down

# Deletar banco antigo
rm data/iedi.db

# Reiniciar o sistema (criará novo banco)
docker-compose up -d
```

## O que a Migração Faz

O script `migrate_db.py` adiciona as seguintes colunas e tabelas:

### Tabela `analises`
- **periodo_referencia** (TEXT): Período de referência da análise (ex: "1T2025")
- **tipo** (TEXT): Tipo de análise ("mensal" ou "resultados")

### Tabela `periodos_banco` (nova)
Armazena períodos individuais para cada banco em análises de resultados:
- analise_id
- banco_id
- data_divulgacao
- data_inicio
- data_fim
- dias_coleta
- total_mencoes

### Tabela `mencoes`
- **category_detail** (TEXT): Campo da Brandwatch para identificação do banco

## Verificação

Após a migração, você pode verificar se tudo está correto:

```bash
# Acessar o container
docker-compose exec iedi-system bash

# Verificar schema
sqlite3 data/iedi.db ".schema analises"
sqlite3 data/iedi.db ".schema periodos_banco"
sqlite3 data/iedi.db ".schema mencoes"
```

## Compatibilidade

- ✅ **v1.0 → v2.0**: Migração automática preserva dados
- ✅ **v2.0 → v3.0**: Compatível, sem migração necessária
- ✅ **v3.0+**: Totalmente compatível

## Suporte

Se encontrar problemas durante a migração:

1. Faça backup do arquivo `data/iedi.db` antes de migrar
2. Verifique os logs do Docker: `docker-compose logs iedi-system`
3. Execute a migração manualmente dentro do container se necessário

## Histórico de Mudanças

### v2.0 (Nov 2024)
- Adicionado suporte a períodos diferentes por banco
- Segregação por categoryDetail da Brandwatch
- Nova tabela periodos_banco

### v3.0 (Nov 2024)
- Calculadora IEDI baseada em fórmulas do Power BI
- Pesos e denominadores validados
- Sem mudanças no schema (compatível com v2.0)
