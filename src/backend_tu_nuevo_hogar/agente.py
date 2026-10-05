import json
import logging
import threading
import time

import ollama
from llama_stack_client import APIConnectionError, APIStatusError, APITimeoutError

from backend_tu_nuevo_hogar.catalogo import HERRAMIENTA_DESARROLLO
from backend_tu_nuevo_hogar.conocimiento import HERRAMIENTA_INFORMACION
from backend_tu_nuevo_hogar.whatsapp import ErrorWhatsApp

logger = logging.getLogger(__name__)

MENSAJE_BLOQUEO = "Lo siento, no puedo ayudar con ese mensaje. Si buscas casa, escríbeme tu duda."
MENSAJE_RESPUESTA_BLOQUEADA = "No puedo compartir esa respuesta. Un asesor se pondrá en contacto contigo."
MENSAJE_ESCALAMIENTO = "Claro, en un momento un asesor te contacta directamente por este medio."
MENSAJE_SALUDO = (
    "Hola, soy el asistente de Tu Nuevo Hogar. Puedo informarte sobre nuestras casas, precios, "
    "créditos y el proceso de compra. ¿En qué puedo ayudarte?"
)
MENSAJE_SOLO_TEXTO = "Por ahora solo puedo leer mensajes de texto. ¿Me escribes tu duda?"
MENSAJE_SIN_RESPUESTA = "No encontré esa información. Un asesor puede confirmártela directamente."
MENSAJE_ERROR = "Estamos teniendo un problema técnico. Intenta de nuevo en un momento."

