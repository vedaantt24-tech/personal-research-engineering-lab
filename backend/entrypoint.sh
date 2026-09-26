#!/bin/sh
set -eu
if [ "${AUTO_CREATE_TABLES:-true}" = "false" ]; then
  alembic -c /app/alembic.ini upgrade head
fi
PORT="${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
