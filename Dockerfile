# Usar imagem oficial do Python
FROM python:3.11-slim

# Instala dependências do sistema para OCR (Tesseract)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código e arquivo de sessão do Telegram
COPY fraud_hunter.py .
# COPY fraud_hunter.session .  # sessão salva localmente

# Copiar .env
COPY .env .

# Comando para rodar o script
CMD ["python", "fraud_hunter.py"]