FRASES_ESCALAMIENTO = [
    "hablar con alguien", "hablar con una persona", "hablar con un asesor", "hablar con una asesora",
    "agente humano", "asesor humano", "que me llamen", "que me contacten",
    "agendar una visita", "agendar visita", "agendar una cita", "agendar cita",
]
FRASES_SALUDO = ["hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "que tal", "buen dia", "buen día"]

SYSTEM_PROMPT = (
    "Eres el asistente de Tu Nuevo Hogar, una desarrolladora de vivienda. Orientas a personas interesadas en comprar casa. "
    "Responde de forma breve (2-4 lineas) y en español. "
    "Solo usa una herramienta cuando el usuario pregunte algo especifico que la herramienta pueda responder "
    "(los condominios y sus casas, precios, caracteristicas y disponibilidad, o una duda sobre el proceso de compra, "
    "creditos, mensualidades, promociones y demas informacion de la inmobiliaria). No uses ninguna herramienta para "
    "confirmaciones o respuestas cortas del usuario (como 'si, por favor' o 'gracias'). "
    "No puedes apartar casas, agendar visitas, autorizar creditos ni negociar precios o descuentos — solo puedes "
    "consultar el catalogo y explicar la informacion oficial. Si el usuario quiere apartar, visitar o iniciar un "
    "tramite, dile que escriba 'hablar con un asesor' para que un asesor lo contacte. "
    "No des asesoria legal, fiscal ni financiera personalizada, y nunca asegures que un credito sera aprobado. "
    "Para dudas de informacion responde unicamente con lo que diga el fragmento que regrese la herramienta. "
    "Si una herramienta no encuentra una respuesta, dilo honestamente en vez de inventar un dato. "
    "Si una herramienta SI regresa un resultado real, siempre comunicalo claramente al usuario; nunca lo ignores ni te niegues a compartirlo. "
    "Responde siempre de forma directa con la informacion final, basandote unicamente en el resultado real de las "
    "herramientas; nunca inventes precios, fechas ni datos que no vengan de una herramienta. "
    "Nunca describas tu proceso, ni menciones nombres de funciones, parametros o claves de un resultado."
)

HERRAMIENTAS = [HERRAMIENTA_DESARROLLO, HERRAMIENTA_INFORMACION]


class HerramientaDesconocida(Exception):
    pass


def es_solo_saludo(texto_low):
    return texto_low.strip(" ,.!¡¿?") in FRASES_SALUDO


class Agente:
    def __init__(self, cliente, modelo, almacen, conocimiento, catalogo, llama_guard, prompt_guard, whatsapp):
        self.cliente = cliente  # LlamaStackClient
        self.modelo = modelo
        self.almacen = almacen
        self.llama_guard = llama_guard
        self.prompt_guard = prompt_guard  # None si no se pudo cargar
        self.whatsapp = whatsapp
        self.funciones = {
            "consultar_desarrollo": lambda args: catalogo.consultar(args.get("nombre")),
            "buscar_informacion": lambda args: conocimiento.buscar(args.get("pregunta", "")),
        }
        # Un lock por numero de telefono, para serializar mensajes del mismo usuario
        # (evita dos respuestas en paralelo sobre la misma conversacion de Llama Stack)
        self._locks = {}
        self._locks_guard = threading.Lock()

    def _obtener_lock(self, numero):
        with self._locks_guard:
            return self._locks.setdefault(numero, threading.Lock())

    def obtener_conversacion(self, numero):
        conversation_id = self.almacen.obtener_conversacion(numero)
        if conversation_id is None:
            conversation_id = self.cliente.conversations.create().id
            self.almacen.guardar_conversacion(numero, conversation_id)
        return conversation_id

    def generar_respuesta(self, numero, texto_usuario):
        conversation_id = self.obtener_conversacion(numero)
        respuesta = self.cliente.responses.create(
            model=self.modelo,
            input=texto_usuario,
            conversation=conversation_id,
            instructions=SYSTEM_PROMPT,
            tools=HERRAMIENTAS,
        )

        llamadas_funcion = [item for item in respuesta.output if item.type == "function_call"]
        if llamadas_funcion:
            resultados = []
            for llamada in llamadas_funcion:
                if llamada.name not in self.funciones:
                    raise HerramientaDesconocida(llamada.name)
                argumentos = json.loads(llamada.arguments or "{}")
                resultados.append({
                    "type": "function_call_output",
                    "call_id": llamada.call_id,
                    "output": self.funciones[llamada.name](argumentos),
                })
            respuesta = self.cliente.responses.create(
                model=self.modelo,
                input=resultados,
                conversation=conversation_id,
                instructions=SYSTEM_PROMPT,
                tools=HERRAMIENTAS,
            )

        return (respuesta.output_text or "").strip() or MENSAJE_SIN_RESPUESTA

    def decidir_y_responder(self, numero, texto):
        # Regresa el nombre de la ruta que tomo el mensaje
        texto_low = texto.lower()

        # 1. Seguridad sobre la entrada
        if self.prompt_guard is not None and self.prompt_guard.es_inyeccion(texto):
            self.almacen.registrar_bloqueo(numero, texto, "prompt_guard", "inyeccion de prompt")
            self.whatsapp.enviar(numero, MENSAJE_BLOQUEO)
            return "bloqueado_prompt_guard"

        seguro, categoria = self.llama_guard.revisar([{"role": "user", "content": texto}])
        if not seguro:
            self.almacen.registrar_bloqueo(numero, texto, "llama_guard_entrada", categoria)
            self.whatsapp.enviar(numero, MENSAJE_BLOQUEO)
            return "bloqueado_llama_guard_entrada"

        # 2. Reglas fijas
        if any(frase in texto_low for frase in FRASES_ESCALAMIENTO):
            self.almacen.registrar_solicitud_contacto(numero, texto)
            self.whatsapp.enviar(numero, MENSAJE_ESCALAMIENTO)
            return "regla_escalamiento"
        if es_solo_saludo(texto_low):
            self.whatsapp.enviar(numero, MENSAJE_SALUDO)
            return "regla_saludo"

        # 3. Llama con herramientas
        respuesta = self.generar_respuesta(numero, texto)

        # 4. Seguridad sobre la salida
        seguro, categoria = self.llama_guard.revisar([
            {"role": "user", "content": texto},
            {"role": "assistant", "content": respuesta},
        ])
        if not seguro:
            self.almacen.registrar_bloqueo(numero, respuesta, "llama_guard_salida", categoria)
            self.whatsapp.enviar(numero, MENSAJE_RESPUESTA_BLOQUEADA)
            return "bloqueado_llama_guard_salida"

        self.whatsapp.enviar(numero, respuesta)
        return "llama"

    def _registrar_error(self, numero, texto, causa, detalle, error, avisar=True):
        logger.error("%s: %s (%r)", causa, detalle, error)
        self.almacen.registrar_error(numero, texto, causa, detalle, error)
        if avisar:
            try:
                self.whatsapp.enviar(numero, MENSAJE_ERROR)
            except ErrorWhatsApp:
                pass  # si ni el aviso de error se pudo mandar, no hay mas que intentar aqui

    def procesar_y_responder(self, numero, texto):
        with self._obtener_lock(numero):
            inicio = time.perf_counter()
            ruta = "error"
            try:
                ruta = self.decidir_y_responder(numero, texto)
            except APITimeoutError as e:
                self._registrar_error(numero, texto, "llama_timeout", "Llama Stack conecto pero la generacion tardo demasiado.", e)
            except APIConnectionError as e:
                self._registrar_error(numero, texto, "llama_stack_no_disponible", "No se pudo conectar a Llama Stack.", e)
            except APIStatusError as e:
                self._registrar_error(numero, texto, "llama_stack_error_http", f"Llama Stack respondio con error HTTP {e.status_code}.", e)
            except (ConnectionError, ollama.ResponseError) as e:
                self._registrar_error(numero, texto, "llama_guard_no_disponible", "Fallo la llamada a Ollama desde la capa de seguridad (Llama Guard).", e)
            except HerramientaDesconocida as e:
                self._registrar_error(numero, texto, "herramienta_no_reconocida", f"El modelo pidio ejecutar una herramienta que no existe: {e}.", e)
            except ErrorWhatsApp as e:
                # No se intenta avisar al usuario: si fallo mandar el mensaje a WhatsApp, el aviso fallaria igual
                self._registrar_error(numero, texto, "whatsapp_api_error", "Fallo el envio a la API de WhatsApp (graph.facebook.com).", e, avisar=False)
            except Exception as e:
                self._registrar_error(numero, texto, "desconocido", "Error no clasificado.", e)
            finally:
                duracion = round(time.perf_counter() - inicio, 2)
                self.almacen.registrar_metrica(numero, ruta, duracion)
                logger.info("mensaje procesado ruta=%s duracion_s=%s", ruta, duracion)

    def responder_no_texto(self, numero):
        try:
            self.whatsapp.enviar(numero, MENSAJE_SOLO_TEXTO)
        except ErrorWhatsApp as e:
            logger.error("whatsapp_api_error al responder un mensaje que no es de texto (%r)", e)
