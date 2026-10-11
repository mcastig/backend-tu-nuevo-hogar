from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # WhatsApp Cloud API
    verify_token: str
    whatsapp_access_token: str
    phone_number_id: str
    whatsapp_app_secret: str | None = None  # si se define, se valida la firma de cada webhook
    graph_api_version: str = "v25.0"

    # Modelos
    llama_stack_url: str = "http://localhost:8321"
    ollama_host: str = "http://localhost:11434"
    modelo_chat: str = "ollama/llama3.1:8b"
    modelo_guard: str = "llama-guard3"
    modelo_embeddings: str = "paraphrase-multilingual-MiniLM-L12-v2"
    prompt_guard_modelo: str = "meta-llama/Llama-Prompt-Guard-2-86M"
    hf_token: str | None = None  # sin token no se carga Prompt Guard (repositorio restringido)
    umbral_conocimiento: float = 0.30  # similitud minima para considerar que la base cubre la pregunta
    horas_conversacion: float = 3  # horas sin mensajes tras las que se empieza una conversacion nueva

    # Servidor
    database_path: Path = Path("data/bot.sqlite3")
    admin_token: str | None = None  # habilita GET /metricas
    host: str = "0.0.0.0"
    port: int = 8000
