# -*- coding: utf-8 -*-
import six
import bugzilla
import inspect
import os
import pytest
import re
import logging
from distutils.version import LooseVersion
from functools import wraps
"""This plugin integrates pytest with bugzilla

It allows the tester to mark a test with a bug id. The test will be skipped
until the bug status is no longer NEW, ON_DEV, or ASSIGNED.

You must set the url either at the command line or in bugzilla.cfg.

An update to this plugin brings new possibilities. You can now add multiple
bugs to one test:

    @pytest.mark.bugzilla(1234, 2345, "3456")
    def test_something():
        pass

In order to skip the test, all of the specified bugs must lead to skipping.
Even just one unskipped means that the test will not be skipped.

You can also add "conditional guards", which will xfail or skip the test when
condition is met:

    @pytest.mark.bugzilla(1234, skip_when=lambda bug: bug.status == "POST")
    or
    @pytest.mark.bugzilla(
        567, xfail_when=lambda bug, version: bug.fixed_in > version
    )

The guard is a function, it will receive max. 2 parameters. It depends what
parameters you specify.
The parameters are:

    `bug` which points to a specific BZ bug
    `version` which is tested product version.

Order or presence does not matter.

In additional to the original parameters of this marker you can use:

    --bugzilla-looseversion-fields

It accepts a string of field names comma separated. The specified fields have
getter function which returns instance of LooseVersion instead of string
allows you easy comparison in condition guards or inside tests.

    --bugzilla-looseversion-fields=fixed_in,target_release

Authors:
    Eric L. Sammons
    Milan Falešník
"""
logger = logging.getLogger(__name__)
_bugs_pool = {}  # Cache bugs for greater speed
_default_looseversion_fields = "fixed_in,target_release"


def get_value_from_config_parser(parser, option, default=None):
    """Wrapper around ConfigParser to do not fail on missing options."""
    value = parser.defaults().get(option, default)
    if value is not None and isinstance(value, six.string_types):
        value = value.strip()
        if not value:
            value = default
    return value


def kwargify(f):
    """Convert function having only positional args to a function taking
    dictionary."""
    @wraps(f)
    def wrapped(**kwargs):
        args = []
        for arg in inspect.getargspec(f).args:
            if arg not in kwargs:
                raise TypeError(
                    "Required parameter {0} not found in the "
                    "context!".format(arg)
                )
            args.append(kwargs[arg])
        return f(*args)
    return wrapped


class BugWrapper(object):
    def __init__(self, bug, loose):
        self._bug = bug
        # We need to generate looseversions for simple comparison of the
        # version params.
        for loose_version_param in loose:
            param = getattr(bug, loose_version_param, "")
            if param is None:
                param = ""
            if not isinstance(param, six.string_types):
                param = str(param)
            setattr(
                self,
                loose_version_param,
                LooseVersion(re.sub(r"^[^0-9]+", "", param))
            )

    def __getattr__(self, attr):
        """Relay the query to the bug object if we did not override."""
        return getattr(self._bug, attr)


class BugzillaBugs(object):
    def __init__(self, bugzilla, loose, *bug_ids):
        self.bugzilla = bugzilla
        self.bug_ids = bug_ids
        self.loose = loose

    @property
    def bugs_gen(self):
        for bug_id in self.bug_ids:
            if bug_id not in _bugs_pool:
                bug = BugWrapper(self.bugzilla.getbug(bug_id), self.loose)
                _bugs_pool[bug_id] = bug
            yield _bugs_pool[bug_id]

    def bug(self, id):
        """Returns Bugzilla's Bug object for given ID"""
        id = int(id)
        if id not in self.bug_ids:
            raise ValueError("Could not find bug with id {0}".format(id))

        if id in _bugs_pool:
            return _bugs_pool[id]

        bug = BugWrapper(self.bugzilla.getbug(id), self.loose)
        _bugs_pool[id] = bug
        return bug


