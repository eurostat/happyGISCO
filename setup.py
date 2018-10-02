#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**References**

https://packaging.python.org/tutorials/packaging-projects/
https://packaging.python.org/specifications/core-metadata/
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://docs.python.org/3/distutils/sourcedist.html
https://docs.python.org/3/distutils/setupscript.html
https://jonemo.github.io/neubertify/2017/09/13/publishing-your-first-pypi-package/
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Tue Oct  2 00:02:47 2018

#==============================================================================
# GENERAL SETUP
#==============================================================================

from __future__ import print_function#analysis:ignore

import os, imp
# from io import open

try:
    import setuptools#analysis:ignore
except ImportError:
    from distutils.core import setup
    from mypackage import walk_packages
    def find_packages(adir, prefix=""):
        yield prefix
        prefix = prefix + "."
        for _, name, ispkg in walk_packages(adir, prefix):
            if ispkg:
                yield name
else:
    from setuptools import setup, find_packages, find_namespace_packages#analysis:ignore
    # from setuptools.command.test import test as TestCommand

#try:
#    eval('import ' + metadata.package)
#except:
#    print("Installing {project}.".format(project=metadata.project))
#
## Add the current directory to the module search path.
#sys.path.append('.')

#==============================================================================
# RELATIVE DEFINITIONS
#==============================================================================


# Import metadata: load the metadata module by path, effectively side-stepping
# any dependency problem (avoid importing names from some other modules where
# these modules have third-party dependencies that need being installed...)
try:
    here = os.path.abspath(os.path.dirname(__file__))
    projdir = os.path.dirname(os.path.abspath(__file__))
    metadata = imp.load_source('metadata', os.path.join(projdir, 'metadata.py'))
except:
    projdir = os.path.abspath('.')
    metadata = {'project'     : 'happyGISCO',
                'package'     : 'happygisco'
                }                                                       
else:
    metadata = metadata.metadata                            

DOCDIR              = 'docs'
NBKDIR              = 'notebooks'
DATADIR             = 'data'

## other directories
PACKAGES            = find_packages(where=projdir) # find_packages(where=projdir, exclude=(TESTDIR,))
# PACKAGES            = happygisco.__all__
PACKAGE_DIR         = {'': metadata.project}
PACKAGE_DATA        = {'': [os.path.join(DATADIR,'*.geojson')]}
DATA_FILES          = [(DATADIR,''), (NBKDIR,'')]
#DATA_FILES          = [('', ['happyGISCO.conf', 'happyGISCO.conf']),
#                       ('', ['README.md', 'README.md']),
#                       ('', ['VERSION', 'VERSION'])],      

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
# https://setuptools.readthedocs.io/en/latest/setuptools.html
# <https://docs.python.org/3/distutils/setupscript.html>
# <http://pythonhosted.org/setuptools/setuptools.html>
# <https://pythonhosted.org/an_example_pypi_project/setuptools.html>

