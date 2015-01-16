#!/usr/bin/env python
import os
import sys

def setup_path():
    root_dir = os.path.dirname(__file__)
    site_packages = os.path.join(root_dir, 'env', 'lib', 'python2.7',
                                 'site-packages')
    sys.path.insert(0, site_packages)
    sys.path.insert(0, root_dir)

if __name__ == "__main__":
    setup_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thesquirrel.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