class BugzillaHooks(object):
    def __init__(self, config, bugzilla, loose, version="0"):
        self.config = config
        self.bugzilla = bugzilla
        self.version = version
        self.loose = loose

    def add_bug_to_cache(self, bug_obj):
        """For test purposes only"""
        _bugs_pool[str(bug_obj.id)] = BugWrapper(bug_obj, self.loose)

    def _should_skip_due_to_api(self, item, engines):

        if not engines:
            return True

        return item.parent.obj.api in engines

    def _should_skip_due_to_storage(self, item, storages):

        if not storages:
            return True

        if "storage" in item.fixturenames and hasattr(item, "callspec"):
            parametrized_params = getattr(item.callspec, "params", {})
            parametrized_storage = parametrized_params.get("storage")
            if parametrized_storage:
                for storage in storages:
                    if storage in parametrized_storage:
                        return True
            return False
        else:
            return item.parent.obj.storage in storages

    def _should_skip_due_to_ppc(self, item, is_ppc):
        return is_ppc is None or is_ppc is True

    def _should_skip(self, item, bz_mark):

        is_ppc_affected = self._should_skip_due_to_ppc(
                item, bz_mark.get('ppc')
        )

        is_api_affected = self._should_skip_due_to_api(
            item, bz_mark.get('engine')
        )

        is_storage_affected = self._should_skip_due_to_storage(
            item, bz_mark.get('storage')
        )

        if is_api_affected and is_storage_affected and is_ppc_affected:
            return True

        return False

    def pytest_runtest_setup(self, item):
        """
        Run test setup.
        :param item: test being run.
        """

        if "bugzilla" not in item.keywords:
            return

        bugs_in_cache = item.funcargs["bugs_in_cache"]
        bugzilla_marker_related_to_case = item.get_closest_marker(name='bugzilla')
        xfail = kwargify(
            bugzilla_marker_related_to_case.kwargs.get(
                "xfail_when", lambda: False
            )
        )
        if xfail:
            xfailed = self.evaluate_xfail(xfail, bugs_in_cache)
            if xfailed:
                url = "{0}?id=".format(
                    self.bugzilla.url.replace("xmlrpc.cgi", "show_bug.cgi"),
                )
                item.add_marker(
                    pytest.mark.xfail(
                        reason="xfailing due to bugs: {0}".format(
                            ", ".join(
                                map(
                                    lambda bug: "{0}{1}".format(
                                        url, str(bug.id)
                                    ),
                                    xfailed)
                            )
                        )
                    )
                )
                return

        skip = kwargify(
            bugzilla_marker_related_to_case.kwargs.get(
                "skip_when", lambda: False
            )
        )
        if skip:
            self.evaluate_skip(skip, bugs_in_cache)

        bugs_related_to_case = bugzilla_marker_related_to_case.args[0]
        bugs_objs = []

        for bug_id in bugs_related_to_case.keys():
            bugs_objs.append(bugs_in_cache[bug_id])

        skippers = []

        for bz in bugs_objs:
            for bug in bz.bugs_gen:
                if bug.status == "CLOSED":
                    logger.info(
                        "Id:{0}; Status:{1}; Resolution:{2}; [RUNNING]".format(
                            bug.id, bug.status, bug.resolution
                        )
                    )
                elif bug.status in ["VERIFIED", "ON_QA"]:
                    logger.info(
                        "Id: {0}; Status: {1}; [RUNNING]".format(
                            bug.id, bug.status
                        )
                    )
                elif self._should_skip(
                        item, bugs_related_to_case[str(bug.id)]
                ):
                    skippers.append(bug)
                    logger.info(
                        "Id: {0}; Status: {1}; [SKIPPING]".format(
                            bug.id, bug.status
                        )
                    )

        url = "{0}?id=".format(
            self.bugzilla.url.replace("xmlrpc.cgi", "show_bug.cgi"),
        )

        if skippers:
            skipping_summary = (
                "Skipping due to: "
                "\n".join(
                    [
                        "Bug summary: {0} Status: {1} URL: {2}{3}".format(
                            bug.summary, bug.status, url, bug.id
                        )
                        for bug in skippers
                    ]
                )
            )

            logger.info(
                "Test case {0} will be skipped due to:\n {1}".format(
                    item.name, skipping_summary
                )
            )

            pytest.skip(skipping_summary)

    def evaluate_skip(self, skip, bugs):
        bugs_obj = bugs.values()

        for bug_obj in bugs_obj:
            for bz in bug_obj.bugs_gen:
                context = {"bug": bz}
                if self.version:
                    context["version"] = LooseVersion(self.version)
                if skip(**context):
                    pytest.skip(
                        "Skipped due to a given condition: {0}".format(
                            inspect.getsource(skip)
                        )
                    )

    def evaluate_xfail(self, xfail, bugs):
        results = []

        # for bug in bugs.bugs_gen:
        bugs_obj = bugs.values()

        for bug_obj in bugs_obj:
            for bz in bug_obj.bugs_gen:
                context = {"bug": bz}
                if self.version:
                    context["version"] = LooseVersion(self.version)
                if xfail(**context):
                    results.append(bz)
        return results

    def pytest_collection_modifyitems(self, session, config, items):
        reporter = config.pluginmanager.getplugin("terminalreporter")
        # When run as xdist slave you don't have access to reporter
        if reporter:
            reporter.write("Checking for bugzilla-related tests\n", bold=True)
        cache = {}
        for item in items:
            for marker in item.iter_markers(name='bugzilla'):
                bugs = marker.args[0]
                bugs_ids = bugs.keys()

                for bz_id in bugs_ids:
                    if bz_id not in cache:
                        if reporter:
                            reporter.write(".")
                        cache[bz_id] = BugzillaBugs(
                            self.bugzilla, self.loose, bz_id
                        )

                item.funcargs["bugs_in_cache"] = cache

        if reporter:
            reporter.write(
                "\nChecking for bugzilla-related tests has finished\n",
                bold=True,
            )
            reporter.write(
                "{0} bug marker sets found.\n".format(len(cache)), bold=True,
            )


