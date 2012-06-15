from setuptools import setup

setup(
    name="pytest-marker-bugzilla",
    version="0.01",
    description='py.test bugzilla integration plugin, using markers',
    long_description=open('README.md').read(),
    license='GPL',
    author='Eric Sammons',
    author_email='elsammons@gmail.com' ,
    py_modules=['pytest_marker_bugzilla',],
    )
