import hmac
import json
import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from backend_tu_nuevo_hogar.agente import Agente
from backend_tu_nuevo_hogar.config import Configuracion
from backend_tu_nuevo_hogar.whatsapp import ClienteWhatsApp, firma_valida, normalizar_numero_mx

logger = logging.getLogger(__name__)


def construir_agente(config):
    import ollama
    from llama_stack_client import LlamaStackClient

    from backend_tu_nuevo_hogar.almacenamiento import Almacen
    from backend_tu_nuevo_hogar.catalogo import Catalogo, cargar_desarrollos
    from backend_tu_nuevo_hogar.conocimiento import BaseConocimiento, cargar_fragmentos, crear_codificador
    from backend_tu_nuevo_hogar.seguridad import LlamaGuard, cargar_prompt_guard

    return Agente(
        # timeout alto y sin reintentos: un reintento automatico duplica turnos en la conversacion
        cliente=LlamaStackClient(base_url=config.llama_stack_url, timeout=300, max_retries=0),
        modelo=config.modelo_chat,
        almacen=Almacen(config.database_path),
        conocimiento=BaseConocimiento(
            cargar_fragmentos(), crear_codificador(config.modelo_embeddings), config.umbral_conocimiento
        ),
        catalogo=Catalogo(cargar_desarrollos()),
        llama_guard=LlamaGuard(ollama.Client(host=config.ollama_host), config.modelo_guard),
        prompt_guard=cargar_prompt_guard(config.prompt_guard_modelo, config.hf_token),
        whatsapp=ClienteWhatsApp(config.whatsapp_access_token, config.phone_number_id, config.graph_api_version),
    )


def crear_app(config=None, agente=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.config = config or Configuracion()
        app.state.agente = agente or construir_agente(app.state.config)
        if not app.state.config.whatsapp_app_secret:
            logger.warning("WHATSAPP_APP_SECRET no definido: no se valida la firma de los webhooks.")
        yield

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/webhook")
    async def verificar_webhook(request: Request):
        params = request.query_params
        token = params.get("hub.verify_token", "")
        if params.get("hub.mode") == "subscribe" and hmac.compare_digest(
            token.encode(), request.app.state.config.verify_token.encode()
        ):
            return PlainTextResponse(params.get("hub.challenge", ""))
        raise HTTPException(status_code=403, detail="token invalido")

    @app.post("/webhook")
    async def recibir_mensaje(request: Request, background_tasks: BackgroundTasks):
        config = request.app.state.config
        agente = request.app.state.agente
        cuerpo = await request.body()
        if config.whatsapp_app_secret and not firma_valida(
            config.whatsapp_app_secret, cuerpo, request.headers.get("X-Hub-Signature-256")
        ):
            raise HTTPException(status_code=403, detail="firma invalida")
        try:
            body = json.loads(cuerpo)
        except ValueError:
            raise HTTPException(status_code=400, detail="json invalido")

        # Siempre se responde 200 de inmediato; el trabajo pesado va a BackgroundTasks
        for mensaje in extraer_mensajes(body):
            try:
                wamid = mensaje["id"]
                numero = normalizar_numero_mx(mensaje["from"])
            except (KeyError, TypeError):
                continue
            if not agente.almacen.marcar_procesado(wamid):
                continue  # Meta reenvio el mismo mensaje; ya se proceso, se ignora
            if mensaje.get("type") == "text":
                background_tasks.add_task(agente.procesar_y_responder, numero, mensaje["text"]["body"])
            else:
                background_tasks.add_task(agente.responder_no_texto, numero)
        return {"status": "ok"}

    @app.get("/health")
    async def health(request: Request):
        return {"status": "ok", "prompt_guard": request.app.state.agente.prompt_guard is not None}

    @app.get("/metricas")
    async def metricas(request: Request):
        admin_token = request.app.state.config.admin_token
        if not admin_token:
            raise HTTPException(status_code=404)
        recibido = request.headers.get("Authorization", "")
        if not hmac.compare_digest(recibido.encode(), f"Bearer {admin_token}".encode()):
            raise HTTPException(status_code=401)
        return request.app.state.agente.almacen.resumen_metricas()

    return app


def extraer_mensajes(body):
    # Un webhook puede traer varios mensajes; las notificaciones de estado (sent, delivered) no traen "messages"
    mensajes = []
    try:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                mensajes.extend(change.get("value", {}).get("messages", []))
    except AttributeError:
        return []
    return [m for m in mensajes if isinstance(m, dict)]


app = crear_app()
