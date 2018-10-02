#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**References**

https://packaging.python.org/tutorials/packaging-projects/
https://jonemo.github.io/neubertify/2017/09/13/publishing-your-first-pypi-package/
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Tue Oct  2 00:02:47 2018

from __future__ import print_function#analysis:ignore

import os, imp

#==============================================================================
# GENERAL SETUP
#==============================================================================

# Import metadata: load the metadata module by path, effectively side-stepping
# any dependency problem (avoid importing names from some other modules where
# these modules have third-party dependencies that need being installed...)
try:
    projdir = os.path.dirname(os.path.abspath(__file__))
    metadata = imp.load_source('metadata', os.path.join(projdir, 'metadata.py'))
except:
    projdir = os.path.abspath('.')
    metadata = {'project'     : 'happyGISCO',
                'package'     : 'happygisco'
                }                                                       
else:
    metadata = metadata.metadata                            

#try:
#    eval('import ' + metadata.package)
#except:
#    print("Installing {project}.".format(project=metadata.project))
#
## Add the current directory to the module search path.
#sys.path.append('.')

try:
    import setuptools#analysis:ignore
except ImportError:
    from distutils.core import setup
    from mypackage import walk_packages
    # path = metadata.__pkgdir__ or os.path.dirname(SRCDIR)
    def find_packages(adir, prefix=""):
        yield prefix
        prefix = prefix + "."
        for _, name, ispkg in walk_packages(os.path.join(projdir, adir), prefix):
            if ispkg:
                yield name
else:
    from setuptools import setup, find_packages
    # from setuptools.command.test import test as TestCommand

## other directories
PACKAGES            = find_packages(metadata.package) # find_packages(exclude=(TESTS_DIRECTORY,))
PACKDIR             = {'': metadata.package}

DOCDIR              = 'docs'
TESTDIR             = 'tests'
NBKDIR              = 'notebooks'

# requirements
REQUIRES            = []

# define install_requires for specific Python versions
PYTHON_VERSION_INSTALL_REQUIRES = []
INSTALL_REQUIRES = ['setuptools>2.0', 'uuid', 'threadpool', 'virtualenv'] \
                    + PYTHON_VERSION_INSTALL_REQUIRES

VERSION_FILE    = "VERSION"
    
# test flags
PYTEST_FLAGS    = ['--doctest-modules']

#/****************************************************************************/

# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>
__setup_kwargs = dict(
    name            = metadata.package, # metadata.project
    version         = metadata.get('version',''), # get_version(), 
    author          = metadata.get('author',''),
    author_email    = metadata.get('contact',''),
    ## maintainer      = metadata.__author__,
    ## maintainer_email=metadata.__contact__,
    license         = metadata.get('license',''),
    url             = metadata.get('url',''),
    description     = metadata.get('description',''),
    ## long_description = read('readme.rst'),
    long_description = open(os.path.join(os.path.dirname(__file__),'README.rst')).read(),
    # list of classifiers: <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    classifiers=[
        'Development Status :: 1 - Planning',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    package_dir     = PACKDIR, # metadata.__package__
    packages        = PACKAGES, # find_packages()
    #py_modules      = [os.path.splitext(os.path.basename(i))[0]             \
    #    for i in glob.glob("{src}/*.py".format(src=metadata.package))],
    requires        = REQUIRES,
    install_requires = INSTALL_REQUIRES,
    ## # Allow tests to be run with `python setup.py test'.
    ## tests_require=[
    ##     'pytest==2.5.1',
    ##     'mock==1.0.1',
    ##     'flake8==2.1.0',
    ## ],
    ## cmdclass={'test': TestAllCommand},
    zip_safe=False,  # don't use eggs
    ## # data files for easy_install
    ## data_files      = [('', ['happyGISCO.conf', 'happyGISCO.conf']),
    ##                    ('', ['README.md', 'README.md']),
    ##                    ('', ['VERSION', 'VERSION'])],      
    keywords=["Eurostat",
              "GISCO"
              ],
    entry_points={
        # 'console_scripts': [
        #     'happyGISCO_cli = happyGISCO.main:entry_point'
        # ],
        # if you have a gui, use this
        # 'gui_scripts': [
        #     'happyGISCO_gui = happyGISCO.gui:entry_point'
        # ]
    },
    ## # data files for pip
    ## include_package_data=True,
    ## package_data    = {'': ["ez_setup.py", '*.conf']},
    platforms       = ('Windows', 'Mac OS', 'Linux')
)

#/****************************************************************************/
def __setup():
    setup(**__setup_kwargs)
    #setup(name              = 'happyGISCO',
    #      packages          = find_packages()
    #      )

#/****************************************************************************/
if __name__ == '__main__':
    __setup()
    
