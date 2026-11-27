"""Configurações locais carregadas de variáveis de ambiente."""
import os
from dotenv import load_dotenv


def load_settings():
    load_dotenv()
    return {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017"),
        "DB_NAME": os.getenv("MONGO_DATABASE", "acolhimento_db"),
        "WRITE_TOKEN": os.getenv("API_WRITE_TOKEN", ""),
        "LOG_PATH": os.getenv("LOG_PATH", "logs/acoes.log"),
        "APP_HOST": os.getenv("APP_HOST", "127.0.0.1"),
        "APP_PORT": int(os.getenv("APP_PORT", "5000")),
        "TCP_HOST": os.getenv("TCP_HOST", "127.0.0.1"),
        "TCP_PORT": int(os.getenv("TCP_PORT", "9090")),
    }
