#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. settings.py

Basic definitions for NUTS datasets and webservices.

**About**

*credits*:      `grazzja <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      0.1
--
*since*:        Sat Mar 31 21:54:08 2018

**Contents**
"""

import os, sys#analysis:ignore
import inspect

#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

PACKAGE             = "place2nuts"

PROTOCOLS           = ('http', 'https', 'ftp')
"""
Recognised protocols (API, bulk downloads,...).
"""
DEF_PROTOCOL        = 'http'
PROTOCOL            = DEF_PROTOCOL
"""
Default protocol used by the API.
"""
LANGS               = ('en','de','fr')
"""
Languages supported by this package.
"""
DEF_LANG            = 'en'
"""
Default language used when launching Eurostat API.
"""

EC_URL              = 'europa.eu'
"""
European Commission URL.
"""
GISCO_DOMAIN        = 'webtools/rest/gisco/'
"""
GISCO domain under European Commission URL.
"""
GISCO_URL           = '%s/%s' % (EC_URL, GISCO_DOMAIN)
"""
GISCO complete URL.
"""

CODER_GISCO         = 'gisco'
KEY_GISCO           = None
CHECK_TYPE          = True
CHECK_OSM_KEY       = True

CODER_GOOGLE        = 'GoogleV3'
CODER_GOOGLE_MAPS   = 'GMaps'
CODER_GOOGLE_PLACES = 'GPlace'
KEY_GOOGLE          = 'key'

CODER_GEONAME       = 'GeoNames'

CODER_LIST          = [CODER_GISCO, CODER_GOOGLE, CODER_GOOGLE_MAPS, CODER_GOOGLE_PLACES]
CODER_PROJ          = {CODER_GISCO: 'WGS84',
                       CODER_GOOGLE: 'EPSG3857',
                       CODER_GOOGLE_MAPS: 'EPSG3857', 
                       CODER_GOOGLE_PLACES: 'EPSG3857'}

DRIVER_NAME         = '' # 'ESRI Shapefile'
                       
VERBOSE             = False



