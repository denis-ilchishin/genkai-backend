from datetime import timedelta
from pathlib import Path

from core.env import Env
from django.db import models

env = Env()


# ================== BASE DJANGO SETTINGS ==================
DJANGO_ENVIRONMENT = env.allowed(
    'DJANGO_ENVIRONMENT', 'production', values=('local', 'production')
)

IS_LOCAL = DJANGO_ENVIRONMENT == 'local'

DJANGO_APPLICATION = env.allowed('DJANGO_APPLICATION', 'api', values=('api', 'admin'))

DEBUG = env.bool('DJANGO_DEBUG', False)

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = env.str('DJANGO_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': env.str('DB_HOST', 'db'),
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'PORT': env.str('DB_PORT', '5432'),
    }
}

# Set value as 60 seconds to prevent django reopen and close new connection on each request
# TODO: setup postgres loadbalancer
CONN_MAX_AGE = 60

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS') if not IS_LOCAL else ['*']

INSTALLED_APPS = [
    'nested_admin',
    'adminsortable2',
    'apps.core.apps.CoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'apps.api.apps.ApiConfig',
    'apps.users.apps.UsersConfig',
    'apps.content.apps.ContentConfig',
    'apps.titles.apps.TitlesConfig',
    'apps.translations.apps.TranslationsConfig',
    'apps.comments.apps.CommentsConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.push_notifications.apps.PushNotificationsConfig',
    'rest_framework',
    'corsheaders',
    'django_celery_beat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ipaddr.middleware.IPAddrMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Make possible to differentiate, separate and isolate "api" from "admin" application
# and make them running on different hosts, domains, subdomains etc. for extra security
ROOT_URLCONF = f'config.urls.{DJANGO_APPLICATION}'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Authorization

AUTH_USER_MODEL = 'users.User'

# Internationalization

LANGUAGE_CODE = 'ru'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = env.str('TIME_ZONE', 'Europe/Kiev')

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

# Media files

MEDIA_URL = '/uploads/'

MEDIA_ROOT = BASE_DIR / 'uploads'

AUTHENTICATION_BACKENDS = ('apps.authentication.backends.EmailBackend',)

# ================== LOGGING SETTINGS ==================

LOGGING_APPS = map(
    lambda app: app.split('.')[1],
    filter(lambda app: app.startswith('apps.'), INSTALLED_APPS),
)

LOGGING_DIR = BASE_DIR / 'logs'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'common': {
            'format': '{levelname} {asctime} {module} - {message}',
            'style': '{',
        },
        'update': {
            'format': '{levelname} {asctime} — {service} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR / 'log.log',
            'formatter': 'common',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR / 'error.log',
            'formatter': 'common',
        },
        'update': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR / 'update.log',
            'formatter': 'update',
        },
    },
    'loggers': {
        'apps': {'handlers': ['log', 'error'], 'level': 'INFO', 'propagate': True,},
        'apps.translations.services': {
            'handlers': ['update'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Register own logger for every app
for app in LOGGING_APPS:
    LOGGING['handlers'][app] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': LOGGING_DIR / f'{app}.log',
        'formatter': 'common',
    }
    LOGGING['loggers'][f'apps.{app}'] = {
        'handlers': [app],
        'level': 'INFO',
        'propagate': False,
    }


# ================== CACHE SETTINGS ==================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str('REDIS_URL', 'redis://redis:6379').rstrip('/') + '/0',
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "dj_cache",
    }
}


# ================== REST FRAMEWORK SETTINGS ==================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.rest.Pagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer',],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Token',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}


# ================== APPLICATION BASED SETTINGS ==================
class SERVICES(models.TextChoices):
    kodik = 'kodik'
    youtube = 'youtube'


FRONTEND_URL = env.str('FRONTEND_URL')

SEARCH_MIN_LENGTH = 3
SEARCH_MAX_LENGTH = 30

ALLOWED_IMAGES_MIMES = ('image/png', 'image/jpeg', 'image/webp', 'image/gif')
ARRAY_FIELD_DELIMITER = '\n'


PUSH_NOTIFICATIONS_PUBLIC_KEY = env.str('PUSH_NOTIFICATIONS_PUBLIC_KEY')
PUSH_NOTIFICATIONS_PRIVATE_KEY = env.str('PUSH_NOTIFICATIONS_PRIVATE_KEY')
PUSH_NOTIFICATIONS_BASE64_PUBLIC_KEY = env.str('PUSH_NOTIFICATIONS_BASE64_PUBLIC_KEY')


USERS_PASSWORD_MIN_LENGTH = 6
USERS_USERNAME_MAX_LENGTH = 30
USERS_USERNAME_MIN_LENGTH = 6
USERS_PROFILE_ABOUTMYSELF_MAX_LENGTH = 255

NOTIFICATIONS_MAX_NUMBER_SELECTED = 20

TITLES_SEARCH_MIN_LENGTH = 3
TITLES_SEARCH_MAX_LENGTH = 30
TITLES_RANK_EPISODES_DAYS_COUNT = 7
TITLES_HOME_PAGE_LIMIT = 20
TITLES_HOME_PAGE_CACHE_TIMEOUT = 60 * 30  # 30 min

COMMENTS_COMMENT_MAX_LENGTH = 255


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': USERS_PASSWORD_MIN_LENGTH,},
    },
]

# ================== THIRD PARTY CONFIG AND ACCESS SETTINGS ==================
KODIK_API_TOKEN = env.str('KODIK_API_TOKEN')
KODIK_API_URL = 'https://kodikapi.com/list'

RECAPTCHA_SECRET_KEY = env.str('RECAPTCHA_SECRET_KEY')
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = env.str('AWS_S3_CUSTOM_DOMAIN', None)
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    'ACL': 'public-read',
}

TELEGRAM_API_TOKEN = env.str(
    'TELEGRAM_API_TOKEN', '1005378038:AAFQF_P0Bg329T_nRKpBaovA0UxSOqIwcNI'
)


# ================== CELERY SETTINGS ==================
CELERY_BROKER_URL = env.str('REDIS_URL', 'redis://redis:6379').rstrip('/') + '/1'
CELERY_WORKER_HIJACK_ROOT_LOGGER = True


# ================== CORS SETTINGS ==================
if IS_LOCAL:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = (FRONTEND_URL,)

# Add possibility to override settings for local environment via "local_settings.py" file
if IS_LOCAL:
    try:
        from .local_settings import *
    except Exception:
        pass

