#!/bin/bash

set -e

case $1 in
    launch-migrations-and-serve)
        echo "→ Executing migrate"
        gosu ${runUID} python manage.py migrate --noinput
        echo "✓ Migrations applied"
        echo "→ Starting uwsgi server"
        exec gosu ${runUID} uwsgi --ini=/etc/uwsgi/uwsgi.ini
        ;;

    run-uwsgi)
        exec gosu ${runUID} uwsgi --ini=/etc/uwsgi/uwsgi.ini
        ;;

    run-migrations)
        /entrypoint.sh launch-migrations
        exec gosu ${runUID} sleep infinity
        ;;

    run-uwsgitop)
        exec gosu ${runUID} uwsgitop localhost:9090
        ;;

    run-devel)
        if [ ! -e /app/app.ini ]; then
            cp /srv/app.ini /app/app.ini
        fi
        chmod 666 /app/app.ini
        echo "→ Running as runserver mode"
        exec gosu ${runUID} python manage.py runserver 0.0.0.0:8000
        ;;

    run-debug)
        if [ ! -e /app/app.ini ]; then
            cp /srv/app.ini /app/app.ini
        fi
        chmod 666 /app/app.ini
        echo "→ Running as runserver mode with remote debug"
        exec gosu ${runUID} python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 ./manage.py runserver 0.0.0.0:8000
        ;;

    run-debug-pytest)
        if [ ! -e /app/app.ini ]; then
            cp /srv/app.ini /app/app.ini
        fi
        chmod 666 /app/app.ini
        shift
        echo "→ Running pytest with remote debug. Waiting for client for running tests..."
        exec gosu ${runUID} python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m pytest "$@"
        ;;

    run-celery)
        echo "→ Executing celery"
        DJANGO_CELERY_QUEUES="${DJANGO_CELERY_QUEUES:-HodlWatcher}"
        CELERY_LOG_LEVEL="${CELERY_LOG_LEVEL:-${LOG_LEVEL:-INFO}}"
        exec gosu ${runUID} celery -A main.celery worker -l ${CELERY_LOG_LEVEL} -Q ${DJANGO_CELERY_QUEUES} -E --pidfile="/tmp/celery.pid"
        ;;

    run-flower)
        echo "→ Executing flower"
        exec gosu ${runUID} celery -A main.celery flower --address=0.0.0.0
        ;;

    run-celery-beat)
        echo "→ Executing celery beat"
        exec gosu ${runUID} celery -A main.celery beat -l info --pidfile="/tmp/celerybeat.pid"
        ;;

    run-tests)
        cd /srv
        pipenv install --system --dev
        cd /app
        echo "→ Executing tests"
        exec gosu ${runUID} pytest --create-db --migrations && bandit -c pyproject.toml -r .
        echo "✓ Tests done"
        ;;

    launch-migrations)
        echo "→ Executing migrate"
        exec gosu ${runUID} python manage.py migrate --noinput
        echo "✓ Migrations applied"
        ;;

    launch-liveness-probe)
        exec curl -f localhost:8080/health/ || exit 1
        ;;

    launch-readiness-probe)
        exec gosu ${runUID} python manage.py showmigrations | grep -c "\[ \]" -m 1 | grep -q 0 \
        && if [  "${CHECK_EMAIL,,}" = "true" ]; then
            gosu ${runUID} test `python manage.py status_mail | grep -vE '^[0-9]+/[0-9]+/[0-9]{0,2}$' | wc -l` = 1;
        fi \
        || exit 1
        ;;

    launch-celery-liveness-probe)
        exec gosu ${runUID}  celery inspect -t ${CELERY_INSPECT_TIMEOUT} ping -A main.celery -d celery@${HOSTNAME} | grep "celery@${HOSTNAME}: OK" | grep -v grep || exit 1
        ;;

    launch-celery-beat-liveness-probe)
        exec gosu ${runUID}  test `ps aux | grep beat | grep -v grep | wc -l` -gt 0 || exit 1
        ;;

    launch-flower-probe)
        exec curl -f localhost:5555 || exit 1
        ;;

    wait-for-it)
        echo "→ Waiting for Postgres"
        until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -q; do
            echo "→ Postgres is unavailable, sleeping"
            sleep 1
        done
        echo "→ Postgres ready"
        shift
        exec gosu ${runUID} "$@"
        ;;

    *)
        exec gosu ${runUID} "$@"
        ;;
esac
