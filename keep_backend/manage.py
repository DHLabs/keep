#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
<<<<<<< HEAD
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")

=======
#    sys.path.append('/home/ubuntu/.virtualenvs/dhlab_backend3/keep/keep_backend')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")


>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
