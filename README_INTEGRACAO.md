# Integração Brandwatch - Sistema IEDI

## Novidades da Integração

O sistema IEDI agora possui **integração completa com a Brandwatch API**, permitindo extrair menções diretamente da plataforma e executar análises IEDI de forma totalmente automatizada.

## Funcionalidades Adicionadas

### 1. Extração Automática de Menções

O sistema agora pode se conectar à Brandwatch API e extrair menções automaticamente, sem necessidade de exportação manual de dados.

**Características**:
- Extração por intervalo de datas
- Filtragem automática de menções de imprensa (News)
- Processamento em lotes para grandes volumes
- Logging detalhado do processo

### 2. Interface Web para Execução

Nova página **"Executar Análise"** no menu lateral que permite:
- Configurar credenciais da Brandwatch
- Definir período de análise
- Executar extração e cálculo IEDI em um único clique
- Visualizar resultados imediatamente

### 3. API REST Expandida

Novos endpoints para integração programática:

```bash
# Verificar status da integração
GET /api/brandwatch/status

# Extrair menções e executar análise
POST /api/brandwatch/extrair
{
  "data_inicio": "2025-01-01",
  "data_fim": "2025-01-31",
  "query_name": "nome_da_query"  // opcional
}
```

## Como Usar

### Passo 1: Instalar Dependências

A integração requer a biblioteca `bcr-api`:

```bash
pip install bcr-api
```

Ou, se usando Docker, reconstrua a imagem:

```bash
docker-compose build
docker-compose up -d
```

### Passo 2: Configurar Credenciais

1. Acesse a página **"Executar Análise"** no menu lateral
2. Clique em **"Configurar Agora"**
3. Preencha os dados:
   - **Email Brandwatch**: Seu email de login
   - **Senha**: Sua senha
   - **ID do Projeto**: ID do projeto na Brandwatch
   - **Nome da Query**: Nome da query configurada
4. Clique em **"Salvar Configuração"**

### Passo 3: Executar Análise

1. Na mesma página, defina o período:
   - **Data Início**: Data inicial da análise
   - **Data Fim**: Data final da análise
2. (Opcional) Sobrescreva o nome da query
3. Clique em **"🚀 Executar Análise IEDI"**

O sistema irá:
1. Conectar à Brandwatch API
2. Extrair todas as menções do período
3. Filtrar apenas menções de imprensa
4. Identificar bancos mencionados
5. Calcular IEDI de cada banco
6. Aplicar balizamento final
7. Salvar resultados no banco de dados
8. Exibir ranking IEDI na tela

### Passo 4: Visualizar Resultados

Após a execução, você pode:
- Ver o ranking diretamente na página
- Clicar em **"Ver Detalhes Completos"** para análise detalhada
- Acessar **"Análises"** no menu para histórico completo

## Arquitetura da Integração

### Módulos Adicionados

**`app/brandwatch_service.py`**
- Classe `BrandwatchService` para comunicação com API
- Métodos para extração por data, últimos dias, etc.
- Filtragem automática de menções de imprensa
- Tratamento de erros e logging

**`app/brandwatch_extractor.py`**
- Script original de extração (mantido para referência)
- Pode ser usado standalone via linha de comando

**`templates/executar_analise.html`**
- Interface web completa
- Formulário de configuração
- Formulário de execução
- Exibição de resultados em tempo real

### Fluxo de Dados

```
Brandwatch API
    ↓
BrandwatchService.extract_mentions()
    ↓
Filtragem (apenas News)
    ↓
CalculadoraIEDI.identificar_banco()
    ↓
CalculadoraIEDI.calcular_iedi_banco()
    ↓
CalculadoraIEDI.calcular_iedi_final_com_balizamento()
    ↓
Database.save_resultado_iedi()
    ↓
Interface Web (Ranking)
```

## Configuração via Variáveis de Ambiente

Alternativamente, você pode configurar via `.env`:

```env
BW_EMAIL=seu_email@exemplo.com
BW_PASSWORD=sua_senha
BW_PROJECT=id_do_projeto
BW_QUERY_NAME=nome_da_query
```

## Troubleshooting

### Erro: "Brandwatch API não está disponível"

**Causa**: Biblioteca `bcr-api` não instalada

**Solução**:
```bash
pip install bcr-api
```

### Erro: "Configuração Brandwatch não encontrada"

**Causa**: Credenciais não foram salvas

**Solução**: Configure as credenciais pela interface web

### Erro: "Nenhuma menção de imprensa encontrada"

**Causa**: A query não retornou menções classificadas como "News"

**Solução**: 
- Verifique se a query está correta
- Amplie o período de busca
- Confirme que há menções de imprensa no período

### Erro de Autenticação

**Causa**: Credenciais inválidas

**Solução**: Verifique email, senha e ID do projeto

## Vantagens da Integração

### Antes (Manual)
1. Acessar Brandwatch
2. Configurar query
3. Exportar CSV
4. Fazer upload no sistema
5. Executar análise

### Agora (Automatizado)
1. Definir período
2. Clicar em "Executar"
3. ✅ Pronto!

## Segurança

- Credenciais são armazenadas de forma segura no banco SQLite
- Senhas não são expostas em logs
- Comunicação via HTTPS com Brandwatch
- Validação de entrada em todos os endpoints

## Performance

- Processamento em lotes de até 5000 menções
- Filtragem eficiente antes do cálculo
- Logging detalhado para monitoramento
- Tratamento de erros robusto

## Próximos Passos

Possíveis melhorias futuras:
- Agendamento de análises automáticas
- Notificações por email ao concluir
- Comparação entre períodos
- Exportação de relatórios em PDF
- Dashboard com gráficos interativos

## Suporte

Para dúvidas sobre a integração Brandwatch:
1. Consulte a [documentação da Brandwatch API](https://developers.brandwatch.com/)
2. Verifique os logs do sistema
3. Entre em contato com o desenvolvedor

## Changelog

### v2.0 - Integração Brandwatch
- ✅ Módulo `brandwatch_service.py`
- ✅ Interface web para execução
- ✅ API REST expandida
- ✅ Filtragem automática de imprensa
- ✅ Logging detalhado
- ✅ Tratamento de erros

### v1.0 - Sistema Base
- ✅ Cálculo IEDI manual
- ✅ Interface de administração
- ✅ Gerenciamento de bancos e veículos
- ✅ API REST básica
