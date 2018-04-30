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

from happygisco.settings import happyError, _Types, _geoDecorators

#==============================================================================
# GLOBAL VARIABLES/METHODS
#==============================================================================

from .base import runtest as BaseRuntest

#==============================================================================
# TESTING UNITS
#==============================================================================

#/****************************************************************************/
# _TypesTestCase
#/****************************************************************************/
class _TypesTestCase(unittest.TestCase):
    module = 'settings'

    #/************************************************************************/
    def test_1_istype(self):
        class dummy(object):
            pass
        self.assertTrue(_Types.istype(dummy(),'dummy'))
        self.assertFalse(_Types.istype(dummy(),'another'))

    #/************************************************************************/
    def test_2_isstring(self):
        self.assertTrue(_Types.isstring('dummy'))
        self.assertFalse(_Types.isstring(5))

    #/************************************************************************/
    def test_3_issequence(self):
        self.assertTrue(_Types.issequence([]))
        self.assertFalse(_Types.issequence({}))
        self.assertFalse(_Types.issequence(5))

    #/************************************************************************/
    def test_4_ismapping(self):
        self.assertTrue(_Types.ismapping({}))
        self.assertFalse(_Types.ismapping([]))
        self.assertFalse(_Types.ismapping(5))
        
#/****************************************************************************/
# _geoDecoratorTestCase
#/****************************************************************************/
class _geoDecoratorTestCase(unittest.TestCase):
    """Class of tests for class :class:`_geoDecorator`
    """    
    module = 'settings'

    #/************************************************************************/
    def test_1_coordinate(self):
        func = lambda coord, *args, **kwargs: coord
        new_func = _geoDecorators.parse_coordinate(func)
        self.assertEqual(new_func(coord=[[1,-1],[2,-2]], order='Ll'), 
                         [[-1, 1], [-2, 2]])
        self.assertEqual(new_func(**{'lat':[1,2], 'Lon': [-1,-2]}),
                         [[1, -1], [2, -2]])
        self.assertEqual(new_func(lat=[1,2], Lon=[-1,-2], order='Ll'),
                         [[-1, 1], [-2, 2]])
        self.assertEqual(new_func(**{'y':[1,2], 'x': [-1,-2]}),
                         [[1, -1], [2, -2]])
        self.assertEqual(new_func([1,-1]), 
                         [[1,-1]])
        self.assertEqual(new_func([1,2],[-1,-2]),
                         [[1, -1], [2, -2]])
        self.assertEqual(new_func(coord=[[1,-1],[2,-2]]),
                         [[1, -1], [2, -2]])
        self.assertRaises(happyError,
                          new_func([[1,-1],[2,-2]], lat=[1,2], Lon=[-1,-2]))
        class dummy(object):
            @_geoDecorators.parse_coordinate
            def meth(self, coord, **kwargs):
                return coord
        self.assertEqual(dummy.meth([1, -1]), 
                         [1, -1])
        self.assertEqual(dummy.meth(lat=1, Lon=-1), 
                         [1, -1])
        self.assertEqual(dummy.meth(**{'lat': 1, 'Lon': -1}), 
                         [1, -1])
        self.assertRaises(happyError,
                          new_func(coord=[[1,-1],[2,-2]], lat=[1,2], Lon=[-1,-2]))

    #/************************************************************************/
    def test_2_place(self):
        func = lambda place, *args, **kwargs: place
        new_func = _geoDecorators.parse_place(func)
        self.assertEqual(new_func(func)('A'),
                         'A')
        self.assertEqual(new_func(func)({'place': 'A'}), 
                         'A')
        self.assertEqual(new_func(place='Bruxelles, Belgium'),
                         ['Bruxelles, Belgium'])
        self.assertEqual(new_func(city=['Athens','Heraklion'],country='Hellas'),
                         ['Athens, Hellas', 'Heraklion, Hellas'])
        self.assertEqual(new_func(**{'address':['72 avenue Parmentier','101 Avenue de la République'], 
                                     'city':'Paris', 'country':'France'}),
                        ['72 avenue Parmentier, Paris, France', '101 Avenue de la République, Paris, France'])
        self.assertEqual(new_func(place=['Eurostat', 'DIGIT', 'EIB'],city='Luxembourg'),
                        ['Eurostat, Luxembourg', 'DIGIT, Luxembourg', 'EIB, Luxembourg'])
        self.assertEqual(new_func('Athens, Hellas'),
                         ['Athens, Hellas'])
        class dummy(object):
            @_geoDecorators.parse_place
            def meth(self, place, **kwargs):
                return place
        self.assertEqual(dummy.meth('A'), 
                         'A')
        self.assertEqual(dummy.meth(place='A'), 
                         'A')
        self.assertEqual(dummy.meth(**{'place': 'A'}), 
                         'A')
        self.assertRaises(happyError,
                          new_func('Athens, Hellas', place='Berlin, Germany'))
        
    #/************************************************************************/
    def test_3_place_or_coordinate(self):
        func = lambda *args, **kwargs: [kwargs.get('coord'), kwargs.get('place')]
        new_func = _geoDecorators.parse_place_or_coordinate(func)
        self.assertEqual(new_func(lat=[1,2], Lon=[-1,-2]),
                         [[[1, -1], [2, -2]], None])
        self.assertEqual(new_func(place='Bruxelles, Belgium'),
                         [None, ['Bruxelles, Belgium']])
        class dummy(object):
            @_geoDecorators.parse_place_or_coordinates
            def meth(self, **kwargs):
                return kwargs.get('place') or [kwargs.get('lat'),kwargs.get('Lon')]
        self.assertEqual(dummy.meth(place='A'), 'A')
        self.assertEqual(dummy.meth(lat=1, Lon=-1), [[1], [-1]])
        
    #/************************************************************************/
    def test_4_geometry(self):
        func = lambda *args, **kwargs: kwargs.get('coord')
        new_func = _geoDecorators.parse_geometry(func)
        geom = {'A': 1, 'B': 2}
        self.assertEqual(new_func(geom=geom),
                         [])
        self.assertRaises(happyError,
                          new_func(geom=geom))
        geom = {'geometry': {'coordinates': [1, 2], 'type': 'Point'},
                             'properties': {'city': 'somewhere', 
                                            'country': 'some country',
                                            'street': 'sesame street',
                                            'osm_key': 'place'},
                             'type': 'Feature'}
        self.assertEqual(new_func(geom=geom),
                         [[2, 1]])
        self.assertEqual(new_func(geom, order='Ll'),
                         [[1, 2]])
        func = lambda *args, **kwargs: kwargs.get('place')
        new_func = _geoDecorators.parse_geometry(func)
        self.assertEqual(new_func(geom=geom, filter='place'),
                         ['sesame street, somewhere, some country'])            
        
    #/************************************************************************/
    def test_5_nuts(self):
        func = lambda *args, **kwargs: kwargs.get('nuts')
        new_func = _geoDecorators.parse_nuts(func)
        nuts = {'A': 1, 'B': 2}
        self.assertEqual(new_func(nuts),
                         [])
        self.assertRaises(happyError,
                          new_func(nuts=nuts))
        nuts = {'attributes': {'CNTR_CODE': 'EU', 'LEVL_CODE': '0'},
                'NUTS_NAME': 'EU',
                'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                'value': 'EU'}
        self.assertTrue([nuts] == new_func(**nuts))
        self.assertTrue([nuts] == new_func(nuts=nuts))

    #/************************************************************************/
    def test_5_projection(self):
        func = lambda *args, **kwargs: kwargs.get('proj')
        new_func = _geoDecorators.parse_projection(func)
        self.assertEqual(new_func(proj='WGS84'),
                         4326)
        self.assertEqual(new_func(proj='EPSG3857'),
                         3857)
        self.assertEqual(new_func(proj=3857),
                         3857)
        self.assertEqual(new_func(proj='LAEA'),
                         3035)
        self.assertRaises(happyError,
                          new_func(proj='dumb'))
 
    #/************************************************************************/
    def test_6_year(self):
        func = lambda *args, **kwargs: kwargs.get('year')
        new_func = _geoDecorators.parse_year(func)
        self.assertEqual(new_func(year=2013),
                         2013)
        self.assertRaises(happyError,
                          new_func(year=2000))

#==============================================================================
# MAIN METHOD AND TESTING AREA
#==============================================================================

def runtest():
    BaseRuntest(_geoDecoratorTestCase)
    return
    
if __name__ == '__main__':
    unittest.main()
        
