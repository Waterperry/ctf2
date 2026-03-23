FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim


ARG INTERNAL_FORUM_HOST="http://localhost"
ARG INTERNAL_FORUM_PORT="8000"

ARG OLLAMA_HOST="http://ollama"
ARG OLLAMA_PORT="11434"
ARG OLLAMA_USE_GPU="0"
ARG OLLAMA_MODEL="gemma4:e4b"
ARG SLEEP_DURATION="60"  # how many seconds the script generator will sleep between attempted rewrites

ENV INTERNAL_FORUM_HOST=${INTERNAL_FORUM_HOST}
ENV INTERNAL_FORUM_PORT=${INTERNAL_FORUM_PORT}
ENV OLLAMA_HOST=${OLLAMA_HOST}
ENV OLLAMA_PORT=${OLLAMA_PORT}
ENV OLLAMA_MODEL=${OLLAMA_MODEL}
ENV SLEEP_DURATION=${SLEEP_DURATION}

COPY . /app/agent
WORKDIR /app/agent
RUN uv sync

WORKDIR /app/server
COPY ./internal_forum.py /app/server
COPY ./pyproject.toml /app/server
RUN uv sync

EXPOSE ${INTERNAL_FORUM_PORT}
RUN chmod +x /app/agent/run.sh
ENTRYPOINT /app/agent/run.sh
