import sqlite3
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS conversaciones (
    numero TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS mensajes_procesados (
    wamid TEXT PRIMARY KEY,
    recibido TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS metricas (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL,
    ruta TEXT NOT NULL,
    duracion_s REAL NOT NULL,
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS errores (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL,
    texto TEXT NOT NULL,
    causa TEXT NOT NULL,
    detalle TEXT NOT NULL,
    error TEXT NOT NULL,
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS bloqueos (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL,
    texto TEXT NOT NULL,
    capa TEXT NOT NULL,
    detalle TEXT NOT NULL,
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS solicitudes_contacto (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL,
    texto TEXT NOT NULL,
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class Almacen:
    """Estado que en el notebook vivia en memoria y debe sobrevivir a un reinicio."""

    def __init__(self, ruta):
        self.ruta = str(ruta)
        Path(self.ruta).parent.mkdir(parents=True, exist_ok=True)
        with self._conexion() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.executescript(ESQUEMA)

    @contextmanager
    def _conexion(self):
        con = sqlite3.connect(self.ruta, timeout=30)
        try:
            with con:
                yield con
        finally:
            con.close()

    def marcar_procesado(self, wamid):
        # Regresa False si Meta reenvio un mensaje que ya se habia despachado
        with self._conexion() as con:
            cursor = con.execute("INSERT OR IGNORE INTO mensajes_procesados (wamid) VALUES (?)", (wamid,))
            return cursor.rowcount == 1

    def obtener_conversacion(self, numero):
        with self._conexion() as con:
            fila = con.execute("SELECT conversation_id FROM conversaciones WHERE numero = ?", (numero,)).fetchone()
        return fila[0] if fila else None

    def guardar_conversacion(self, numero, conversation_id):
        with self._conexion() as con:
            con.execute(
                "INSERT OR REPLACE INTO conversaciones (numero, conversation_id) VALUES (?, ?)",
                (numero, conversation_id),
            )

    def registrar_metrica(self, numero, ruta, duracion_s):
        with self._conexion() as con:
            con.execute(
                "INSERT INTO metricas (numero, ruta, duracion_s) VALUES (?, ?, ?)", (numero, ruta, duracion_s)
            )

    def registrar_error(self, numero, texto, causa, detalle, error):
        with self._conexion() as con:
            con.execute(
                "INSERT INTO errores (numero, texto, causa, detalle, error) VALUES (?, ?, ?, ?, ?)",
                (numero, texto, causa, detalle, repr(error)),
            )

    def registrar_bloqueo(self, numero, texto, capa, detalle):
        with self._conexion() as con:
            con.execute(
                "INSERT INTO bloqueos (numero, texto, capa, detalle) VALUES (?, ?, ?, ?)",
                (numero, texto, capa, detalle),
            )

    def registrar_solicitud_contacto(self, numero, texto):
        with self._conexion() as con:
            con.execute("INSERT INTO solicitudes_contacto (numero, texto) VALUES (?, ?)", (numero, texto))

    def resumen_metricas(self):
        with self._conexion() as con:
            por_ruta = dict(con.execute("SELECT ruta, COUNT(*) FROM metricas GROUP BY ruta").fetchall())
            promedio = con.execute("SELECT AVG(duracion_s) FROM metricas").fetchone()[0]
            promedio_llama = con.execute("SELECT AVG(duracion_s) FROM metricas WHERE ruta = 'llama'").fetchone()[0]
            causas = dict(con.execute("SELECT causa, COUNT(*) FROM errores GROUP BY causa").fetchall())
            solicitudes = con.execute("SELECT COUNT(*) FROM solicitudes_contacto").fetchone()[0]
        total = sum(por_ruta.values())
        errores = por_ruta.get("error", 0)
        return {
            "mensajes_procesados": total,
            "volumen_por_ruta": por_ruta,
            "tasa_error": errores / total if total else 0.0,
            "tiempo_promedio_s": round(promedio, 2) if promedio is not None else None,
            "tiempo_promedio_llama_s": round(promedio_llama, 2) if promedio_llama is not None else None,
            "causas_error": causas,
            "solicitudes_contacto": solicitudes,
        }
