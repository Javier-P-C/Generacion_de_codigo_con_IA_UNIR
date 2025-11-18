#!/bin/bash
set -e

POSTGRES_HOST=${POSTGRES_HOST:-db}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

echo "[entrypoint] Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT ..."
for i in {1..30}; do
  if nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; then
    echo "[entrypoint] PostgreSQL is available."; break
  fi
  echo "[entrypoint] Database not ready yet (attempt $i)..."
  sleep 1
done

echo "[entrypoint] Applying migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Ensuring default superuser exists..."
python manage.py create_default_superuser || true

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "[entrypoint] Starting Django server..."
exec "$@"

