[![Build Status][travisimg]][travis]

# Intro
[PyTest][pytest] plugin for bugzilla integration. This plugin currently
assumes the following workflow:

  * bug_status in ['NEW', 'ASSIGNED', 'ON_DEV'] means the bug is known
  and is being worked on and therefore the test should be skipped and will be.

  * bug_status not in ['NEW', 'ASSIGNED', 'ON_DEV'] means the bug is in a state
  ready for QE and the test will be run and reported on.

Please feel free to contribute by forking and submitting pull requests or by
submitting feature requests or issues to [issues][githubissues]

## Requires
  * pytest >= 2.2.3
  * python-bugzilla >= 0.6.2
  * six

## Installation
``pip-python install pytest_marker_bugzilla``

## Usage
  1. Create a bugzilla.cfg in the root of your tests.
     You can also put it under $HOME and /etc.

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
     
     ``py.test --help``
     
  2. Mark your tests with bugzilla marker and bug id(s).

     ```python
     @pytest.mark.bugzilla('bug_id', ...)
     ```

     In order to skip the test, all of the specified bugs must lead to
     skipping. Even just one unskipped means that the test will not be skipped.
     
  3. Run py.test with bugzilla option to enable the plugin.
  
     ``py.test --bugzilla``

### Conditional guards

The conditional guards, are functions which can xfail or skip the test when
condition is met.

```python
@pytest.mark.bugzilla(1234, skip_when=lambda bug: bug.status == "POST")
```

```python
@pytest.mark.bugzilla(
    567, xfail_when=lambda bug, version: bug.fixed_in > version
)
```

The guard is a function, it will receive max. 2 parameters. It depends what
parameters you specify.

The parameters are:

  * bug - specific BZ bug
  * version - tested product version

Order or presence does not matter.

## Test library

When you do changes please make sure that you pass current tests.

``tox``

Please also try to cover new features by writing new tests.

Enjoy.

[pytest]: http://pytest.org/latest/
[githubissues]: https://github.com/eanxgeek/pytest_marker_bugzilla/issues
[travisimg]: https://travis-ci.org/eanxgeek/pytest_marker_bugzilla.svg?branch=master
[travis]: https://travis-ci.org/eanxgeek/pytest_marker_bugzilla
