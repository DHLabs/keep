from settings import *

DEBUG = True
<<<<<<< HEAD
=======
#DEBUG = False #PM
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static/'),
)

# Instead of sending out real emails the console backend just writes the emails
# that would be send to the standard output. By default, the console backend
# writes to stdout.
#To specify this backend, put the following in your settings:
<<<<<<< HEAD
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
=======
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
