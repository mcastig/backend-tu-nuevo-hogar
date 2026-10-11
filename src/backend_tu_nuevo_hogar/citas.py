import re
from datetime import date, datetime, timedelta, timezone

from backend_tu_nuevo_hogar.catalogo import quitar_acentos

# Datos del centro de ventas, tomados de INFO.md (secciones 2 y 7): si cambian alla, cambian aqui
DIRECCION = "Av. de los Fresnos 120, Col. El Mirador, Huichapan, Hidalgo"
# Citas cada hora en punto, por dia de la semana (lunes = 0); la ultima es a las 18:00, y a las 13:00 los sabados
HORAS_POR_DIA = {0: range(10, 19), 1: range(10, 19), 2: range(10, 19), 3: range(10, 19), 4: range(10, 19), 5: range(10, 14)}
DIAS_ADELANTE = 10  # se ofrecen citas desde manana hasta dentro de estos dias
MINUTOS_AGENDA = 30  # una agenda a medias se abandona sola tras este tiempo sin respuesta
# Hora del centro de Mexico, que ya no tiene horario de verano
ZONA = timezone(timedelta(hours=-6))

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
DIAS_CON_ACENTO = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Con que se pide, se cambia o se cancela una cita (se comparan sin acentos). "Necesito cita para ver las casas?"
# es una pregunta para el modelo, por eso se exige un verbo de agendar
FRASES_CITA = re.compile(
    r"\b(agendar|agendarme|agendame|agendo|reagendar|reservar|programar|sacar|hacer|pedir|cambiar|mover|"
    r"quiero|quisiera)\b (una |un |la |mi )?(visita|cita|recorrido)\b|\b(quiero|quisiera|gustaria) (ir a )?visitar|"
    # Preguntar si se puede ir cierto dia tambien se contesta con los dias y horas libres; el modelo se equivoca
    # con el horario ("el sabado esta cerrado")
    r"\b(ir|pasar|acudir) a (ver|conocer|visitar)\b|\bpuedo (ir|pasar|visitarlos) (el|este|manana|pasado|hoy)\b"
)
FRASES_CANCELAR_CITA = re.compile(r"\b(cancelar|cancela|cancelo|cancelen|cancelame)\b.*\b(cita|visita|recorrido)\b")
FRASES_SALIR = re.compile(r"\b(salir|cancelar|cancela|cancelalo|olvidalo|ya no|mejor no)\b")
# Un dia de la semana o "mañana" (no "de la mañana") en la respuesta: el usuario esta nombrando un dia, no una hora
NOMBRA_UN_DIA = re.compile(rf"\b({'|'.join(DIAS)})\b|(?<!de la )\bmanana\b")

MENSAJE_DIAS = "📅 Estos son los días disponibles para visitar nuestro centro de ventas:\n{}\n¿Qué día te gustaría venir?"
MENSAJE_HORAS = "Para el {} tengo estos horarios:\n{}\n¿A qué hora te esperamos?"
MENSAJE_NOMBRE = (
    "Perfecto, el {} a las {}:00 h. ¿A nombre de quién agendo la visita? "
    "Tu nombre se usa solo para que el asesor te reciba."
)
MENSAJE_CITA_AGENDADA = (
    "✅ ¡Listo, {}! Tu visita quedó agendada para el {} a las {}:00 h en nuestro centro de ventas: " + DIRECCION + ". "
    "Un asesor te estará esperando; el recorrido dura unos 40 minutos y no necesitas llevar documentos. "
    "Si necesitas cancelarla, escribe 'cancelar mi cita'."
)
MENSAJE_YA_TIENES_CITA = "Ya tienes una visita agendada para el {} a las {}:00 h; si eliges otra fecha, la cambio.\n\n"
MENSAJE_DIA_NO_ENTENDIDO = "No identifiqué ese día entre los disponibles. "
MENSAJE_HORA_NO_ENTENDIDA = "No identifiqué esa hora entre las disponibles. "
MENSAJE_NOMBRE_INVALIDO = "Escríbeme solo tu nombre y apellido, por favor (o escribe 'salir' para dejar la cita)."
MENSAJE_HORA_OCUPADA = "Esa hora se acaba de ocupar. "
MENSAJE_PARA_SALIR = "\nSi prefieres dejarlo para después, escribe 'salir'."
MENSAJE_CITA_ABANDONADA = "De acuerdo, no agendé ninguna visita. Cuando quieras retomarlo, escribe 'agendar una visita'."
MENSAJE_SIN_DISPONIBILIDAD = (
    "Por ahora no tengo horarios libres en los próximos días. Escribe 'hablar con un asesor' y te contactamos."
)
MENSAJE_CITA_CANCELADA = "Tu visita del {} a las {}:00 h quedó cancelada. Para elegir otra fecha, escribe 'agendar una visita'."
MENSAJE_SIN_CITA = "No encuentro ninguna visita agendada con este número. Para agendar una, escribe 'agendar una visita'."


