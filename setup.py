#!/usr/bin/env python

import os, sys

from setuptools import setup, find_packages
from setuptools import Command


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings


        settings.configure(
            DATABASES = {
                'default': {
                    # 'NAME': ':memory:',
                    # 'TEST_NAME': ':memory:',
                    'NAME': 'cody.sqlite3',
                    'TEST_NAME': 'cody.sqlite3',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS = (
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.sites',
                'django.contrib.sitemaps',
                'floppyforms',
                'multifilefield',
            )
        )

        import django


        if django.VERSION[:2] >= (1, 7):
            from django.core.management import call_command

            django.setup()

            call_command('test', 'multifilefield')
        else:
            from multifilefield.runtests import runtests

            runtests()


setup(
    name='multifilefield',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A pluggable django html5 field for multiple files.',
    long_description=README,
    url='https://github.com/invisiblehands/django-multifilefield/',
    author_email='cody@invisiblehands.ca',
    author='Cody Redmond',
    install_requires=[
        'Django>=1.6.0',
        'django-floppyforms>=1.1.1',
        'six>=1.9.0'
    ],
    tests_require=[
        'Django>=1.6.0',
        'django-floppyforms>=1.1.1',
        'six>=1.9.0'
    ],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)
