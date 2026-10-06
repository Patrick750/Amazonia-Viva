#!/usr/bin/env bash
set -o errexit
set -o nounset

pip install -r requirements.txt

# Pruebas aisladas antes de desplegar; nunca poblar cuentas de demostración.
: "${TEST_DATABASE_URL:?Configure una base PostgreSQL aislada para las pruebas de despliegue}"
if [ "${TEST_DATABASE_URL}" = "${DATABASE_URL:-}" ]; then
    echo 'La base de pruebas debe ser distinta de la base operativa.' >&2
    exit 1
fi
DATABASE_URL="${TEST_DATABASE_URL}" python manage.py test autenticacion --noinput
python manage.py makemigrations --check --dry-run
python manage.py check --deploy --tag security --fail-level WARNING
python manage.py collectstatic --no-input
python manage.py migrate --noinput
