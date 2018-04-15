#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_tests_services

Unit test of module :mod:`happygisco.services`.

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      1
--
*since*:        Sun Apr  8 20:35:49 2018

**Description**

**Usage**

    >>> from tests import services
    >>> services.runtest()
    
**Dependencies**

*call*:         :mod:`happygisco.tests.base`, :mod:`happygisco.services`
                
*require*:      :mod:`unittest`, :mod:`warnings`, :mod:`numpy`
"""


#==============================================================================
# PROGRAM METADATA
#==============================================================================

from happygisco.metadata import metadata

metadata = metadata.copy()
metadata.update({ 
                'date': 'Sun Apr  8 20:35:49 2018'
                #, 'credits':  ['gjacopo']
                })


#==============================================================================
# IMPORT STATEMENTS
#==============================================================================

import unittest
import warnings
import requests

try:                               
    import numpy as np
    Array, memArray=np.ndarray, np.memmap
    np.set_printoptions(precision=5)
    np.set_printoptions(suppress=True)
except ImportError:
    raise IOError

from happygisco import settings
from happygisco.services import GISCOService, APIService, GDALservice

#==============================================================================
# GLOBAL VARIABLES/METHODS
#==============================================================================

from .base import runtest as BaseRuntest

PARIS = {'place': 'Paris, France',
                 'lat': 48.8566, # 48.8566101
                 'lon':  2.3515, # 2.3514992
                 'woe_id': 615702} 
BERLIN = {'place': 'Berlin, Germany',
                 'lat':   52.5170, # 52.5170365
                 'lon':   13.3888, # 13.3888599
                 'woe_id': None}
BRUXELLES = {'place': 'Bruxelles, Belgium',
                 'lat':   None, 
                 'lon':   None,
                 'woe_id': None}

#==============================================================================
# TESTING UNITS
#==============================================================================

#/****************************************************************************/
# GISCOServiceTestCase
#/****************************************************************************/
class GISCOServiceTestCase(unittest.TestCase):
    """Class of tests for class :class:`GISCOService`
    """    
    module = 'services'

    #/************************************************************************/
    def setUp(self):
        pass
        self.paris = PARIS
        self.berlin = BERLIN
        self.bruxelles = BRUXELLES
        self.delta = 0.0001
        self.serv = GISCOService()

    #/************************************************************************/
    def test__init__(self):
        self.assertEqual(GISCOService().domain.domain, 
                         settings.GISCO_URL)
        self.assertEqual(GISCOService(domain='A').domain, 
                         'A')
        self.assertRaises(IOError, 
                          GISCOService, domain='A')
        self.assertIsInstance(GISCOService().session,
                         requests.sessions.Session)

    #/************************************************************************/
    def test_place2coord(self):
        self.assertRaises(IOError, 
                          self.serv.place2coord, 'averyunlikelynameforacity, inanunknowncountry')
        lat, lon = self.serv.place2coord(self.paris['place'])
        self.assertAlmostEqual(lat, self.paris['lat'], delta = self.delta)
        self.assertAlmostEqual(lon, self.paris['lon'], delta = self.delta)

    #/************************************************************************/
    def test_coord2place(self):
        self.assertRaises(IOError, 
                          self.serv.coord2place, [-1000, 1000])
        place = self.serv.coord2place(self.berlin['lat'], self.berlin['lon'])
        self.assertTrue('geometry' in place)
        self.assertEqual(', '.join(place['geometry']['city'],place['geometry']['city']),
                         self.berlin['place'])
        
#/****************************************************************************/
# APIServiceTestCase
#/****************************************************************************/
class APIServiceTestCase(unittest.TestCase):
    """Class of tests for class :class:`APIService`
    """    
    module = 'services'

    #/************************************************************************/
    def setUp(self):
        pass
        self.paris = PARIS
        self.berlin = BERLIN
        self.bruxelles = BRUXELLES

    #/************************************************************************/
    def test1_googleMaps(self):
        """Test API methods in location._googleMapsAPI
        Reproduce tests from https://pypi.python.org/pypi/googlemaps
        """
        try: 
            import googlemaps#analysis:ignore
            assert GOOGLE_KEY not in ('',None)
        except: 
            warnings.warn('API Google Maps not imported') 
            return 
        try:
            self.serv = APIService(coder='GMaps', key=GOOGLE_KEY)
        except:
            warnings.warn('API Google Maps service not available') 
        self.assertEqual(self.serv.coder_key,            GOOGLE_KEY)
        # reproduce tests from https://pypi.python.org/pypi/googlemaps ?
        try:    
            lat, lon = self.serv.place2coord(self.paris['place'])
        except: # usuallt HTTP Error 403
            warnings.warn('Usage API data not available: check your credentials/rights') 
            return 
        self.assertEqual(lat, self.paris['lat']) and  self.assertEqual(lon, self.paris['lon'])
         
    #/************************************************************************/
    def test2_googlePlaces(self):
        """Test API methods in location._googlePlacesAPI
        Reproduce tests from https://github.com/slimkrazy/python-google-places
        """
        try: 
            import googleplaces#analysis:ignore
        except: 
            warnings.warn('API Google Places not imported') 
            return 
        try:
            self.serv = APIService(coder='GPlaces', key=GOOGLE_KEY)
        except:
            warnings.warn('API Google Maps service not available') 
        self.assertEqual(self.serv.coder_key,            GOOGLE_KEY)
        # reproduce tests from https://github.com/slimkrazy/python-google-places
        try:    
            lat, lon = self.serv.place2coord(self.paris['place'])
        except: # usuallt HTTP Error 403
            warnings.warn('Usage API data not available: check your credentials/rights') 
            return 
        self.assertEqual(lat, self.paris['lat']) and  self.assertEqual(lon, self.paris['lon'])

    #/************************************************************************/
    def test5_geoCoder(self):
        """Test API methods in location._geoCoderAPI
        Reproduce tests from https://github.com/geopy/geopy
        """
        try:
            self.serv = APIService(coder='GoogleV3', key=GOOGLE_KEY)
        except:
            warnings.warn('API geopy service not available') 
        code = self.serv.geocode(self.paris['place'])    
        self.assertTrue(np.abs(code[0] - self.paris['lat'] < TOL))
        self.assertTrue(np.abs(code[1] - self.paris['lon'] < TOL))
        paris = self.serv.reverse(self.paris['lat'], self.paris['lon'])
        # first note that Geographer.reverse accepts arguments: (lat, Lon) or "lat, Lon"...
        self.assertEqual(self.serv.reverse("{}, {}".format(self.paris['lat'], self.paris['lon'])), 
                         paris)
        # also note that Geographer.reverse is nothing else than Geographer.code
        # passed with KW_REVERSE argument set to True
        self.assertEqual(self.serv.geocode("{}, {}".format(self.paris['lat'], self.paris['lon']), reverse=True), 
                         paris)

#/****************************************************************************/
# GDALserviceTestCase
#/****************************************************************************/
class GDALserviceTestCase(unittest.TestCase):
    """Class of tests for class :class:`GDALservice`
    """    
    module = 'services'
        
#==============================================================================
# MAIN METHOD AND TESTING AREA
#==============================================================================

def runtest():
    BaseRuntest(GISCOServiceTestCase, APIServiceTestCase, GDALserviceTestCase)
    return
    
if __name__ == '__main__':
    unittest.main()
