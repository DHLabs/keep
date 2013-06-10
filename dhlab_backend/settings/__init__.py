# Django settings for dhlab_backend project.
from .defaults.database import *
from .defaults.django import *
from .defaults.logging import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
    'organizations',

    # Third party modules
    'guardian',                 # Per-object permissions
    'twofactor',                # Needed to harden login/database
    'registration',             # Needed for user signup
    'tastypie',                 # Needed for our RESTful API
    'storages',                 # Needed for S3 file storage
    'django_mailgun'            # Easy email API
)

ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    # Set up 2Factor authentication settings
    'twofactor.auth_backends.TwoFactorAuthBackend',
    # Set up per-object permissions backend
    'guardian.backends.ObjectPermissionBackend',
)

TWOFACTOR_ENCRYPTION_KEY = ''

ACCOUNT_ACTIVATION_DAYS = 1
