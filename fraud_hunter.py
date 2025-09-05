import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
import psycopg2

# Carregar variáveis de ambiente
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Conectar ao banco
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

# Criar tabela hunter_data se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS hunter_data (
    id SERIAL PRIMARY KEY,
    grupo TEXT,
    usuario TEXT,
    mensagem TEXT,
    data TIMESTAMP,
    tipo_fraude TEXT
)
""")
conn.commit()

# Diagrama de classificação de fraudes
FRAUDE_GRUPOS = {
    "Contas": ["laranja", "anjo"],
    "Golpes e esquemas": ["vazamento", "exploit", "backdoor", "bug", "esquema", "clone", "tela", "tela fake", "golpe"],
    "Venda de contas": ["virada", "transformar", "saldo", "limite", "desbloqueio", "viradinha"],
    "Cartões": ["Info CC", "CC full", "aprovação", "CC", "bin", "virtual", "cartão virtual", "cartão", "clonado", "score alto"],
    "Ilícitos": ["bico", "ref", "referência"]
}

# Iniciar cliente Telegram com sessão salva
client = TelegramClient("fraud_hunter.session", API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    if event.is_group:
        grupo = (await event.get_chat()).title
        sender = await event.get_sender()
        usuario = sender.username if sender.username else f"id_{sender.id}"
        mensagem = event.message.message
        data = event.message.date

        # Detectar tipo de fraude
        tipo_fraude_detectado = None
        for tipo_fraude, termos in FRAUDE_GRUPOS.items():
            if any(term.lower() in mensagem.lower() for term in termos):
                tipo_fraude_detectado = tipo_fraude
                break

        # Salvar no banco apenas se algum tipo de fraude for detectado
        if tipo_fraude_detectado:
            print(f"[{grupo}] {usuario}: {mensagem} | Tipo: {tipo_fraude_detectado}")
            cursor.execute(
                "INSERT INTO hunter_data (grupo, usuario, mensagem, data, tipo_fraude) VALUES (%s, %s, %s, %s, %s)",
                (grupo, usuario, mensagem, data, tipo_fraude_detectado)
            )
            conn.commit()

# Conectar e rodar
client.start()
print("📥 Coletando mensagens com palavras-chave e salvando no banco hunter_data...")
client.run_until_disconnected()
