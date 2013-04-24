from settings import *

ALLOWED_HOSTS = [ '*' ]

DEBUG = False

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
STATIC_ROOT = '/usr/share/nginx/www/keep_static'
