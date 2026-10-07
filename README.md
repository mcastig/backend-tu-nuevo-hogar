# Tu Nuevo Hogar WhatsApp advisor

A WhatsApp assistant for a **fictitious** real-estate developer ("Tu Nuevo Hogar"). It answers questions about the
housing developments, prices, credits and the buying process. It is the production version of the course notebook
*Proyecto Integrador: Agente Funcional en Producción*, with the library example swapped for real estate.

All company data (condominios, prices, policies, staff) is invented. `INFO.md` is the fact sheet for the business, and the bot's data in `src/backend_tu_nuevo_hogar/datos/` is written from it.

## How a message is handled

1. Meta calls `POST /webhook`. The signature is checked (when `WHATSAPP_APP_SECRET` is set), repeated message ids are dropped, and the work moves to a background task. Messages that are not text get a fixed "text only" reply.
2. **Input safety:** Prompt Guard (prompt injection) and Llama Guard (unsafe content).
3. **Fixed rules:** greetings get a canned reply; "hablar con un asesor" and similar phrases record a contact request.
4. **Llama 3.1 with tools:** `consultar_desarrollo` (catalog lookup) and `buscar_informacion` (RAG over the knowledge base).
5. **Output safety:** Llama Guard reviews the reply before it is sent.

Messages from the same phone number are handled one at a time. If a step fails, the user gets a generic "technical problem" reply and the failure is stored with a named cause (for example `llama_timeout` or `whatsapp_api_error`). A message id is marked as processed when it arrives, so a message that failed is not retried when Meta redelivers it.

Conversation ids, processed message ids, metrics, errors, blocks and contact requests are stored in SQLite (`data/bot.sqlite3`). The conversation history itself is kept by Llama Stack. The `data/` directory is created on first run and is git-ignored.

## Requirements

