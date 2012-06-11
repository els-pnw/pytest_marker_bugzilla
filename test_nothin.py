import pytest
import os

@pytest.mark.nondestructive
@pytest.mark.skip_selenium
@pytest.mark.bugzilla('12345')
def test_nothin():
    assert(os.path.exists('/etc'))
