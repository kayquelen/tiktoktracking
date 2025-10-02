FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretório para instância (caso use SQLite como fallback)
RUN mkdir -p instance

# Expor porta (EasyPanel geralmente usa 5000)
EXPOSE 5000

# Variáveis de ambiente padrão
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PORT=5000

# Comando para iniciar
CMD ["python", "main.py"]
