#!/usr/bin/env python
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
    version_file = open_as_of_py3(filename, encoding='utf-8').read()  # pylint: disable=consider-using-with
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
            # pylint: disable-next=consider-using-with
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
    os.system(f'git tag -a {VERSION!s} -m \'version {VERSION!s}\'')
    os.system("git push --tags")
    sys.exit()

# pylint: disable-next=consider-using-with
README = open_as_of_py3(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8').read()
# pylint: disable-next=consider-using-with
CHANGELOG = open_as_of_py3(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst'), encoding='utf-8').read()

setup(
    name='super-csv',
    version=VERSION,
    description="""CSV Processor""",
    long_description=README + '\n\n' + CHANGELOG,
    long_description_content_type='text/x-rst',
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
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
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
