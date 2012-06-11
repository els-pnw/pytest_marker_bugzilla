import pytest
import os

@pytest.mark.skip_selenium
@pytest.mark.nondestructive
class TestNothin(object):
    @pytest.mark.bugzilla('824975')
    def test_new_bz(self):
        print('hello')
        assert(os.path.exists('/etc'))
        
    @pytest.mark.bugzilla('12345')
    def test_closed_bz(self):
        assert(os.path.exists('/etc'))
           
    @pytest.mark.bugzilla('12345')
    def test_closed_bz_with_failure(self):
        assert(os.path.exists('/etcccc')) 
    
