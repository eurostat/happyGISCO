#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_tests_settings_

Unit test of module :mod:`happygisco.settings`

**Usage**

    >>> from tests import settings
    >>> settings.runtest()
    
**Dependencies**

*call*:         :mod:`happygisco.tests.base`, :mod:`happygisco.settings`
                
*require*:      :mod:`unittest`, :mod:`warnings`
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:41:10 2018

#==============================================================================
# PROGRAM METADATA
#==============================================================================

from happygisco.metadata import metadata

metadata = metadata.copy()
metadata.update({ 
                'date': 'Sat Apr  7 01:41:10 2018'
                #, 'credits':  ['gjacopo']
                })


#==============================================================================
# IMPORT STATEMENTS
#==============================================================================

import unittest

from happygisco.settings import happyWarning, happyError, happyVerbose, happyType 

#==============================================================================
# GLOBAL VARIABLES/METHODS
#==============================================================================

from . import runtest as _runtest

#==============================================================================
# TESTING UNITS
#==============================================================================

#/****************************************************************************/
# happyWarningTestCase
#/****************************************************************************/
class happyWarningTestCase(unittest.TestCase):
    module = 'settings'

#/****************************************************************************/
# happyErrorTestCase
#/****************************************************************************/
class happyErrorTestCase(unittest.TestCase):
    module = 'settings'

#/****************************************************************************/
# happyVerboseTestCase
#/****************************************************************************/
class happyVerboseTestCase(unittest.TestCase):
    module = 'settings'

#/****************************************************************************/
# happyTypeTestCase
#/****************************************************************************/
class happyTypeTestCase(unittest.TestCase):
    module = 'settings'

    #/************************************************************************/
    def test_1_istype(self):
        class dummy(object):
            pass
        self.assertTrue(happyType.istype(dummy(),'dummy'))
        self.assertFalse(happyType.istype(dummy(),'another'))

    #/************************************************************************/
    def test_2_isstring(self):
        self.assertTrue(happyType.isstring('dummy'))
        self.assertFalse(happyType.isstring(5))

    #/************************************************************************/
    def test_3_issequence(self):
        self.assertTrue(happyType.issequence([]))
        self.assertFalse(happyType.issequence({}))
        self.assertFalse(happyType.issequence(5))

    #/************************************************************************/
    def test_4_ismapping(self):
        self.assertTrue(happyType.ismapping({}))
        self.assertFalse(happyType.ismapping([]))
        self.assertFalse(happyType.ismapping(5))

#==============================================================================
# MAIN METHOD AND TESTING AREA
#==============================================================================

def runtest():
    _runtest(happyTypeTestCase)
    return
    
if __name__ == '__main__':
    unittest.main()
        
