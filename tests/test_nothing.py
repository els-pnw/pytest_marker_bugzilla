"""
How to add new test?

There is file called test_bugzilla.py.in, this file contains real usage
of bugzilla plugin.
It uses bugzilla mark and does its job.

In this file we have same test cases as in test_bugzilla.py.in,
but here we test whether test case from test_bugzilla.py.in has expected
result.

If you want to add new test into both files, one test bugzilla mark,
and second verify expected result.

NOTE: if you want to use different bug ID, please add it to conftests.py
"""
import os
import re
import sys
import subprocess
import pytest


@pytest.mark.skip_selenium
@pytest.mark.nondestructive
class TestNothing(object):

    result_file = "results.txt"
    test_file = os.path.join(os.path.dirname(__file__), "test_bugzilla.py")
    results = None

    @classmethod
    def setup_class(cls):
        # Create config file
        config = "bugzilla.cfg"
        if not os.path.exists(config):
            with open(config, "w") as fh:
                fh.write(
                    "\n".join(
                        [
                            "[DEFAULT]",
                            "bugzilla_url = "
                            "https://bugzilla.redhat.com/xmlrpc.cgi",
                        ]
                    )
                )

        # Create test
        with open(cls.test_file + ".in") as fhs:
            with open(cls.test_file, 'w') as fht:
                fht.write(fhs.read())

        # Run test runner with plugin enabled
        cmd = [
            'py.test', '--bugzilla', '--result-log=%s' % cls.result_file,
            cls.test_file,
        ]
        env = os.environ.copy()
        env['PYTHONPATH'] = ":".join(sys.path)
        p = subprocess.Popen(
            subprocess.list2cmdline(cmd),
            shell=True,
            env=env,
        )
        p.communicate()
        assert os.path.exists(cls.result_file)

        # Read results of tests
        with open(cls.result_file) as fh:
            data = fh.read()
        regex = re.compile("^(?P<code>[sfex.]) (?P<name>.+)\n", re.I | re.M)
        cls.results = dict(
            (m.group('name').split("::")[-1], m.group('code'))
            for m in regex.finditer(data)
        )

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.test_file):
            os.unlink(cls.test_file)

    def _assert_result(self, expected, test_name):
        status = self.results[test_name]
        assert status == expected

    def test_new_bz(self):
        """
        New bug, test-case should be skipped.
        """
        self._assert_result('s', 'test_new_bz')

    def test_closed_bz(self):
        """
        Closed bug, passing test-case, it should pass.
        """
        self._assert_result('.', 'test_closed_bz')

    def test_closed_bz_with_failure(self):
        """
        Closed bug, failing test-case, it should fail.
        """
        self._assert_result('F', 'test_closed_bz_with_failure')

    def test_without_bugzilla(self):
        """
        No decorator, passsing test-case, it should pass
        """
        self._assert_result('.', 'test_without_bugzilla')

    def test_fail_without_bugzilla(self):
        """
        No decorator, failing test-case, it should fail.
        """
        self._assert_result('F', 'test_fail_without_bugzilla')
