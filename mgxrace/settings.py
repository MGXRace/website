"""Django settings for mgxrace project"""
import os
import sys
from datetime import timedelta

import djcelery
djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


##########
# Celery
##########


BROKER_URL = os.environ.get('MGXRACE_BROKER', 'amqp://guest:guest@localhost//')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

CELERYD_HIJACK_ROOT_LOGGER = False

CELERYBEAT_SCHEDULE = {
    'evaluate-maps-every-1-minute': {
        'task': 'racesow.tasks.recompute_updated_maps',
        'schedule': timedelta(minutes=1),
    },
}


##########
# Rest Framework
##########


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.OrderingFilter',),
    'ORDERING_PARAM': 'sort',
    'PAGE_SIZE': 50,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
}


##########
# Django
##########


SECRET_KEY = os.environ.get('MGXRACE_SECRET', 'insecuresecret')
DEBUG = os.environ.get('MGXRACE_PRODUCTION', True)
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = os.environ.get('MGXRACE_HOSTS', '').split()
INTERNAL_IPS = ['127.0.0.1']


USE_TZ = True
TIME_ZONE = 'UTC'


LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
DATE_FORMAT = 'Y-m-d H:i:s'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MAP_PK3_URL = 'http://pk3.mgxrace.net/racesow/'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'simple_history',
    'rest_framework',
    'rest_framework.authtoken',
    'racesowold',
    'racesow',
    'djcelery',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'racesow.middleware.ServerAuthenticationMiddleware',
    'racesow.middleware.TimezoneMiddleware',
)


ROOT_URLCONF = 'mgxrace.urls'
WSGI_APPLICATION = 'mgxrace.wsgi.application'


DATABASES = {
    'default': None,
}


if DEBUG:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'racesow',
        'USER': 'rs_django',
        'PASSWORD': os.environ['MGXRACE_DBPASS'],
        'HOST': 'localhost',
    }


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.debug',
                'django.core.context_processors.request',
                'django.core.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    },
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s %(process)d'
                       '%(thread)d %(message)s')
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'mgxrace.log'),
            'interval': 1,
            'when': 'midnight',
            'backupCount': 180,
            'utc': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
