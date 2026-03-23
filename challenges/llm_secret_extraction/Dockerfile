FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ARG OLLAMA_HOST="http://ollama"
ARG OLLAMA_PORT="11434"
ARG OLLAMA_MODEL="gemma3:4b"
ARG PORT="8000"

ENV OLLAMA_HOST=${OLLAMA_HOST}
ENV OLLAMA_PORT=${OLLAMA_PORT}
ENV OLLAMA_MODEL=${OLLAMA_MODEL}
ENV PORT=${PORT}

WORKDIR /app
COPY pyproject.toml .
RUN uv sync
COPY app.py .
COPY flag.txt .
COPY index.html .

EXPOSE ${PORT}
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
