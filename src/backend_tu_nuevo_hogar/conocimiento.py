import json
import re
from pathlib import Path

import numpy as np

from backend_tu_nuevo_hogar.catalogo import quitar_acentos

RUTA_CONOCIMIENTO = Path(__file__).parent / "datos" / "conocimiento.json"

SIN_COBERTURA = "La informacion disponible no cubre esa pregunta; un asesor puede confirmarla directamente."

HERRAMIENTA_INFORMACION = {
    "type": "function",
    "name": "buscar_informacion",
    "description": (
        "Busca en la informacion oficial de la inmobiliaria la respuesta a dudas sobre horarios, ubicacion, "
        "contacto, visitas, proceso de compra, apartado, enganche, creditos, tasas, mensualidades estimadas, "
        "documentos, escrituracion, promociones, amenidades, servicios, mascotas, mantenimiento, garantia, "
        "entrega, asesores y aviso de privacidad."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "pregunta": {
                "type": "string",
                "description": "La pregunta del usuario, en texto libre.",
            }
        },
        "required": ["pregunta"],
    },
}


# El modelo de embeddings puntua bajo las preguntas muy cortas ("¿Tiene alberca?"); si la pregunta
# comparte una palabra clave con el fragmento, se le suma este bono a la similitud
BONO_PALABRA_CLAVE = 0.20
# Bono adicional por cada palabra clave de la pregunta que aparece en el titulo del fragmento (maximo 2):
# entre varios fragmentos que mencionan "enganche", gana el que trata de eso
BONO_TITULO = 0.10
PALABRAS_GENERICAS = {
    "casa", "casas", "condominio", "condominios", "nuevo", "hogar", "puedo", "puede", "pueden", "tiene", "tienen",
    "tengo", "tenemos", "tener", "cuanto", "cuanta", "cuantos", "cuantas", "donde", "cuando", "cual", "cuales",
    "quien", "quienes", "como", "porque", "necesito", "quiero", "gustaria", "sobre", "informacion", "saber",
    "esta", "este", "esto", "estos", "estas", "estan", "estamos", "esos", "esas", "ella", "ellos", "ustedes",
    "para", "pero", "solo", "algo", "algun", "alguna", "cada", "todo", "toda", "todos", "todas", "otro", "otra",
    "mucho", "tipo", "bien", "aqui", "alla", "hola", "unos", "unas", "sino", "pues", "favor", "gracias",
    "desde", "hasta", "entre", "hacia", "antes", "despues", "ademas", "tambien", "sera", "seria", "serian", "sido",
    "hace", "hacer", "hacen", "dice", "debo", "deben", "manejan", "cuesta", "cuestan", "compra", "comprar",
}


def palabras_clave(texto):
    # Se comparan raices de 5 letras, para que "entregan" coincida con "entrega" y "citas" con "cita"
    palabras = set(re.findall(r"[a-z]{4,}", quitar_acentos(texto.lower()))) - PALABRAS_GENERICAS
    return {p.removesuffix("s")[:5] for p in palabras} - PALABRAS_GENERICAS


def cargar_fragmentos(ruta=RUTA_CONOCIMIENTO):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def crear_codificador(nombre_modelo):
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(nombre_modelo)
    return lambda textos: modelo.encode(textos, normalize_embeddings=True)


class BaseConocimiento:
    """RAG sobre los fragmentos: `codificar` recibe una lista de textos y regresa embeddings normalizados."""

    def __init__(self, fragmentos, codificar, umbral):
        self.fragmentos = fragmentos
        self.codificar = codificar
        self.umbral = umbral
        self.embeddings = np.asarray(codificar(fragmentos))
        self.palabras = [palabras_clave(f) for f in fragmentos]
        self.palabras_titulo = [palabras_clave(f.split(":")[0]) for f in fragmentos]

    def similitudes(self, pregunta):
        embedding_pregunta = np.asarray(self.codificar([pregunta]))
        similitudes = np.dot(self.embeddings, embedding_pregunta.T).flatten()
        claves = palabras_clave(pregunta)
        bono = np.array([
            (BONO_PALABRA_CLAVE if claves & palabras else 0.0) + BONO_TITULO * min(len(claves & titulo), 2)
            for palabras, titulo in zip(self.palabras, self.palabras_titulo)
        ])
        return similitudes + bono

    def buscar(self, pregunta, k=3):
        similitudes = self.similitudes(pregunta)
        indices = np.argsort(similitudes)[::-1][:k]
        relevantes = [i for i in indices if similitudes[i] >= self.umbral]
        if not relevantes:
            return SIN_COBERTURA
        return "Fragmentos de la informacion oficial: " + " | ".join(self.fragmentos[i] for i in relevantes)
