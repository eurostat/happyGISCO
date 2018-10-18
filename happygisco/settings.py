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

*require*:      :mod:`sys`, :mod:`warnings`, :mod:`six`, :mod:`inspect`, :mod:`collection`, :mod:`itertools`, :mod:`functools`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Mar 31 21:54:08 2018

#%%
#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

PACKAGE             = "happygisco"

PROTOCOLS           = ('http', 'https', 'ftp')
"""Recognised protocols (APIs, bulk downloads,...).
"""
DEF_PROTOCOL        = 'https' # 'http'
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
GISCO_CACHEDOMAIN   = 'eurostat/cache/GISCO/distribution/v2'
"""Domain of cache database, *e.g.* countries and |NUTS| vector datasets themes, 
for download/distribution.
"""
GISCO_CACHEURL      = 'ec.%s/%s' % (EC_DOMAIN, GISCO_CACHEDOMAIN) 
"""Complete URL of |GISCO| cache database.
"""

GISCO_NUTSTHEME     = 'nuts'
"""NUTS theme used for URL naming.
"""
GISCO_NUTSDOMAIN    = GISCO_NUTSTHEME
"""Subdomain of |NUTS|.
"""
GISCO_NUTSURL       = '%s/%s' % (GISCO_CACHEURL, GISCO_NUTSDOMAIN) 
"""Complete URL of |NUTS| download/distribution services.
"""
GISCO_CTRYTHEME     = 'countries'
"""NUTS theme used for URL naming.
"""
GISCO_CTRYDOMAIN    = GISCO_CTRYTHEME
"""Subdomain of countries.
"""
GISCO_CTRYURL       = '%s/%s' % (GISCO_CACHEURL, GISCO_CTRYDOMAIN) 
"""Complete URL of countries download/distribution services.
"""

GISCO_PATTERNS      = {'bulk': 
                            {'domain':      'download', 
                             'compress':    'zip'
                             },
                       'distribution': 
                            {'domain':      GISCO_CACHEDOMAIN, 
                             'base':        ''
                             },                             
                       'country':
                            {'theme':       GISCO_CTRYTHEME, 
                             'domain':      'distribution', # GISCO_CTRYDOMAIN,
                             'base':        'CNTR_',
                             'info':        'countries-{year}-units', 
                             'bulk':        'ref-countries-',
                             'fmt':         'json'
                             },
                       'nuts':
                            {'theme':       GISCO_NUTSTHEME, 
                             'domain':      'distribution', # GISCO_NUTSDOMAIN,
                             'base':        'NUTS_',
                             'info':        'nuts-{year}-units', 
                             'bulk':        'ref-nuts-',
                             'fmt':         'json'
                             },
                        'nutsid':
                            {'info':        'NUTS_AT_{year}',
                             'fmt':         'csv'
                             }
                       }
"""String patterns used to define:
    
* domains of the services used for theme vector datasets: :literal:`download` for 
  bulk datasets or :literal:`distribution` for single areas,
* name and type of the file storing all :literal:`nuts` unit datasets,
* name and type of the file storing all :literal:`country` unit datasets,
* Name and type of the file storing the correspondance table between NUTS names
and their IDs.
"""

GISCO2GDAL_DRIVERS  = {'geojson': 
                            {'driver':      'GeoJSON',
                             'options':     ['RFC7946=YES', 'WRITE_BBOX=YES']
                             },
                        #  'topojson':
                        #        {'driver':       'TopoJSON',
                        #         'options':      None 
                        #         },
                       'shp': 
                            {'driver':      'ESRI Shapefile',
                             'options':      None 
                             }
                       }
"""Driver and translate options between |GISCO| disseminated dataset formats 
and |GDAL| accepted formats.
"""
DEF_DRIVER_NAME         = 'ESRI Shapefile'
"""|GDAL| driver name.
"""             

