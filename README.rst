super-csv
=============================

|pypi-badge| |CI| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

Generic CSV Processing for Django Apps

Overview
------------------------

This library provides a `CSVProcessor <https://github.com/openedx/super-csv/blob/master/super_csv/csv_processor.py>`_ class
which should be subclassed to implement your own per-row processing of CSV files.
At minimum, override `process_row(row)`.

The mixins support optional checksums of arbitrary columns, and asynchronous processing of files using Celery.

Documentation
-------------

Super CSV is a stand alone library that can be used for CSV management, both syncronous and async.

Testing
-------
::

    make requirements

Will install all prerequisites. ::

    make test

Runs the unit tests in local environment.

Using with Docker Devstack
--------------------------
Prerequisite: Have your Open edX https://github.com/openedx/devstack properly installed.
Note: When you see "from inside the lms" below, it means that you've run ``make lms-shell`` from your devstack directory
and are on a command prompt inside the LMS container.

#. Clone this repo into ``../src/`` directory (relative to your "devstack" repo location). This will mount the directory
   in a way that is accessible to the lms container.

#. Clone inside the lms, uninstall super-csv and reinstall your local copy.
   You can run the following line from inside the lms, or from the host machine run ``make install-local``.
   This is necessary if one wants to use latest version for testing/development purposes::

    pip uninstall super-csv -y; pip install -e /edx/src/super-csv

#. Setup dev environment (since virtual environments are recommended for python development, here is an example of using
   virtualenv. Other tools would work as well). By default, edx containers come with virtualenv preinstalled ::

    cd /edx/src/super-csv
    virtualenv super-csv-env
    source super-csv-env/bin/activate
    make requirements

#. That's it.


License
-------

The code in this repository is licensed under the Apache v2 License unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/openedx/.github/blob/master/CONTRIBUTING.md>`_ for details.


The pull request description template should be automatically applied if you are creating a pull request from GitHub. Otherwise you
can find it at `PULL_REQUEST_TEMPLATE.md <https://github.com/openedx/super-csv/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_.

The issue report template should be automatically applied if you are creating an issue on GitHub as well. Otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/openedx/super-csv/blob/master/.github/ISSUE_TEMPLATE.md>`_.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@openedx.org.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help


.. |pypi-badge| image:: https://img.shields.io/pypi/v/super-csv.svg
    :target: https://pypi.python.org/pypi/super-csv/
    :alt: PyPI

.. |CI| image:: https://github.com/openedx/super-csv/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/openedx/super-csv/actions?query=workflow%3A%22Python+CI%22
    :alt: CI

.. |codecov-badge| image:: http://codecov.io/github/edx/super-csv/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/super-csv?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/super-csv/badge/?version=latest
    :target: http://super-csv.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/super-csv.svg
    :target: https://pypi.python.org/pypi/super-csv/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/super-csv.svg
    :target: https://github.com/openedx/super-csv/blob/master/LICENSE.txt
    :alt: License
