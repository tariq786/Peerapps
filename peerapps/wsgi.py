"""
WSGI config for peerapps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import sys
root_path = os.path.abspath(os.path.split(__file__)[0])
sys.path.insert(0, os.path.join(root_path, 'peerapps'))
sys.path.insert(0, root_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "peerapps.settings")

application = get_wsgi_application()