GISCO_DATA_INPUT    = ['UNIT', 'FILE', 'URL', 'LAYER', 'FEATURE', 'GEOMETRY', 'RESPONSE', 'CONTENT']
"""Type/nature of data parsing a given |GISCO| dataset, *e.g.* a NUTS or a country 
file.
"""
GISCO_DATA_DIMENSIONS = ['SOURCE', 'YEAR', 'PROJECTION', 'SCALE', 'VECTOR', 'LEVEL', 'IFORMAT'
                         ]
"""Descriptors/parameters used to define a given |GISCO| dataset, *e.g.* a NUTS
or a country file.
"""
GISCO_YEARS         = [2003, 2006, 2010, 2013, 2016
                       ]
"""Years of adoption/revision of |NUTS| areas.
"""
DEF_GISCO_YEAR      = 2016
"""Default year considered for |NUTS| datasets (not the most recent, but up-to-date).
"""
GISCO_PROJECTIONS   = {'WGS84':             4326,
                       'EPSG4326':          4326, 
                       # 'longlat':           4326,
                       'ETRS89':            4258,
                       'EPSG4258':          4258, 
                       'longlat':           4258,
                       'Mercator':          3857,
                       'merc':              3857,
                       'EPSG3857':          3857, 
                       'LAEA':              3035,
                       'EPSG3035':          3035,
                       'laea':              3035
                       }
"""Projections and EPSG codes currently supported by |GISCO| services. 
See http://spatialreference.org for the list of all EPSG codes and corresponding 
spatial references.
"""
DEF_GISCO_PROJECTION = 4326
"""Default projection used by |GISCO| services.
"""
GISCO_SCALES        = {1: '01m', 3: '03m', 10: '10m', 20: '20m', 60: '60m'
                       } 
"""Scale (1:`scale` Million) of vector datasets.
"""
DEF_GISCO_SCALE    = GISCO_SCALES[max(GISCO_SCALES.keys())] # largest scale: '60m'
"""Default scale for |GISCO| vector datasets.
"""
GISCO_VECTORS      = {'region':            'RG', 
                      'label':             'LB',
                      'line':              'BN',
                      'boundary':          'BN'
                      }
"""Dictionary of spatial typologies, *i.e.* the vector features of |GISCO| datasets. 
"""
DEF_GISCO_VECTOR    = 'RG'
"""Default spatial typology.
"""
GISCO_LEVELS        = [0, 1, 2, 3
                       ]
"""Levels of |NUTS| areas.
"""
DEF_GISCO_LEVEL     = GISCO_LEVELS[0]
"""Default |NUTS| level.
"""
GISCO_FORMATS       = {'shp':               'shx',   # 'shapefile': 'shp', 
                       'geojson':           'geojson',  
                       'topojson':          'json',  # useless topojson, see NUTS2JSON instead
                       # 'gdb':               'gdb', # bah...
                       'pbf':               'pbf',
                       'csv':               'csv'
                       # 'eps':             'eps'    # seriously? who gives a shit about EPS?
                       }
"""Format of |GISCO| vector data files.
"""
DEF_GISCO_FORMAT    = 'geojson'
"""Default format for |GISCO| vector datasets.
"""

