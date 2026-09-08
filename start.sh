#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput
daphne -b 0.0.0.0 -p "${PORT:-8000}" config.asgi:application
