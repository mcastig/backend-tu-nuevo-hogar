# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A WhatsApp assistant for a fictitious real-estate developer ("Tu Nuevo Hogar"), ported from a course Colab notebook (a library assistant) to a production FastAPI service. The package is `backend_tu_nuevo_hogar`. Code identifiers, comments and all bot-facing text are in Spanish, following the notebook; keep that convention.

## Commands

Managed with `uv` (Python 3.12).

- Install: `uv sync` (app + tests) or `uv sync --group stack` (also the Llama Stack server)
- Tests: `uv run pytest`; single test: `uv run pytest tests/test_bot.py::test_saludo_usa_regla_fija`
- Run the webhook server: `uv run backend-tu-nuevo-hogar` (needs `.env`, see `.env.example`)
- Run Llama Stack with the Ollama model registered: `uv run backend-tu-nuevo-hogar-stack`
- Run everything in Docker: `docker compose up -d --build --wait`; add `--profile tunel` for the ngrok tunnel. On macOS set `COMPOSE_FILE=compose.yaml:compose.ollama-local.yaml` first, to use the host's Ollama (no GPU inside Docker there)

The server needs three processes: Ollama (`llama3.1:8b`, `llama-guard3`), Llama Stack on :8321, and the app on :8000. There is no linter or formatter configured.

The `Dockerfile` has two targets built on shared dependency layers: `app` and `stack` (which adds the `stack` group). `compose.yaml` hardcodes the in-network URLs and the database path over whatever `.env` says, and passes `MODELO_CHAT` to the stack container, so the `.env` gotcha below does not apply there. Only the app gets `.env` as `env_file`; the other services receive single variables through Compose interpolation (`NGROK_AUTHTOKEN` for the `tunel` service, `ngrok/ngrok`, whose inspector is published on :4040). `compose.ollama-local.yaml` switches the `ollama` and `ollama-pull` services off by giving them a profile, which works because `stack` depends on `ollama-pull` with `required: false`.

## Architecture

`app.py` builds the FastAPI app through `crear_app(config, agente)`. In production the lifespan calls `construir_agente`, which loads the embedding model and connects the clients; tests pass a prebuilt `Agente` with fakes, so they need no models or network.

`POST /webhook` only validates and dispatches: it checks the signature, normalizes Mexican numbers (`521…` to `52…`), marks the message id as processed, and hands the work to `BackgroundTasks`. The id is marked before the work runs, so a message whose processing fails is not retried when Meta redelivers it. The pipeline is synchronous and runs in the threadpool, which is why the per-number locks are `threading.Lock` and `Almacen` opens a new SQLite connection per operation.

`Agente` (`agente.py`) owns the message pipeline, and its order matters:

1. Prompt Guard, then Llama Guard on the incoming text (`seguridad.py`)
2. Fixed rules, in this order: escalation phrases (recorded as a contact request), bare greetings, bare farewells or thanks
3. `generar_respuesta`: Llama Stack Responses API with one round of function calling, then the clean-up of the reply described under Gotchas (text tool calls, refusals, internal names)
4. The greeting is prepended if the user opened with one; a `MENSAJE_SIN_RESPUESTA` reply is sent here, without step 5
5. Llama Guard on the reply before sending

`procesar_y_responder` wraps that pipeline, holds a per-phone-number lock, maps each exception to a named cause, and records one metric row per message. A Llama Guard failure is an error, never a pass. `decidir_y_responder` returns the route name stored in that metric row (`llama`, `sin_informacion`, `regla_saludo`, `regla_despedida`, `regla_escalamiento`, `bloqueado_prompt_guard`, `bloqueado_llama_guard_entrada`, `bloqueado_llama_guard_salida`, `error`); `GET /metricas` groups by it, so a new branch needs its own name.

