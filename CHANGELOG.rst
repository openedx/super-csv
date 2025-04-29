Change Log
----------

..
   All enhancements and patches to super_csv will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
----------
[4.1.0] - 2025-04-24
~~~~~~~~~~~~~~~~~~~~

* Added django52 support.


[3.2.0] - 2023-07-31
~~~~~~~~~~~~~~~~~~~~

* Added support of python 3.11 and 3.12
* Dropped django32 support.


[3.1.0] - 2023-07-31
~~~~~~~~~~~~~~~~~~~~

* Switch from ``edx-sphinx-theme`` to ``sphinx-book-theme`` since the former is
  deprecated.  See https://github.com/openedx/edx-sphinx-theme/issues/184 for
  more details.
* Added support of Django 4.2

[3.0.1] - 2022-02-17
~~~~~~~~~~~~~~~~~~~~

* fix: encode the csv data before save

[3.0.0] - 2022-02-17
~~~~~~~~~~~~~~~~~~~~

* Fix `dev.in` to pull from `ci.txt` rather than `travis.txt`.
* Dropped Django22, 30 and 31 support.
* Added Django40 support.

[2.1.1] - 2021-09-01
~~~~~~~~~~~~~~~~~~~~

* Fix missing file error for bulk grade. Some of the files were expired but the code still expect to read it without `try/catch`.

[2.1.0] - 2020-07-26
~~~~~~~~~~~~~~~~~~~~

* Added Django 3.0, 3.1 & 3.2 Support

[2.0.1] - 2020-03-12
~~~~~~~~~~~~~~~~~~~~

* Update write_file and get_iterator to allow row/column overrides

[2.0.0] - 2020-12-23
~~~~~~~~~~~~~~~~~~~~

* Removed python 3.5 support
* Adds support for celery 5

[1.1.0] - 2020-12-02
~~~~~~~~~~~~~~~~~~~~

* Add code_owner custom attribute for monitoring celery tasks.

[1.0.3] - 2020-11-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Updated travis badge in README.rst to point to travis-ci.com

[1.0.2] - 2020-09-14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Move to Apache License

[1.0.1] - 2020-09-14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Minor updates to attrs, code-annotations, and freezegun dependencies

[1.0.0] - 2020-09-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Upgrade celery to 4.2.2

[0.9.9] - 2020-05-28
~~~~~~~~~~~~~~~~~~~~

* Removed caniusepython3 & python_2_unicode_compatible packages

[0.9.8] - 2020-05-04
~~~~~~~~~~~~~~~~~~~~

* dropped support for Django version less than 2.2 and Added support for python 3.8

[0.9.7] - 2020-03-05
~~~~~~~~~~~~~~~~~~~~

* Remove django-celery dependency

[0.9.6] - 2019-11-20
~~~~~~~~~~~~~~~~~~~~

* Django 2.2 support

[0.9.5] - 2019-10-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Decode the input file before passing to DictReader if necessary

[0.9.4] - 2019-09-24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Let the ``DeferrableMixin.save()`` method take an optional ``operating_user`` parameter.

[0.9.3] - 2019-09-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Commit after ``CSVOperation`` creation so that async celery tasks can find the operation record when they start.

[0.9.2] - 2019-09-17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If a class inheriting from DeferrableMixin has a field user_id, use that user for the CSVOperation

[0.9.1] - 2019-07-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Reverses the ordering of CSV operation history rows

[0.8] - 2019-07-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Changes checksum column to avoid CSV quoting issues

[0.7.1] - 2019-07-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Exposes additional fields in serialized history of operations re:degree of success of the operation

[0.5.0] - 2019-07-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Exposes methods for serializing history of operations for particular processors.

[0.1.0] - 2019-05-15
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
