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
from happygisco.tools import GeoLocation, GeoDistance, GeoAngle, GeoCoordinate, GDALTool

#==============================================================================
# TESTING UNITS
#==============================================================================

#/****************************************************************************/
# GeoLocationTestCase
#/****************************************************************************/
class GeoLocationTestCase(unittest.TestCase):

    module = 'tools'

    #/************************************************************************/
    def setUp(self):
        pass

    #/************************************************************************/
    def test_1_from_degrees_radians(self):
        # test degree to radian conversion
        loc1 = GeoLocation.from_degrees(26.062951, -80.238853)
        loc2 = GeoLocation.from_radians(loc1.rad_lat, loc1.rad_Lon)
        self.assertEqual(loc1.rad_lat, loc2.rad_lat)
        self.assertEqual(loc1.rad_Lon, loc2.rad_Lon)
        self.assertEqual(loc1.deg_lat, loc2.deg_lat)
        self.assertEqual(loc1.deg_Lon, loc2.deg_Lon)

    #/************************************************************************/
    def test_2_distance_to(self):
        # test distance between two locations
        loc1 = GeoLocation.from_degrees(26.062951, -80.238853)
        loc2 = GeoLocation.from_degrees(26.060484,-80.207268)
        self.assertAlmostEqual(loc1.distance_to(loc1))
        self.assertEqual(loc1.distance_to(loc2), loc2.distance_to(loc1))

    #/************************************************************************/
    def test_3_bounding_locations(self):
        # test bounding box
        loc = GeoLocation.from_degrees(26.062951, -80.238853)
        distance = 1  # 1 kilometer
        SW_loc, NE_loc = loc.bounding_locations(distance)
        self.assertLessEqual(loc.distance_to(SW_loc), distance)
        self.assertLessEqual(loc.distance_to(NE_loc), distance)

#/****************************************************************************/
# GeoDistanceTestCase
#/****************************************************************************/
class GeoDistanceTestCase(unittest.TestCase):

    module = 'tools'

    #/************************************************************************/
    def setUp(self):
        self.tol = 0.1 # np.spacing(np.single(1e2)) 

    #/************************************************************************/
    def test_1_units_to(self):
        self.assertEqual(GeoDistance.units_to('mi', 'm',  1.),
                         GeoDistance.MI_TO[GeoDistance.M_DIST_UNIT])
        self.assertEqual(GeoDistance.units_to('ft', 'mi',  1.),
                         GeoDistance.FT_TO[GeoDistance.MI_DIST_UNIT])
        self.assertEqual(GeoDistance.units_to('m', 'km',  dist=1000),            
                         1000*GeoDistance.M_TO[GeoDistance.KM_DIST_UNIT])
        self.assertEqual(GeoDistance.units_to('mi', 'ft',  10.),      
                         10.*GeoDistance.MI_TO[GeoDistance.FT_DIST_UNIT])
        self.assertEqual(GeoDistance.units_to('km', 'mi',  100.),     
                         100.*GeoDistance.KM_TO[GeoDistance.MI_DIST_UNIT])

    #/************************************************************************/
    def test_2_convert_units(self):
        # test the conversion operators
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
    def test_3_estimate_radius(self):
        self.assertEqual(GeoDistance.estimate_radius_WGS84(0.),  
                         GeoDistance.EARTH_RADIUS_EQUATOR)
        self.assertAlmostEqual(GeoDistance.estimate_radius_WGS84(math.pi/2.), 
                               GeoDistance.EARTH_RADIUS_POLAR)

