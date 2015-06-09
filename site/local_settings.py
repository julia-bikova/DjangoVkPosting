# -*- encoding: utf-8 -*-

TEMPLATE_DIRS = ()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'site',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',                      # Set to empty string for default.
    }
}

STATIC_ROOT = ''
MEDIA_ROOT = ''