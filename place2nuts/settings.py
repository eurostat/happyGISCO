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
DEF_PROTOCOL        = 'https'
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

GOOGLE_KEY          = ''
GOOGLE_CODER        = 'GoogleV3'
DRIVER_NAME         = '' # 'ESRI Shapefile'

GISCO_SERVICE       = True
API_SERVICE         = True
                       
VERBOSE             = False



