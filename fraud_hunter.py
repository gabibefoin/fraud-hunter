import os
import re
import asyncio
import psycopg2
from psycopg2 import sql
from telethon import TelegramClient, events
from PIL import Image
import pytesseract

# -----------------------
# Configurações
# -----------------------
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
PHONE = os.getenv("TG_PHONE")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Termos de fraude
FRAUD_TERMS = {
    "Contas": ["laranja", "anjo"],
    "Golpes e esquemas": ["vazamento", "exploit", "backdoor", "bug", "esquema", "clone", "tela", "tela fake", "golpe"],
    "Venda de contas": ["virada", "transformar", "saldo", "limite", "desbloqueio", "viradinha"],
    "Cartões": ["info CC", "CC full", "aprovação", "CC", "bin", "virtual", "cartão virtual", "cartão", "clonado", "score alto"],
    "Ilícitos": ["bico", "ref", "referência"]
}

# Marcas monitoradas
BRANDS = ["nubank", "itau", "picpay", "mercado pago", "infinite pay", "bradesco", "santander", "inter"]

# -----------------------
# Função para conectar ao DB e criar tabela
# -----------------------
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fraudhunter_data (
                id SERIAL PRIMARY KEY,
                message_text TEXT,
                fraud_type TEXT,
                brands TEXT,
                from_user TEXT,
                chat_title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        return conn
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return None

# -----------------------
# Funções de classificação
# -----------------------
def classify_fraud(message):
    detected_types = []
    for fraud_type, terms in FRAUD_TERMS.items():
        for term in terms:
            if re.search(rf"\b{re.escape(term)}\b", message, re.IGNORECASE):
                detected_types.append(fraud_type)
                break
    return ", ".join(detected_types) if detected_types else None

def detect_brands(message):
    detected = [brand for brand in BRANDS if re.search(rf"\b{re.escape(brand)}\b", message, re.IGNORECASE)]
    return ", ".join(detected) if detected else None

# -----------------------
# Função para processar imagens via OCR
# -----------------------
def extract_text_from_image(file_path):
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang="por")
        return text
    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return ""

# -----------------------
# Função principal
# -----------------------
async def main():
    conn = get_db_connection()
    if not conn:
        print("[DB] Conexão falhou")
        return

    client = TelegramClient('fraud_hunter.session', API_ID, API_HASH)
    await client.start(PHONE)
    print("[Telegram] Bot rodando e monitorando mensagens...")

    @client.on(events.NewMessage)
    async def handler(event):
        message_text = event.message.message or ""
        if event.message.media:
            file_path = await event.message.download_media()
            ocr_text = extract_text_from_image(file_path)
            message_text += " " + ocr_text

        if not message_text.strip():
            return

        fraud_type = classify_fraud(message_text)
        brands = detect_brands(message_text)

        # Salvar apenas se encontrar fraude + marca
        if fraud_type and brands:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO fraudhunter_data (message_text, fraud_type, brands, from_user, chat_title)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (message_text, fraud_type, brands, str(event.sender_id), event.chat.title if event.chat else None)
                )
                conn.commit()
                cursor.close()
                print(f"[DB] Mensagem salva: Fraud={fraud_type}, Brands={brands}")
            except Exception as e:
                print(f"[DB ERROR] {e}")
                conn.rollback()
        else:
            print("[SKIP] Não tinha fraude + marca, ignorado.")

    await client.run_until_disconnected()

# -----------------------
# Entry point
# -----------------------
if __name__ == "__main__":
    asyncio.run(main())