GISCO_TILEDOMAIN    = 'webtools/maps/tiles'
"""Domain of |GISCO| background tiling service.
"""
GISCO_TILEURL       = '%s/%s' % (EC_DOMAIN, GISCO_TILEDOMAIN) 
"""Complete URL of |GISCO| background tiling service.
"""
GISCO_TILES         = {'bmarble':           
                            {'bckgrd':      'bmarble', 
                             'proj':        True,           
                             'attr':        '© NASA’s Earth Observatory', 
                             'label':       'Blue marble mosaic of Earth'
                             },
                       'boundaries':        
                           {'bckgrd':       'countryboundaries_world', 
                            'proj':         True, 
                            'attr':         '© Eurogeographics @UN-FAO @Turkstat', 
                            'label':        'boundaries of all countries'},
                       'roadswater':       
                           {'bckgrd':       'roadswater_europe', 
                            'proj':         True, 
                            'attr':         '© Eurogeographics', 
                            'label':        'cities, roads and rivers'},
                       'hypso':             
                           {'bckgrd':       'hypso', 
                            'proj':         True,             
                            'attr':         '© Natural Earth', 
                            'label':        'climate shaded relief of Earth'},
                       'coast':             
                           {'bckgrd':       'coast', 
                            'proj':         True,             
                            'attr':         '© EC-GISCO', 
                            'label':        'continental outlines'},
                       'copernicus':        
                           {'bckgrd':       'copernicus003', 
                            'proj':         False,    
                            'attr':         '© Core003 Mosaic', 
                            'label':        'Copernicus Core003'},
                       'osmec':             
                           {'bckgrd':       'osm-ec', 
                            'proj':         False,           
                            'attr':         '© OpenStreetMap', 
                            'label':        'OpenStreetMap'},
                       'graybg':            
                           {'bckgrd':       'gray-bg', 
                            'proj':         True,           
                            'attr':         '© Eurogeographics', 
                            'label':        'boundaries on gray background'},
                       'countrynames':           
                           {'bckgrd':       'countrynames_europe', 
                            'proj':         True, 
                            'attr':         '© Eurogeographics', 
                            'label':        'European country names'},
                       'gray':              
                           {'bckgrd':       'gray', 
                            'proj':         True,              
                            'attr':         '© Natural Earth', 
                            'label':        'gray shaded relief of Earth'},
                       'natural':           
                           {'bckgrd':       'natural', 
                            'proj':         True,           
                            'attr':         '© Natural Earth', 
                            'label':        'landcover shaded relief of Earth'},
                       'citynames':              
                           {'bckgrd':       'citynames_europe', 
                            'proj':         True,  
                            'attr':         '© Eurogeographics', 
                            'label':        'names of settlement'},
                       'cloudless':         
                           {'bckgrd':       'sentinelcloudless', 
                            'proj':         False,
                            'attr':         'Sentinel Cloudless', 
                            'label':        'Sentinel Cloudless' } 
                       }
"""Dictionary for the various |GISCO| background tiles service. See the list
of `available tiles servers <https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=webtools&title=Map+-+available+tiles+servers>`_.
"""
GISCO_TILEORDER     = '{z}/{y}/{x}'
"""|GISCO| background tile ordering (used for visualisation).
"""
DEF_GISCO_TILE      = 'osmec' # 'bmarble'
"""Default |GISCO| background tile.
"""
DEF_GISCO_TILEPROJ  = 3857
"""Default |GISCO| background tile projection.
"""
DEF_GISCO_ZOOM      = 4
"""Default zooming value in map displays.
"""

GISCO_LAUDOMAIN     = 'documents/345175/501971'
"""
"""
GISCO_LAUURL        = '%s/%s' % (ESTAT_URL, GISCO_LAUDOMAIN) 
"""Complete URL of |GISCO| LAU resources.
"""
NUTS2LAU            =  {2016: 
                            {2018:          'EU-28-LAU-2018-NUTS-2016.xlsx',
                             2017:          'EU-28_LAU_2017_NUTS_2016.xlsx'
                             },
                        2013: 
                            {2017:          'EU-28_LAU_2017_NUTS_2013.xlsx',
                             2016:          'EU-28_LAU_2016',
                             2015:          'EU-28_2015.xlsx',
                             2014:          'EU-28_2014.xlsx',
                             2013:          'EU-28_2013.xlsx',
                             2012:          'EU-28_2012.xlsx',
                             2011:          'EU-28_2011.xlsx',
                             2010:          'EU-28_2010.xlsx'
                             }
                        }
"""Conversion tables between LAU and NUTS datasets.
"""
NUTS_FORMATS        = {'geojson':           'json',  
                       # 'topojson':         'json',
                       'geopandas':         'gpd',
                       'text':              'txt'
                       }

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
NUTS2JSON_SCALES    = GISCO_SCALES.copy()
"""Map dimension (in pixel) adopted for the fetching of |Nuts2json|. Currently, 
all maps are squared.
"""
DEF_NUTS2JSON_SCALE = DEF_GISCO_SCALE
"""Default map dimension (in pixel).
"""
NUTS2JSON_LEVELS    = GISCO_LEVELS
NUTS2JSON_DATA_DIMENSIONS = GISCO_DATA_DIMENSIONS
# dumb variables

