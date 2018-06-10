#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os, sys

try:
    import simplejson as json
except:
    try:
        import json#analysis:ignore
    except:
        pass

IS_READTHEDOCS      = True

HAPPYGISCO          = 'happyGISCO'
HAPPYMODULES        = ['settings', 'tools', 'services', 'features'] 
DIRHAPPYGISCO       = '../'
try:
    assert not IS_READTHEDOCS
    DIRHAPPYGISCO   = os.path.abspath(DIRHAPPYGISCO)
except AssertionError:
    pass

DEF_METADATA        = {'project'     : HAPPYGISCO,
                       'description' : 'Simple API to Eurostat GISCO web-services',
                       'package'     : HAPPYGISCO.lower(),
                       'version'     : '1.0',
                       'date'        : '2018',
                       'author'      : 'J. Grazzini',
                       'contact'     : 'jacopo.grazzini@ec.europa.eu',
                       'license'     : 'European Union Public Licence (EUPL-1.2)',
                       'copyright'   : 'European Union',
                       'organisation': 'European Commission (EC - DG ESTAT)',
                       'url'         : 'https://github.com/eurostat/happyGISCO'
                       }
METADATA            = 'metadata.json' # 'metadata.py'
METADATA            = os.path.join(DIRHAPPYGISCO, METADATA)
    
this = os.path.dirname(os.path.abspath(__file__))

# import project metadata
try:    
    assert json and os.path.exists(METADATA) and os.path.isfile(METADATA)
except:
    # raise IOError('metadata file not loaded')
    metadata = {'project': HAPPYGISCO}
else:
    ## metadata = imp.load_source('metadata', file_metadata) 
    ## # for consistency when using keys [''] to retrieve the fields
    ## metadata = metadata.__dict__ 
    with open(METADATA,'r') as f:
        metadata = json.load(f) 

# -- Project information -----------------------------------------------------

# project = 'happyGISCO'
try:
    project         = metadata['project']
except KeyError: 
    try:
        project     = metadata['package'].upper()
    except KeyError: 
        raise IOError('project and package names not defined')
project             = project.strip()

# package = 'happygisco'
try:
    package         = metadata['package']
except KeyError:
    package         = project.lower()
package = "".join(package.split())

# at this stage, we can simplofy the search exercise...
#sys.path.insert(0, '.')
sys.path.insert(0, DIRHAPPYGISCO)
sys.path.insert(0, os.path.join(DIRHAPPYGISCO,package))
# sys.path.insert(0, os.path.abspath(os.path.join(DIRHAPPYGISCO,'../',project)))

# further integration with ReadTheDocs
# https://media.readthedocs.org/pdf/docs-python2readthedocs/master/docs-python2readthedocs.pdf
try:
    assert False and IS_READTHEDOCS # bug in ReadTheDocs?
    import mock
except AssertionError:
    pass
except ImportError:
    # raise IOError('environment not set to mock {package} modules' package)
    pass
else:
    MOCK_MODULES = [package, ] + [package + '.' + m for m in HAPPYMODULES]
    for m in MOCK_MODULES:  sys.modules[m] = mock.Mock()

# spoiler: we cheat here!!! we load the package so that automodule actually works
try:
    assert not IS_READTHEDOCS
    ## deprecated: import importlib
    ## deprecated: imp.load_module(package, *imp.find_module(package, path=[DIRHAPPYGISCO,]))#analysis:ignore
    import importlib
    # importlib.find_loader(DIRHAPPYGISCO)
    __package = importlib.import_module(package)#analysis:ignore
    #    [importlib.import_module(m, package=package) for m in __package.__all__] 
    # or [___________________________________________ for m in HAPPYMODULES]
except AssertionError:
    # cheating again...
    metadata.update(DEF_METADATA)
except ImportError:
    # raise IOError('environment not set to import {package} - short doc only' % package)
    pass
else:
    try:
        assert 'package' in metadata
    except AssertionError: 
        metadata.update(getattr(__package,'metadata'))

# author
author              = str(metadata.get('author',''))

# copyright
copyright           = ''
try:
    assert False
    copyright       = metadata['copyright']
except (AssertionError,KeyError):
    try:
        copyright   = metadata['date']
    except KeyError:
        pass
    else:
        copyright   += ', '
    try:
        assert True
        copyright   += author 
    except AssertionError:
        pass
    else:
        copyright   += ', '      
    try:    
        copyright   += metadata['organisation']
    except KeyError:
        pass 
    if copyright != '':
        copyright       += ' -- ' 
    try:    
        copyright   += 'Licensed under ' + metadata['license']
    except KeyError:
        pass 
copyright           = str(copyright.strip())

# description
description         = metadata.get('description','')
    
# the short X.Y version
try:
    version         = metadata['version']
except:
    version         = '1.0'

# the full version, including alpha/beta/rc tags
try:
    release         = metadata['release']
except:
    release         = version

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx      = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# sys.path.append(os.path.abspath('sphinxext'))

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions          = ['sphinx.ext.autodoc',
                       'sphinx.ext.autosummary', 
                       'sphinx.ext.doctest',
                       'sphinx.ext.intersphinx',
                       'sphinx.ext.todo',
                       'sphinx.ext.coverage',
                       'sphinx.ext.mathjax',
                       #'sphinx.ext.imgmath',
                       'sphinx.ext.ifconfig',
                       'sphinx.ext.viewcode',
                       'sphinx.ext.githubpages',
                       'sphinx.ext.napoleon',
                       # 'sphinxjp.themes.basicstrap' # not supported by readthedocs
                       ]

# Napoleon settings
napoleon_numpy_docstring = True
#napoleon_google_docstring = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar   = False
napoleon_use_param  = True
napoleon_use_rtype  = False

# Add any paths that contain templates here, relative to this directory.
templates_path      = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix         = ['.rst', '.md']
source_suffix       = '.rst'

# The master toctree document.
master_doc          = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language            = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns    = ['_build', 'Thumbs.db', '.DS_Store', '__pycache__']

# The default language to highlight source code in. 
highlight_language  = 'python3' 

# The name of the Pygments (syntax highlighting) style to use.
pygments_style      = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
## basicstrap - https://pythonhosted.org/sphinxjp.themes.basicstrap/index.html
#html_theme          = 'basicstrap'
## default
# html_theme          = 'default'
## nature
#html_theme = 'nature'
##'alabaster'
#html_theme = 'alabaster'
## ReadTheDocs special theme
html_theme          = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
if html_theme == 'basicstrap':
    html_theme_options = {
        'header_inverse': True,
        'relbar_inverse': True,
        'inner_theme': True,
        'inner_theme_name': 'bootswatch-cosmo',
    }    
elif html_theme == 'sphinx_rtd_theme':
    html_theme_options = {
        'logo_only': False,
        'display_version': True,
        'prev_next_buttons_location': 'bottom',
        'style_external_links': False,
        'collapse_navigation': True,
        'sticky_navigation': True,
        'navigation_depth': 2,
        'includehidden': True,
        'titles_only': False
    }
else:
    html_theme_options = {}
    
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path    = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html']``.
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html'],
}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = True

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Extra local configuration. This is useful for placing the class description
# in the class docstring and the __init__ parameter documentation in the
# __init__ docstring. See
# <http://sphinx-doc.org/ext/autodoc.html#confval-autoclass_content> for more
# information.
autoclass_content = 'both'

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project + 'doc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  (master_doc, project + '.tex', project +' Documentation', author, 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, project, project +' Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, project, project +' Documentation',
     author, 'project', description,
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/3': None}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
