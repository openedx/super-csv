super-csv
=============================

|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

Generic CSV Processing for Django Apps

Overview
------------------------

This library provides a `CSVProcessor <https://github.com/edx/super-csv/blob/master/super_csv/csv_processor.py>`_ class which should be subclassed to implement your own per-row processing of CSV files. At minimum, override `process_row(row)`.

The mixins support optional checksums of arbitrary columns, and asynchronous processing of files using Celery.

Documentation
-------------

The full documentation is at https://super-csv.readthedocs.org.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

The pull request description template should be automatically applied if you are creating a pull request from GitHub. Otherwise you
can find it at `PULL_REQUEST_TEMPLATE.md <https://github.com/edx/super-csv/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_.

The issue report template should be automatically applied if you are creating an issue on GitHub as well. Otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/edx/super-csv/blob/master/.github/ISSUE_TEMPLATE.md>`_.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help


.. |pypi-badge| image:: https://img.shields.io/pypi/v/super-csv.svg
    :target: https://pypi.python.org/pypi/super-csv/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.org/edx/super-csv.svg?branch=master
    :target: https://travis-ci.org/edx/super-csv
    :alt: Travis

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
    :target: https://github.com/edx/super-csv/blob/master/LICENSE.txt
    :alt: License
