#!/usr/bin/env python3
import os
import subprocess
import sys

if __name__ == "__main__":
    root_dir = os.path.abspath(os.path.dirname(__file__))
    django_admin = os.path.join(root_dir, 'env', 'bin', 'django-admin')
    os.environ["PYTHONPATH"] = root_dir
    os.environ["DJANGO_SETTINGS_MODULE"] = "thesquirrel.settings"

    subprocess.run([django_admin] + sys.argv[1:])
