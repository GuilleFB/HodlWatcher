# HodlWatcher

You can install and run this project in local or in Docker. If you are going to develop in this project frequently,
you probably want to install it in local. If you are not a developer, you are only going to have a look or do a quick
development, you probably want to install it in Docker.

Anyway, take into account that the project will be deployed in staging and live environments using Docker.


## Common dependencies

* [Git](https://git-scm.com/downloads).
* [Editorconfig](http://editorconfig.org/#download) to keep consistent file indentations.
* It is strongly recommended to configure your IDE to check [Flake8](https://flake8.pycqa.org) errors. Tests will fail
  if the code is not Flake8 compliant.
  * [VS Code linting](https://code.visualstudio.com/docs/python/linting).
  * PyCharm already has [code inspections](https://www.jetbrains.com/help/pycharm/code-inspection.html) that
  are very similar to Flake8, so you should not have problems. If you need/want to use Flake8, you can configure it as
  an [external tool](https://www.jetbrains.com/help/pycharm/configuring-third-party-tools.html).


## Git branches and flow

At the beginning `main` is used for development and `staging` for the
staging environment.

When the production environment becomes available, `main`  will then be used for production
and the `develop` branch will be created for development.


## Installation and set-up

1. Clone the project
    ```sh
    cd /home/gfollana/workspace/  # or wherever your workspace directory is
    git clone https://gitlab.apsl.net/HodlWatcher/HodlWatcher
    cd HodlWatcher
    ```

2. Follow the steps for the local or Docker installation:
    * [Local installation](./docs/local.md)
    * [Docker installation](./docs/docker.md)


## Special cases

If you need to customize your Dockerfile, you can change the base image by commenting/uncommenting:

```Dockerfile
FROM registry.apsl.net/library/django-cookiecutter-base:2024.07.26
#FROM python:3.11-bullseye
```
