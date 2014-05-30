# -*- coding: utf-8 -*-
import bugzilla
import ConfigParser
import pytest
import os
"""This plugin integrates pytest with bugzilla

It allows the tester to mark a test with a bug id. The test will then be skipped until the bug
status is no longer NEW, ON_DEV, or ASSIGNED.

You must set the url either at the command line or in bugzilla.cfg.

Author: Eric L. Sammons
"""
_bugs_pool = {}


class BugzillaBugs(object):
    def __init__(self, appliance_version, bugzilla, *bug_ids):
        self.version = appliance_version
        self.bugzilla = bugzilla
        self.bug_ids = bug_ids

    @property
    def bugs_gen(self):
        for bug_id in self.bug_ids:
            bug = self.bugzilla.getbug(bug_id)
            if bug_id not in _bugs_pool:
                _bugs_pool[bug_id] = bug
            yield _bugs_pool[bug_id]


class BugzillaHooks(object):
    def __init__(self, config, bugzilla, version=None):
        self.config = config
        self.bugzilla = bugzilla
        self.version = version

    def pytest_runtest_setup(self, item):
        """
        Run test setup.
        :param item: test being run.
        """
        if "bugzilla" not in item.keywords:
            return
        bugs = item.funcargs["bugs"]
        will_skip = True
        skippers = []
        for bug in bugs.bugs_gen:
            if bug.status not in {"NEW", "ASSIGNED", "ON_DEV"}:
                will_skip = False
            else:
                skippers.append(bug)

        if will_skip:
            pytest.skip(
                "Skipping this test because all of these assigned bugs:\n{}".format(
                    "\n".join(
                        [
                            "{} https://bugzilla.redhat.com/show_bug.cgi?id={}".format(
                                bug.status, bug.id
                            )
                            for bug
                            in skippers
                        ]
                    )
                )
            )

    def pytest_collection_modifyitems(self, session, config, items):
        reporter = config.pluginmanager.getplugin("terminalreporter")
        reporter.write("Checking for bugzilla-related tests\n", bold=True)
        cache = {}
        for i, item in enumerate(filter(lambda i: i.get_marker("bugzilla") is not None, items)):
            marker = item.get_marker('bugzilla')
            bugs = tuple(sorted(set(map(int, marker.args))))  # (O_O) for caching
            if bugs not in cache:
                reporter.write(".")
                cache[bugs] = BugzillaBugs(self.version, self.bugzilla, *bugs)
            item.funcargs["bugs"] = cache[bugs]
        reporter.write("\nChecking for bugzilla-related tests has finished\n", bold=True)


def pytest_addoption(parser):
    """
    Add a options section to py.test --help for bugzilla integration.
    Parse configuration file, bugzilla.cfg and / or the command line options
    passed.

    :param parser: Command line options.
    """
    group = parser.getgroup('Bugzilla integration')
    group.addoption('--bugzilla',
                    action='store_true',
                    default=False,
                    dest='bugzilla',
                    help='Enable Bugzilla support.')

    config = ConfigParser.ConfigParser()
    if os.path.exists('bugzilla.cfg'):
        config.read('bugzilla.cfg')
    else:
        return

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
    group.addoption('--bugzilla-project-version',
                    action='store',
                    dest='bugzilla_version',
                    default=config.get('DEFAULT', 'bugzilla_version'),
                    metavar='version',
                    help='Overrides the project version in bugzilla.cfg.')


def pytest_configure(config):
    """
    If bugzilla is neabled, setup a session
    with bugzilla_url.

    :param config: configuration object
    """
    if config.getvalue("bugzilla") and all([config.getvalue('bugzilla_url'),
                                            config.getvalue('bugzilla_username'),
                                            config.getvalue('bugzilla_password'),
                                            config.getvalue('bugzilla_version')]):
        url = config.getvalue('bugzilla_url')
        user = config.getvalue('bugzilla_username')
        password = config.getvalue('bugzilla_password')
        version = config.getvalue('bugzilla_version')

        bz = bugzilla.Bugzilla(url=url, user=user, password=password)

        my = BugzillaHooks(config, bz, version)
        assert config.pluginmanager.register(my, "bugzilla_helper")
