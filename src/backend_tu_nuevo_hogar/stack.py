"""Levanta Llama Stack con el modelo de Ollama registrado (requiere `uv sync --group stack`)."""

import os
from pathlib import Path


def main() -> None:
    import httpx
    import llama_stack
    import yaml

    from backend_tu_nuevo_hogar.config import Configuracion

    # Solo se usan los campos con valor por defecto; el servidor de modelos no necesita las credenciales de WhatsApp
    campos = Configuracion.model_fields
    ollama_host = os.environ.get("OLLAMA_HOST", campos["ollama_host"].default)
    modelo = os.environ.get("MODELO_CHAT", campos["modelo_chat"].default).removeprefix("ollama/")
    puerto = os.environ.get("LLAMA_STACK_PORT", "8321")

    # Sin Ollama, Llama Stack falla al registrar el modelo con un "Connection error" dificil de leer
    try:
        etiquetas = httpx.get(ollama_host.rstrip("/") + "/api/tags", timeout=5).raise_for_status().json()
    except httpx.HTTPError as e:
        raise SystemExit(f"No se pudo conectar a Ollama en {ollama_host} ({e!r}). Inicialo con `ollama serve`.")
    if modelo not in [m["name"] for m in etiquetas.get("models", [])]:
        raise SystemExit(f"Ollama no tiene el modelo {modelo}. Descargalo con `ollama pull {modelo}`.")

    os.environ.setdefault("OLLAMA_URL", ollama_host.rstrip("/") + "/v1")

    config_path = Path(llama_stack.__file__).parent / "distributions" / "starter" / "config.yaml"
    config = yaml.safe_load(config_path.read_text())
    config["registered_resources"]["models"].append({
        "model_id": modelo,
        "provider_id": "ollama",
        "provider_model_id": modelo,
        "model_type": "llm",
    })

    mi_config_path = Path("data") / "llama_stack.yaml"
    mi_config_path.parent.mkdir(parents=True, exist_ok=True)
    mi_config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))

    os.execvp("llama", ["llama", "stack", "run", str(mi_config_path), "--port", puerto])