OSM_URL           = 'nominatim.openstreetmap.org/'
"""|OSM| web-service complete URL.
"""
CODER_OSM         = 'osm'
"""Identifier of |OSM| geocoder.
"""
KEY_OSM           = None
"""Dummy |OSM| key (connection to |OSM| web-services does not require authentication).
"""

# dummy variables
CHECK_TYPE          = True
CHECK_OSM_KEY       = False # True

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
CODER_PROJECTIONS   = {CODER_GISCO:         DEF_GISCO_PROJECTION,
                       CODER_GOOGLE:        'EPSG3857',
                       CODER_GOOGLE_MAPS:   'EPSG3857', 
                       CODER_GOOGLE_PLACES: 'EPSG3857'
                       }
"""Default geographical projections available with the different geocoders.
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
EU_AGGREGATES       = { 'EU28':             ['BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 
                                             'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 
                                             'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE', 'UK'],
                        'EU27':             ['BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 
                                             'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 
                                             'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE'],
                        'EFTA':             ['IS', 'LI', 'NO', 'CH'],
                        'CACO':             ['ME', 'MK', 'AL', 'RS', 'TR']
                        }
"""ISO-codes of countries (Member States) in the EU and other euro area aggregates;
see `this page <https://ec.europa.eu/eurostat/statistics-explained/index.php/Tutorial:Country_codes_and_protocol_order>`_.
"""

POLYLINE            = False
"""
Boolean flag set to import the package :mod:`polylines` that will enable you to 
generate polylines (see the `package website <https://pypi.python.org/pypi/polyline/>`_). 
Not really necessary to generate the routes.
"""

HTTP_ERROR_STATUS   = { # Informational.
                        100:
                            {'name':        'Continue', 
                             'desc':        'Continue with the request.'
                             },
                        101: 
                            {'name':        'Switching Protocols', 
                             'desc':        'Server is switching to a different protocol.'
                             },
                        102: 
                            {'name':        'Processing', 
                             'desc':        'Server has received and is processing the request, but no response is available yet.'
                             },
                        # Success
                        200: 
                            {'name':        'OK', 
                             'desc':        'Request was successful.'
                             },
                        201: 
                            {'name':        'Created', 
                             'desc':        'Request was successful, and a new resource has been created.'
                             },
                        202: 
                            {'name':        'Accepted', 
                             'desc':        'Request has been accepted but not yet acted upon.'
                             },
                        203: 
                            {'name':        'Non-Authoritative Information', 
                             'desc':        'Request was successful, but server is returning information that may be from another source.'
                             },
                        204: 
                            {'name':        'No Content', 
                             'desc':        'There is no content to send for this request, but the headers may be useful.'
                             },
                        205: 
                            {'name':        'Reset Content', 
                             'desc':        'Server successfully processed the request, but is not returning any content.'
                             },
                        206: 
                            {'name':        'Partial Content', 
                             'desc':        'Download is separated into multiple streams, due to range header.'
                             },
                        207: 
                            {'name':        'Multi-Status', 
                             'desc':        'Message body that follows is an XML message and can contain a number of separate response codes.'
                             },
                        208: 
                            {'name':        'Already Reported', 
                             'desc':        'Response is a representation of the result of one or more instance-manipulations applied to the current instance.'
                             },
                        226: 
                            {'name':        'IM Used', 
                             'desc':        'The server has fulfilled a GET request for the resource, and the response is a representation of the result of one or more instance-manipulations applied to the current instance.'
                             },
                        # Redirection.
                        300: 
                            {'name':        'Multiple Choices', 
                             'desc':        'Request has more than one possible response.'
                             },
                        301: 
                            {'name':        'Moved Permanently', 
                             'desc':        'URI of this resource has changed.'
                             },
                        302: 
                            {'name':        'Found', 
                             'desc':        'URI of this resource has changed, temporarily.'
                             },
                        303: 
                            {'name':        'See Other', 
                             'desc':        'Client should get this resource from another URI.'
                             },
                        304: 
                            {'name':        'Not Modified', 
                             'desc':        'Response has not been modified, client can continue to use a cached version.'
                             },
                        305: 
                            {'name':        'Use Proxy', 
                             'desc':        'Requested resource may only be accessed through a given proxy.'
                             },
                        306: 
                            {'name':        'Switch Proxy', 
                             'desc':        'No longer used. Requested resource may only be accessed through a given proxy.'
                             },
                        307: 
                            {'name':        'Temporary Redirect', 
                             'desc':        'URI of this resource has changed, temporarily. Use the same HTTP method to access it.'
                             },
                        308: 
                            {'name':        'Permanent Redirect', 
                             'desc':        'The request, and all future requests should be repeated using another URI.'
                             }, 
                        # Client Error.
                        400: 
                            {'name':        'Bad Request', 
                             'desc':        'Server could not understand the request, due to invalid syntax.'
                             },
                        401: 
                            {'name':        'Unauthorized', 
                             'desc':        'Authentication is needed to access the given resource.'
                             },
                        402: 
                            {'name':        'Payment Required', 
                             'desc':        'Some form of payment is needed to access the given resource.'
                             },
                        403: 
                            {'name':        'Forbidden', 
                             'desc':        'Client does not have rights to access the content.'
                             },
                        404: 
                            {'name':        'Not Found', 
                             'desc':        'Server cannot find requested resource.'
                             },
                        405: 
                            {'name':        'Method Not Allowed', 
                             'desc':        'Server has disabled this request method and cannot be used.'
                             },
                        406: 
                            {'name':        'Not Acceptable', 
                             'desc':        'Requested resource is only capable of generating content not acceptable according to the Accept headers sent.'
                             },
                        407: 
                            {'name':        'Proxy Authentication Required', 
                             'desc':        'Authentication by a proxy is needed to access the given resource.'
                             },
                        408: 
                            {'name':        'Request Timeout', 
                             'desc':        'Server would like to shut down this unused connection.'
                             },
                        409: 
                            {'name':        'Conflict', 
                             'desc':        'Request could not be processed because of conflict in the request, such as an edit conflict.'
                             },
                        410: 
                            {'name':        'Gone', 
                             'desc':        'Requested content has been delected from the server'
                             },
                        411: 
                            {'name':        'Length Required', 
                             'desc':        'Server requires the Content-Length header to be defined.'
                             },
                        412: 
                            {'name':        'Precondition Failed', 
                             'desc':        'Client has indicated preconditions in its headers which the server does not meet.'
                             },
                        413: 
                            {'name':        'Request Entity Too Large', 
                             'desc':        'Request entity is larger than limits defined by server.'
                             },
                        414: 
                            {'name':        'Request-URI Too Long', 
                             'desc':        'URI requested by the client is too long for the server to handle.'
                             },
                        415: 
                            {'name':        'Unsupported Media Type', 
                             'desc':        'Media format of the requested data is not supported by the server.'
                             },
                        416: 
                            {'name':        'Requested Range Not Satisfiable', 
                             'desc':        "Range specified by the Range header in the request can't be fulfilled."
                             },
                        417: 
                            {'name':        'Expectation Failed', 
                             'desc':        "Expectation indicated by the Expect header can't be met by the server."
                             },
                        418: 
                            {'name':        'I\'m a Teapot', 
                             'desc':        'HTCPCP server is a teapot; the resulting entity body may be short and stout.'
                             },
                        419: 
                            {'name':        'Authentication Timeout',     
                             'desc':        'Authentication Timeout.'
                             },
                        422: 
                            {'name':        'Unprocessable Entity', 
                             'desc':        'Request was well-formed but was unable to be followed due to semantic errors.'
                             },
                        423: 
                            {'name':        'Locked', 
                             'desc':        'Resource that is being accessed is locked.'
                             },
                        424: 
                            {'name':        'Failed Dependency', 
                             'desc':        'Request failed due to failure of a previous request (e.g. a PROPPATCH).'
                             },
                        #425:  
                        #    {'name':        'Unordered Collection', 
                        #     'desc':        'unordered'
                        #     },
                        426: 
                            {'name':        'Upgrade Required', 
                             'desc':        'Client should switch to a different protocol such as TLS/1.0.'
                            },
                        428: 
                            {'name':        'Precondition Required', 
                             'desc':        'Origin server requires the request to be conditional.'
                             },
                        429: 
                            {'name':        'Too Many Requests', 
                             'desc':        'User has sent too many requests in a given amount of time.'
                             },
                        431: 
                            {'name':        'Header Fields Too Large', 
                             'desc':        'Server rejected the request because either a header, or all the headers collectively, are too large.'
                             },
                        440: 
                            {'name':        'Login Timeout', 
                             'desc':        'Your session has expired. (Microsoft)'
                             },
                        444: 
                            {'name':        'No Response', 
                             'desc':        'Server has returned no information to the client and closed the connection (Ngnix).'
                             },
                        449: 
                            {'name':        'Retry With', 
                             'desc':        'Request should be retried after performing the appropriate action (Microsoft).'
                             },
                        450: 
                            {'name':        'Blocked By Windows Parental Controls', 
                             'desc':        'Windows Parental Controls are turned on and are blocking access to the given webpage.'
                             },
                        451: 
                            {'name':        'Unavailable For Legal Reasons', 
                             'desc':        'You attempted to access a Legally-restricted Resource. This could be due to censorship or government-mandated blocked access.'
                             },
                        494: 
                            {'name':        'Request Header Too Large', 
                             'desc':        'Nginx internal code'
                             },
                        495: 
                            {'name':        'Cert Error', 
                             'desc':        'SSL client certificate error occurred.'
                             },
                        496: 
                            {'name':        'No Cert', 
                             'desc':        'Client did not provide certificate.'
                             },
                        497: 
                            {'name':        'HTTP to HTTPS', 
                             'desc':        'Plain HTTP request sent to HTTPS port.'
                             },
                        499: 
                            {'name':        'Client Closed Request', 
                             'desc':        'Connection has been closed by client while the server is still processing its request.'
                             },
                        # Server Error.
                        500: 
                            {'name':        'Internal Server Error', 
                             'desc':        "Server has encountered a situation it doesn't know how to handle."
                             },
                        501: 
                            {'name':        'Not Implemented', 
                             'desc':        'Request method is not supported by the server and cannot be handled.'
                             },
                        502: 
                            {'name':        'Bad Gateway', 
                             'desc':        'Server, while working as a gateway to get a response needed to handle the request, got an invalid response.'
                             },
                        503: 
                            {'name':        'Service Unavailable', 
                             'desc':        'Server is not yet ready to handle the request.'
                             },
                        504: 
                            {'name':        'Gateway Timeout', 
                             'desc':        'Server is acting as a gateway and cannot get a response in time.'
                             },
                        505: 
                            {'name':        'HTTP Version Not Supported', 
                             'desc':        'HTTP version used in the request is not supported by the server.'
                             },
                        506: 
                            {'name':        'Variant Also Negotiates', 
                             'desc':        'Transparent content negotiation for the request results in a circular reference.'
                             },
                        507: 
                            {'name':        'Insufficient Storage', 
                             'desc':        'Server is unable to store the representation needed to complete the request.'
                             },
                        508: 
                            {'name':        'Loop Detected', 
                             'desc':        'The server detected an infinite loop while processing the request'
                             },
                        #509: 
                        #    {'name':        'Bandwidth Limit Exceeded', 
                        #     'desc':        'This status code, while used by many servers, is not specified in any RFCs.'
                        #     },
                        510: 
                            {'name':        'Not Extended', 
                             'desc':        'Further extensions to the request are required for the server to fulfill it.'
                             },
                        511: 
                            {'name':        'Network Authentication', 
                             'desc':        'The client needs to authenticate to gain network access.'
                             }
}
"""Descriptions of HTTP status codes. See https://en.wikipedia.org/wiki/List_of_HTTP_status_codes.
"""