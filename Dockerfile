# https://hub.docker.com/_/python/
FROM python:3.11-bullseye

ARG APP_ENV=prod

WORKDIR /srv

RUN mkdir -p /data/static && mkdir -p /data/media && chmod -R 777 /data
COPY docker/locale.gen /etc/locale.gen
COPY bin ./bin
COPY system-requirements.txt ./system-requirements.txt
COPY system-dev-requirements.txt ./system-dev-requirements.txt

RUN <<EOF
    apt-get -qq update
    xargs apt-get -qq install -y gosu gettext < system-requirements.txt
    if [ ${APP_ENV} = "devel" ]; then
        xargs apt-get -qq install -y < system-dev-requirements.txt
    fi
    rm -rf /var/lib/apt/lists/*
EOF

# pipenv
RUN pip install pipenv=="2024.4.1"
COPY Pipfile* ./
RUN [ -f Pipfile.lock ] && pipenv install "$(test $APP_ENV = devel && echo "--dev")" --system --deploy
# end pipenv

#ENV ENABLE_BASIC_AUTH=True \
#    ALWAYS_RUN_MIGRATIONS=True \
#    UWSGI_PROCESSES=1 \
#    UWSGI_THREADS=32 \
#    CELERY_INSPECT_TIMEOUT=5

WORKDIR /app
COPY src/ .

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/app.docker.ini /app/app.ini
COPY docker/app.docker.ini /srv/app.ini
COPY --chmod=777 docker/uwsgi.ini /etc/uwsgi/uwsgi.ini

ARG UID=1001
ARG GID=1001
ENV runUID=${UID}
ENV runGID=${GID}
RUN groupadd -r -g ${runGID} HodlWatcher && \
    useradd -r -u ${runUID} -g ${runGID} -d /app --no-log-init HodlWatcher && \
    chown ${runUID}.${runGID} /app -R

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run-uwsgi"]
EXPOSE 8080 1717

HEALTHCHECK --interval=30s --timeout=3s CMD ["launch-probe"]

RUN echo "Compiling messages..." && \
    CACHE_TYPE=dummy SECRET_KEY=HodlWatcher gosu ${runUID} python manage.py compilemessages && \
    echo "Compressing..." && \
    CACHE_TYPE=dummy SECRET_KEY=HodlWatcher gosu ${runUID} python manage.py compress --traceback --force && \
    echo "Collecting statics..." && \
    CACHE_TYPE=dummy SECRET_KEY=HodlWatcher gosu ${runUID} python manage.py collectstatic --noinput --traceback -v 0

# VOLUME /data/static
