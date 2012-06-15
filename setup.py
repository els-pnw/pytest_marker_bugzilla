from setuptools import setup

setup(
    name="pytest-marker-bugzilla",
    version="0.02",
    description='py.test bugzilla integration plugin, using markers',
    author='Eric Sammons',
    author_email='elsammons@gmail.com' ,
    url='https://github.com/eanxgeek/pytest_marker_bugzilla.git',
    py_modules=['pytest_marker_bugzilla',],
    license='GPL',
    entry_points={'pytest11': ['pytest_marker_bugzilla = pytest_marker_bugzilla']},
    install_requires = ['python-bugzilla', 'py>=1.4', 'pytest>=2.2.4']
    keywords='py.test pytest bugzilla',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'])
