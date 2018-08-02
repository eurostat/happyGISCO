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
.. _Nuts2json: https://github.com/eurostat/Nuts2json
.. |Nuts2json| replace:: `Nuts2json <Nuts2json_>`_

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
import collections, itertools, six

#%%
#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

PACKAGE             = "happygisco"

PROTOCOLS           = ('http', 'https', 'ftp')
"""Recognised protocols (APIs, bulk downloads,...).
"""
DEF_PROTOCOL        = 'http'
"""Default protocol used by the APIs.
"""
PROTOCOL            = DEF_PROTOCOL
LANGS               = ('en','de','fr')
"""Languages supported by this package.
"""
DEF_LANG            = 'en'
"""Default language used when launching |Eurostat| |GISCO| API.
"""

EC_DOMAIN           = 'europa.eu'
"""Domain of European Commission generic web-services.
"""
EC_URL              = 'ec.%s' % EC_DOMAIN
"""URL of the European Commission website.
"""
ESTAT_DOMAIN        = 'eurostat'
"""Domain of |Eurostat| website under European Commission URL.
"""
ESTAT_URL           = '%s://%s/%s' % (PROTOCOL, EC_URL, ESTAT_DOMAIN)
"""Complete URL of |Eurostat| website.
"""

GISCO_WEBDOMAIN     = 'webtools'
"""Domain of |GISCO| web-service under the European Commission URL.
"""
GISCO_RESTDOMAIN    = 'rest/gisco/'
"""Domain of |GISCO| REST webservices and webtools.
"""
GISCO_RESTURL           = '%s/%s/%s' % (EC_DOMAIN, GISCO_WEBDOMAIN, GISCO_RESTDOMAIN)
"""Complete URL of |GISCO| REST webservices and webtools.
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
GISCO_PROJECTIONS   = {'WGS84':     4326,
                       'EPSG4326':  4326, 
                       'ETRS89':    4258,
                       'EPSG4258':  4258, 
                       'Mercator':  3857,
                       'EPSG3857':  3857, 
                       'LAEA':      3035,
                       'EPSG3035':  3035
                       }
"""Projections and EPSG codes currently supported by |GISCO| services. 
See http://spatialreference.org for the list of all EPSG codes and corresponding 
spatial references.
"""
DEF_GISCO_PROJECTION = 4326
"""Default projection used by |GISCO| services.
"""
GISCO_CACHEDOMAIN    = 'eurostat/cache/GISCO/distribution/v2'
"""Domain of cache database, *e.g.* countries and |NUTS| vector datasets themes, 
for download/distribution.
"""
GISCO_CACHEURL       = 'ec.%s/%s' % (EC_DOMAIN, GISCO_CACHEDOMAIN) 
"""Complete URL of |GISCO| cache database.
"""
GISCO_TILEDOMAIN    = 'webtools/maps/tiles'
"""Domain of |GISCO| background tiling service.
"""
GISCO_TILEURL       = '%s/%s' % (EC_DOMAIN, GISCO_TILEDOMAIN) 
"""Complete URL of |GISCO| background tiling service.
"""
GISCO_TILES         = {'bmarble':       {'bckgrd':'bmarble', 'proj': True,           'attr': '© NASA’s Earth Observatory', 'label': 'Blue marble mosaic of Earth'},
                       'boundaries':    {'bckgrd':'countryboundaries_world', 'proj': True, 'attr': '© Eurogeographics @UN-FAO @Turkstat', 'label': 'boundaries of all countries'},
                       'roadswater':    {'bckgrd':'roadswater_europe', 'proj': True, 'attr': '© Eurogeographics', 'label': 'cities, roads and rivers'},
                       'hypso':         {'bckgrd':'hypso', 'proj': True,             'attr': '© Natural Earth', 'label': 'climate shaded relief of Earth'},
                       'coast':         {'bckgrd':'coast', 'proj': True,             'attr': '© EC-GISCO', 'label': 'continental outlines'},
                       'copernicus':    {'bckgrd':'copernicus003', 'proj': False,    'attr': '© Core003 Mosaic', 'label': 'Copernicus Core003'},
                       'osmec':         {'bckgrd':'osm-ec', 'proj': False,           'attr': '© OpenStreetMap', 'label': 'OpenStreetMap'},
                       'graybg':        {'bckgrd':'gray-bg', 'proj': True,           'attr': '© Eurogeographics', 'label': 'boundaries on gray background'},
                       'country':       {'bckgrd':'countrynames_europe', 'proj': True, 'attr': '© Eurogeographics', 'label': 'European country names'},
                       'gray':          {'bckgrd':'gray', 'proj': True,              'attr': '© Natural Earth', 'label': 'gray shaded relief of Earth'},
                       'natural':       {'bckgrd':'natural', 'proj': True,           'attr': '© Natural Earth', 'label': 'landcover shaded relief of Earth'},
                       'city':          {'bckgrd':'citynames_europe', 'proj': True,  'attr': '© Eurogeographics', 'label': 'names of settlement'},
                       'cloudless':     {'bckgrd':'sentinelcloudless', 'proj': False,'attr': 'Sentinel Cloudless', 'label': 'Sentinel Cloudless' } 
                       }
"""Dictionary for the various |GISCO| background tiles service. See the list
of `available tiles servers <https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=webtools&title=Map+-+available+tiles+servers>`_.
"""
GISCO_TILEORDER     = '{z}/{y}/{x}'
"""|GISCO| background tile ordering (used for visualisation).
"""
DEF_GISCO_TILEPROJ  = 3857
"""Default |GISCO| background tile projection.
"""
DEF_GISCO_ZOOM      = 4
"""Default zooming value in map displays.
"""
GISCO_NUTSDOMAIN    = 'nuts'
"""Subdomain of |NUTS|.
"""
GISCO_NUTSURL       = '%s/%s' % (GISCO_CACHEURL, GISCO_NUTSDOMAIN) 
"""Complete URL of |NUTS| download/distribution services.
"""
GISCO_NUTSTHEME     = 'nuts'
"""NUTS theme used for URL naming.
"""
GISCO_NUTSDATASET   = {'data':'nuts-{year}-units', 'fmt':'json'} 
"""Name and type of the file storing all unit datasets.
"""
GISCO_CTRYDOMAIN    = 'countries'
"""Subdomain of countries.
"""
GISCO_CTRYURL       = '%s/%s' % (GISCO_CACHEURL, GISCO_CTRYDOMAIN) 
"""Complete URL of countries download/distribution services.
"""
GISCO_CTRYDATASET   = {'data':'countries-{year}-units', 'fmt':'json'
                       }
"""Name and type of the file storing all country datasets.
"""
GISCO_DISTRIBUTION  = {'download': {'domain':'download', 'basename':'ref-nuts'},
                       'distribution': {'domain':'distribution', 'basename':''}
                       }
"""Type of service for theme vector datasets: :literal:`download` for the
bulk datasets, :literal:`distribution` for single areas.
"""
GISCO_NUTSLEVELS    = [0, 1, 2, 3
                       ]
"""Levels of |NUTS| areas.
"""
GISCO_NUTS2ID       = {'data':'NUTS_AT_{year}', 'fmt':'csv'
                       }
"""Name and type of the file storing the correspondance table between NUTS names
and their IDs.
"""
GISCO_SCALES        = {1: '01m', 3: '03m', 10: '10m', 20: '20m', 60: '60m'
                       } 
"""Scale (1:`scale` Million) of vector datasets.
"""
DEF_GISCO_SCALE    = '01m'
"""Default scale for |GISCO| vector datasets.
"""
GISCO_YEARS         = [2003, 2006, 2010, 2013, 2016
                       ]
"""Years of adoption/revision of |NUTS| areas.
"""
DEF_GISCO_YEAR      = 2013
"""Default year considered for |NUTS| datasets (not the most recent, but up-to-date).
"""
GISCO_FORMATS       = {'shp': 'shx',  # 'shapefile': 'shp', 
                       'geojson': 'geojson',  
                       'topojson': 'json', 
                       'gdb': 'gdb', 
                       'pbf': 'pbf', 
                       }
"""Format of |GISCO| vector data files.
"""
DEF_GISCO_FORMAT    = 'geojson'
"""Default format for |GISCO| vector datasets.
"""
GISCO_GEOMETRIES    = {'region':'RG', 
                       'label':'LB',
                       'line':'BN',
                       'boundary':'BN'
                       }
"""Dictionary of spatial typologies, *i.e.* the geometry of |GISCO| feature datasets. 
"""
DEF_GISCO_GEOMETRY  = 'RG'
"""Default spatial typology.
"""
GISCO_REFNAME       = ''
"""Generic name used to reference the bulk datasets.
"""

OSM_URL             = 'nominatim.openstreetmap.org/'
"""|OSM| web-service complete URL.
"""
CODER_OSM         = 'osm'
"""Identifier of |OSM| geocoder.
"""
KEY_OSM           = None
"""Dummy |OSM| key (connection to |OSM| web-services does not require authentication).
"""

EU_GEOCENTRE        = [50.033333, 10.35]
"""The German municipality of `Gädheim <https://en.wikipedia.org/wiki/Gädheim>`_ 
(in the district of Haßberge in Bavaria) serves as the geographical centre of the 
European Union (when the United Kingdom leaves on April 2019).

