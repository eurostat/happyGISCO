#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_settings

Basic definitions for the use of various geolocation web-services.

**Description**

This module contains some basic definitions (classes and variables) that are used
for:

* query and collection through _Eurostat GISCO webservices,
* query and collection through external GIS webservices,
* simple geographical data handling and processing.

**Contents**

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `_Eurostat_ <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _googlemaps: https://pypi.python.org/pypi/googlemaps
.. |googlemaps| replace:: `googlemaps <googlemaps_>`_
.. _googleplaces: https://github.com/slimkrazy/python-google-places
.. |googleplaces| replace:: `googleplaces <googleplaces_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_
.. _gdal: https://pypi.python.org/pypi/GDAL
.. |gdal| replace:: `gdal <gdal_>`_
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Mar 31 21:54:08 2018

import os, sys#analysis:ignore
import inspect#analysis:ignore
import warnings

#%%
#==============================================================================
# CLASSES Error/Warning/Verbose
#==============================================================================

class happyError(Exception):
    """Base class for exceptions in this package."""
    def __init__(self, msg, expr=None):    
        self.msg = msg
        if expr is not None:    self.expr = expr
        Exception.__init__(self, msg)
    def __str__(self):              return repr(self.msg)

class happyWarning(Warning):
    """Base class for warnings in this package."""
    def __init__(self, msg, expr=None):    
        self.msg = msg
        if expr is not None:    self.expr = expr
        # logging.warning(self.msg)
        warnings.warn(self.msg)
    def __repr__(self):             return self.msg
    def __str__(self):              return repr(self.msg)
    
class happyVerbose(object):
    """Base class for verbose printing mode in this package."""
    def __init__(self, msg, expr=None, verb=True):    
        self.msg = msg
        if verb is True:
            print('\n[verbose] - %s' % self.msg)
        if expr is not None:    self.expr = expr
    def __repr__(self):             return self.msg
    def __str__(self):              return repr(self.msg)

#%%
#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

PACKAGE             = "happygisco"

PROTOCOLS           = ('http', 'https', 'ftp')
"""Recognised protocols (APIs, bulk downloads,...).
"""
DEF_PROTOCOL        = 'http'
PROTOCOL            = DEF_PROTOCOL
"""Default protocol used by the APIs.
"""
LANGS               = ('en','de','fr')
"""Languages supported by this package.
"""
DEF_LANG            = 'en'
"""Default language used when launching |Eurostat| |GISCO| API.
"""

EC_URL              = 'europa.eu'
"""European Commission URL.
"""
GISCO_DOMAIN        = 'webtools/rest/gisco/'
"""|GISCO| web-service domain under European Commission URL.
"""
GISCO_URL           = '%s/%s' % (EC_URL, GISCO_DOMAIN)
"""|GISCO| web-service complete URL.
"""

GISCO_ARCGIS        = 'webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/'
"""|GISCO| ArcGIS server.
"""

CODER_GISCO         = 'gisco'
"""Identifier of GISCO geocoder.
"""
# key for using GISCO web-services.
KEY_GISCO           = None
# dummy variables
CHECK_TYPE          = True
CHECK_OSM_KEY       = True

CODER_GOOGLE        = 'GoogleV3'
"""Identifier of GISCO geocoder.
"""
CODER_GOOGLE_MAPS   = 'GMaps'
"""Identifier of |googlemaps| geocoder.
"""
CODER_GOOGLE_PLACES = 'GPlace'
"""Identifier of |googleplaces| geocoder.
"""
KEY_GOOGLE          = 'key'
"""Personal key used for connecting to the various Google web-services.
"""

CODER_GEONAME       = 'GeoNames'
"""Default geocoder used when defined with the generic |geopy| package.
"""

CODER_LIST          = [CODER_GISCO, CODER_GOOGLE, CODER_GOOGLE_MAPS, CODER_GOOGLE_PLACES]
"""List of geocoders available.
"""
CODER_PROJ          = {CODER_GISCO: 'WGS84',
                       CODER_GOOGLE: 'EPSG3857',
                       CODER_GOOGLE_MAPS: 'EPSG3857', 
                       CODER_GOOGLE_PLACES: 'EPSG3857'}
"""Geographical projections available through the different geocoders.
"""

DRIVER_NAME         = 'ESRI Shapefile'
"""GDAL driver name.
"""                

VERBOSE             = True
      



