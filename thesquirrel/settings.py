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
exec(open(local_settings_path).read())

BASE_URL = 'http://thesquirrel.org'

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
        },
        'TEST_SERIALIZE': False,
    },
}

DEBUG = DEV
TEMPLATE_DEBUG = DEBUG
if DEV:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home'

INSTALLED_APPS = (
    # our apps
    'accounts',
    'articles',
    'docs',
    'editor',
    'events',
    'mediabuilder',
    'thesquirrel',
    'overlaybanner',
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ),
            'loaders': (
                'django.template.loaders.app_directories.Loader',
            ),
        }

    },
]

LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

ROOT_URLCONF = 'thesquirrel.urls'
WSGI_APPLICATION = 'wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_BUILDER = {
    'BUNDLE_MEDIA': not DEV,
    'DOWNLOADS': {
        'jquery.js': 'http://code.jquery.com/jquery-2.1.3.js',
        'jquery.form.js': 'http://malsup.github.com/jquery.form.js',
        'jquery.cookie': ('https://github.com/carhartl/'
                          'jquery-cookie/archive/v1.4.1.tar.gz'),
        'Pikaday': 'https://github.com/dbushell/Pikaday/archive/1.3.2.zip',
        'underscore': ('https://github.com/jashkenas/underscore/'
                       'archive/1.8.3.tar.gz'),
    },
    'SASS_BUNDLES': {
        'app.css': {
            'sources': [
                # External CSS first because we may want to override them
                'mediabuilder/downloads/Pikaday/css/pikaday.css',
                # Now our SCSS because it may override external SCSS variables
                'thesquirrel/scss/app.scss',
                'events/scss/events.scss',
                'overlaybanner/scss/overlaybanner.scss',
            ],
            'include_paths': [
                'editor/scss',
            ],
        },
    },
    'JS_BUNDLES': {
        'app.js': {
            'sources': [
                'mediabuilder/downloads/jquery.js',
                'mediabuilder/downloads/jquery.form.js',
                'mediabuilder/downloads/jquery.cookie/jquery.cookie.js',
                'mediabuilder/downloads/Pikaday/pikaday.js',
                'mediabuilder/downloads/underscore/underscore.js',
                'thesquirrel/js/*.js',
                'editor/js/editor.js',
                'events/js/events.js',
                'overlaybanner/js/overlaybanner.js',
            ],
        },
    },
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/user-media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'user-media')

# Last step is to exec settings_override.py  This allows it to change any
# settings defined here.
settings_override_path = os.path.join(BASE_DIR, 'settings_override.py')
if os.path.exists(settings_override_path):
    exec(open(settings_override_path).read())
