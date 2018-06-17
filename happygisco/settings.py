#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_settings

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _NUTS: http://ec.europa.eu/eurostat/web/nuts/background
.. |NUTS| replace:: `NUTS background <NUTS_>`_
.. _GISCOWIKI: https://webgate.ec.europa.eu/fpfis/wikis/display/GISCO/Geospatial+information+services+for+the+European+Commission+and+other+EU+users
.. |GISCOWIKI| replace:: `GISCO offline wiki <GISCOWIKI_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `Open Street Map <OSM_>`_
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. |Nominatim| replace:: `Nominatim <Nominatim_>`_
.. _Google: https://www.google.com/
.. |Google| replace:: `Google <Google_>`_
.. _Google_Maps: https://developers.google.com/maps/
.. |Google_Maps| replace:: `Google Maps <Google_Maps_>`_
.. _Google_Places: https://developers.google.com/places/
.. |Google_Places| replace:: `Google Places <Google_Places_>`_
.. _googlemaps: https://pypi.python.org/pypi/googlemaps
.. |googlemaps| replace:: `Google Maps <googlemaps_>`_
.. _googleplaces: https://github.com/slimkrazy/python-google-places
.. |googleplaces| replace:: `Google Places <googleplaces_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_
.. _GDAL: https://pypi.python.org/pypi/GDAL
.. |GDAL| replace:: `Geospatial Data Abstraction Library (GDAL) <GDAL_>`_
.. _ArcGIS: http://arcgis.com
.. |ArcGIS| replace:: `ArcGIS <ArcGIS_>`_

Basic definitions for the use of various geolocation web-services.

**Description**

This module contains some basic definitions (classes and variables) that are used
for:

* query and collection through |Eurostat| |GISCO| webservices,
* query and collection through external GIS webservices,
* simple geographical data handling and geospatial processing.

**Note**

The classes exposed in this module (*i.e.*, type class :class:`happyType` and 
logging classes :class:`happyVerbose`, :class:`happyWarning`, :class:`happyError`) 
**can be ignored** at the first glance since they are not strictly requested to 
run the services. 
They are provided here for the sake of an exhaustive documentation.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`collection`, :mod:`six`, :mod:`inspect`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Mar 31 21:54:08 2018

import os, sys#analysis:ignore
import inspect#analysis:ignore
import collections, six

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

EC_URL              = 'ec.europa.eu'
"""European Commission URL.
"""
ESTAT_DOMAIN        = 'eurostat'
"""|Eurostat| domain under European Commission URL.
"""
ESTAT_URL           = '%s://%s/%s' % (PROTOCOL, EC_URL, ESTAT_DOMAIN)
"""|Eurostat| complete URL.
"""

EC_DOMAIN           = 'europa.eu'
"""European Commission web-service domain.
"""
GISCO_DOMAIN        = 'webtools/rest/gisco/'
"""|GISCO| web-service domain under European Commission URL.
"""
GISCO_URL           = '%s/%s' % (EC_DOMAIN, GISCO_DOMAIN)
"""|GISCO| web-service complete URL.
"""
GISCO_ARCGIS        = 'webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/'
"""|GISCO| |ArcGIS| server.
"""
CODER_GISCO         = 'GISCO'
"""Identifier of |GISCO| geocoder.
"""
KEY_GISCO           = None
"""Dummy |GISCO| key. It is set to :data:`None` since connection to |GISCO| web-services does
not require authentication.
"""
GISCO_MAPDOMAIN     = 'webtools/maps/tiles'
"""|GISCO| background map domain.
"""
GISCO_MAPURL        = '%s/%s' % (EC_DOMAIN, GISCO_MAPDOMAIN) 
"""|GISCO| background map URL.
"""
GISCO_BCKGRD        = {'bmarble':       {'bckgrd':'bmarble', 'attr': 'GISCO blue marble mosaic of Earth'},
                       'boundaries':    {'bckgrd':'countryboundaries_world', 'attr': 'GISCO boundaries of all countries'},
                       'roadswater':    {'bckgrd':'roadswater_europe', 'attr': 'GISCO cities, roads and rivers'},
                       'hypso':         {'bckgrd':'hypso', 'attr': 'GISCO climate shaded relief of Earth'},
                       'coast':         {'bckgrd':'coast', 'attr': 'GISCO continental outlines'},
                       'copernicus':    {'bckgrd':'copernicus003', 'attr': 'GISCO Copernicus'},
                       'osm-ec':        {'bckgrd':'osm-ec', 'attr': 'GISCO custom OpenStreetMap'},
                       'gray-bg':       {'bckgrd':'gray-bg', 'attr': 'GISCO boundaries on gray background'},
                       'countrynames':  {'bckgrd':'countrynames_europe', 'attr': 'GISCO European country names'},
                       'gray':          {'bckgrd':'gray', 'attr': 'GISCO gray shaded relief of Earth'},
                       'natural':       {'bckgrd':'natural', 'attr': 'GISCO landcover shaded relief of Earth'},
                       'citynames':     {'bckgrd':'citynames_europe', 'attr': 'GISCO names of settlement'}
                       }
