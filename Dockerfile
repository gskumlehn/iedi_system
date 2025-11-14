FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretório de dados
RUN mkdir -p /app/data

# Expor porta
ENV PORT=8080
EXPOSE 8080

# Comando para iniciar (use gunicorn, expand PORT at runtime)
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers=2 --threads=8 --timeout=0 --access-logfile - wsgi:app"]
