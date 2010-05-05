# pytest_bugzilla is a py.test plugin to integrate it with Bugzilla
# Copyright (C) <2010> <Noufal Ibrahim>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
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
just invoke ``py.test`` as usual. The plugin is activated by default.

To disable it (eg. if your bugzilla installation is slow), you can use
the --buzilla-disable command line option

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

You can change the bugzilla server URL/username/password using command
line options. You can edit the plugin file to change the defaults so
that they work without having to pass these options explicitly.
"""


import re
import xmlrpclib

import pyzilla

class BugZillaInteg(object):
    def get_bug_status(self, bugid):
        "Returns the status of the bug with id bugid"
        try:
            bug = self.bugzilla.Bug.get(dict(ids = [int(bugid)]))
            return bug['bugs'][0]['internals']['bug_status']
        except xmlrpclib.Fault, m:
            print "Fault received '%s'"% m
            return "Error"

    def analysed(self, infostr):
        "Returns True if bug mentioned in the given docstring exists and is open"
        if infostr:
            val = re.search("#([0-9]*)", infostr)
            if val:
                bugid = val.groups()[0]
                status = self.get_bug_status(bugid)
                if status in ["ASSIGNED", "NEW"]:
                    return True
                else:
                    pass
                    #print "Bug exists but is in the '%s' state"% status
        return False

    def pytest_report_teststatus(self,report):
        if not self.config.getvalue("bugzilla_disable") and report.failed:
            if self.analysed(report.item.function.__doc__):
                return "analysed", "A", "ANALYSED"

    def __init__(self, config, bugzilla):
        self.config = config
        self.bugzilla = bugzilla

def pytest_addoption(parser):
    group = parser.getgroup('Bugzilla integration')
    group.addoption('--bugzilla-disable', action='store_true', default=False,
                    dest='bugzilla_disable',
                    help="Don't query bugzilla to find analysed bugs")
    group.addoption("--bugzilla-username", action="store", default = "username",
                    dest = "bugzilla_username",
                    help="Use this username for bugzilla queries")
    group.addoption("--bugzilla-password", action="store", default = "password",
                    dest = "bugzilla_pw",
                    help="Use this password for bugzilla queries")
    group.addoption("--bugzilla-url", action="store", default = "https://bugzilla.example.com/xmlrpc.cgi",
                    dest = "bugzilla_url",
                    help="Use this url for bugzilla XML-RPC server")
    group.addoption("--bugzilla-verbose", action="store_true", default = False,
                    dest = "bugzilla_verbose",
                    help="Enable debugging output for bugzilla plugin (don't use except during plugin development)")
    
def pytest_configure(config):
    bugzilla_disable =  config.getvalue("bugzilla_disable")
    if not bugzilla_disable:
        bzilla = pyzilla.BugZilla(config.getvalue("bugzilla_url"), config.getvalue("bugzilla_verbose"))
        bzilla.login (username = config.getvalue("bugzilla_username"),
                      password = config.getvalue("bugzilla_pw"))
        config.pluginmanager.register(BugZillaInteg(config, bzilla), "bugzilla")
    
        
        
    
    