def ahora():
    return datetime.now(ZONA)


def festivos(anio):
    # Dias de descanso obligatorio en Mexico: el centro de ventas cierra
    def lunes(mes, n):
        primero = date(anio, mes, 1)
        return primero + timedelta(days=(7 - primero.weekday()) % 7 + 7 * (n - 1))

    return {date(anio, 1, 1), lunes(2, 1), lunes(3, 3), date(anio, 5, 1), date(anio, 9, 16), lunes(11, 3), date(anio, 12, 25)}


def horas_de(fecha):
    if fecha in festivos(fecha.year):
        return []
    return list(HORAS_POR_DIA.get(fecha.weekday(), []))


def nombre_dia(fecha):
    return f"{DIAS_CON_ACENTO[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]}"


def interpretar_dia(texto, fechas, hoy):
    # Regresa la fecha ofrecida que nombra el texto ("el 15", "lunes", "pasado mañana"), o None
    sin_hora = re.sub(r"\ba las? \d{1,2}(:\d\d)?", " ", texto)
    for numero in re.findall(r"\d+", sin_hora):
        for fecha in fechas:
            if fecha.day == int(numero):
                return fecha
    for indice, dia in enumerate(DIAS):
        if re.search(rf"\b{dia}\b", sin_hora):
            return next((fecha for fecha in fechas if fecha.weekday() == indice), None)
    if re.search(r"\bpasado manana\b", sin_hora):
        return hoy + timedelta(days=2) if hoy + timedelta(days=2) in fechas else None
    if re.search(r"\bmanana\b", sin_hora):
        return hoy + timedelta(days=1) if hoy + timedelta(days=1) in fechas else None
    return None


def interpretar_hora(texto, horas):
    # Regresa la hora ofrecida que nombra el texto ("11", "a las 4 pm", "16:00"), o None
    coincidencia = re.search(r"\b(\d{1,2})(?::(\d\d))?\b", texto)
    if not coincidencia or coincidencia.group(2) not in (None, "00"):
        return None
    hora = int(coincidencia.group(1))
    # De la 1 a las 7 solo puede ser por la tarde: el centro de ventas abre a las 10
    if hora < 8 or (hora < 12 and re.search(r"\b(pm|p\.m|tarde)\b", texto)):
        hora += 12
    return hora if hora in horas else None


def limpiar_nombre(texto):
    # Las reglas del formulario del sitio: de 3 a 80 caracteres, solo letras, espacios, puntos, guiones y apostrofos
    nombre = " ".join(re.sub(r"^\s*(me llamo|mi nombre es|soy|a nombre de)\b", "", texto, flags=re.IGNORECASE).split())
    nombre = nombre.strip(" .,!")
    if not 3 <= len(nombre) <= 80 or not re.fullmatch(r"[^\W\d_]+(?:[ .'-]+[^\W\d_]+)*", nombre):
        return None
    return nombre