def pytest_addoption(parser):
    """
    Add a options section to py.test --help for bugzilla integration.
    Parse configuration file, bugzilla.cfg and / or the command line options
    passed.

    :param parser: Command line options.
    """
    config = six.moves.configparser.ConfigParser()
    config.read(
        [
            '/etc/bugzilla.cfg',
            os.path.expanduser('~/bugzilla.cfg'),
            'bugzilla.cfg',
        ]
    )

    group = parser.getgroup('Bugzilla integration')
    group.addoption(
        '--bugzilla',
        action='store_true',
        default=False,
        dest='bugzilla',
        help='Enable Bugzilla support.',
    )
    group.addoption(
        '--bugzilla-url',
        action='store',
        dest='bugzilla_url',
        default=get_value_from_config_parser(config, 'bugzilla_url'),
        metavar='url',
        help='Overrides the xmlrpc url for bugzilla found in bugzilla.cfg.',
    )
    group.addoption(
        '--bugzilla-user',
        action='store',
        dest='bugzilla_username',
        default=get_value_from_config_parser(config, 'bugzilla_username', ''),
        metavar='username',
        help='Overrides the bugzilla username in bugzilla.cfg.',
    )
    group.addoption(
        '--bugzilla-password',
        action='store',
        dest='bugzilla_password',
        default=get_value_from_config_parser(config, 'bugzilla_password', ''),
        metavar='password',
        help='Overrides the bugzilla password in bugzilla.cfg.',
    )
    group.addoption(
        '--bugzilla-project-version',
        action='store',
        dest='bugzilla_version',
        default=get_value_from_config_parser(config, 'bugzilla_version'),
        metavar='version',
        help='Overrides the project version in bugzilla.cfg.',
    )
    group.addoption(
        '--bugzilla-looseversion-fields',
        action='store',
        dest='bugzilla_loose',
        default=get_value_from_config_parser(
            config, 'bugzilla_loose', _default_looseversion_fields,
        ),
        metavar='loose',
        help='Overrides the project loose in bugzilla.cfg.',
    )


def pytest_configure(config):
    """
    If bugzilla is neabled, setup a session
    with bugzilla_url.

    :param config: configuration object
    """

    config.addinivalue_line(
        "markers",
        "bugzilla(*bug_ids, **guards): Bugzilla integration",
    )
    if config.getvalue("bugzilla") and config.getvalue('bugzilla_url'):
        url = config.getvalue('bugzilla_url')
        user = config.getvalue('bugzilla_username')
        password = config.getvalue('bugzilla_password')
        version = config.getvalue('bugzilla_version')
        loose = [
            x.strip()
            for x in config.getvalue('bugzilla_loose').strip().split(",", 1)
        ]
        if len(loose) == 1 and not loose[0]:
            loose = []

        bz = bugzilla.Bugzilla(url=url, user=user, password=password)

        my = BugzillaHooks(config, bz, loose, version)
        assert config.pluginmanager.register(my, "bugzilla_helper")
