# https://hub.docker.com/_/python/
FROM python:3.11-bullseye

WORKDIR /srv

RUN mkdir -p /data/static && mkdir -p /data/media && chmod -R 777 /data
COPY docker/locale.gen /etc/locale.gen
COPY bin ./bin
COPY system-requirements.txt ./system-requirements.txt

RUN apt-get -qq update && \
    xargs apt-get -qq install -y gosu gettext < system-requirements.txt && \
    rm -rf /var/lib/apt/lists/* && \
    locale-gen

# pipenv
RUN pip install pipenv=="2024.4.1"
COPY Pipfile* ./
RUN pipenv install --system --deploy

WORKDIR /app
COPY src/ .

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/app.docker.ini /app/app.ini
COPY docker/uwsgi.ini /etc/uwsgi/uwsgi.ini

ARG UID=1001
ARG GID=1001
ENV runUID=${UID}
ENV runGID=${GID}
RUN groupadd -r -g ${runGID} HodlWatcher && \
    useradd -r -u ${runUID} -g ${runGID} -d /app --no-log-init HodlWatcher && \
    chown ${runUID}.${runGID} /app -R

ENV PORT=8080 \
    UWSGI_PROCESSES=2 \
    UWSGI_THREADS=4 \
    CELERY_INSPECT_TIMEOUT=5

RUN echo "Compiling messages..." && \
    CACHE_TYPE=dummy SECRET_KEY=HodlWatcher gosu ${runUID} python manage.py compilemessages && \
    echo "Collecting statics..." && \
    CACHE_TYPE=dummy SECRET_KEY=HodlWatcher gosu ${runUID} python manage.py collectstatic --noinput --traceback -v 0

ENTRYPOINT ["/entrypoint.sh"]
CMD ["launch-migrations-and-serve"]