See the Wikipedia  page on the 
`geographical midpoint of Europe <https://en.wikipedia.org/wiki/Geographical_midpoint_of_Europe>`_
for discussions on the topic. For the determination of the actual geographical 
coordinates (50°02′N 10°21′E), see also 
`this page <https://tools.wmflabs.org/geohack/geohack.php?pagename=Gädheim&params=50_02_N_10_21_E_type:city(1272)_region:DE-BY>`_.
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
CODER_LIST          = [CODER_GISCO, CODER_GOOGLE, CODER_GOOGLE_MAPS, CODER_GOOGLE_PLACES
                       ]
"""List of geocoders available.
"""
CODER_PROJ          = {CODER_GISCO:         DEF_GISCO_PROJECTION,
                       CODER_GOOGLE:        'EPSG3857',
                       CODER_GOOGLE_MAPS:   'EPSG3857', 
                       CODER_GOOGLE_PLACES: 'EPSG3857'
                       }
"""Default geographical projections available through the different geocoders.
"""

GISCO_LAUDOMAIN     = 'documents/345175/501971'
"""
"""
GISCO_LAUURL        = '%s/%s' % (ESTAT_URL, GISCO_LAUDOMAIN) 
"""Complete URL of |GISCO| LAU resources.
"""
NUTS2LAU            =  {2016: {2018: 'EU-28-LAU-2018-NUTS-2016.xlsx',
                               2017: 'EU-28_LAU_2017_NUTS_2016.xlsx'},
                        2013: {2017: 'EU-28_LAU_2017_NUTS_2013.xlsx',
                               2016: 'EU-28_LAU_2016',
                               2015: 'EU-28_2015.xlsx',
                               2014: 'EU-28_2014.xlsx',
                               2013: 'EU-28_2013.xlsx',
                               2012: 'EU-28_2012.xlsx',
                               2011: 'EU-28_2011.xlsx',
                               2010: 'EU-28_2010.xlsx'}
                        }
