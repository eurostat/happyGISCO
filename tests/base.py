#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
..  _tests_base

Utility functions for `place2nuts` unit test module.

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      1
--
*since*:        Sun Apr  8 18:41:05 2018
    
**Dependencies**

*call*:         :mod:`place2nuts`
    
*require*:      :mod:`unittest`, :mod:`os`, :mod:`sys`, :mod:`re`, :mod:`warnings`, 
                :mod:`datetime`
"""


#==============================================================================
# PROGRAM METADATA
#==============================================================================

from place2nuts.__metadata__ import metadata as __metadata__
metadata = __metadata__.copy()
# metadata.update({'date': 'Sun Apr  8 18:41:05 2018'})

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

assert metadata.project == 'place2nuts' and metadata.package == 'place2nuts'

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