- [uv](https://docs.astral.sh/uv/) and Python 3.12
- [Ollama](https://ollama.com) with the two models: `ollama pull llama3.1:8b` and `ollama pull llama-guard3`
- A WhatsApp Cloud API app (access token, phone number id, app secret)
- Optional: a Hugging Face token with access to `meta-llama/Llama-Prompt-Guard-2-86M`

## First-time setup

```bash
cp .env.example .env                   # fill in the values (see Configuration)
uv sync --group stack                  # app + Llama Stack server
ollama pull llama3.1:8b
ollama pull llama-guard3
```

The first start of the bot also downloads the embedding model (`paraphrase-multilingual-MiniLM-L12-v2`) from Hugging Face, and Prompt Guard if `HF_TOKEN` is set.

## Run locally

Run everything from the project folder, each command in its own terminal, in this order:

1. **Ollama.** Skip this if Ollama already runs as a service ("address already in use").

   ```bash
   ollama serve
   ```

2. **Llama Stack**, on :8321 with the Ollama model registered. Wait until it is listening.

   ```bash
   uv run backend-tu-nuevo-hogar-stack
   ```

3. **The bot**, on :8000. It loads the embedding model before it starts answering; check it with `curl http://localhost:8000/health`.

   ```bash
   uv run backend-tu-nuevo-hogar
   ```

4. **A tunnel**, because Meta only calls public HTTPS URLs. Any tunnel works; for example:

   ```bash
   ngrok http 8000
   ```

5. **The Callback URL in Meta.** In the Meta app, under WhatsApp → Configuration, set the Callback URL to `https://<tunnel-url>/webhook` with `VERIFY_TOKEN` as the verify token, and subscribe to the `messages` field. The bot must already be running, because Meta calls it to verify. A free tunnel gets a new URL on every restart, so repeat this step each time.

6. **Send a WhatsApp message** to the test number. The bot's terminal logs `mensaje procesado ruta=...` for each message.

### If something fails

- **The Llama Stack launcher stops with "No se pudo conectar a Ollama" or "Ollama no tiene el modelo":** start Ollama, or pull the model it names.
- **Replies stop arriving and the bot logs `whatsapp_api_error`:** the access token has probably expired. The temporary token from Meta's API Setup page lasts about 24 hours; put a new one in `.env` and restart the bot.
- **Replies are slow:** the model runs on your machine, and each message makes several model calls (two safety checks, then one or two for the answer).
- **You want a clean start:** conversations and metrics are kept in `data/` between runs. Stop the bot and delete `data/bot.sqlite3`.

## Run with Docker

Docker Compose runs Llama Stack and the app (and, on a server, Ollama too) as containers, so you do not need uv or Python installed. The app is published on `127.0.0.1:8000` only; Ollama and Llama Stack have no authentication and stay on the internal network.

### Run locally with Docker

These steps use the Ollama installed on your machine and run Llama Stack and the app in containers. That is the right setup on macOS, where Docker cannot use the GPU. Run everything from the project folder.

1. **Requirements.** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and [Ollama](https://ollama.com), and start Docker Desktop.

2. **Configuration.** Create `.env` and fill in the values (see Configuration).

   ```bash
   cp .env.example .env
   ```

3. **Ollama**, with both models. Leave `ollama serve` running in its own terminal; skip it if Ollama already runs as a service ("address already in use"). The pulls are only needed once.

   ```bash
   ollama serve
   ollama pull llama3.1:8b
   ollama pull llama-guard3
   ```

4. **Select the Compose files** for this terminal, so the commands below need no `-f` flags.

   ```bash
   export COMPOSE_FILE=compose.yaml:compose.ollama-local.yaml
   ```

5. **Build and start** Llama Stack and the app. The first build takes a few minutes, and the first start downloads the embedding model (and Prompt Guard if `HF_TOKEN` is set). The command returns when both containers are healthy.

   ```bash
   docker compose up -d --build --wait
   ```

6. **Check it.** Both services should show `healthy`, and the health endpoint should answer.

   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```

7. **Open a tunnel**, because Meta only calls public HTTPS URLs. This adds an [ngrok](https://ngrok.com) tunnel as a container; it needs `NGROK_AUTHTOKEN` in `.env` (the authtoken from the ngrok dashboard, not an API key). The second command prints the public URL, which is also shown in ngrok's inspector at `http://localhost:4040`.

   ```bash
   docker compose --profile tunel up -d
   docker compose logs tunel | grep -o 'url=https://[^ ]*'
   ```

8. **Set the Callback URL in Meta** to `https://<tunnel-url>/webhook`, as in step 5 of *Run locally*. If the URL changes after a restart, repeat this step.

9. **Send a WhatsApp message** to the test number and follow the logs; the app logs `mensaje procesado ruta=...` for each message.

   ```bash
   docker compose logs -f app
   ```

10. **Stop it.** Add `-v` to also delete the data volumes (database, conversation history, downloaded models).

    ```bash
    docker compose --profile tunel down
    ```

After changing code or `.env`, run step 5 again. To run Ollama in a container as well (CPU only on macOS, and about 10 GB of model downloads), skip steps 3 and 4.

### Run on a Linux server

Everything runs in containers, Ollama included. The first start downloads both Ollama models (about 10 GB) into a volume:

```bash
docker compose up -d --build
docker compose -f compose.yaml -f compose.gpu.yaml up -d --build   # with NVIDIA GPUs (needs NVIDIA Container Toolkit)
```

For a permanent deployment, use an ngrok reserved domain, or replace the tunnel with a reverse proxy with TLS (Caddy, nginx) in front of port 8000, and use that URL as the Callback URL.

### How Compose configures the app

Compose passes `.env` to the app but sets `LLAMA_STACK_URL`, `OLLAMA_HOST`, `DATABASE_PATH`, `HOST` and `PORT` itself, so those values in `.env` are ignored; use `PUERTO_APP` to change the published port. `MODELO_CHAT` and `MODELO_GUARD` in `.env` are picked up by the model download, Llama Stack and the app alike.

State lives in four volumes: `datos` (the SQLite file), `llama-stack` (the conversation history), `ollama` (the models) and `huggingface` (the embedding model and Prompt Guard). The containers do not use the `data/` folder of a non-Docker run.

## Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `VERIFY_TOKEN` | yes | Token Meta sends when verifying the webhook |
| `WHATSAPP_ACCESS_TOKEN` | yes | Permanent (system user) token |
| `PHONE_NUMBER_ID` | yes | Sender phone number id |
| `WHATSAPP_APP_SECRET` | recommended | Enables webhook signature validation; without it any caller can post messages |
| `HF_TOKEN` | no | Loads Prompt Guard; without it only Llama Guard runs |
| `ADMIN_TOKEN` | no | Enables `GET /metricas` (`Authorization: Bearer <token>`) |
| `LLAMA_STACK_URL`, `OLLAMA_HOST`, `DATABASE_PATH`, `HOST`, `PORT` | no | Defaults: `http://localhost:8321`, `http://localhost:11434`, `data/bot.sqlite3`, `0.0.0.0`, `8000` |
| `MODELO_CHAT`, `MODELO_GUARD`, `MODELO_EMBEDDINGS` | no | Defaults: `ollama/llama3.1:8b`, `llama-guard3`, `paraphrase-multilingual-MiniLM-L12-v2` |
| `UMBRAL_CONOCIMIENTO` | no | Minimum similarity for a knowledge fragment to count as an answer. Default `0.30` |

The webhook server reads these from `.env`. The Llama Stack launcher (`backend-tu-nuevo-hogar-stack`) does not read `.env`: it takes `OLLAMA_HOST`, `MODELO_CHAT` and `LLAMA_STACK_PORT` (default `8321`) from the shell environment. If you change `OLLAMA_HOST` or `MODELO_CHAT` in `.env`, export the same value before starting the launcher, or the app will ask for a model the stack has not registered.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /webhook` | Meta's verification handshake |
| `POST /webhook` | Incoming messages |
| `GET /health` | Reports whether Prompt Guard is loaded |
| `GET /metricas` | Message count per route, error rate and causes, average response time, and contact requests. Needs `ADMIN_TOKEN` |

## Changing the company data

The bot's content is two JSON files in `src/backend_tu_nuevo_hogar/datos/`:

- `catalogo.json`: one entry per condominio (price, size, layout, what the house includes, amenities, availability, delivery date, reservation fee, maintenance fee, promotions). `alias` lists other spellings people use for the name.
- `conocimiento.json`: the knowledge base, a list of short text fragments about schedules, credits, estimated monthly payments, the buying process and so on.

Both files are written from `INFO.md`. When a fact changes, update `INFO.md` and then both files: prices, promotions and fees appear in each. Promotions carry their end date in the text; nothing removes them when they expire.

Keep each fragment short, about one topic, and starting with its title (`Enganche: ...`). The title counts extra in the search, so use the words people ask with. After editing fragments, check retrieval with the real embedding model: the tests use a fake encoder and will not notice a fragment that no longer matches its questions.

## Tests

```bash
uv run pytest                                  # all tests (no models or network needed)
uv run pytest tests/test_bot.py::test_saludo_usa_regla_fija
```
