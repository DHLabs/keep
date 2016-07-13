""" Test settings and globals which allow us to run our test suite locally """

from settings import *

DEBUG = True
TESTING = True
USE_TZ = False

TEST_RUNNER = 'discover_runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = PROJECT_ROOT
TEST_DISCOVER_ROOT = PROJECT_ROOT
TEST_DISCOVER_PATTERN = 'test_*'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}

MONGODB_DBNAME = 'test'

# Run celery tasks locally
CELERY_ALWAYS_EAGER = True
