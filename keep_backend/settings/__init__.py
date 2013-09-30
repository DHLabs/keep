import socket

# Django settings for dhlab_backend project.
from .defaults.database import *
from .defaults.django import *
from .defaults.logging import *

from credentials import SECRET_KEY, TWOFACTOR_ENCRYPTION_KEY

DEBUG = True
TEMPLATE_DEBUG = DEBUG

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # KEEP related modules
    'backend',
    'openrosa',
    'repos',
    'studies',
    'organizations',
    'vocab',

    # Third party modules
    'guardian',                 # Per-object permissions
    'twofactor',                # Needed to harden login/database
    'registration',             # Needed for user signup
    'tastypie',                 # Needed for our RESTful API
    'storages',                 # Needed for S3 file storage
    'django_mailgun',           # Easy email API
    'south',                    # Database migrations
    'raven.contrib.django.raven_compat',    # Smart error logging. See logging.py for raven settings
)

ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    # Set up 2Factor authentication settings
    'twofactor.auth_backends.TwoFactorAuthBackend',
    # Set up per-object permissions backend
    'guardian.backends.ObjectPermissionBackend',
)

ACCOUNT_ACTIVATION_DAYS = 1

# Setup the default TASTYPIE_DEFAULT_FORMATS
# See this page for more info:
# http://django-tastypie.readthedocs.org/en/latest/settings.html#settings-tastypie-default-formats
TASTYPIE_DEFAULT_FORMATS = ['json', 'xml']
