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

import djcelery
djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qaddpa2wq=vdb(a61uy(3@wvwfgld2p&*7o&#ukuj2e+@5b9r*'

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

# http://www.marinamele.com/2014/02/how-to-install-celery-on-django-and.html
# http://www.caktusgroup.com/blog/2014/06/23/scheduling-tasks-celery/
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
    'debug_toolbar',
    'djcelery',
)
DEBUG_TOOLBAR_PATCH_SETTINGS = False

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'racesow.middleware.ServerAuthenticationMiddleware'
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
        'NAME': 'racesow_celery',
        'USER': 'rs_django',
        'PASSWORD': '0L7l2PUWtQDCmqNEZw02',
        'HOST': 'localhost',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ['HOME'] + '/static/'

# added for
TEMPLATE_CONTEXT_PROCESSORS = {
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
}

INTERNAL_IPS = ['127.0.0.1']
# INTERNAL_IPS = ['127.0.0.1', '217.122.146.83']  # debug toolbar

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