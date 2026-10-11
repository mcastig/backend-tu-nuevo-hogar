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

## Technical decisions

### State

State is split in two, by who needs it:

- **The conversation history lives in Llama Stack.** Each phone number gets a conversation there (`conversations.create()`), and every model call passes its id, so the model sees the earlier turns without the app resending them.
- **Everything else lives in one SQLite file**, behind the `Almacen` class (`almacenamiento.py`):

| Table | What it holds |
| --- | --- |
| `conversaciones` | Which Llama Stack conversation belongs to each phone number |
| `mensajes_procesados` | Ids of the WhatsApp messages already handled, so a redelivery from Meta is ignored |
| `agendas` | The step a number is at in the visit-scheduling flow (lapses after 30 minutes) |
| `citas` | Booked visits, unique per day and hour |
| `solicitudes_contacto` | Requests to talk to an advisor |
| `metricas`, `errores`, `bloqueos` | One row per message with its route and duration, plus the failures and the blocked messages |

Three choices follow from how the service runs:

- **SQLite instead of a database server.** The bot is a single process on one machine; a file needs no extra service and survives restarts.
- **A lock per phone number.** The webhook answers Meta at once and the work runs in a background thread, so two quick messages from the same person could otherwise run at the same time and mix their turns. Messages from different numbers still run in parallel.
- **A conversation is replaced after 3 hours of silence.** Ollama runs the model with a 4,096-token context; once the history outgrows it, every call reprocesses a full context and replies become slow.

Blocked messages and fixed-rule replies never reach Llama Stack, so the model does not see them on later turns.

### Function calling

Yes. The model answers through the Llama Stack Responses API with two tools, and one round of calls per message:

| Tool | Source | Used for |
| --- | --- | --- |
| `consultar_desarrollo` | `datos/catalogo.json`, exact lookup by condominio name | Prices, sizes, amenities, availability |
| `buscar_informacion` | `datos/conocimiento.json`, embedding search (RAG) with a keyword bonus | Credits, process, policies, opening hours |

The split is deliberate: figures that must be exact come from a lookup, never from similarity search, and the system prompt holds no prices or dates, so every figure in a reply has to come from a tool result.

`llama3.1:8b` does not always call tools cleanly, so the code corrects it instead of trusting it:

- A tool call written as plain text (`{"name": ..., "parameters": ...}`), often with a misspelled name, is detected and the closest-named tool is run.
- When every tool result says the data does not cover the question, the app sends the fixed "no cuento con esa información" message and skips the second model call, so there is nothing to invent.
- Sentences that mention the tools by name are removed from the reply before it is sent.

Not everything goes through the model. Greetings, farewells, the request for an advisor and the whole visit-scheduling flow are fixed rules in code: they are predictable, instant, and a booking must not depend on the model reading a date correctly.

### Security layers

In the order a message meets them:

1. **Webhook signature.** `POST /webhook` checks Meta's `X-Hub-Signature-256` header (HMAC-SHA256 of the body with the app secret) and rejects anything else with 403. It runs when `WHATSAPP_APP_SECRET` is set.
2. **Prompt Guard** (`Llama-Prompt-Guard-2-86M`) classifies the incoming text and blocks prompt-injection attempts. It needs a Hugging Face token; without one the bot starts with Llama Guard only, and `GET /health` reports it.
3. **Llama Guard 3 on the input** blocks harmful content before the model sees it.
4. **Llama Guard 3 on the output** checks the reply, together with the question, before it is sent.
5. **Admin token.** `GET /metricas` and `GET /citas` require a bearer token and return 404 when none is configured. FastAPI's docs pages are switched off.

Details that matter:

- **Fail closed.** If Llama Guard fails or returns something other than `safe` or `unsafe`, the message is treated as an error, never as safe.
- **A blocked message gets a fixed reply** and is recorded in `bloqueos` with the layer and the category, but never reaches the model or its history.
- **Tokens are compared in constant time** (`hmac.compare_digest`).
- **One exception:** while a number is in the middle of scheduling a visit, its replies skip both guards. They are only matched against the offered days and hours, and Llama Guard blocks a bare number such as "13".

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
