# Variáveis de Ambiente - Sistema IEDI

Este documento lista todas as variáveis de ambiente necessárias para executar o sistema IEDI.

## Banco de Dados (MySQL)

```bash
DB_HOST=localhost          # Host do banco de dados MySQL
DB_PORT=3306              # Porta do MySQL
DB_USER=root              # Usuário do banco
DB_PASSWORD=senha_aqui    # Senha do banco
DB_NAME=iedi              # Nome do database
```

## Flask

```bash
FLASK_ENV=production      # Ambiente (development/production)
FLASK_DEBUG=False         # Debug mode (True/False)
SECRET_KEY=chave_secreta  # Chave secreta para sessões
```

## Como Configurar

### Desenvolvimento Local

1. Copie este arquivo para `.env`:
```bash
cp ENV_VARS.md .env
```

2. Edite `.env` com suas credenciais reais

3. O arquivo `.env` é carregado automaticamente pelo docker-compose

### Docker

O `docker-compose.yml` já está configurado para ler o arquivo `.env`:

```yaml
env_file:
  - .env
```

## Notas Importantes

- ⚠️ **NUNCA** commite o arquivo `.env` no Git
- ✅ O `.gitignore` já está configurado para ignorar `.env`
- 📝 Use `ENV_VARS.md` como template/documentação
- 🔒 Mantenha credenciais seguras e privadas
