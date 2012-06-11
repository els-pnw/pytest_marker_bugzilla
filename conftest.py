import re
import xmlrpclib
import pytest
import ConfigParser


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
    
    config = ConfigParser.ConfigParser()
    config.read('bugzilla.cfg')
    
    group = parser.getgroup('Bugzilla integration')
    group.addoption('--bugzilla', 
                    action='store_true', 
                    default=False,
                    dest='bugzilla',
                    help='Enable Bugzilla support.')
    group.addoption('--bugzilla-url',
                    action='store',
                    dest='bugzilla_url',
                    default=config.get('DEFAULT', 'bugzilla_url'),
                    metavar='url',
                    help='Overrides the xmlrpc url for bugzilla found in bugzilla.cfg.')
    group.addoption('--bugzilla-user',
                    action='store',
                    dest='bugzilla_username',
                    default=config.get('DEFAULT', 'bugzilla_username'),
                    metavar='username',
                    help='Overrides the bugzilla username in bugzilla.cfg.')
    group.addoption('--bugzilla-password',
                    action='store',
                    dest='bugzilla_password',
                    default=config.get('DEFAULT', 'bugzilla_password'),
                    metavar='password',
                    help='Overrides the bugzilla password in bugzilla.cfg.')
    
def pytest_configure(config):
    if config.getvalue("bugzilla"):
        my = BugzillaHooks(config)
        ok = config.pluginmanager.register(my, "bugzilla_helper")
        assert ok