"""Conversion tables between LAU and NUTS datasets.
"""

NUTS2JSON_DOMAIN    = 'raw.githubusercontent.com/eurostat/Nuts2json/gh-pages'
"""Domain of |Nuts2json| database.
"""
NUTS2JSON_PROJECTIONS = GISCO_PROJECTIONS.copy()
"""Projections and encoding strings currently supported by |Nuts2json| service
(for dissemination). 
See http://spatialreference.org for the list of all EPSG codes and corresponding 
spatial references.
"""
DEF_NUTS2JSON_PROJECTION = 3857
"""Default projection used by |Nuts2json| services.
"""
NUTS2JSON_FORMATS   = {'geojson':           'json',  
                       'topojson':          'json'
                       }
"""Format of |Nuts2json| vector data files.
"""
DEF_NUTS2JSON_FORMAT = 'topojson'
"""Default format for |Nuts2json| vector datasets.
"""
NUTS2JSON_MAPSIZE   = [400, 600, 800, 1000, 1200
                       ]
"""Map dimension (in pixel) adopted for the fetching of |Nuts2json|. Currently, 
all maps are squared.
"""
NUTS2JSON_NUTSLEVELS = GISCO_NUTSLEVELS
# dumb variable

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
    
    ::
        
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
    
    ::
    
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
    
    ::

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
    
    ::
    
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
    
    ::
        
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
        :literal:`instance.__class__.__name__`.
        
        ::
    
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
        
        ::
        
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
        
        ::
        
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
        
        ::
        
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
        
        ::
        
            >>> ans = _Types.ismapping(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is an instance of the 
            :class:`collections.Mapping` class.
        """
        return (isinstance(arg, collections.Mapping))  
    
    #/************************************************************************/
    @classmethod
    def seqflatten(cls, arg):
        #ignore
        """Flatten a list of lists.
        
        ::
        
            >>> flat = _Types.seqflatten(arg)
            
        Arguments
        ---------
        arg : list[list]
            a list of nested lists.
      
        Returns
        -------
        flat : list
            a list from which all nested elements have been flatten from 1 "level"
            up.
            
        Examples
        --------
        
        ::
            
            >>> happyType.seqflatten([[1],[[2,3],[4,5]],[6,7]])
                [1, [2, 3], [4, 5], 6, 7]
            >>> happyType.seqflatten([[1,1],[[2,2],[3,3],[[4,4],[5,5]]]])
                [1, 1, [2, 2], [3, 3], [[4, 4], [5, 5]]]
        """
        return list(itertools.chain.from_iterable(arg))