#/****************************************************************************/
# GeoAngleTestCase
#/****************************************************************************/
class GeoAngleTestCase(unittest.TestCase):
    # test the angle conversion operators

    module = 'tools'

    #/************************************************************************/
    def setUp(self):
        self.tol = 0.1 # np.spacing(np.single(1e2)) 

    #/************************************************************************/
    def test_1_conversions(self):
        self.assertAlmostEqual(GeoAngle.dps2deg([48, 51, 52.9776]),
                               48.864716)
        self.assertEqual(GeoAngle.deg2dps(0),
                         (0, 0, 0.0))
        self.assertEqual(GeoAngle.deg2dps(90),
                         (90, 0, 0.0))
        self.assertEqual(GeoAngle.deg2dps(22.5),
                         (22, 30, 0.0))
        self.assertEqual(GeoAngle.deg2dps(48.864716),
                         (48, 51, 52.9776))
        self.assertEqual(GeoAngle.deg2rad(90),
                         math.pi/2)
        self.assertEqual(GeoAngle.deg2rad(45),
                         math.pi/4)
        self.assertEqual(GeoAngle.dps2rad([45,0,0]),
                         math.pi/4)
        self.assertEqual(GeoAngle.rad2dps(math.pi),
                         (180, 0, 0.0))
        self.assertEqual(GeoAngle.rad2deg(dps2rad([45,0,0])),
                         45)
        self.assertEqual(GeoAngle.rad2deg(math.pi),
                         180)
        self.assertAlmostEqual(GeoAngle.dps2rad([48, 51, 52.9776]),
                               0.8528501822519535)
        self.assertEqual(GeoAngle.rad2dps(GeoAngle.dps2rad([48, 51, 52.9776])),
                         (48, 51, 52.9776))

    #/************************************************************************/
    def test_2_ang_units_to(self):
        self.assertEqual(GeoAngle.ang_units_to('deg', 'rad', ang=180),
                         math.pi)
        self.assertEqual(GeoAngle.ang_units_to('rad', 'deg', ang=math.pi),
                         180)       
        self.assertEqual(GeoAngle.ang_units_to('dps', 'deg', ang=(180,0,0)),
                         180)       
        self.assertEqual(GeoAngle.ang_units_to('rad', 'dps', ang=GeoAngle.dps2rad([48, 51, 52.9776])),
                         (48, 51, 52.9776))       

    #/************************************************************************/
    def test_3_angle_units(self):
        self.assertEqual(GeoAngle.convert_angle_units(to_='deg', **{'rad': math.pi/2, 'dps': (45,0,0)}),
                         135)
        self.assertEqual(GeoAngle.convert_angle_units(to_='rad', deg=22.5, dps=(22, 30, 0.0)),
                         math.pi/4)
                        

#/****************************************************************************/
# GeoCoordinateTestCase
#/****************************************************************************/
class GeoCoordinateTestCase(unittest.TestCase):

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
    def test_1_from_degrees_radians_dps(self):
        # test degree to radian conversion
        coord1 = GeoCoordinate.from_degrees(26.062951, -80.238853)
        coord2 = GeoCoordinate.from_radians(coord1.rad_lat, coord1.rad_Lon)
        coord3 = GeoCoordinate.from_dps(coord1.dps_lat, coord1.dps_Lon)
        self.assertEqual(coord1.deg_lat, coord2.deg_lat)
        self.assertEqual(coord1.deg_Lon, coord2.deg_Lon)
        self.assertEqual(coord1.deg_lat, coord3.deg_lat)
        self.assertEqual(coord1.deg_Lon, coord3.deg_Lon)
        self.assertEqual(coord1.rad_lat, coord2.rad_lat)
        self.assertEqual(coord1.rad_Lon, coord2.rad_Lon)
        self.assertEqual(coord1.dps_lat, coord3.dps_lat)
        self.assertEqual(coord1.dps_Lon, coord3.dps_Lon)
        
    #/************************************************************************/
    def test_3_distance(self):
        """
        # test some geolocation utilities
        loc1 = GeoLocation.from_degrees(26.062951, -80.238853)        
        loc2 = GeoLocation.from_degrees(26.060484,-80.207268)
        dist_a = GeoDistance.distance_to_from((loc1.deg_lat,loc1.deg_Lon), (loc2.deg_lat,loc2.deg_Lon), 
                                            rad=False, unit='km')
        dist_b = loc1.distance_to(loc2)
        self.assertLessEqual(np.abs(dist_a - dist_b),
                             self.tol)                                


    #/************************************************************************/
    def test_bbox(self):
        lLr = GeoCoordinate.bbox2latlon(self.bbox)
        self.assertEqual(lLr[:2], 
                         self.lLr[:2])        
        self.assertLessEqual(abs(lLr[2] - self.lLr[2]),
                             self.tol)
        # GeoTool.bbox2latlon returns the (lat,Lon,rad) parameters defining the 
        # CIRCUMcirle of the bounding box 
        # GeoTool.latlon2bbox returns the bounding box whose INcircle is the
        # circle defined by parameters (lat,Lon,rad)
        self.assertTrue(GeoCoordinate.bboxwithin(self.bbox, GeoCoordinate.latlon2bbox(*self.lLr)))
        self.assertEqual(GeoCoordinate.bbox2polygon(self.bbox), self.bounding_box)
        self.assertEqual(GeoCoordinate.polygon2bbox(self.bounding_box), self.bbox)
        self.assertEqual(GeoCoordinate.bbox2polygon(self.bbox,order='Ll'), self.bounding_box_Ll)
