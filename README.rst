|Build Status| |Code Coverage|

Intro
=====

`PyTest <http://pytest.org/latest/>`__ plugin for bugzilla
integration. This plugin currently assumes the following workflow:

-  bug\_status in ['NEW', 'ASSIGNED', 'ON\_DEV'] means the bug is
   known and is being worked on and therefore the test should be skipped
   and will be.

-  bug\_status not in ['NEW', 'ASSIGNED', 'ON\_DEV'] means the bug is
   in a state ready for QE and the test will be run and reported on.

Please feel free to contribute by forking and submitting pull requests or by
submitting feature requests or issues to
`issues <https://github.com/eanxgeek/pytest_marker_bugzilla/issues>`__

Requires
--------

-  pytest >= 2.2.3
-  python-bugzilla >= 0.6.2
-  six

Installation
------------

.. code:: sh

  pip-python install pytest_marker_bugzilla

Usage
-----

#. Create a bugzilla.cfg in the root of your tests. You can also put it under
   $HOME and /etc.

   .. code::

        [DEFAULT]
        bugzilla_url = https://bugzilla.fqdn/xmlrpc.cgi
        # Username for authentication
        bugzilla_username = USERNAME (or blank for public bugs)
        # Password for authentication
        bugzilla_password = PASSWORD (or blank for public bugs)
        # Version of your product
        bugzilla_version = X.Y (or blank if not relevant)
        # Tuple of fixed_in and target_release attribute of bug
        bugzilla_loose = (leave blank for default)

   Options can be overridden with command line options.

   .. code:: sh

     py.test --help

#. Mark your tests with bugzilla marker and bug id(s).

   .. code:: python

     @pytest.mark.bugzilla('bug_id', ...)

   In order to skip the test, all of the specified bugs must lead to
   skipping. Even just one unskipped means that the test will not be
   skipped.

#. Run py.test with bugzilla option to enable the plugin.

   .. code:: sh

     py.test --bugzilla

Conditional guards
~~~~~~~~~~~~~~~~~~

The conditional guards, are functions which can xfail or skip the test
when condition is met.

.. code:: python

    @pytest.mark.bugzilla(1234, skip_when=lambda bug: bug.status == "POST")

.. code:: python

    @pytest.mark.bugzilla(
        567, xfail_when=lambda bug, version: bug.fixed_in > version
    )

The guard is a function, it will receive max. 2 parameters. It depends what
parameters you specify.

The parameters are:

-  bug - specific BZ bug
-  version - tested product version

Order or presence does not matter.

Test library
------------

When you do changes please make sure that you pass current tests.

.. code:: sh

  tox

Please also try to cover new features by writing new tests.

Enjoy.

.. |Build Status| image:: https://travis-ci.org/eanxgeek/pytest_marker_bugzilla.svg?branch=master
   :target: https://travis-ci.org/eanxgeek/pytest_marker_bugzilla
.. |Code Coverage| image:: https://codecov.io/gh/eanxgeek/pytest_marker_bugzilla/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/eanxgeek/pytest_marker_bugzilla
