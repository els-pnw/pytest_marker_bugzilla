import re
import xmlrpclib
import pytest
import bugzilla
import ConfigParser


class BugzillaHooks(object):
    def __init__(self, config, bugzilla):
        self.config = config
        self.bugzilla = bugzilla

    def pytest_runtest_makereport(self, __multicall__, item):
        if isinstance(item, item.Function):
            func = item.obj
            bugzilla_marker = getattr(func, "bugzilla", None)
            if bugzilla_marker is None:
                return
            report = __multicall__.execute()
            report.bug_id = bugzilla_marker.args[0]
            
            return report

    def pytest_report_teststatus(self, report):
        bug_id = getattr(report, "bug_id", None)
        if bug_id is not None:
            if report.failed:
                return "failed", "P", "PENDINGFIX"

def pytest_addoption(parser):
    """
    Add a options section to py.test --help for bugzilla integration.
    Parse configuration file, bugzilla.cfg and / or the command line options
    passed.
    """
    
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
    """
    If bugzilla is neabled, setup a session
    with bugzilla_url.
    """
    if config.getvalue("bugzilla"):
        url = config.getvalue('bugzilla_url')
        user = config.getvalue('bugzilla_username')
        password = config.getvalue('bugzilla_password')
        
        bz = bugzilla.Bugzilla(url=url)
        bz.login(user,password)
        
        my = BugzillaHooks(config, bz)
        ok = config.pluginmanager.register(my, "bugzilla_helper")
        assert ok

