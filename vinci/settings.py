"""
Django settings for vinci project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

root_path = lambda *paths: os.path.join(BASE_DIR, *paths)  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vinci'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taggit',
    'django_extensions',
    'vinci',
    'rest_framework',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'vinci.urls'

WSGI_APPLICATION = 'vinci.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

from django.conf import global_settings

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'OPTIONS': {
        'debug': False,
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'vinci.processors.site_title',
            'vinci.processors.api_key',
        ],
    },
}]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Vinci settings
VINCI_SITE_TITLE = 'Vinci'
VINCI_SITE_TITLE_SEP = ' | '
VINCI_DEFAULT_SEARCH_ORDER = '-date'
VINCI_RESULTS_PER_PAGE = 10
VINCI_PLUGINS = [
    'youtube',
    'hashtags',
    'image',
    'pagelink',
    'md',
    'sp',
]
VINCI_ENABLE_NON_REST_APIS = False
VINCI_SEARCH_INDEX_DIR = os.path.join(BASE_DIR, 'search.idx')
VINCI_GENERATE_ENTRY_DOCUMENT_FUNCTION = None
VINCI_SEARCH_SCHEMA = None

VINCI_DEFAULT_API_KEY_USERNAME = None
VINCI_API_KEY = None

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': root_path('debug.log'),
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# Modes
# These are filenames that get loaded and replaced with the actual templates
VINCI_MODE_TEMPLATE_BASE = '{}/vinci/templates/modes'.format(BASE_DIR)
VINCI_MODE_LIST = [ 'log', 'note', 'wiki', 'journal' ]

TEMPLATE_SETTINGS = None

from local_settings import *  # noqa

if TEMPLATE_SETTINGS:
    TEMPLATES[0]['OPTIONS']['debug'] = TEMPLATE_SETTINGS['debug']

if SECRET_KEY == 'vinci':
    raise ImproperlyConfigured('SECRET_KEY must be provided.')

import logging.config
logging.config.dictConfig(LOGGING)
