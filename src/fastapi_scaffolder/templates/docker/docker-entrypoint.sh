#!/bin/sh
set -e

# When the app is configured to use Alembic migrations (Postgres/MySQL),
# apply them before starting the server. This runs on every container
# start, which is safe — `alembic upgrade head` is a no-op if the
# schema is already current.
if [ "$USE_MIGRATIONS" = "True" ] || [ "$USE_MIGRATIONS" = "true" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
