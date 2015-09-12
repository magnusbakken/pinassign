#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()

from pinassign import __version__

setup(name='pinassign',
      version=__version__,
      description='Implementation of an algorithm for efficiently assigning players to machines in a Pinball tournament.',
      long_description=long_description,
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.4',
          'Natural Language :: English',
      ],
      keywords='pinball python',
      author='Magnus Grindal Bakken',
      author_email='magnusbakken@gmail.com',
      maintainer='Magnus Grindal Bakken',
      maintainer_email='magnusbakken@gmail.com',
      url='https://github.com/magnusbakken/pinassign',
      license='MIT',
      packages=['pinassign'],
      install_requires=['tabulate>=0.7.5', 'while>=0.24.0'],
      zip_safe=False
)