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
import random
import sys

TEMPLATE = """\
# local-settings.py
#
# This file contains django settings specific to a single server

# Database Auth Info
MYSQL_DB = 'ENTER_DATABASE_NAME'
MYSQL_USER = 'ENTER_DATABASE_USER'
MYSQL_PASS = 'ENTER_DATABASE_PASSWORD'
# Change these if needed
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'

# Email Info
EVENTS_EMAIL = None
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None

# Set to False for production servers
DEV = True

# Server-specific secret key.  No need to change this, but make sure you keep
# it secret
SECRET_KEY = '%(secret_key)s'
"""

def make_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(random.choice(chars) for i in xrange(50))

def make_content():
    return TEMPLATE % {
        'secret_key': make_secret_key(),
    }

def main():
    out_path = os.path.join(os.path.dirname(__file__), 'local_settings.py')
    if os.path.exists(out_path):
        sys.stderr.write("""\
local_settings.py already exists!
If you want a new one, delete the file, then re-run generate-local-settings.py
""")
        sys.exit(1)
    with open(out_path, 'w') as f:
        f.write(make_content())
    print 'local_settings.py created'
    print 'next step is to open it in an editor and fill in the values'

if __name__ == '__main__':
    main()
