from settings import *

DEBUG = True

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static/'),
)

# Instead of sending out real emails the console backend just writes the emails
# that would be send to the standard output. By default, the console backend
# writes to stdout.
#To specify this backend, put the following in your settings:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'