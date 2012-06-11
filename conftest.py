import re
import xmlrpclib
import pytest


class BugzillaHooks(object):
    def __init__(self, config):
        self.config = config

    def pytest_runtest_makereport(self, __multicall__, item):
        if isinstance(item, item.Function):
            func = item.obj
            bugzilla_marker = getattr(func, "bugzilla", None)
            if bugzilla_marker is None:
                return
            report = __multicall__.execute()
            report.bugzilla_url = bugzilla_marker.args[0]
            return report

    def pytest_report_teststatus(self, report):
        url = getattr(report, "bugzilla_url", None)
        if url is not None:
            if report.failed:
                return "failed", "P", "PENDINGFIX"

def pytest_addoption(parser):
    group = parser.getgroup('Bugzilla integration')
    group.addoption('--bugzilla', action='store_true', default=False,
          dest='bugzilla',
          help="Query bugzilla to find to check statuses of tests associated with bugs")

def pytest_configure(config):
    if config.getvalue("bugzilla"):
        my = BugzillaHooks(config)
        ok = config.pluginmanager.register(my, "bugzilla_helper")
        assert ok

