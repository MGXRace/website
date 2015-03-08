"""
Django settings for mgxrace project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from datetime import timedelta
from keys import cfg

import djcelery
djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg.get('secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

USE_TZ = True

ALLOWED_HOSTS = []
# ALLOWED_HOSTS = ['*']

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'


BROKER_URL = 'amqp://guest:guest@localhost//'

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'south',
    'racesowold',
    'racesow',
    'djcelery',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'racesow.middleware.ServerAuthenticationMiddleware',
    'racesow.middleware.TimezoneMiddleware',
)

ROOT_URLCONF = 'mgxrace.urls'

WSGI_APPLICATION = 'mgxrace.wsgi.application'

PASSWORD_HASHERS = (
    'racesow.hashers.SHA256Hasher',
)


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'racesow',
        'USER': 'rs_django',
        'PASSWORD': cfg.get('db_pass'),
        'HOST': 'localhost',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

DATE_FORMAT = 'Y-m-d H:i:s'  # 2015-02-25 03:16:57

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ['HOME'] + '/static/'
MAP_PK3_URL = 'http://pk3.mgxrace.net/racesow/'

# added for
TEMPLATE_CONTEXT_PROCESSORS = {
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "django.contrib.auth.context_processors.auth",
}

INTERNAL_IPS = ['127.0.0.1']

CELERYD_HIJACK_ROOT_LOGGER = False

# http://celery.readthedocs.org/en/latest/userguide/periodic-tasks.html#entries
CELERYBEAT_SCHEDULE = {
    'evaluate-maps-every-1-minute': {
        'task': 'racesow.tasks.recompute_updated_maps',
        'schedule': timedelta(minutes=1),
    },
}



LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': True,
        # },
    }
}