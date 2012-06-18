Intro
=====
[pytest] plugin for bugzilla integration.  This plugin currently assumes the
following workflow:

bug_status in ['NEW', 'ASSIGNED', 'ON_DEV'] means the bug is known and is being worked
on and therefore the test should be skipped and will be.

bug_status not in ['NEW', 'ASSIGNED', 'ON_DEV'] means the bug is in a state ready 
for QE and the test will be run and reported on.

Please feel free to contribute by forking and submitting pull requests or by submitting
feature requests or issues to [githubissues]

Requires
========
  * pytest >= 2.2.3
  * python-bugzilla >= 0.6.2
 
Installation
============
  pip-python install pytest_marker_bugzilla
    
Usage
=====
  1. Create a bugzilla.cfg in the root of your tests
  
         [DEFAULT]  
         bugzilla_url = https://bugzilla.fqdn/xmlrpc.cgi  
         bugzilla_username = USERNAME (or blank for public bugs)  
         bugzilla_password = PASSWORD (or blank for public bugs)  
             
     Options can be overridden with command line options.
     
       py.test --help
     
  2. Mark your tests with bugzilla marker and bug id.
  
     @pytest.mark.bugzilla('bug_id')
     
  3. Run py.test with bugzilla option to enable the plugin.  
  
       py.test --bugzilla   
     
[pytest]: http://pytest.org/latest/
[githubissues]: https://github.com/eanxgeek/pytest_marker_bugzilla/issues
