import difflib
import json
import logging
import re
import threading
import time

import ollama
from llama_stack_client import APIConnectionError, APIStatusError, APITimeoutError

from backend_tu_nuevo_hogar.catalogo import HERRAMIENTA_DESARROLLO, quitar_acentos
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
MENSAJE_DESPEDIDA = "Estamos a sus órdenes para cualquier duda futura. ¡Hasta pronto!"
MENSAJE_SOLO_TEXTO = "Por ahora solo puedo leer mensajes de texto. ¿Me escribes tu duda?"
MENSAJE_SIN_RESPUESTA = "No encontré esa información. Un asesor puede confirmártela directamente."
MENSAJE_ERROR = "Estamos teniendo un problema técnico. Intenta de nuevo en un momento."

FRASES_ESCALAMIENTO = [
    "hablar con alguien", "hablar con una persona", "hablar con un asesor", "hablar con una asesora",
    "agente humano", "asesor humano", "que me llamen", "que me contacten",
    "agendar una visita", "agendar visita", "agendar una cita", "agendar cita",
]
# Una despedida es un mensaje que trae al menos una de estas frases y nada mas que relleno alrededor
# (se comparan sin acentos; "si" no es relleno porque "si, gracias" suele ser aceptar algo, no despedirse)
FRASES_DESPEDIDA = (
    r"gracias|adios|hasta (luego|pronto|manana|la proxima)|bye|nos vemos|chao|chau|(eso )?(es|seria) todo|"
    r"que (tenga|tengas|tengan) (un )?(buen|bonito|excelente) dia"
)
RELLENO_DESPEDIDA = (
    r"ok|okay|okey|vale|perfecto|listo|entendido|excelente|de acuerdo|muy bien|muy amable|no|muchas|muchisimas|mil|"
    r"por (todo|la informacion|la ayuda|su ayuda|tu ayuda|la atencion|su atencion)|igualmente|"
    r"buen dia|buenos dias|buenas tardes|buenas noches"
)

# Con que se contesta cada saludo del usuario; los que no estan aqui ("hola", "buenas") regresan "¡Hola! "
SALUDOS_DE_VUELTA = {
    "buenos dias": "¡Buenos días! ", "buenos días": "¡Buenos días! ", "buen dia": "¡Buenos días! ", "buen día": "¡Buenos días! ",
    "buenas tardes": "¡Buenas tardes! ", "buenas noches": "¡Buenas noches! ",
}
FRASES_SALUDO = ["hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "que tal", "buen dia", "buen día"]

SYSTEM_PROMPT = (
    "Eres el asistente de Tu Nuevo Hogar, una desarrolladora de vivienda. Orientas a personas interesadas en comprar casa. "
    "Responde de forma breve (1-2 lineas), con un tono amable y en español. "
    "Si preguntan que condominios o casas hay, menciona los cuatro condominios por su nombre. "
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

RESULTADO_EN_MENSAJE = (
    "Resultado de la consulta: {}\n\nResponde mi pregunta anterior en texto normal, usando solo esa informacion."
)

HERRAMIENTAS = [HERRAMIENTA_DESARROLLO, HERRAMIENTA_INFORMACION]


class HerramientaDesconocida(Exception):
    pass


def extraer_llamada_en_texto(texto):
    # llama3.1:8b a veces escribe la llamada como texto ({"name": ..., "parameters": {...}}) en vez de pedirla,
    # sobre todo cuando se equivoca en el nombre de la herramienta; regresa (nombre, argumentos) o None
    try:
        datos = json.loads((texto or "").strip().removeprefix("<|python_tag|>"))
    except ValueError:
        return None
    if not isinstance(datos, dict) or not isinstance(datos.get("name"), str):
        return None
    argumentos = datos.get("parameters", datos.get("arguments"))
    return datos["name"], argumentos if isinstance(argumentos, dict) else {}


def es_solo_despedida(texto_low):
    texto = " ".join(re.sub(r"[^a-z ]", " ", quitar_acentos(texto_low)).split())
    resto = re.sub(rf"\b({FRASES_DESPEDIDA}|{RELLENO_DESPEDIDA})\b", " ", texto)
    return not resto.strip() and re.search(rf"\b({FRASES_DESPEDIDA})\b", texto) is not None


def es_solo_saludo(texto_low):
    return texto_low.strip(" ,.!¡¿?") in FRASES_SALUDO


def saludo_inicial(texto_low):
    # Regresa el saludo con el que empieza el texto (None si no empieza con uno); las frases largas se prueban primero
    frases = "|".join(sorted(FRASES_SALUDO, key=len, reverse=True))
    coincidencia = re.match(rf"[\s¡]*({frases})\b", texto_low)
    return coincidencia.group(1) if coincidencia else None


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
        elif llamada_en_texto := extraer_llamada_en_texto(respuesta.output_text):
            nombre, argumentos = llamada_en_texto
            # El nombre suele venir casi bien ("consulta_desarrollo"); se acepta el mas parecido
            parecidos = difflib.get_close_matches(nombre, self.funciones, n=1, cutoff=0.8)
            if not parecidos:
                raise HerramientaDesconocida(nombre)
            logger.warning("El modelo escribio la llamada a %s como texto; se ejecuta %s.", nombre, parecidos[0])
            # No hay call_id al cual responder, asi que el resultado se manda como un mensaje mas
            respuesta = self.cliente.responses.create(
                model=self.modelo,
                input=[{"role": "user", "content": RESULTADO_EN_MENSAJE.format(self.funciones[parecidos[0]](argumentos))}],
                conversation=conversation_id,
                instructions=SYSTEM_PROMPT,
                tools=HERRAMIENTAS,
            )

        texto = (respuesta.output_text or "").strip()
        # Una llamada escrita como texto nunca se le manda al usuario
        if not texto or extraer_llamada_en_texto(texto):
            return MENSAJE_SIN_RESPUESTA
        return texto

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
        if es_solo_despedida(texto_low):
            self.whatsapp.enviar(numero, MENSAJE_DESPEDIDA)
            return "regla_despedida"

        # 3. Llama con herramientas
        respuesta = self.generar_respuesta(numero, texto)
        # Si el usuario saludo junto con su pregunta, se le regresa el saludo (el modelo no siempre lo hace)
        saludo = saludo_inicial(texto_low)
        if saludo and not saludo_inicial(respuesta.lower()):
            respuesta = SALUDOS_DE_VUELTA.get(saludo, "¡Hola! ") + respuesta

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