"""Dictionary for the various |GISCO| background tiles service.
"""
GISCO_BCKGRD_ORD    = '{z}/{y}/{x}'
"""
"""
GISCO_BCKGRD_PROJ   = '3857'
 
OSM_URL             = 'nominatim.openstreetmap.org/'
"""
|OSM| web-service complete URL.
"""
CODER_OSM         = 'osm'
"""Identifier of |OSM| geocoder.
"""
KEY_OSM           = None
"""
Dummy |OSM| key (connection to |OSM| web-services does not require authentication).
"""

# dummy variables
CHECK_TYPE          = True
CHECK_OSM_KEY       = True

CODER_GOOGLE        = 'GoogleV3'
"""Identifier of |GISCO| geocoder.
"""
CODER_GOOGLE_MAPS   = 'GMaps'
"""Identifier of |googlemaps| geocoder.
"""
CODER_GOOGLE_PLACES = 'GPlace'
"""Identifier of |googleplaces| geocoder.
"""
KEY_GOOGLE          = 'key'
"""Personal key used for connecting to the various |Google| web-services.
"""

CODER_GEONAME       = 'GeoNames'
"""Default geocoder used when the generic :mod:`geopy` package (see website |geopy|) 
is run for connecting to the "external" (all but |GISCO|) web-services.
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
"""|GDAL| driver name.
"""             
   
POLYLINE            = False
"""
Boolean flag set to import the package :mod:`polylines` that will enable you to 
generate polylines (see the `package website <https://pypi.python.org/pypi/polyline/>`_). 
Not really necessary to generate the routes.
"""

VERBOSE             = False # True

REDUCE_ANSWER       = False # ! used for testing purpose: do not change !
EXCLUSIVE_ARGUMENTS = False # ! used for settings: do not change !

#%%
#==============================================================================
# CLASSES happyError/happyWarning/happyVerbose
#==============================================================================

class happyWarning(Warning):
    """Dummy class for warnings in this package.
    
        >>> happyWarning(warnmsg, expr=None)

    Arguments
    ---------
    warnmsg : str
        warning message to display.
        
    Keyword arguments
    -----------------
    expr : str 
        input expression in which the warning occurs; default: :data:`expr` is 
        :data:`None`.
        
    Example
    -------
    >>> happyWarning('This is a very interesting warning');
        happyWarning: ! This is a very interesting warning !
    """
    def __init__(self, warnmsg, expr=None):    
        self.warnmsg = warnmsg
        if expr is not None:    self.expr = expr
        else:                   self.expr = '' 
        # warnings.warn(self.msg)
        print(self)
    def __repr__(self):             return self.msg
    def __str__(self):              
        #return repr(self.msg)
        return ( 
                "! %s%s%s !" %
                (self.warnmsg, 
                 ' ' if self.warnmsg and self.expr else '',
                 self.expr
                 )
            )
    
class happyVerbose(object):
    """Dummy class for verbose printing mode in this package.
    
        >>> happyVerbose(msg, verb=True, expr=None)

    Arguments
    ---------
    msg : str
        verbose message to display.
        
    Keyword arguments
    -----------------
    verb : bool
        flag set to :data:`True` when the string :literal:`[verbose] -` is added
        in front of each verbose message displayed.
    expr : str 
        input expression in which the verbose mode is called; default: :data:`expr` is 
        :data:`None`.
        
    Example
    -------
    >>> happyVerbose('The more we talk, we less we do...', verb=True);
        [verbose] - The more we talk, we less we do...
    """
    def __init__(self, msg, expr=None, verb=VERBOSE):    
        self.msg = msg
        if verb is True:
            print('\n[verbose] - %s' % self.msg)
        if expr is not None:    self.expr = expr
    #def __repr__(self):             
    #    return self.msg
    def __str__(self):              
        return repr(self.msg)
    
class happyError(Exception):
    """Dummy class for exception raising in this package.
    
        >>> raise happyError(errmsg, errtype=None, errcode=None, expr='')

    Arguments
    ---------
    errmsg : str
        message -- explanation of the error.
        
    Keyword arguments
    -----------------
    errtype : object
        error type; when :data:`errtype` is left to :data:`None`, the system tries
        to retrieve automatically the error type using :data:`sys.exc_info()`.
    errcode : (float,int)
        error code; default: :data:`errcode` is :data:`None`.
    expr : str 
        input expression in which the error occurred; default: :data:`expr` is 
        :data:`None`.
        
    Example
    -------
    >>> try:
            assert False
        except:
            raise happyError('It is False')
        Traceback ...
        ...
        happyError: !!! AssertionError: It is False !!!
    """
    
    def __init__(self, errmsg, errtype=None, errcode=None, expr=''):   
        self.errmsg = errmsg
        if expr is not None:        self.expr = expr
        else:                       self.expr = '' 
        if errtype is None:
            try:
                errtype = sys.exc_info()[0]
            except:
                pass
        if inspect.isclass(errtype):            self.errtype = errtype.__name__
        elif isinstance(errtype, (int,float)):  self.errtype = str(errtype)
        else:                               self.errtype = errtype
        if errcode is not None:     self.errcode = str(errcode)
        else:                       self.errcode = ''
        # super(happyError,self).__init__(self, msg)

    def __str__(self):              
        # return repr(self.msg)
        return ( 
                "!!! %s%s%s%s%s%s%s !!!" %
                (self.errtype or '', 
                 ' ' if self.errtype and self.errcode else '',
                 self.errcode or '',
                 ': ' if (self.errtype or self.errcode) and (self.errmsg or self.expr) else '',
                 self.errmsg or '', 
                 ' ' if self.errmsg and self.expr else '',
                 self.expr or '' #[' ' + self.expr if self.expr else '']
                 )
            )

#%%
#==============================================================================
# CLASS happyType
#==============================================================================
    
class happyType(object):
    """Class implementing various dummy types' checking.
    """
    
    #/************************************************************************/
    @classmethod
    def typename(cls, inst): 
        """Return the class name of a given instance: nothing else than 
        :literal:`instance.__class__.__name__`\ .  
    
            >>> name = typename(inst)  
            
        Arguments
        ---------
        inst : object
            an instance of a class.
            
        Returns
        -------
        name : str
            name of the class of the instance :data:`inst`.
        """
        try:
            return inst.__class__.__name__
        except:
            raise happyError('input not recognised as an instance')
    
    #/************************************************************************/
    @classmethod
    def istype(cls, inst, str_cls):
        """Determine if a given instance is of a certain type defined by a string 
        (instead of a :class:`type` like in :meth:`isintance`).
        
            >>> ans = istype(inst, str_cls)
            
        Arguments
        ---------
        inst : object
            an instance of a class.
        str_cls : str
            the name of a class to test (not the class itself).
            
        Returns
        -------
        ans : bool
            :data:`True` when :data:`inst` class name is :data:`str_cls`, :data:`False`
            otherwise.
        """
        try:
            return happyType.typename(inst) == str_cls
        except:
            raise happyError('class not recognised')
    
    #/************************************************************************/
    @classmethod
    def isstring(cls, arg):
        """Check whether an argument is a string.
        
            >>> ans = _Types.isstring(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is a string, :data:`False` 
            otherwise.
        """
        return isinstance(arg, six.string_types)
    
    #/************************************************************************/
    @classmethod
    def issequence(cls, arg):
        """Check whether an argument is a "pure" sequence (*e.g.*, a :data:`list` 
        or a :data:`tuple`), *i.e.* an instance of the :class:`collections.Sequence`,
        except strings excepted.
        
            >>> ans = _Types.issequence(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is an instance of the 
            :class:`collections.Sequence` class, but not a string (*i.e.,* not an 
            instance of the :class:`six.string_types` class), :data:`False` 
            otherwise.
        """
        return (isinstance(arg, collections.Sequence) and not happyType.isstring(arg))
    
    #/************************************************************************/
    @classmethod
    def ismapping(cls, arg):
        """Check whether an argument is a dictionary.
        
            >>> ans = _Types.ismapping(arg)
      
        Arguments
        ---------
        arg : 
            any input to test
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is an instance of the 
            :class:`collections.Mapping` class.
        """
        return (isinstance(arg, collections.Mapping))   
