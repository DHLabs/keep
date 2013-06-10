from settings import *
from credentials import AWS, MAILGUN, RDS

ALLOWED_HOSTS = [ '*' ]

DEBUG = False

# # Setup Amazon RDS access
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'keep',
#         'PORT': 3306,
#         'HOST': RDS[ 'HOST' ],
#         'USER': RDS[ 'USER' ],
#         'PASSWORD': RDS[ 'PASSWORD' ]
#     }
# }

# Setup S3 file storage for our static files.
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_ACCESS_KEY_ID       = AWS[ 'ACCESS_KEY_ID' ]
AWS_SECRET_ACCESS_KEY   = AWS[ 'SECRET_KEY' ]
AWS_STORAGE_BUCKET_NAME = 'keep-static'
# Use Amazon Cloudfront
AWS_S3_CUSTOM_DOMAIN    = 's3.amazonaws.com/keep-static'
AWS_HEADERS = {
    #'Expires': 'Thu, 15 Apr 2030 20:00:00 GMT',
    #'Cache-Control': 'max-age=86400',
    'Cache-Control': 'max-age=10',
}

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Setup Mailgun as our email backend
# http://mailgun.net
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY      = MAILGUN[ 'ACCESS_KEY' ]
MAILGUN_SERVER_NAME     = MAILGUN[ 'SERVER_NAME' ]
