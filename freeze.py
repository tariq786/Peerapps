"""
py2app/py2exe build script for PeerApps.

Will automatically ensure that all build prerequisites are available
via ez_setup

Usage (Mac OS X):
    python freeze.py py2app

Usage (Windows):
    python freeze.py py2exe
"""

import shutil
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup

"""
def add_path_tree( base_path, path, skip_dirs=[ '.svn', '.git' ]):
  path = os.path.join( base_path, path )
  partial_data_files = []
  for root, dirs, files in os.walk( os.path.join( path )):
    sample_list = []
    for skip_dir in skip_dirs:
      if skip_dir in dirs:
        dirs.remove( skip_dir )
    if files:
      for filename in files:
        sample_list.append( os.path.join( root, filename ))
    if sample_list:
      partial_data_files.append((
        root.replace(
          base_path + os.sep if base_path else '',
          '',
          1
        ),
        sample_list
      ))
  return partial_data_files

py2app_data_files = []

# django admin files
#import django
#django_admin_path = os.path.normpath( django.__file__.split('/django/')[0] + '/django/contrib/admin' )
#py2app_data_files += add_path_tree( django_admin_path, 'templates' )
#py2app_data_files += add_path_tree( django_admin_path, 'static' )

# project files
#py2app_data_files += add_path_tree( '', 'LICENSE' )
#py2app_data_files += add_path_tree( '', 'frontend' )
"""

mainscript = 'peerapps.py'
additional_packages = [
    "django",
    "bitcoin",
    "bitcoinrpc",
    "external_db",
    "peerapps",
    "minting",
    "peerblog",
    "peermessage",
    "setup",
    "frontend"
]

if sys.platform == 'darwin':
    extra_options = {
        "setup_requires": ['py2app'],
        "app": [mainscript],
        "options": {
            "py2app": {
                "argv_emulation": True,
                "packages": additional_packages
            }
        },
        #"data_files": py2app_data_files
    }
elif sys.platform == 'win32':
    extra_options = {
        "setup_requires": ['py2exe'],
        "app": [mainscript],
        "options": {
            "py2exe": {
                "packages": additional_packages
            }
        },
    }
else:
    extra_options = {
        "scripts": [mainscript],
    }

setup(
    name="Peerapps",
    **extra_options
)