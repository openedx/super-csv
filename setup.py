#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package metadata for super_csv.
"""

import os
import re
import sys
from io import open as open_as_of_py3

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open_as_of_py3(filename, encoding='utf-8').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Returns:
        list: Requirements file relative path strings
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip() for line in open_as_of_py3(path, encoding='utf-8').readlines()
            if is_requirement(line.strip())
        )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment, a URL, or an included file
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


VERSION = get_version('super_csv', '__init__.py')

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system(u"git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

README = open_as_of_py3(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8').read()
CHANGELOG = open_as_of_py3(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst'), encoding='utf-8').read()

setup(
    name='super-csv',
    version=VERSION,
    description="""CSV Processor""",
    long_description=README + '\n\n' + CHANGELOG,
    author='edX',
    author_email='oscm@edx.org',
    url='https://github.com/edx/super-csv',
    packages=[
        'super_csv',
    ],
    include_package_data=True,
    install_requires=load_requirements('requirements/base.in'),
    license="Apache 2.0",
    zip_safe=False,
    keywords='Django edx',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'lms.djangoapp': [
            "super_csv = super_csv.apps:SuperCSVConfig",
        ],
    }
)
