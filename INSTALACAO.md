# Guia de Instalação - Sistema IEDI

## Requisitos

- **Docker** e **Docker Compose** instalados
- OU **Python 3.11+** para execução local

## Instalação Rápida com Docker (Recomendado)

### 1. Extrair o arquivo ZIP

```bash
unzip iedi_system_completo.zip
cd iedi_system
```

### 2. Iniciar o sistema

```bash
docker-compose up -d
```

### 3. Acessar o sistema

Abra seu navegador em: **http://localhost:5000**

### 4. Carregar dados iniciais

- Clique no botão **"🌱 Carregar Dados Iniciais"** no dashboard
- Isso criará bancos e veículos de exemplo

## Instalação Local (sem Docker)

### 1. Extrair e entrar no diretório

```bash
unzip iedi_system_completo.zip
cd iedi_system
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a aplicação

```bash
python app.py
```

### 4. Acessar o sistema

Abra seu navegador em: **http://localhost:5000**

## Comandos Úteis (Docker)

### Ver logs em tempo real
```bash
docker-compose logs -f
```

### Parar o sistema
```bash
docker-compose down
```

### Reiniciar o sistema
```bash
docker-compose restart
```

### Rebuild completo
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Persistência de Dados

O banco de dados SQLite é armazenado em `./data/iedi.db` e persiste mesmo quando o container é removido.

### Fazer backup
```bash
cp data/iedi.db backup_$(date +%Y%m%d).db
```

### Restaurar backup
```bash
cp backup_20250112.db data/iedi.db
docker-compose restart
```

## Estrutura do Sistema

```
iedi_system/
├── app.py                 # Aplicação Flask principal
├── app/
│   ├── models.py         # Modelos do banco de dados
│   └── iedi_calculator.py # Lógica de cálculo do IEDI
├── templates/            # Páginas HTML
├── static/              # CSS e JavaScript
├── data/                # Banco de dados SQLite
├── Dockerfile           # Configuração Docker
├── docker-compose.yml   # Orquestração
└── requirements.txt     # Dependências Python
```

## Próximos Passos

1. **Configure os Bancos** em `/bancos`
2. **Adicione Porta-vozes** em `/porta-vozes`
3. **Configure Veículos** em `/veiculos`
4. **Ajuste Pesos** em `/configuracoes`
5. **Execute Análises** via API (veja README.md)

## Troubleshooting

### Porta 5000 já está em uso
```bash
# Edite docker-compose.yml e altere a porta:
ports:
  - "8080:5000"  # Acesse em http://localhost:8080
```

### Permissões no diretório data
```bash
chmod -R 755 data/
```

### Container não inicia
```bash
docker-compose logs
```

## Suporte

Consulte o arquivo **README.md** para documentação completa da API e metodologia IEDI.
