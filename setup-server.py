#!/usr/bin/env python3
#
# setup-server.py
#
# This script sets up things needed to run the server:
#   - sets up the python virtualenv
#   - checks for a valid local_settings.py file
#   - runs database migrations
#   - downloads web libraries
#   - builds and collects static media files (production only)
#
# It can also be used to update things after code changes.  On production you
# should probably run this whenever you pull in new code.  On dev, run it when
# a pip module or web library dependency changes.
#

import os
import subprocess

BASE_DIR = os.path.dirname(__file__)

def setup_virtualenv():
    subprocess.check_call(['env/bin/pip', 'install', 'setuptools==57.5.0'])
    subprocess.check_call(['env/bin/pip', 'install', '-r',
                           'requirements.txt'])

def manage(*command):
    subprocess.check_call(['env/bin/python3', 'manage.py' ] + list(command))

def production():
    mod_dict = {}
    exec(open(os.path.join(BASE_DIR, 'local_settings.py')).read(), mod_dict)
    return not mod_dict.get('DEV')

def main():
    os.chdir(BASE_DIR)
    setup_virtualenv()
    manage('migrate')
    manage('buildmedia')
    if production():
        manage('collectstatic', '--noinput')
        # touch wsgi.py to make apache restart the wsgi daemon
        os.utime(os.path.join(BASE_DIR, 'wsgi.py'), None)

if __name__ == '__main__':
    main()
