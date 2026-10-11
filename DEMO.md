# Demo: Tu Nuevo Hogar WhatsApp advisor

A WhatsApp assistant for a fictitious real-estate developer. People write to a WhatsApp number and a local Llama 3.1 model answers questions about the houses, prices, credits and the buying process. Setup instructions are in [README.md](README.md).

## Features

- **Answers from real data.** The model calls two tools: `consultar_desarrollo` (prices and details of each condominio) and `buscar_informacion` (search over the company's knowledge base).
- **Safety on both sides.** Prompt Guard and Llama Guard check each incoming message, and Llama Guard checks the reply before it is sent.
- **Fixed rules for simple cases.** Greetings, farewells and "hablar con un asesor" get an instant canned reply, without calling the model.
- **Hand-off to a person.** Asking for an advisor or a visit is stored as a contact request.
- **Honest when it does not know.** Questions the data does not cover get one fixed message instead of an invented answer.
- **Memory per phone number.** Each number has its own conversation, so follow-up questions work.
- **Metrics.** `GET /metricas` reports how many messages took each route, the error rate and the average response time.

## A sample conversation

These are real replies from the bot. The route is what the app logs for each message.

| The user writes | The bot answers | Route |
| --- | --- | --- |
| Hola | Hola, soy el asistente de Tu Nuevo Hogar. Puedo informarte sobre nuestras casas, precios, créditos y el proceso de compra. ¿En qué puedo ayudarte? | `regla_saludo` |
| ¿Alguno tiene alberca? | Sí, solo el condominio Tulipán tiene alberca. | `llama` |
| ¿Cuál es el horario de atención? | El horario de atención es de lunes a viernes de 10:00 a 19:00 y los sábados de 10:00 a 14:00. Los domingos y los días festivos oficiales estamos cerrados. | `llama` |
| ¿Aceptan mascotas? | Sí, los cuatro condominios permiten la presencia de mascotas, siempre y cuando se las cuiden en áreas comunes con correa. | `llama` |
| Quiero hablar con un asesor | Claro, en un momento un asesor te contacta directamente por este medio. | `regla_escalamiento` |
| *(a question the data does not cover)* | No cuento con esa información; sin embargo, puedes hablar con alguno de nuestros asesores para cualquier otra duda que tengas. | `sin_informacion` |
| *(a message asking how to hurt someone)* | Lo siento, no puedo ayudar con ese mensaje. Si buscas casa, escríbeme tu duda. | `bloqueado_llama_guard_entrada` |
| Gracias | Estamos a sus órdenes para cualquier duda futura. ¡Hasta pronto! | `regla_despedida` |

The model's wording changes from one run to the next; the fixed replies are always the same.

## How a message is handled

The whole pipeline is one function, `decidir_y_responder` in `src/backend_tu_nuevo_hogar/agente.py`. Shortened:

```python
def decidir_y_responder(self, numero, texto):
    # 1. Seguridad sobre la entrada
    if self.prompt_guard is not None and self.prompt_guard.es_inyeccion(texto):
        self.whatsapp.enviar(numero, MENSAJE_BLOQUEO)
        return "bloqueado_prompt_guard"
    seguro, categoria = self.llama_guard.revisar([{"role": "user", "content": texto}])
    if not seguro:
        self.whatsapp.enviar(numero, MENSAJE_BLOQUEO)
        return "bloqueado_llama_guard_entrada"

    # 2. Reglas fijas
    if any(frase in texto.lower() for frase in FRASES_ESCALAMIENTO):
        self.almacen.registrar_solicitud_contacto(numero, texto)
        self.whatsapp.enviar(numero, MENSAJE_ESCALAMIENTO)
        return "regla_escalamiento"

    # 3. Llama con herramientas
    respuesta = self.generar_respuesta(numero, texto)

    # 4. Seguridad sobre la salida
    seguro, categoria = self.llama_guard.revisar([
        {"role": "user", "content": texto},
        {"role": "assistant", "content": respuesta},
    ])
    if not seguro:
        self.whatsapp.enviar(numero, MENSAJE_RESPUESTA_BLOQUEADA)
        return "bloqueado_llama_guard_salida"

    self.whatsapp.enviar(numero, respuesta)
    return "llama"
```

## Try the catalog tool

The catalog tool is plain Python, so it runs without WhatsApp or the models:

```bash
uv run python -c '
from backend_tu_nuevo_hogar.catalogo import Catalogo, cargar_desarrollos
print(Catalogo(cargar_desarrollos()).consultar("Jacaranda"))'
```

It prints the text the model reads before answering:

```text
Condominio Jacaranda (últimas 12 casas, entrega marzo de 2027). Casas con balcón en una privada de 64 viviendas.
Precio desde $1,190,000 MXN. Casa: 2 recamaras, 1.5 banos, 72 m2 de construccion, 90 m2 de terreno,
estacionamiento para 1 auto. ...
```

Call `consultar()` with no name to get the comparison of the four condominios.

## Run the tests

The tests use fake models, so they need no downloads and finish in under a second:

```bash
uv run pytest
```
