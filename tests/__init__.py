#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_tests__init__

Testing units for :mod:`happygisco` API to Eurostat GISCO web-services.

**Description**

Utility functions for :mod:`happygisco` unit test module.

**Usage**

    >>> from happygisco import tests
    
**Dependencies**

*call*:         :mod:`happygisco`
    
*require*:      :mod:`unittest`, :mod:`os`, :mod:`sys`, :mod:`re`, :mod:`warnings`, 
                :mod:`datetime`    
"""

__all__ = ['settings', 'services', 'entities']#analysis:ignore

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Fri Apr  6 11:27:15 2018

#==============================================================================
# PROGRAM METADATA
#==============================================================================

from happygisco.__metadata__ import metadata as __metadata__
metadata = __metadata__.copy()
# metadata.update({'date': 'Fri Apr  6 11:27:15 2018'})

#==============================================================================
# IMPORT STATEMENTS
#==============================================================================

import os, sys #analysis:ignore
import unittest
import re#analysis:ignore
import datetime, time#analysis:ignore

#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

assert metadata.project == 'happyGISCO' and metadata.package == 'happygisco'

#==============================================================================
# METHODS
#==============================================================================

#/****************************************************************************/
def __runonetest(testCase, **kwargs):
    try:
        t_class = testCase.__name__
        t_module = testCase.__module__
    except: raise IOError('unexpected input testing class entity')
    else:
        t_module_basename = t_module.split('.')[-1]        
    try:
        t_submodule = testCase.module
    except: raise IOError('unrecognised tested submodule')
    message = ''
    #message = '\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    message += '\n{}: Test {}.py module of {}.{}'
    print(message.format(t_class, t_submodule, metadata.package, t_module_basename))
    #warnings.warn()
    verbosity = kwargs.pop('verbosity',2)
    suite = unittest.TestLoader().loadTestsFromTestCase(testCase)
    unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return

#/****************************************************************************/
def runtest(*TestCases, **kwargs):
    if len(TestCases)==0:                       
        return
    for testCase in TestCases:
        __runonetest(testCase, **kwargs)
        if len(TestCases)>1 and testCase!=TestCases[-1]: 
            time.sleep(1)
    return
