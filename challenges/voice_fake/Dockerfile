FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ARG WHISPER_MODEL="base"
ENV MODEL=${WHISPER_MODEL}

RUN apt update
RUN apt install -y gcc ffmpeg
RUN mkdir /app
WORKDIR /app
COPY . /app

RUN uv sync --no-dev
RUN uv run python -c 'import os; from faster_whisper import download_model, WhisperModel; download_model(os.getenv("MODEL"))'
EXPOSE 8000
ENTRYPOINT uv run --no-sync uvicorn challenge:app --host 0.0.0.0 --port 8000
