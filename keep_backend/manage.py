#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
#    sys.path.append('/home/ubuntu/.virtualenvs/dhlab_backend3/keep/keep_backend')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")


    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
