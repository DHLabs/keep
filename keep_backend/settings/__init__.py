import socket

# Load and initialize Django-celery module.
import djcelery
djcelery.setup_loader()

from credentials import SECRET_KEY, TWOFACTOR_ENCRYPTION_KEY

# Django settings for dhlab_backend project.
from .defaults.celery import *
from .defaults.database import *
from .defaults.django import *
from .defaults.logging import *

#DEBUG = True
DEBUG = False#PM
TESTING = False
TEMPLATE_DEBUG = DEBUG

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # KEEP related modules
    'backend',
    'openrosa',                 # OpenROSA API implementation
    'repos',                    # Data repository ( "data diary" ) models & views
    'studies',                  # Studies models & views
    'organizations',            # Organizations models & views
    'visualizations',                      # Data Visualization models & views
    'vocab',                    # Standard Vocab models & views

    # Third party modules
    'guardian',                 # Per-object permissions
    'twofactor',                # Needed to harden login/database
    'registration',             # Needed for user signup
    'tastypie',                 # Needed for our RESTful API
    'storages',                 # Needed for S3 file storage
    'django_mailgun',           # Easy email API
    'south',                    # Database migrations
    'djcelery',                 # Distributed Task Queue
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
#PM added
LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
                },
            }
    }
