PyTest plugin for bugzilla integration.
	
	* http://pytest.org/latest/

# Requires
  * pytest >= 2.2.3
  * python-bugzilla >= 0.6.2
  
# How To Use
  1. Create a bugzilla.cfg in the root of your tests
     ``[DEFAULT]
       bugzilla_url = https://bugzilla.fqdn/xmlrpc.cgi
       bugzilla_username = USERNAME (or blank for public bugs)
       bugzilla_password = PASSWORD (or blank for public bugs)
       ``
     Options can be overridden with command line options.
     ``py.test --help``
  2. Mark your tests with bugzilla marker and bug id.
     ``@pytest.mark.bugzilla('bug_id')``
  3. Run py.test with bugzilla option to enable the plugin.
     ``py.test --bugzilla``