import hashlib
import hmac

import httpx


class ErrorWhatsApp(Exception):
    pass


def normalizar_numero_mx(numero):
    if numero.startswith("521") and len(numero) == 13:
        return "52" + numero[3:]
    return numero


def firma_valida(app_secret, cuerpo, cabecera):
    # Meta firma cada webhook con el App Secret: X-Hub-Signature-256: sha256=<hmac del cuerpo>
    if not cabecera or not cabecera.startswith("sha256="):
        return False
    esperada = hmac.new(app_secret.encode(), cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, cabecera.removeprefix("sha256="))


class ClienteWhatsApp:
    def __init__(self, token, phone_id, version):
        self.url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
        self.headers = {"Authorization": f"Bearer {token}"}

    def enviar(self, numero, texto):
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": texto},
        }
        try:
            r = httpx.post(self.url, headers=self.headers, json=payload, timeout=15)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ErrorWhatsApp(str(e)) from e
