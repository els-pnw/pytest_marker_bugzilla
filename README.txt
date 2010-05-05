===============
pytest_bugzilla
===============

py.test plugin to integrate it with bugzilla so that it's possible to
annotate tests with the identifier of the bug they're testing.

If the bug has been closed but the test still fails, a warning is
generated and if the bug is still open, the test is flagged as
analysed (instead of Failed)

Usage
-----

After installation (e.g. via ``pip install pytest-bugzilla``) you can
just invoke ``py.test``with the ``--bugzilla`` flag.

Use ``py.test --help`` for additional options.

Annotating tests
----------------

To mark a test as being for a specific issue (say issue no. 12345),
Put "#12345" somewhere in the test functions docstring e.g.::
  
  def test_something():
    "This test is for bug #12345"
    do_test()

Bugzilla credentials
--------------------

You have to change the bugzilla server URL/username/password using
command line options. You can edit the plugin file to change the
defaults so that they work without having to pass these options
explicitly.


