from setuptools import setup

setup(
    name="pytest-marker-bugzilla",
    version="0.05",
    description='py.test bugzilla integration plugin, using markers',
    long_description=open('README.txt').read(),
    license='GPL',
    author='Eric Sammons',
    author_email='elsammons@gmail.com' ,
    url='http://github.com/eanxgeek/pytest_marker_bugzilla',
    platforms=['linux', 'osx', 'win32'],
    py_modules=['pytest_marker_bugzilla'],
    entry_points = {'pytest11': ['pytest_marker_bugzilla = pytest_marker_bugzilla'],},
    zip_safe=False,
    install_requires = ['python-bugzilla>=0.6.2','pytest>=2.2.4'],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Utilities',
    'Programming Language :: Python',
    ],
)
