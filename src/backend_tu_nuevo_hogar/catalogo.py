import json
import unicodedata
from pathlib import Path

RUTA_CATALOGO = Path(__file__).parent / "datos" / "catalogo.json"

HERRAMIENTA_DESARROLLO = {
    "type": "function",
    "name": "consultar_desarrollo",
    "description": (
        "Consulta en el catalogo los condominios y sus casas: precio, recamaras, banos, metros, estacionamiento, "
        "distribucion, equipamiento, amenidades, disponibilidad, fecha de entrega, casa muestra, apartado, cuota de "
        "mantenimiento y promociones. Si el usuario no menciono un condominio, omite el parametro para obtener "
        "la lista comparativa de todos los condominios."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "nombre": {
                "type": "string",
                "description": "Nombre del condominio (o de varios, para compararlos). Omite este parametro si el usuario no dio uno.",
            }
        },
        "required": [],
    },
}


def quitar_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


# Amenidades por las que se pregunta con si o no. El modelo contesta "si" cuando el resultado no las menciona,
# asi que su ausencia se dice de forma explicita
AMENIDADES_DESTACADAS = ("alberca", "gimnasio")


def tiene_amenidad(desarrollo, amenidad):
    return any(amenidad in a for a in desarrollo["amenidades"])


def normalizar(texto):
    return quitar_acentos(texto.lower()).strip(" ¿?¡!.\"'")


def cargar_desarrollos(ruta=RUTA_CATALOGO):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def describir_casa(desarrollo):
    return (
        f"{desarrollo['recamaras']} recamaras, {desarrollo['banos']:g} bano{'s' if desarrollo['banos'] != 1 else ''}, "
        f"{desarrollo['construccion_m2']} m2 de construccion, {desarrollo['terreno_m2']} m2 de terreno, "
        f"estacionamiento para {desarrollo['estacionamiento']}"
    )


class Catalogo:
    def __init__(self, desarrollos):
        self.desarrollos = desarrollos
        # Nombre y alias normalizados: el usuario puede escribir "cempazuchil" o "las bugambilias"
        self.nombres = [
            [normalizar(n) for n in [d["nombre"], *d.get("alias", [])]] for d in desarrollos
        ]

    def consultar(self, nombre=None):
        if not nombre or not normalizar(nombre):
            destacadas = " ".join(
                f"Con {a}: solo {', '.join(d['nombre'] for d in self.desarrollos if tiene_amenidad(d, a)) or 'ninguno'}."
                for a in AMENIDADES_DESTACADAS
            )
            return "Condominios: " + " | ".join(self._resumir(d) for d in self.desarrollos) + " | " + destacadas

        nombre_norm = normalizar(nombre)
        encontrados = [
            d for d, nombres in zip(self.desarrollos, self.nombres) if any(n in nombre_norm for n in nombres)
        ]
        if encontrados:
            return " | ".join(self._detallar(d) for d in encontrados)
        return f"No encontramos «{nombre}» en el catalogo. " + self.consultar()

    def _resumir(self, desarrollo):
        return (
            f"{desarrollo['nombre']} ({desarrollo['estado']}, entrega {desarrollo['entrega']}): "
            f"desde ${desarrollo['precio']:,} MXN, " + describir_casa(desarrollo)
        )

    def _detallar(self, desarrollo):
        promociones = " ".join(desarrollo["promociones"]) or "ninguna."
        faltan = [a for a in AMENIDADES_DESTACADAS if not tiene_amenidad(desarrollo, a)]
        # Al final del texto: en medio, el modelo lo pasa por alto
        no_tiene = f" Importante: {desarrollo['nombre']} NO tiene {' ni '.join(faltan)}." if faltan else ""
        return (
            f"Condominio {desarrollo['nombre']} ({desarrollo['estado']}, entrega {desarrollo['entrega']}). "
            f"{desarrollo['descripcion']} Precio desde ${desarrollo['precio']:,} MXN. "
            f"Casa: {describir_casa(desarrollo)}. "
            f"Distribucion: {desarrollo['distribucion']} "
            f"Incluye: {desarrollo['incluye']} "
            f"Amenidades: {', '.join(desarrollo['amenidades'])}. "
            f"Disponibilidad: {desarrollo['disponibilidad']} "
            f"Casa muestra: {desarrollo['casa_muestra']} "
            f"Apartado: ${desarrollo['apartado']:,} MXN. "
            f"Cuota de mantenimiento estimada: ${desarrollo['mantenimiento']:,} MXN al mes. "
            f"Promociones vigentes: {promociones}{no_tiene}"
        )
