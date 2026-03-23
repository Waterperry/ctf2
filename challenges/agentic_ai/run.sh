#!/bin/bash

set -euox pipefail;
cd /app/server;
uv run uvicorn internal_forum:app --host 0.0.0.0 &
cd /app/agent;
uv run harness.py;
