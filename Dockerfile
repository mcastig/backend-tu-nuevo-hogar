# syntax=docker/dockerfile:1

# Dos imagenes a partir de las mismas capas: `app` (el webhook) y `stack` (Llama Stack, que agrega el grupo `stack`)
FROM python:3.12-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_NO_DEV=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    HOME=/home/app

# Los directorios que se montan como volumen se crean aqui para que hereden al usuario sin privilegios
RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app/data /home/app/.llama /home/app/.cache/huggingface \
    && chown -R app:app /app/data /home/app

WORKDIR /app


# Las dependencias van en su propia capa: solo se reinstalan cuando cambia uv.lock, no con cada cambio de codigo
FROM base AS dependencias-app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project


FROM dependencias-app AS dependencias-stack
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --group stack


FROM dependencias-stack AS stack
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --group stack
USER app
EXPOSE 8321
CMD ["backend-tu-nuevo-hogar-stack"]


FROM dependencias-app AS app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable
USER app
EXPOSE 8000
CMD ["backend-tu-nuevo-hogar"]
