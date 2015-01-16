#!/usr/bin/python
#
# setup-server.py
#
# This script sets up things needed to run the server, for example:
#   - sets up the python virtualenv
#   - checks for a valid local_settings.py file
#   - runs database migrations
#
# It can be used for both installation and updating things after a code change

import os
import subprocess

PROJECT_ROOT = os.path.dirname(__file__)

def setup_virtualenv():
    subprocess.check_call(['env/bin/pip', 'install', '-r',
                           'requirements.txt'])

def main():
    os.chdir(PROJECT_ROOT)
    setup_virtualenv()

if __name__ == '__main__':
    main()
