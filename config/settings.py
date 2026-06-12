"""Configuración central del agente.

Único punto de verdad. Toda la app lee de aquí; nadie lee os.environ directamente
(excepto LiteLLM, que necesita GROQ_API_KEY en el entorno — por eso cargamos .env
con load_dotenv antes de construir Settings).

Cambiar de proveedor de IA = cambiar AI_MODEL en .env. Cero cambios de código.
Cambiar de base de datos = cambiar DATABASE_URL en .env. Cero cambios de código.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Carga .env en os.environ para que LiteLLM encuentre GROQ_API_KEY automáticamente.
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Capa IA (LiteLLM) ---
    AI_MODEL: str = "groq/llama-3.1-8b-instant"
    GROQ_API_KEY: str

    # --- Telegram ---
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    # --- Gmail ---
    GMAIL_CREDENTIALS_FILE: str = "credentials.json"
    GMAIL_TOKEN_FILE: str = "data/gmail_token.json"

    # --- Base de datos ---
    DATABASE_URL: str = "sqlite:///data/financial_agent.db"

    # --- Runtime ---
    FETCH_INTERVAL_HOURS: int = 5
    LOOKBACK_HOURS: int = 5
    # Query de Gmail: remitentes financieros objetivo del MVP.
    GMAIL_QUERY: str = "(from:seekingalpha.com OR from:investing.com)"


settings = Settings()
