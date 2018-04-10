#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_tests_settings_

Unit test of module :mod:`happygisco.settings`

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      1
--
*since*:        Sat Apr  7 01:41:10 2018

**Description**

**Usage**

    >>> from tests import settings
    >>> settings.runtest()
    
**Dependencies**

*call*:         :mod:`happygisco.tests.base`, :mod:`happygisco.settings`
                
*require*:      :mod:`unittest`, :mod:`warnings`
"""

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
import warnings

from happygisco.settings import _geoDecorators

#==============================================================================
# GLOBAL VARIABLES/METHODS
#==============================================================================

from .base import runtest as BaseRuntest

#==============================================================================
# TESTING UNITS
#==============================================================================

#/****************************************************************************/
# _geoDecoratorTestCase
#/****************************************************************************/
class _geoDecoratorTestCase(unittest.TestCase):
    """Class of tests for class :class:`_geoDecorator`
    """    
    module = 'settings'

    #/************************************************************************/
    def test_1_place(self):
        dummy = lambda place, *kwargs: place
        self.assertEqual(_geoDecorators.parse_place(dummy)('A'),
                         'A')
        self.assertEqual(_geoDecorators.parse_place(dummy)({'place': 'A'}), 
                         'A')
        class dummy(object):
            @_geoDecorators.parse_place
            def meth(self, place, **kwargs):
                return place
        self.assertEqual(dummy.meth('A'), 
                         'A')
        self.assertEqual(dummy.meth(place='A'), 
                         'A')
        self.assertEqual(dummy.meth({'place': 'A'}), 
                         'A')

    #/************************************************************************/
    def test_2_coordinate(self):
        dummy = lambda lat, lon, *kwargs: [lat, lon]
        self.assertEqual(_geoDecorators.parse_coordinate(dummy)(1, -1), 
                         [1, -1])
        self.assertEqual(_geoDecorators.parse_coordinate(dummy)([1, -1]), 
                         [1, -1])
        self.assertEqual(_geoDecorators.parse_coordinate(dummy)({'lat': 1, 'lon': -1}), 
                         [1, -1])
        class dummy(object):
            @_geoDecorators.parse_coordinate
            def meth(self, lat, lon, **kwargs):
                return lat, lon
        self.assertEqual(dummy.meth([1, -1]), 
                         [1, -1])
        self.assertEqual(dummy.meth(lat=1, lon=-1), 
                         [1, -1])
        self.assertEqual(dummy.meth({'lat': 1, 'lon': -1}), 
                         [1, -1])
        
    #/************************************************************************/
    def test_3_place_or_coordinate(self):
        class dummy(object):
            @_geoDecorators.parse_place_or_coordinates
            def meth(self, **kwargs):
                return kwargs.get('place') or [kwargs.get('lat'),kwargs.get('lon')]
        self.assertEqual(dummy.meth(place='A'), 'A')
        self.assertEqual(dummy.meth(lat=1, lon=-1), [[1], [-1]])
        
#==============================================================================
# MAIN METHOD AND TESTING AREA
#==============================================================================

def runtest():
    BaseRuntest(_geoDecoratorTestCase)
    return
    
if __name__ == '__main__':
    unittest.main()
        
