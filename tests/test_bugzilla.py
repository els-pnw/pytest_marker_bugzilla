"""
This is test suite for bugzilla plugin.
"""


CONFTEST = """
from collections import namedtuple
import pytest


FAKE_BUGS = {
    "1": {
        "id": 1,
        "version": None,
        "fixed_in": None,
        "status": 'NEW',
        "target_release": None,
        "resolution": 'foo 1',
        "summary": 'ONE',
    },
    "2": {
        "id": 2,
        "version": None,
        "fixed_in": None,
        "status": 'CLOSED',
        "target_release": None,
        "resolution": 'foo 2',
        "summary": 'TWO',
    },
    "3": {
        "id": 3,
        "version": 1.0,
        "fixed_in": 2.0,
        "status": 'POST',
        "target_release": None,
        "resolution": 'foo 3',
        "summary": 'THREE',
    },
    "4": {
        "id": 4,
        "version": None,
        "fixed_in": None,
        "status": 'NEW',
        "target_release": None,
        "resolution": 'foo 4',
        "summary": 'FOUR',
    },
}


# Create fake bug class
FakeBug = namedtuple('FakeBug', FAKE_BUGS['1'].keys())


@pytest.mark.tryfirst
def pytest_collection_modifyitems(session, config, items):
    plug = config.pluginmanager.getplugin('bugzilla_helper')
    assert plug is not None
    for bug in FAKE_BUGS.values():
        plug.add_bug_to_cache(FakeBug(**bug))
"""


BUGZILLA_ARGS = (
    '--bugzilla',
    '--bugzilla-url=https://bugzilla.redhat.com/xmlrpc.cgi',
)


def test_pass_without_marker(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        def test_pass():
            assert True
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(1, 0, 0)


def test_fail_without_marker(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        def test_pass():
            assert False
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 0, 1)


def test_new_bug_failing(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1')
        def test_new_bug():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 1, 0)


def test_new_int_bug_failing(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla(1)
        def test_new_bug():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 1, 0)


def test_new_bug_passing(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1')
        def test_new_bug():
            assert True
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 1, 0)


def test_closed_bug(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('2')
        def test_closed_bug():
            assert(os.path.exists('/etc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(1, 0, 0)


def test_closed_bug_with_failure(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('2')
        def test_closed_bug_with_failure():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 0, 1)


def test_more_cases(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1')
        def test_new_bug():
            assert(os.path.exists('/etcccc'))

        @pytest.mark.bugzilla('2')
        def test_closed_bug():
            assert(os.path.exists('/etc'))

        @pytest.mark.bugzilla('2')
        def test_closed_bug_with_failure():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(1, 1, 1)


def test_multiple_bugs_skip_1(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1', '4', '2')
        def test_new_bug():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 1, 0)


def test_multiple_bugs_skip_2(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1', '4')
        def test_new_bug():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 1, 0)


def test_skip_when_feature(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('3', skip_when=lambda bug: bug.status == "POST")
        def test_new_bug():
            assert(os.path.exists('/etcccc'))
    """)
    result = testdir.runpytest(*BUGZILLA_ARGS)
    result.assert_outcomes(0, 1, 0)


def test_xfail_when_feature(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('3', xfail_when=lambda bug, version: bug.fixed_in > version)
        def test_new_bug():
            assert(os.path.exists('/etcccc'))
    """)
    args = BUGZILLA_ARGS + ('--bugzilla-project-version', '1.6')
    result = testdir.runpytest(*args)
    d = result.parseoutcomes()
    assert d.get('xfailed', 0) == 1


def test_config_file(testdir):
    testdir.makefile(
        '.cfg',
        bugzilla="\n".join([
            '[DEFAULT]',
            'bugzilla_url = https://bugzilla.redhat.com/xmlrpc.cgi',
        ])
    )
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1')
        def test_new_bug():
            assert True
    """)
    result = testdir.runpytest('--bugzilla')
    result.assert_outcomes(0, 1, 0)


def test_more_cases_with_xdist(testdir):
    testdir.makeconftest(CONFTEST)
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.mark.bugzilla('1')
        def test_new_bug():
            assert(os.path.exists('/etcccc'))

        @pytest.mark.bugzilla('2')
        def test_closed_bug():
            assert(os.path.exists('/etc'))

        @pytest.mark.bugzilla('2')
        def test_closed_bug_with_failure():
            assert(os.path.exists('/etcccc'))
    """)
    args = BUGZILLA_ARGS + ('-n', '2')
    result = testdir.runpytest(*args)
    result.assert_outcomes(1, 1, 1)
