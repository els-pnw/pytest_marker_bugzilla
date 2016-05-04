import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        self.test_args = "-s tests/"

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded elsewhere
        import pytest
        print "Running: pytest %s" % self.test_args
        sys.path.insert(0, 'lib')
        pytest.main(self.test_args)

os.environ['SKIP_GENERATE_AUTHORS'] = '1'


if __name__ == "__main__":
    setup(
        setup_requires=['pbr'],
        pbr=True,
        cmdclass={'test': PyTest, },
    )
