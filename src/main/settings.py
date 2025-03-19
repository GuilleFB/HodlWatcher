from pathlib import Path
from typing import Any

from configurations import Configuration
from django.contrib.messages import constants as messages
from kaio import Options, mixins


opts = Options()


class Base(
    mixins.CachesMixin,
    mixins.DatabasesMixin,
    mixins.CompressMixin,
    mixins.PathsMixin,
    mixins.LogsMixin,
    mixins.SentryMixin,
    mixins.EmailMixin,
    mixins.SecurityMixin,
    mixins.DebugMixin,
    mixins.WhiteNoiseMixin,
    mixins.StorageMixin,
    mixins.CeleryMixin,
    Configuration,
):
    """
    Project settings for development and production.
    """

    DEBUG = opts.get("DEBUG", True)

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = opts.get("APP_ROOT", Path(__file__).resolve().parent.parent)
    APP_SLUG = opts.get("APP_SLUG", "HodlWatcher")
    SITE_ID = 1
    SECRET_KEY = opts.get("SECRET_KEY", "key")

    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LANGUAGE_CODE = "es"
    TIME_ZONE = "Europe/Madrid"

    ROOT_URLCONF = "main.urls"
    WSGI_APPLICATION = "main.wsgi.application"

    INSTALLED_APPS = [
        # django
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # apps
        "main",
        # 3rd parties
        "compressor",
        "constance",
        "constance.backends.database",
        "django_extensions",
        "django_yubin",
        "kaio",
        "logentry_admin",
        "robots",
        "storages",
        "django_celery_beat",
        "django_celery_results",
        "django_prometheus",
    ]

    HEALTH_CHECK_APPS = [
        "health_check",
        "health_check.db",
        "health_check.cache",
        # "health_check.contrib.celery",
        # "health_check.storage",
        # "health_check.contrib.s3boto3_storage",
    ]

    INSTALLED_APPS += HEALTH_CHECK_APPS

    MIDDLEWARE = [
        "django_prometheus.middleware.PrometheusBeforeMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "django_prometheus.middleware.PrometheusAfterMiddleware",
    ]

    # SecurityMiddleware options
    SECURE_BROWSER_XSS_FILTER = True

    TEMPLATES: list[dict[str, Any]] = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.tz",
                    "django.template.context_processors.request",
                    "constance.context_processors.config",
                ],
            },
        },
    ]

    # Bootstrap 3 alerts integration with Django messages
    MESSAGE_TAGS = {
        messages.ERROR: "danger",
        messages.DEBUG: "light",
    }

    # Sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

    # Constance
    CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
    CONSTANCE_DATABASE_CACHE_BACKEND = "default"
    CONSTANCE_CONFIG = {"THE_ANSWER": (42, "Answer to the Ultimate Question of Life, The Universe, and Everything")}

    # Robots
    ROBOTS_SITEMAP_URLS = [opts.get("SITEMAP_URL", "")]

    # database and pgBouncer
    # https://docs.djangoproject.com/en/4.2/ref/databases/#transaction-pooling-server-side-cursors
    DISABLE_SERVER_SIDE_CURSORS = True
    # https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    # Prometheus
    PROMETHEUS_EXPORT_MIGRATIONS = False

    # Celery
    # The default must be the same as in run-celery case in entrypoint.sh
    BROKER_TRANSPORT_OPTIONS = {"global_keyprefix": "HodlWatcher"}
    RESULT_BACKEND_TRANSPORT_OPTIONS = {"global_keyprefix": "HodlWatcher"}

    # https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]


class Test(Base):
    """
    Project settings for testing.
    """

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    MEDIA_ROOT = opts.get("TEST_MEDIA_ROOT", "/tmp/HodlWatcher-media_test")  # nosec hardcoded_tmp_directory

    CACHE_PREFIX = "HodlWatcher-test"

    SESSION_ENGINE = "django.contrib.sessions.backends.db"

    def DATABASES(self):
        return self.get_databases(prefix="TEST_")
