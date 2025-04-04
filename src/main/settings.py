import os
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
    MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = opts.get("APP_ROOT", Path(__file__).resolve().parent.parent)
    APP_SLUG = opts.get("APP_SLUG", "HodlWatcher")
    SITE_ID = 1
    SECRET_KEY = opts.get("SECRET_KEY", "key")

    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LANGUAGE_CODE = "en"
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
        "django.contrib.humanize",
        "allauth",
        "allauth.account",
        "allauth.mfa",
        # apps
        "main",
        "alertas_bot",
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
        "crispy_forms",
        "crispy_bootstrap5",
        "django_recaptcha",
    ]

    HEALTH_CHECK_APPS = [
        "health_check",
        "health_check.db",
        "health_check.cache",
        "health_check.contrib.celery",
        "health_check.storage",
        "health_check.contrib.s3boto3_storage",
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
        "allauth.account.middleware.AccountMiddleware",
    ]

    # SecurityMiddleware options
    SECURE_BROWSER_XSS_FILTER = True

    TEMPLATES: list[dict[str, Any]] = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                os.path.join(BASE_DIR, "main/templates"),
                # insert additional TEMPLATE_DIRS here
            ],
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

    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

    CRISPY_TEMPLATE_PACK = "bootstrap5"

    # Bootstrap 3 alerts integration with Django messages
    MESSAGE_TAGS = {
        messages.ERROR: "danger",
        messages.DEBUG: "light",
    }

    # Sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"  # Usa el backend de caché por defecto

    # Constance
    CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
    CONSTANCE_DATABASE_CACHE_BACKEND = "default"
    CONSTANCE_CONFIG = {
        "THE_ANSWER": (42, "Answer to the Ultimate Question of Life, The Universe, and Everything"),
        "TELEGRAM_BOT_TOKEN": ("token", "Token del bot de Telegram"),
    }

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

    AUTHENTICATION_BACKENDS = [
        # Needed to login by username in Django admin, regardless of `allauth`
        "django.contrib.auth.backends.ModelBackend",
        # `allauth` specific authentication methods, such as login by email
        "allauth.account.auth_backends.AuthenticationBackend",
    ]

    # Métodos de autenticación (solo email)
    ACCOUNT_LOGIN_METHODS = {"email"}  # Usar solo email para el login

    # Campos requeridos en el registro
    ACCOUNT_SIGNUP_FIELDS = {"username*", "email*", "password1*", "password2*"}  # Email y password obligatorios

    ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True

    # Verificación de email
    ACCOUNT_EMAIL_SUBJECT_PREFIX = "[HodlWatcher] "  # Prefijo en los emails
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Requiere verificación antes de iniciar sesión
    ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1  # Días antes de que expire el enlace de confirmación

    # URLs de redirección
    ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "home"
    ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "account_login"
    ACCOUNT_EMAIL_CONFIRMATION_URL = "account_confirm_email"

    # Configuración del login
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Iniciar sesión automáticamente tras confirmar email
    ACCOUNT_LOGIN_ON_PASSWORD_RESET = True  # Iniciar sesión automáticamente tras resetear contraseña

    # Configuración del logout
    ACCOUNT_LOGOUT_ON_GET = True  # Cerrar sesión al acceder a la URL de logout

    # Unicidad del email
    ACCOUNT_UNIQUE_EMAIL = True  # No se permiten emails duplicados

    ACCOUNT_EMAIL_NOTIFICATIONS = True  # Enviar notificaciones por email

    ACCOUNT_USERNAME_BLACKLIST = ["admin", "root", "superuser"]  # No permitir estos usernames

    # URLs de redirección después del login/logout
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"

    MFA_ENABLED = True  # Habilitar la autenticación de dos factores

    # Habilitar tipos de MFA disponibles
    MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]  # Tipos de MFA disponibles

    # Configurar TOTP (Google Authenticator, Authy, etc.)
    MFA_TOTP_ISSUER = "HodlWatcher"  # Nombre que aparecerá en la app de autenticación
    MFA_TOTP_PERIOD = 30  # Código válido por 30 segundos
    MFA_TOTP_DIGITS = 6  # Código de 6 dígitos (estándar)
    MFA_TOTP_TOLERANCE = 1  # Permitir 1 paso en el pasado/futuro por desfase de reloj

    # Configurar códigos de recuperación
    MFA_RECOVERY_CODE_COUNT = 10  # Generar 10 códigos de recuperación
    MFA_RECOVERY_CODE_DIGITS = 8  # Cada código tiene 8 dígitos

    # Opcional: Configurar WebAuthn (Passkeys)
    MFA_PASSKEY_LOGIN_ENABLED = True  # Deshabilitado por defecto
    MFA_PASSKEY_SIGNUP_ENABLED = True  # Deshabilitado por defecto

    # Habilitar el login con MFA
    # LOGIN_URL = "mfa_login"  # Redirigir al login con MFA
    LOGIN_URL = "account_login"  # Redirigir al login normal
    # LOGIN_REDIRECT_URL = "home"  # Redirigir al home después de login

    MFA_FORMS = {
        "authenticate": "allauth.mfa.base.forms.AuthenticateForm",
        "reauthenticate": "allauth.mfa.base.forms.AuthenticateForm",
        "activate_totp": "allauth.mfa.totp.forms.ActivateTOTPForm",
        "deactivate_totp": "allauth.mfa.totp.forms.DeactivateTOTPForm",
        "generate_recovery_codes": "allauth.mfa.recovery_codes.forms.GenerateRecoveryCodesForm",
    }

    ACCOUNT_FORMS = {
        "add_email": "allauth.account.forms.AddEmailForm",
        "change_password": "allauth.account.forms.ChangePasswordForm",
        "confirm_login_code": "allauth.account.forms.ConfirmLoginCodeForm",
        "login": "allauth.account.forms.LoginForm",
        "request_login_code": "allauth.account.forms.RequestLoginCodeForm",
        "reset_password": "allauth.account.forms.ResetPasswordForm",
        "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
        "set_password": "allauth.account.forms.SetPasswordForm",
        "signup": "allauth.account.forms.SignupForm",
        "user_token": "allauth.account.forms.UserTokenForm",
    }

    SESSION_COOKIE_AGE = 60 * 60 * 24 * 1  # 1 días
    SESSION_COOKIE_SECURE = True

    # Invisible v3 reCAPTCHA
    RECAPTCHA_PUBLIC_KEY = opts.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = opts.get("RECAPTCHA_PRIVATE_KEY")

    # Celery settings
    CELERY_APP = "main"
    CELERY_BROKER_URL = opts.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = opts.get("CELERY_BROKER_URL", "redis://localhost:6379/1")

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": opts.get(
                "CELERY_BROKER_URL", "redis://localhost:6379/1"
            ),  # Especifica el número de base de datos
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            },
            "KEY_PREFIX": "hodlwatcher",  # Añade un prefijo opcional
        }
    }

    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_FILE_OVERWRITE = False

    # Email Yubin
    EMAIL_BACKEND = opts.get("EMAIL_BACKEND")
    MAILER_USE_BACKEND = opts.get("MAILER_USE_BACKEND")
    DEFAULT_FROM_EMAIL = opts.get("DEFAULT_FROM_EMAIL")

    # Configuración para envío de correos
    EMAIL_HOST = opts.get("EMAIL_HOST")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = opts.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = opts.get("EMAIL_HOST_PASSWORD")


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
