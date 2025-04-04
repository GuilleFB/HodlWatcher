.PHONY: all
all: proyect

UID_GID_BUILD_ARGS := --build-arg UID=`id -u` --build-arg GID=`id -g`

.PHONY: proyect
proyect:
	docker compose build ${UID_GID_BUILD_ARGS} proyect
	docker compose run --service-ports --rm proyect; docker compose down

.PHONY: devel
devel:
	docker compose build ${UID_GID_BUILD_ARGS} devel
	docker compose run --service-ports --rm devel; docker compose down

.PHONY: debug
debug:
	docker compose build ${UID_GID_BUILD_ARGS} debug
	docker compose run --service-ports --rm debug; docker compose down

.PHONY: debug-pytest
debug-pytest:
	docker compose build ${UID_GID_BUILD_ARGS} debug
	docker compose run --service-ports --rm --no-deps debug run-debug-pytest $(c); docker compose down

.PHONY: services_up
services_up:
	docker compose up -d postgres redis minio

.PHONY: services_down
services_down:
	docker compose down

.PHONY: create_bucket
create_bucket:
	docker compose run --rm create_bucket

.PHONY: celery
celery:
	docker compose build ${UID_GID_BUILD_ARGS} celery celery-beat flower
	docker compose up -d celery celery-beat flower

.PHONY: logs
logs:
	docker compose logs -f

.PHONY: command
command:
	docker compose build ${UID_GID_BUILD_ARGS} devel
	docker compose run --rm devel wait-for-it ${c}

CONTAINER_NAME := deps_
.PHONY: deps
deps:
	docker compose build deps
	-docker compose run --name $(CONTAINER_NAME) deps bash -c "${c}"
	-docker cp $(CONTAINER_NAME):/deps/Pipfile .
	-docker cp $(CONTAINER_NAME):/deps/Pipfile.lock .
	docker stop $(CONTAINER_NAME)
	docker rm -v $(CONTAINER_NAME)
	chown `id -u`:`id -g` Pipfile Pipfile.lock

.PHONY: bash
bash:
	docker exec -it `docker ps -qf "name=^hodlwatcher-(proyect|devel|debug)-run-"` bash

.PHONY: trivy
trivy:
	docker compose run --rm trivy
