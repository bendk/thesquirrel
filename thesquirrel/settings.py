"""
Django settings for thesquirrel project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# First thing -- we exec local_settings.py to get various settings from there

local_settings_path = os.path.join(BASE_DIR, 'local_settings.py')
if not os.path.exists(local_settings_path):
    sys.stderr.write("No local_settings.py file!\n"
                     "Run setup-server.py\n")
    sys.exit(-1)
execfile(local_settings_path)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DB,
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PASS,
        'HOST': MYSQL_HOST,
        'PORT': MYSQL_PORT,
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    },
}

DEBUG = DEV
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = []
if DEV:
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

INSTALLED_APPS = (
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    # our apps
    'docs',
    'mediabuilder',
    'thesquirrel',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'thesquirrel.urls'
WSGI_APPLICATION = 'wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_BUILDER = {
    'BUNDLE_MEDIA': not DEV,
    'DOWNLOADS': {
        'jquery.js': 'http://code.jquery.com/jquery-2.1.3.js',
        'fontawesome': ('http://fortawesome.github.io/'
                               'Font-Awesome/assets/font-awesome-4.3.0.zip'),
    },
    'SASS_BUNDLES': {
        'app.css': {
            'source': 'thesquirrel/scss/app.scss',
            'include_paths': [
                'mediabuilder/downloads/fontawesome/scss/',
            ],
        },
    },
    'JS_BUNDLES': {
        'app.js': {
            'sources': [
                'mediabuilder/downloads/jquery.js',
                'thesquirrel/js/menus.js',
            ],
        },
    },
    'COPY_TO_STATIC': {
        'fontawesome': 'mediabuilder/downloads/fontawesome/fonts/',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Last step is to exec settings_override.py  This allows it to change any
# settings defined here.
settings_override_path = os.path.join(BASE_DIR, 'settings_override.py')
if os.path.exists(settings_override_path):
    execfile(settings_override_path)
