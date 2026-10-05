import logging

logger = logging.getLogger(__name__)


class LlamaGuard:
    """Revisa el contenido: se aplica al mensaje que entra y a la respuesta antes de enviarla."""

    def __init__(self, cliente_ollama, modelo):
        self.cliente = cliente_ollama
        self.modelo = modelo

    def revisar(self, mensajes):
        r = self.cliente.chat(model=self.modelo, messages=mensajes)
        veredicto = r["message"]["content"].strip().lower()
        if veredicto.startswith("safe"):
            return True, None
        if veredicto.startswith("unsafe"):
            partes = veredicto.split()
            return False, partes[1].upper() if len(partes) > 1 else "sin_categoria"
        raise ValueError(f"Veredicto inesperado de Llama Guard: {veredicto!r}")


class PromptGuard:
    """Revisa la manipulacion: detecta intentos de inyeccion de prompt en el mensaje que entra."""

    def __init__(self, nombre_modelo, token):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(nombre_modelo, token=token)
        self.modelo = AutoModelForSequenceClassification.from_pretrained(nombre_modelo, token=token)

    def es_inyeccion(self, texto):
        entradas = self.tokenizer(texto, return_tensors="pt", truncation=True, max_length=512)
        with self.torch.no_grad():
            logits = self.modelo(**entradas).logits
        etiqueta = self.modelo.config.id2label[logits.argmax().item()].upper()
        return etiqueta not in ("BENIGN", "LABEL_0")


def cargar_prompt_guard(nombre_modelo, token):
    # Si no esta disponible, el agente continua solo con Llama Guard
    if not token:
        logger.warning("HF_TOKEN no definido: el agente continuara solo con Llama Guard.")
        return None
    try:
        return PromptGuard(nombre_modelo, token)
    except Exception:
        logger.exception("Prompt Guard no disponible: el agente continuara solo con Llama Guard.")
        return None
