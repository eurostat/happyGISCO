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
DEF_GISCO_YEAR      = 2013
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
GISCO_NUTSLEVELS    = [0, 1, 2, 3
                       ]
"""Levels of |NUTS| areas.
"""
DEF_GISCO_NUTSLEVEL = GISCO_NUTSLEVELS[0]
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
NUTS2JSON_NUTSLEVELS = GISCO_NUTSLEVELS
NUTS2JSON_DATA_DIMENSIONS = GISCO_DATA_DIMENSIONS
# dumb variables

OSM_URL             = 'nominatim.openstreetmap.org/'
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

