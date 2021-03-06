##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '0.7.1'

import os

from setuptools import setup, find_packages

requires = []
try:
    # Available from Python >= 2.5
    from sys import _current_frames
except ImportError:
    # Otherwise, depend on threadframe, which provide the same functionality as
    # the function in Python >= 2.5
    requires.append('threadframe')

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='repoze.debug',
      version=__version__,
      description='Forensic debugging WSGI middleware',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      keywords='wsgi request response debug middleware',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      tests_require = [
               'Paste',
               'WebOb',
               ],
      install_requires = [
               'Paste',
               'WebOb',
               ] + requires,
      test_suite="repoze.debug.tests",
      entry_points = """\
        [paste.filter_app_factory]
        responselogger = repoze.debug.responselogger:make_middleware
        canary = repoze.debug.canary:make_middleware
        pdbpm = repoze.debug.pdbpm:make_middleware
        threads = repoze.debug.threads:make_middleware
        [console_scripts]
        wsgirequestprofiler = repoze.debug.scripts.requestprofiler:main
      """
      )

