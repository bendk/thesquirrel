"""
WSGI config for thesquirrel project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thesquirrel.settings")

root_dir = os.path.dirname(__file__)
python_dir = 'python{v.major}.{v.minor}'.format(v=sys.version_info)
sys.path.insert(0, os.path.join(root_dir, 'env', 'lib', python_dir,
                   'site-packages'))
sys.path.insert(0, root_dir)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