The two tools the model can call are defined next to their implementation: `consultar_desarrollo` in `catalogo.py` (live data, exact lookup) and `buscar_informacion` in `conocimiento.py` (RAG). Their content is data, not code: `datos/catalogo.json` and `datos/conocimiento.json`. Both are derived by hand from `INFO.md` (the business fact sheet, in sync with the website); when a fact changes, update `INFO.md` first and then both JSON files, since prices, promotions and fees appear in each. The catalog has one entry per condominio (one house type each, no named models); `Catalogo.consultar` matches every condominio named in the query, through its `nombre` or `alias`, and with no name returns the comparison list. The model answers "sí" to a yes/no amenity question when the tool output simply does not mention the amenity, so the catalog states absences explicitly for the ones in `AMENIDADES_DESTACADAS` (at the end of a condominio's detail, and as "Con alberca: solo …" in the comparison list). Adding a tool means adding its schema to `HERRAMIENTAS` and its callable to `Agente.funciones`. Tools take the parsed arguments dict and return a string written for the model to read, including the not-found case.

Retrieval returns the top 3 fragments and adds a keyword bonus to cosine similarity because the embedding model scores short questions low: 0.20 when the question shares a keyword with the fragment, plus 0.10 per keyword found in the fragment's title (the text before the first `:`, at most two). Keywords are compared as 5-letter stems, minus the stopwords in `PALABRAS_GENERICAS`. Before encoding, `quitar_relleno` strips the padding the model adds when it rewrites the question ("los condominios de Tu Nuevo Hogar"), which otherwise pulls the embedding toward the fragments that name the company; keywords still come from the full question. Knowledge fragments work best short and single-topic, and the title carries weight, so write it with the words people use when they ask (`Fechas de entrega, cuándo se entregan las casas: …`). After editing them, check real similarity scores against the 0.30 threshold (`UMBRAL_CONOCIMIENTO`) by building a `BaseConocimiento` with `crear_codificador(...)` and calling `.similitudes(pregunta)`; the unit tests use a fake encoder and will not catch retrieval regressions.

Tests live in one file, `tests/test_bot.py`. The `entorno` fixture gives an `Agente` wired to fakes (`LlamaStackFalso`, `GuardFalso`, `WhatsAppFalso`) and a temp SQLite file; `cliente` wraps it in a `TestClient` with signature validation on, and `publicar` signs the body. `LlamaStackFalso` is scripted through `llamada_pendiente` (the tool call the first turn asks for) and `textos_pendientes` (literal replies, consumed in order; a `None` lets that turn behave normally), and records what is written to the conversation in `items_agregados`.

The unit tests say nothing about how `llama3.1:8b` behaves. To check a prompt, tool-output or retrieval change against the real model without sending WhatsApp messages, run a script inside the app container (`docker exec -e DATABASE_PATH=/tmp/prueba.sqlite3 tu-nuevo-hogar-app-1 python …`) that builds the agent with `construir_agente(Configuracion())`, replaces `agente.whatsapp` with an object whose `enviar` prints, and calls `decidir_y_responder` with a different phone number per question, so each gets a fresh conversation. The model varies from run to run: repeat each question several times and compare against the current behaviour before keeping a change.

State lives in SQLite through `Almacen` (`almacenamiento.py`): the phone-number-to-conversation mapping, processed message ids (webhook dedupe), metrics, errors, blocks and contact requests. The conversation history itself is stored by Llama Stack. A number's conversation is replaced by a new one after `HORAS_CONVERSACION` (default 3) without a message that reaches the model: Ollama runs the model with a 4,096-token context, and once the history exceeds it every model call reprocesses a full context (about 19 s each on the author's Mac, two calls per message). The old conversation stays in Llama Stack, unreferenced.

## Deployment

The bot runs on the author's Mac (host Ollama, Compose, ngrok tunnel); it is a school project with no hosting budget. Render with hosted models was built and reverted on 2026-10-10 because of cost (two 2 GB instances, about $51 a month, plus model usage); nothing of it is in the repo. What that attempt established, if it comes up again:

- Render has no GPU, its free tier has 512 MB and no disk, and it cannot choose a Dockerfile target: it builds the last stage and passes the service's environment variables as build arguments.
- Groq, Together and Cerebras retired Llama 3.1 8B and Llama Guard during 2026. OpenRouter still listed `meta-llama/llama-3.1-8b-instruct` and `meta-llama/llama-guard-4-12b` (no hosted Llama Guard 3). Replies from the hosted model were never tested.
- Llama Guard works through Llama Stack's chat completions (`ollama/llama-guard3`), which removes the app's direct Ollama client, and OpenRouter can be added in `stack.py` as a `remote::openai` provider with its base URL; both were verified locally.

## Gotchas

- The Llama Stack client is created with `max_retries=0` and a long timeout on purpose: an automatic retry duplicates the turn in the conversation.
- `llama-stack` 0.7 breaks with `mcp>=2`; the `stack` dependency group pins `mcp<2.0`.
- Webhook signature validation only runs when `WHATSAPP_APP_SECRET` is set.
- `llama3.1:8b` sometimes writes a tool call as plain text (`{"name": ..., "parameters": ...}`), often with a misspelled tool name. `generar_respuesta` runs the closest-named tool and sends its result back as a user message (there is no `call_id` to answer); a reply that is still a tool call is replaced by `MENSAJE_SIN_RESPUESTA`.
- The model also leaks its internals in prose ("según buscar_informacion…", "mi herramienta no encontró…") despite the prompt. `quitar_rastros_internos` drops every sentence matching `RASTROS_INTERNOS` before the reply is sent, so a word added to that pattern must never appear in a legitimate answer; check `datos/` first.
- The greeting returned when a message opens with one (`saludo_inicial`) is prepended in code, not by the model, and the prompt's brevity wording was picked by comparing variants against the real model: a stricter one made it stop listing the condominios and invent a price.
- Questions the bot cannot answer get the fixed `MENSAJE_SIN_RESPUESTA` and the route `sin_informacion`: when every tool result is `SIN_COBERTURA` (no second model call; the result and the fixed reply are written to the conversation with `conversations.items.create`), or when the model's own reply is a refusal (`SIN_DATOS`, plus `NEGATIVA_SIN_CONSULTAR` when no tool was called). Do not ask for the fixed text in the system prompt: with that sentence the model also answered it when the tool had returned the data.
- On macOS with the host's Ollama, replies of 15 s or more usually mean Ollama is evicting one model to load the other on every step (its log says "predicted to exceed available memory, evicting"): the two models need about 5 GB each and Docker Desktop reserves memory of its own.
- A container keeps the environment it was created with: `docker compose restart`, and the restart loop of a failing container, do not re-read `.env`. A stale container looks like a bad credential (`ERR_NGROK_107` in the tunnel, `401 Unauthorized` from graph.facebook.com in the app); compare `docker inspect` with `.env` before blaming the token, and recreate with `docker compose up -d <service>`. On macOS set `COMPOSE_FILE` first, or recreating also starts the Ollama containers.
- A `MODELO_CHAT` in `.env` that Ollama does not have stops the stack container in a restart loop ("Ollama no tiene el modelo"), and the app with it.
- Blocked messages and fixed-rule replies never reach Llama Stack, so they are absent from the conversation history the model sees on later turns.
- `stack.py` reads `OLLAMA_HOST`, `MODELO_CHAT` and `LLAMA_STACK_PORT` from the process environment only, not from `.env`, while the app reads `.env`; a `MODELO_CHAT` set only in `.env` leaves the stack registering the default model. It regenerates `data/llama_stack.yaml` from the starter distribution on every start, so edits to that file are lost.
- On Linux `torch` resolves to the CPU-only build from the PyTorch index (`[tool.uv.sources]`), which keeps CUDA out of the Docker image; the embedding model and Prompt Guard run on CPU there.
- `httpx`, `pydantic-settings`, `transformers` and `yaml` are imported directly but only arrive transitively (through `fastapi[standard]`, `sentence-transformers` and `llama-stack`).
- Heavy imports (`torch`, `sentence_transformers`, `llama_stack`) are deferred into functions so that importing `app.py` and running the tests stays fast; keep new ones lazy too.
