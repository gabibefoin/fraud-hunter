# Usa imagem oficial do Python
FROM python:3.11-slim

# Instala dependências do sistema + Tesseract com português
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Define variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1

# Comando de execução
CMD ["python", "fraud_hunter.py"]