__setup_kwargs = dict(
    # string corresponding to a version specifier (as defined in PEP 440) for the Python version
    # python_requires = '3',
    
    # this is the name of the (registered) project; it will determine how
    # users can install the project, e.g.:
    #       >>> pip install happyGISCO
    # see: https://packaging.python.org/specifications/core-metadata/#name
    name            = metadata.project, # metadata.package
    
    # versions should comply with PEP 440 (https://www.python.org/dev/peps/pep-0440/)
    # see https://packaging.python.org/en/latest/single_source_version.html
    version         = metadata.get('version',''), # get_version(), 
    
    # authors which owns the project
    author          = metadata.get('author',''),
    author_email    = metadata.get('contact',''),    
    ## maintainer      = metadata.get('author',''),
    ## maintainer_email=metadata.__contact__,
    
    # see: https://packaging.python.org/specifications/core-metadata/#license
    license         = metadata.get('license',''),

    # this is a valid link to the project's main homepage
    # see: https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url             = metadata.get('url',''),
    
    # list additional URLs that are relevant to the project as a dict
    # see: https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    project_urls={  
        'Bug Reports': '%s/issues' % metadata.get('url',''),
        'Source Code': metadata.get('url',''),
        "Documentation": 'http://%s.readthedocs.io' % metadata.package
    },

    # this is a one-line description or tagline of what your project does
    # see: https://packaging.python.org/specifications/core-metadata/#summary
    description     = metadata.get('description',''),

    # this is an optional longer description of the project that represents the body 
    # of text which users will see when they visit PyPI.
    # see: https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description = open(os.path.join(os.path.dirname(__file__),'README.rst'), encoding='utf-8').read(),
    
    # denote that the long_description is in Markdown; valid values are
    # text/plain, text/x-rst, and text/markdown
    # see: https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
    long_description_content_type='text/markdown',  

    # classifiers help users find the project by categorizing it.
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 1 - Planning',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends  ',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    ## package_dir     = PACKDIR, 

    #py_modules      = [os.path.splitext(os.path.basename(i))[0]             \
    #    for i in glob.glob("{src}/*.py".format(src=metadata.package))],
    packages        = PACKAGES, 
    
    ## # if there are data files included in the package that need to be
    ## # installed, they will be specified here.
    ## package_data    = PACKAGE_DATA,
    
    ## include_package_data=True,
    ## package_data    = {'': ["ez_setup.py", '*.conf']},
    
    ## # although 'package_data' is the preferred approach, we may need to place data 
    ## # files outside of the package
    ## # see: http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    ## data_files      = DATA_FILES,

    # this field lists other packages that your project depends on to run.
    # Any package put here will be installed by pip when the project is installed, 
    # so they must be valid existing projects.
    # For an analysis of "install_requires" vs pip's requirements files, see:
    # https://packaging.python.org/en/latest/requirements.html    
    requires        = REQUIRES,
    install_requires = INSTALL_REQUIRES,
    
    ## # list additional groups of dependencies here (e.g. development dependencies)
    ## # Users will be able to install these using the "extras" syntax, for example:
    ## #       >>> pip install happyGISCO[dev]
    ## # similar to `install_requires` above, these must be valid existing projects.
    ## extras_require={  # Optional
    ##         'dev': ['check-manifest'],
    ##         'test': ['pytest==2.5.1', 'mock==1.0.1', 'flake8==2.1.0'],
    ##     },
    
    ## # string naming a unittest.TestCase subclass (or a package or module containing 
    ## # one or more of them, or a method of such a subclass), or naming a function that 
    ## # can be called with no arguments and returns a unittest.TestSuite. If the named 
    ## # suite is a module, and the module has an additional_tests() function, it is 
    ## # called and the results are added to the tests to be run. If the named suite is 
    ## # a package, any submodules and subpackages are recursively added to the overall 
    ## # test suite.
    ## test_suite =
    ## # allow tests to be run with `python setup.py test'.
    ## tests_require=[
    ##     'pytest==2.5.1',
    ##     'mock==1.0.1',
    ##     'flake8==2.1.0',
    ## ],
    
    ## cmdclass={'test': TestAllCommand},
    
    zip_safe=False,  # don't use eggs
    
    # this field adds keywords for your project which will appear on the project
    # page. What does your project relate to?
    keywords=["Eurostat",
              "GISCO"
              ],
              
    ## # to provide executable scripts, use entry points in preference to the
    ## # "scripts" keyword. Entry points provide cross-platform support and allow
    ## # `pip` to create the appropriate form of executable for the target
    ## # platform.
    entry_points={
        # 'console_scripts': [
        #     'happyGISCO_cli = happyGISCO.main:entry_point'
        # ],
        # if you have a gui, use this
        # 'gui_scripts': [
        #     'happyGISCO_gui = happyGISCO.gui:entry_point'
        # ]
    },
    
    platforms       = ('Windows', 'Mac OS', 'Linux')
)

#/****************************************************************************/
def __setup():
    #setup(name              = 'happyGISCO',
    #      packages          = find_packages()
    #      )
    setup(**__setup_kwargs)

#/****************************************************************************/
if __name__ == '__main__':
    __setup()
    
