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
~~~~~~~~~~

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