class Agendador:
    """Lleva al usuario paso a paso (dia, hora, nombre) hasta agendar una visita al centro de ventas."""

    def __init__(self, almacen):
        self.almacen = almacen

    def disponibles(self, hoy):
        # Los dias con citas libres desde manana, cada uno con sus horas; una hora ya agendada no se ofrece
        fechas = [hoy + timedelta(days=n) for n in range(1, DIAS_ADELANTE + 1)]
        ocupadas = self.almacen.horas_ocupadas(fechas[0].isoformat(), fechas[-1].isoformat())
        dias = {}
        for fecha in fechas:
            libres = [hora for hora in horas_de(fecha) if (fecha.isoformat(), hora) not in ocupadas]
            if libres:
                dias[fecha] = libres
        return dias

    def en_curso(self, numero):
        return self.almacen.obtener_agenda(numero, MINUTOS_AGENDA) is not None

    def atender(self, numero, texto):
        # Regresa (ruta, mensaje) si el texto pide, continua o cancela una cita, y None si no tiene que ver
        hoy = ahora().date()
        texto_low = quitar_acentos(texto.lower())
        agenda = self.almacen.obtener_agenda(numero, MINUTOS_AGENDA)
        if agenda is None:
            if FRASES_CANCELAR_CITA.search(texto_low):
                return self._cancelar(numero, hoy)
            if FRASES_CITA.search(texto_low):
                return self._empezar(numero, texto_low, hoy)
            return None
        if FRASES_SALIR.search(texto_low):
            self.almacen.borrar_agenda(numero)
            return "regla_cita", MENSAJE_CITA_ABANDONADA

        paso, fecha, hora = agenda
        dias = self.disponibles(hoy)
        fecha = date.fromisoformat(fecha) if fecha else None
        if paso != "dia" and fecha not in dias:
            # El dia elegido se lleno o ya paso mientras el usuario contestaba
            paso = "dia"
        if paso == "nombre":
            return self._agendar(numero, limpiar_nombre(texto), fecha, hora, dias, hoy)
        if paso == "hora":
            # Tambien puede estar cambiando de dia ("mejor el martes 14")
            otra = interpretar_dia(texto_low, list(dias), hoy) if NOMBRA_UN_DIA.search(texto_low) else None
            hora = interpretar_hora(texto_low, dias[fecha]) if otra is None else None
            if hora is not None:
                return self._pedir_nombre(numero, fecha, hora)
            if otra is None:
                return "regla_cita", MENSAJE_HORA_NO_ENTENDIDA + self._texto_horas(fecha, dias[fecha]) + MENSAJE_PARA_SALIR
            fecha = otra
        else:
            fecha = interpretar_dia(texto_low, list(dias), hoy)
            if fecha is None:
                return "regla_cita", MENSAJE_DIA_NO_ENTENDIDO + self._texto_dias(dias) + MENSAJE_PARA_SALIR
            # "el lunes a las 11" trae las dos respuestas
            con_hora = re.search(r"\ba las? (\d{1,2}.*)", texto_low)
            hora = interpretar_hora(con_hora.group(1), dias[fecha]) if con_hora else None
            if hora is not None:
                return self._pedir_nombre(numero, fecha, hora)
        self.almacen.guardar_agenda(numero, "hora", fecha.isoformat(), None)
        return "regla_cita", self._texto_horas(fecha, dias[fecha])

    def _empezar(self, numero, texto_low, hoy):
        dias = self.disponibles(hoy)
        if not dias:
            return "regla_cita", MENSAJE_SIN_DISPONIBILIDAD
        self.almacen.guardar_agenda(numero, "dia", None, None)
        cita = self.almacen.cita_vigente(numero, hoy.isoformat())
        aviso = MENSAJE_YA_TIENES_CITA.format(nombre_dia(date.fromisoformat(cita[0])), cita[1]) if cita else ""
        # "¿Puedo ir el sabado?" ya trae el dia: se pasa directo a sus horas
        fecha = interpretar_dia(texto_low, list(dias), hoy) if NOMBRA_UN_DIA.search(texto_low) else None
        if fecha is None:
            return "regla_cita", aviso + self._texto_dias(dias)
        self.almacen.guardar_agenda(numero, "hora", fecha.isoformat(), None)
        return "regla_cita", aviso + self._texto_horas(fecha, dias[fecha])

    def _pedir_nombre(self, numero, fecha, hora):
        self.almacen.guardar_agenda(numero, "nombre", fecha.isoformat(), hora)
        return "regla_cita", MENSAJE_NOMBRE.format(nombre_dia(fecha), hora)

    def _agendar(self, numero, nombre, fecha, hora, dias, hoy):
        if nombre is None:
            return "regla_cita", MENSAJE_NOMBRE_INVALIDO
        if hora not in dias[fecha] or not self.almacen.guardar_cita(
            numero, nombre, fecha.isoformat(), hora, hoy.isoformat()
        ):
            horas = [libre for libre in dias[fecha] if libre != hora]
            if not horas:
                self.almacen.guardar_agenda(numero, "dia", None, None)
                return "regla_cita", MENSAJE_HORA_OCUPADA + self._texto_dias({d: h for d, h in dias.items() if d != fecha})
            self.almacen.guardar_agenda(numero, "hora", fecha.isoformat(), None)
            return "regla_cita", MENSAJE_HORA_OCUPADA + self._texto_horas(fecha, horas)
        self.almacen.borrar_agenda(numero)
        return "cita_agendada", MENSAJE_CITA_AGENDADA.format(nombre, nombre_dia(fecha), hora)

    def _cancelar(self, numero, hoy):
        cita = self.almacen.cancelar_cita(numero, hoy.isoformat())
        if cita is None:
            return "regla_cita", MENSAJE_SIN_CITA
        return "cita_cancelada", MENSAJE_CITA_CANCELADA.format(nombre_dia(date.fromisoformat(cita[0])), cita[1])

    def _texto_dias(self, dias):
        return MENSAJE_DIAS.format("\n".join(f"• {nombre_dia(fecha)}" for fecha in dias))

    def _texto_horas(self, fecha, horas):
        return MENSAJE_HORAS.format(nombre_dia(fecha), ", ".join(f"{hora}:00" for hora in horas))
