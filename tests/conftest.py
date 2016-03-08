from collections import namedtuple
import pytest


FAKE_BUGS = {
    "1": {
        "id": '1',
        "version": None,
        "fixed_in": None,
        "status": 'NEW',
        "target_release": None,
        "resolution": 'foo',
        "summary": 'ONE',
    },
    "2": {
        "id": '2',
        "version": None,
        "fixed_in": None,
        "status": 'ON_QA',
        "target_release": None,
        "resolution": 'foo',
        "summary": 'TWO',
    },
    "3": {
        "id": '3',
        "version": None,
        "fixed_in": None,
        "status": 'VERIFIED',
        "target_release": None,
        "resolution": 'foo',
        "summary": 'THREE',
    },
    "4": {
        "id": '4',
        "version": None,
        "fixed_in": None,
        "status": 'CLOSED',
        "target_release": None,
        "resolution": 'DUPLICATE',
        "summary": 'FOUR',
    },
    "5": {
        "id": '5',
        "version": None,
        "fixed_in": None,
        "status": 'MODIFIED',
        "target_release": None,
        "resolution": 'foo',
        "summary": 'FIVE',
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
