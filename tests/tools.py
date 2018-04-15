#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_tests_tools

Unit test of module :mod:`happygisco.tools`.

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      1
--
*since*:        Sun Apr 15 02:17:00 2018

**Description**

**Usage**

    >>> from tests import tools
    >>> tools.runtest()
    
**Dependencies**

*call*:         :mod:`happygisco.tests.base`, :mod:`happygisco.tools`
                
*require*:      :mod:`unittest`, :mod:`warnings`, :mod:`numpy`
"""


#==============================================================================
# PROGRAM METADATA
#==============================================================================

from happygisco.metadata import metadata

metadata = metadata.copy()
metadata.update({ 
                'date': 'Sun Apr 15 02:17:00 2018'
                #, 'credits':  ['gjacopo']
                })


#==============================================================================
# IMPORT STATEMENTS
#==============================================================================

import unittest
import math

try:
    import numpy as np
except ImportError:
    pass

from happygisco import settings
from happygisco.tools import _GeoLocation, GeoDistance, GeoAngle, GeoLocation, GDALTool

#==============================================================================
# TESTING UNITS
#==============================================================================

#/****************************************************************************/
# _GeoLocationTestCase
#/****************************************************************************/
class _GeoLocationTestCase(unittest.TestCase):

    module = 'tools'

    #/************************************************************************/
    def setUp(self):
        pass

    #/************************************************************************/
    def test_1_from_degrees_radians(self):
        # test degree to radian conversion
        loc1 = _GeoLocation.from_degrees(26.062951, -80.238853)
        loc2 = _GeoLocation.from_radians(loc1.rad_lat, loc1.rad_lon)
        self.assertEqual(loc1.rad_lat, loc2.rad_lat)
        self.assertEqual(loc1.rad_lon, loc2.rad_lon)
        self.assertEqual(loc1.deg_lat, loc2.deg_lat)
        self.assertEqual(loc1.deg_lon, loc2.deg_lon)

    #/************************************************************************/
    def test_2_distance_from(self):
        # test distance between two locations
        loc1 = _GeoLocation.from_degrees(26.062951, -80.238853)
        loc2 = _GeoLocation.from_degrees(26.060484,-80.207268)
        self.assertEqual(loc1.distance_to(loc2), loc2.distance_to(loc1))

    #/************************************************************************/
    def test_3_bounding_locations(self):
        # test bounding box
        loc = _GeoLocation.from_degrees(26.062951, -80.238853)
        distance = 1  # 1 kilometer
        SW_loc, NE_loc = loc.bounding_locations(distance)
        print(loc.distance_to(SW_loc))
        print(loc.distance_to(NE_loc))


#/****************************************************************************/
# GeoDistanceTestCase
#/****************************************************************************/
class GeoDistanceTestCase(unittest.TestCase):

    module = 'tools'

    #/************************************************************************/
    def setUp(self):
        self.tol = 0.1 # np.spacing(np.single(1e2)) 

    #/************************************************************************/
    def test_convert_units(self):
        """
        """
        # test the conversion operators
        self.assertEqual(GeoDistance.units_to('m', 'km',  dist=1000),            
                         1)
        self.assertEqual(GeoDistance.units_to('mi', 'ft',  10.),      
                         10.*GeoDistance.MI_TO[GeoDistance.FT_DIST_UNIT])
        self.assertEqual(GeoDistance.units_to('km', 'mi',  100.),     
                         100.*GeoDistance.KM_TO[GeoDistance.MI_DIST_UNIT])
        self.assertEqual(GeoDistance.convert_distance_units('m', **{'km':1,  'm':10}),     
                         1010)
        dist = GeoDistance.convert_distance_units('m', mi=2,  ft=10, km=0.5)
        self.assertEqual(2*GeoDistance.MI_TO[GeoDistance.M_DIST_UNIT]           \
                         + 10.*GeoDistance.FT_TO[GeoDistance.M_DIST_UNIT]       \
                         + 0.5*GeoDistance.KM_TO[GeoDistance.M_DIST_UNIT],
                         dist)
        self.assertEqual(GeoDistance.convert_distance_units('m', mi=2,  **{'ft':10, 'km':0.5}),
                         dist) 

    #/************************************************************************/
    def test_distance(self):
        """
        """
        self.assertEqual(GeoDistance.estimate_radius_WGS84(0.),  
                         GeoDistance.EARTH_RADIUS_EQUATOR)
        self.assertEqual(GeoDistance.estimate_radius_WGS84(math.pi/2.), 
                         GeoDistance.EARTH_RADIUS_POLAR)
        # test some geolocation utilities
        loc1 = GeoAngle.from_degrees(26.062951, -80.238853)        
        loc2 = GeoAngle.from_degrees(26.060484,-80.207268)
        dist_a = GeoDistance.distance_to_from((loc1.deg_lat,loc1.deg_lon), (loc2.deg_lat,loc2.deg_lon), 
                                            rad=False, unit='km')
        dist_b = loc1.distance_to(loc2)
        self.assertLessEqual(np.abs(dist_a - dist_b),
                             self.tol)                                

#/****************************************************************************/
# GeoAngleTestCase
#/****************************************************************************/
class GeoAngleTestCase(unittest.TestCase):

    module = 'tools'

    #/************************************************************************/
    def test_convert_units(self):
        """
        """
        # test the conversion operators
        self.assertLessEqual(np.abs(GeoAngle.ang_units_to('deg', 'rad', ang=180) - 3.14159265359),
                             self.tol)
        self.assertLessEqual(np.abs(GeoAngle.ang_units_to('rad', 'deg', ang=3.14159265359) - 180),
                             self.tol)       
        self.assertEqual(GeoAngle.deg2rad(90),
                         math.pi/2.)
        self.assertEqual(GeoAngle.rad2deg(math.pi), 
                         180.)

#/****************************************************************************/
# GeoLocationTestCase
#/****************************************************************************/
class GeoLocationTestCase(unittest.TestCase):

    module = 'tools'

    #/************************************************************************/
    def setUp(self):
        self.tol = 0.1 # np.spacing(np.single(1e2)) 
        self.lLr = (2.347, 48.85884, 14.50401801879798)
        self.bbox = [2.2241, 48.81554, 2.4699, 48.90214]
        self.bbox_Ll = [48.81554, 2.2241, 48.90214, 2.4699] 
                        # self.bbox[:2][::-1] + self.bbox[2:][::-1]
        self.bounding_box = [[2.2241, 48.81554], [2.4699, 48.81554], 
                             [2.4699, 48.90214], [2.2241, 48.90214]] # like the one used in twitter
        self.bounding_box_Ll = [[48.81554, 2.2241], [48.81554, 2.4699], 
                                [48.90214, 2.4699], [48.90214, 2.2241]]
                            # [lL[::-1] for lL in self.bounding_box] # like the one used in twitter
        
    #/************************************************************************/
    def test_bbox(self):
        lLr = GeoLocation.bbox2latlon(self.bbox)
        self.assertEqual(lLr[:2], 
                         self.lLr[:2])        
        self.assertLessEqual(abs(lLr[2] - self.lLr[2]),
                             self.tol)
        # GeoTool.bbox2latlon returns the (lat,Lon,rad) parameters defining the 
        # CIRCUMcirle of the bounding box 
        # GeoTool.latlon2bbox returns the bounding box whose INcircle is the
        # circle defined by parameters (lat,Lon,rad)
        self.assertTrue(GeoLocation.bboxwithin(self.bbox, GeoLocation.latlon2bbox(*self.lLr)))
        self.assertEqual(GeoLocation.bbox2polygon(self.bbox), self.bounding_box)
        self.assertEqual(GeoLocation.polygon2bbox(self.bounding_box), self.bbox)
        self.assertEqual(GeoLocation.bbox2polygon(self.bbox,order='Ll'), self.bounding_box_Ll)
