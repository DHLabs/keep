from settings import *
from credentials import AWS, MAILGUN

ALLOWED_HOSTS = [ '*' ]

DEBUG = False

# Setup S3 file storage for our static files.
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_ACCESS_KEY_ID       = AWS[ 'ACCESS_KEY_ID' ]
AWS_SECRET_ACCESS_KEY   = AWS[ 'SECRET_KEY' ]
AWS_STORAGE_BUCKET_NAME = 'keep-static'

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Setup Mailgun as our email backend
# http://mailgun.net
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY      = MAILGUN[ 'ACCESS_KEY' ]
MAILGUN_SERVER_NAME     = MAILGUN[ 'SERVER_NAME' ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'local.db',
    }
}
