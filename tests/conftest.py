from collections import namedtuple
import pytest


FAKE_BUGS = {
    "1": {
        "id": 1,
        "version": None,
        "fixed_in": None,
        "status": 'NEW',
        "target_release": None,
    },
    "2": {
        "id": 2,
        "version": None,
        "fixed_in": None,
        "status": 'CLOSED',
        "target_release": None,
    },
}


# Create fake bug class
FakeBug = namedtuple('FakeBug', FAKE_BUGS['1'].keys())


@pytest.mark.tryfirst
def pytest_collection_modifyitems(session, config, items):
    plug = config.pluginmanager.getplugin('bugzilla_helper')
    if not plug:  # First run of pytest
        return
    for bug in FAKE_BUGS.values():
        plug.add_bug_to_cache(FakeBug(**bug))
