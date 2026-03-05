#!/usr/bin/env sh
set -e

exec gunicorn brieffenster_generator.wsgi:app \
  --bind 0.0.0.0:10000 \
  --workers 4 \
  --threads 4 \
  --no-control-socket \
  "$@"
