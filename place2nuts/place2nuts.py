#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_place2nuts

Module for place/location identification and NUTS identifier retrieval.

**About**

*credits*:      `grazzja <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      0.1
--
*since*:        Tue Mar 20 08:38:26 2018

**Description**

Perform offline or online queries in order to define unambiguously geographic 
locations and their NUTS identifiers.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`json`

*optional*:     :mod:`requests`, :mod:`osgeo`, :mod:`googlemaps`, :mod:`googleplaces`

*call*:         :mod:`settings`         

**Contents**

.. Links

.. _googlemaps: https://pypi.python.org/pypi/googlemaps
.. |googlemaps| replace:: `googlemaps <googlemaps_>`_
.. _googleplaces: https://github.com/slimkrazy/python-google-places
.. |googleplaces| replace:: `googleplaces <googleplaces_>`_

"""

# generic import
import os, sys#analysis:ignore
import warnings

import functools#analysis:ignore

# requirements
try:                                
    GISCO_SERVICE = True
    import requests # urllib2
except ImportError:                 
    warnings.warn('REQUESTS package (https://pypi.python.org/pypi/requests/) not loaded - GISCO ONLINE service will not be accessed')
    GISCO_SERVICE = False

try:
    from osgeo import ogr
except ImportError:
    # GDAL_RESOURCE = False
    warnings.warn('GDAL package (https://pypi.python.org/pypi/GDAL) not loaded - Inline resources not available')
else:
    print('GDAL help: https://pcjericks.github.io/py-gdalogr-cookbook/index.html')
    
try:
    API_SERVICE = True
    import googlemaps
except ImportError:
    API_SERVICE = False
    warnings.warn('GOOGLEMAPS package (https://pypi.python.org/pypi/googlemaps/) not loaded')
else:
    print('GOOGLEMAPS help: https://github.com/googlemaps/google-maps-services-python')

try:
    import googleplaces
except ImportError:
    warnings.warn('GOOGLEPLACES package (https://github.com/slimkrazy/python-google-places) not loaded')   
else:
    API_SERVICE = True
    print('GOOGLEPLACES help: https://github.com/slimkrazy/python-google-places')

try:
    import geopy
except ImportError:
    warnings.warn('GEOPY package (https://github.com/geopy/geopy) not loaded')   
else:
    API_SERVICE = True
    print('GEOPY help: http://geopy.readthedocs.io/en/latest/')
   
try:
    assert geopy or googlemaps or googleplaces
except:
    API_SERVICE = False
    warnings.warn('external API service not available')
    
try:                                
    import simplejson as json
except ImportError:
    warnings.warn("missing SIMPLEJSON package (https://pypi.python.org/pypi/simplejson/)", ImportWarning)
    try:                                
        import json
    except ImportError: 
        warnings.warn("JSON module missing in Python Standard Library", ImportWarning)
        class json:
            def loads(arg):  return '%s' % arg

try:
    import numpy as np
except ImportError:
    pass

# local imports
import settings
from settings import nutsVerbose
      

#%%
#==============================================================================
# CLASS _geoDecorators
#==============================================================================
    
class _geoDecorators(object):
    """Base class with dummy decorators used to parse and check place and coordinate 
    arguments, and not only, used in the various methods of the geolocation services 
    classes.
    """
    
    KW_PLACE        = 'place'
    KW_LAT          = 'lat'
    KW_LON          = 'lon'
    KW_COORD        = 'coord'
    KW_PROJECTION   = 'proj' 
    
    #/************************************************************************/
    class __parse(object):
        """Base parsing class for geographical entities. All decorators in 
        :class:`_geoDecorators` will inherit from this class.
        """
        def __init__(self, func, obj=None, cls=None, method_type='function'):
            self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type     
        def __get__(self, obj=None, cls=None):
            if self.obj == obj and self.cls == cls:
                return self 
            if self.method_type=='property':
                return self.func.__get__(obj, cls)
            method_type = ( # note that we added 'property'
                'staticmethod' if isinstance(self.func, staticmethod) else
                'classmethod' if isinstance(self.func, classmethod) else
                'property' if isinstance(self.func, property) else 
                'instancemethod'
                )
            return object.__getattribute__(self, '__class__')( 
                self.func.__get__(obj, cls), obj, cls, method_type) 
        #def __get__(self, obj, objtype):
        #    # support instance methods
        #    return functools.partial(self.__call__, obj)
        def __getattribute__(self, attr_name): 
            try:
                return object.__getattribute__(self, attr_name) 
            except AttributeError:
                return getattr(self.func, attr_name)
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_place(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with place (topo,geo) names to functions and methods.
        """
        def __call__(self, *args, **kwargs):
            if args not in (None,()):      
                if all([isinstance(a,str) for a in args]):
                    place = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    place = args[0]
                else:   
                    raise IOError('input arguments not recognised')
            else:                           
                place = kwargs.pop('place', None)
            if place in (None,[],''):
                raise IOError('no input arguments passed')
            if not isinstance(place,(list,tuple)):
                place = [place,]
            if not all([isinstance(p,str) for p in place]):
                raise IOError('wrong format for input place')
            place = ['+'.join(p.replace(',',' ').split()) for p in place]
            return self.func(place, **kwargs)

    #/************************************************************************/
    class parse_coordinate(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lng)` geographical coordinates to functions and methods.
        """
        def __call__(self, *args, **kwargs):
            coord, lat, lon = None, None, None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2 and all([isinstance(args[0][i],(tuple,list)) for i in (0,1)]):
                        lat, lon = args[0]
                    elif all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
                elif len(args) == 1 and isinstance(args[0],(tuple,list)) and len(args[0])==2:
                    lat, lon = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],(tuple,list)) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    lat, lon = args
                else:   
                    raise IOError('input arguments not recognised')
            else:   
                coord = kwargs.pop('coord', None)         
                lat = kwargs.pop('lat', None) or kwargs.pop('x', None)
                lon = kwargs.pop('lon', None) or kwargs.pop('y', None)
            try:
                assert not(coord is None and lat is None and lon is None) 
            except AssertionError:
                raise IOError('no input arguments passed')
            try:
                assert coord is None or (lat is None and lon is None)
            except AssertionError:
                raise IOError('too many input arguments')
            if coord is not None:
                if not isinstance(coord,(list,tuple)):  
                    coord = [coord]
                try:
                    assert all(['lat' in c and 'lon' in c for c in coord])
                except AssertionError:
                    raise IOError('wrong dictionary keys for input coordinate argument')
                try:
                    lat, lon = [_ for _ in zip(*[(c['lat'], c['lon']) for c in coord])]
                except:
                    raise IOError('wrong input coordinate argument passed')
            if lat is None or lon is None:
                raise IOError('wrong geographical coordinates')
            lat, lon = [lat,], [lon,]
            if not len(lat) == len(lon):
                raise IOError('incompatible geographical coordinates')
            return self.func(lat, lon, **kwargs)
       
    #/************************************************************************/
    class parse_geometry(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lng)` geographical coordinates stored in GISCO-like
        formatted dictionary (from JSON response) to functions and methods.
        """
        KW_FEATURES     = 'features'
        KW_GEOMETRY     = 'geometry'
        KW_PROPERTIES   = 'properties'
        KW_TYPE         = 'type'
        KW_OSM_KEY      = 'osm_key'
        KW_COORDINATES  = 'coordinates'
        def __call__(self, *args, **kwargs):
            coord = None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
            else:   
                coord = kwargs.pop('coord', None)        
            if coord is not None:
                if isinstance(coord,(list,tuple)) and all([isinstance(c,dict) for c in coord]):      
                    coord_ = [c for c in coord                                                               \
                       if self.KW_GEOMETRY in c and self.KW_PROPERTIES in c and self.KW_TYPE in c                 \
                       and c[self.KW_TYPE]=='Feature'                                                 \
                       and (not(settings.CHECK_TYPE) or c[self.KW_GEOMETRY][self.KW_TYPE]=='Point')         \
                       and (not(settings.CHECK_OSM_KEY) or c[self.KW_PROPERTIES][self.KW_OSM_KEY]=='place') \
                       ]
                    coord = coord[0] if coord_==[] else coord_[0]  
                    coord = dict(zip(['lon','lat'],coord[self.KW_GEOMETRY][self.KW_COORDINATES]))
                kwargs.update(coord) 
                return self.func(**kwargs)
            else:
                return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_nuts(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with NUTS information stored in GISCO-like formatted dictionary (from JSON 
        response) to functions and methods.
        """
        KW_RESULTS      = 'results'
        KW_ATTRIBUTES   = 'attributes'
        KW_LEVEL        = 'LEVL_CODE'
        def __call__(self, *args, **kwargs):
            level = kwargs.pop('level',None)
            nuts = None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    nuts = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        nuts = args[0]
            else:   
                nuts = kwargs.pop('nuts', None)                  
            if nuts is None:
                # raise IOError('no NUTS parsed')
                return self.func(*args, **kwargs)
            if not isinstance(nuts,(list,tuple)):
                nuts = [nuts,]
            if not all([isinstance(n,dict) and self.KW_ATTRIBUTES in n for n in nuts]): 
                raise IOError('NUTS attribtues not recognised')
            if level is not None:
                nuts = [n for n in nuts if n[self.KW_ATTRIBUTES][self.KW_LEVEL] == str(level)]
            kwargs.update({'nuts': nuts}) 
            return self.func(**kwargs)
        
    #/************************************************************************/
    class parse_projection(__parse):
        """Generic class decorator used to parse keyword argument with projection 
        information to functions and methods.
        """
        PROJECTION      = {'WGS84': 4326, 4326: 4326,
                           4258: 4258,
                           'EPSG3857': 3857, 3857: 3857, 
                           'LAEA': 3035, 3035: 3035}
        def __call__(self, *args, **kwargs):
            proj = kwargs.pop('proj', 'WGS84')
            if proj not in list(self.PROJECTION.keys() | self.PROJECTION.values()):
                raise IOError('projection %s not supported' % proj)
            kwargs.update({'proj': self.PROJECTION[proj]})                  
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_year(__parse):
        """Generic class decorator used to parse keyword year argument used for  
        NUTS definition.
        """
        YEARS      = [2006, 2013, 2010, # 2016 ?
                      ]
        def __call__(self, *args, **kwargs):
            year = kwargs.pop('year', 2013)
            if year not in tuple(self.YEARS):
                raise IOError('year %s not supported' % year)
            kwargs.update({'year': year})                  
            return self.func(*args, **kwargs)

#==============================================================================
# CLASS OnlineService
#==============================================================================
    
#%%
class GISCOService(object):
    """Class providing geolocation methods based on GISCO online web-services.
    """
    
    CODER = {settings.CODER_GISCO: settings.KEY_GISCO}
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        """Initialisation of a :class:`GISCOService` instance.

            >>> x = GISCOService(**kwargs)
        """
        self.__session, self.__domain = None, ''
        try:
            assert GISCO_SERVICE is not False
        except:
            raise IOError('GISCO service not available')
        self.__session = requests.Session()
        self.__domain = kwargs.pop('domain', settings.GISCO_URL)

    #/************************************************************************/
    @property
    def domain(self):
        """
        """
        return self.__domain
    @domain.setter#analysis:ignore
    def domain(self, domain):
        if not isinstance(domain, str):
            raise IOError('wrong type for DOMAIN parameter')
        self.__domain = domain
        
    #/************************************************************************/
    @property
    def session(self):
        """
        """
        return self.__session
    #@session.setter#analysis:ignore
    #def session(self, session):
    #    if not isinstance(session, requests.sessions.Session):
    #        raise IOError('wrong type for SESSION parameter')
    #    self.__session = session
    
    #/************************************************************************/   
    def get_status(self, url):
        """Retrieve the header of a URL and return the server's status code.
        """ 
        try:
            response = self.session.head(url)
        except: # ConnectionError:
            raise IOError('connection failed')  
        else:
            nutsVerbose('response status from web-service: %s' % response.status_code)
        try:
            response.raise_for_status()
        except:
            raise IOError('wrong request formulated')  
        else:
            status = response.status_code
            response.close()
        return status
    
    #/************************************************************************/
    def get_response(self, url, **kwargs):
        """Retrieve the GET response of a URL.
        """
        try:
            response = self.session.get(url)                
        except:
            raise IOError('wrong request formulated')  
        else:
            nutsVerbose('response reason from web-service: %s' % response.reason)
        try:
            response.raise_for_status()
        except:
            raise IOError('wrong response retrieved')  
        return response   
    
    #/************************************************************************/
    @staticmethod
    def __build_url(*args, **kwargs):
        # retrieve parameters/build url
        if args not in (None,()):       domain = args[0]
        else:                           domain = kwargs.pop('domain','')
        url = domain.strip("/")
        protocol = kwargs.pop('protocol', settings.DEF_PROTOCOL)
        if protocol not in settings.PROTOCOLS:
            raise IOError('web protocol not recognised')
        if not url.startswith(protocol):  
            url = "%s://%s" % (protocol, url)
        if 'path' in kwargs:      
            url = "%s/%s" % (url, kwargs.pop('path'))
        if 'query' in kwargs:      
            url = "%s/%s?" % (url, kwargs.pop('query'))
        if kwargs != {}:
            #_izip_replicate = lambda d : [(k,i) if isinstance(d[k], (tuple,list))        \
            #        else (k, d[k]) for k in d for i in d[k]]
            _izip_replicate = lambda d : [[(k,i) for i in d[k]] if isinstance(d[k], (tuple,list))        \
                else (k, d[k])  for k in d]          
            filters = '&'.join(['{k}={v}'.format(k=k, v=v) for (k, v) in _izip_replicate(kwargs)])
            # filters = '&'.join(map("=".join,kwargs.items()))
            try:        
                last = url.rsplit('/',1)[1]
                if any([last.endswith(c) for c in ('?', '/')]):     sep = ''
            except:     
                sep = '?'
            url = "%s%s%s" % (url, sep, filters)
        return url

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Create a query URL to be be submitted GISCO geolocation web-service.
        
            >>> url = GISCOService.url_geocode(**filters)
           
        Keyword Arguments
        -----------------
        filters : dict
            define the parameters for web-service; allowed parameters are: 
            :literal:`q, lat, lon, distance_sort, limit, osm_tag`, and :literal:`lang`\ .
                
        Returns
        -------
        url : str
            link to GISCO web-service that returns the adequate 'geocode' results
            associated to a given place.

        Note
        ----
        The generic url formatting is: domain/api?{filters}
        
        Example
        -------
        >>> print GISCOService.url_geocode(place='paris, France')
            'http://europa.eu/webtools/rest/gisco/api?q=paris+France'
        """
        keys = ['q', 'lat', 'lon', 'distance_sort', 'limit', 'osm_tag', 'lang']
        url = self.__build_url(domain=self.domain, 
                               query='api', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        nutsVerbose('url used for geocoding service: %s' % url)
        return url
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Create a query URL to be be submitted GISCO geolocation web-service.
        
            >>> url = GISCOService.url_reverse(**filters)
           
        Keyword Arguments
        -----------------
        filters : dict
            define the parameters for web-service; allowed parameters are: 
            :literal:`lat, lon, radius, distance_sort, limit`, and :literal:`lang`\ .
                
        Returns
        -------
        url : str
            link to GISCO web-service that returns the name results associated
            to a given geolocation.

        Note
        ----
        The generic url formatting is: domain/reverse?{filters}.
        
        Example
        -------
        >>> print GISCOService.url_reverse(lon=10, lat=52)
            'http://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52'
        """
        keys = ['lat', 'lon', 'radius', 'distance_sort', 'limit', 'lang']
        url = self.__build_url(domain=self.domain, 
                               query='reverse', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        nutsVerbose('url used for reverse geocoding service: %s' % url)
        return url
    
    #/************************************************************************/
    @_geoDecorators.parse_projection
    def url_nuts(self, **kwargs):
        """Create a query URL to be submitted to the GISCO (simple) web-service 
        for NUTS codes identification.
        
            >>> url = GISCOService.url_nuts(**filters)
           
        Keyword Arguments
        -----------------
        filters : dict
            define the parameters for web-service; allowed parameters are: 
            :literal:`x, y, f, year, proj`, and :literal:`geometry`\ .
            
        Returns
        -------
        url : str
            link to NUTS web service to submit the specified 'NUTS' query that
            identifies the NUTS code of a given geolocation.
            
        Usage
        -----
        x=<lon>&y=<lat>&f=<JSON/XML>&year=<2013/2010/2006>&proj=3035&geometry=<N/Y>

        Note
        ----
        The generic url formatting is: domain/nuts/find-nuts.py?{filters}
        """
        keys = ['x', 'y', 'f', 'year', 'proj', 'geometry']
        url = self.__build_url(domain=self.domain, 
                               path='nuts', 
                               query='find-nuts.py', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        nutsVerbose('url used for NUTS identification service: %s' % url)
        return url
        
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs): # specific use
        """
        """
        if settings.VERBOSE and 'lat' in kwargs and 'lon' in kwargs:
            warnings.warn('location bias added to query: (lat=%s,lon=%s)' % (kwargs.get('lat'),kwargs.get('lon')))
        if settings.VERBOSE and 'N' in kwargs:
            warnings.warn('number of query results adapted to: %s' % kwargs.get('N'))
        if settings.VERBOSE and 'lang' in kwargs:
            warnings.warn('language of query results adjusted to: %s' % kwargs.get('lang'))
        coord = []
        for p in place:
            kwargs.update({'q': p})
            try:
                url = self.url_geocode(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise IOError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in({},None)
            except:
                raise IOError('geolocation for place %s not loaded' % p)
            try:
                assert 'features' in data and data['features'] != [] 
            except:
                raise IOError('geolocation for place %s not recognised' % p)      
            else:
                c = data.get('features')
                coord.append(c if len(c)>1 else c[0])
        return coord if len(coord)>1 else coord[0]
        
    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2place(self, lat, lon, **kwargs): # specific use
        """
        """
        if settings.VERBOSE and 'radius' in kwargs:
            warnings.warn('search radius provided: %s' % kwargs.get('radius'))
        if settings.VERBOSE and 'distance_sort' in kwargs:
            warnings.warn('results sorted by distance')
        if settings.VERBOSE and 'lang' in kwargs:
            warnings.warn('language of query results adjusted to: %s' % kwargs.get('lang'))
        place = []
        for i in range(len(lat)):
            kwargs.update({'lat': lat[i], 'lon': lon[i]})
            try:
                url = self.url_reverse(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise IOError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in({},None)
            except:
                raise IOError('place for geolocation (%s,%s) not loaded' % (lat[i], lon[i]))
            try:
                assert _geoDecorators.parse_geometry.KW_FEATURES in data     \
                    and data[_geoDecorators.parse_geometry.KW_FEATURES] != []
            except:
                raise IOError('place for geolocation (%s,%s) not recognised' % (lat[i], lon[i]))      
            else:
                p = data.get(_geoDecorators.parse_geometry.KW_FEATURES)
                place.append(p if len(p)>1 else p[0])
        return place[0] if len(place)==1 else place
    
    #/************************************************************************/
    @_geoDecorators.parse_year
    @_geoDecorators.parse_projection
    @_geoDecorators.parse_geometry
    @_geoDecorators.parse_coordinate
    def coord2nuts(self, lat, lon, **kwargs):
        """
        """
        kwargs.update({#'year': kwargs.pop('year',2013), 
                       # 'proj': kwargs.pop('proj',4326),
                       'geometry': kwargs.pop('geometry','N'),
                       'f': 'JSON'})
        nuts = []
        for i in range(len(lat)):
            kwargs.update({'x': lon[i], 'y': lat[i]})
            try:
                url = self.url_nuts(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise IOError('error NUTS request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data is not None
            except:
                raise IOError('NUTS of location (%s,%s) not loaded' % (lat[i], lon[i]))
            try:
                # assert 'results' in data and data['results'] != [] 
                assert _geoDecorators.parse_nuts.KW_RESULTS in data     \
                    and data[_geoDecorators.parse_nuts.KW_RESULTS] != []
            except:
                raise IOError('NUTS of location (%s,%s) not recognised' % (lat[i], lon[i]))      
            else:
                nuts = data.get(_geoDecorators.parse_nuts.KW_RESULTS)
        return nuts[0] if len(nuts)==1 else nuts

    #/************************************************************************/
    @_geoDecorators.parse_year
    @_geoDecorators.parse_projection
    @_geoDecorators.parse_place
    def place2nuts(self, place, **kwargs): # specific use
        coord = self.place2coord(place, **kwargs)
        lat, lon = _geoDecorators.parse_geometry(lambda **kw: [kw.get('lat'), kw.get('lon')])(coord)
        nuts = self.coord2nuts(lat, lon, **kwargs)
        res = _geoDecorators.parse_nuts(lambda **kw: kw.get('nuts'))(nuts, **kwargs)
        return res[0] if len(res)==1 else res
    
#/****************************************************************************/
# CLASS _geoCoderAPI    
# Class emulating :mod:`geopy` API.
# Available when module :mod:`geopy` is installed.
#/****************************************************************************/
try:    
    assert API_SERVICE and geopy
except (NameError,AssertionError): 
    class _geoCoderAPI(object):     
        CODER = {}
else:   
    class _geoCoderAPI(object):
        """Class emulating :mod:`geopy` API.

        Inherit all methods from original API.
        
        Most of the :class:`_geoCoderAPI` methods will be inherited by the class
        :class:`OfflineService` through composition and embedding in container 
        attributes. Following, usages are presented using :class:`OfflineService`\ .
        """

        CODER = {'GoogleV3':         None,   # API authentication is only required for Google Maps Premier customers
                 'Bing':             'key',  # valid Bing Maps API key
                 'GeoNames':         'username', # username required for API access
                 'YahooPlaceFinder': 'key',  # Key provided by Yahoo
                 'OpenMapQuest':     None,       # No API Key is needed by the Nominatim based platform
                 'MapQuest':         'key',  # API key provided by MapQuest
                 'LiveAddress':      'token',# Valid authentication token; LiveAddress geocoder provided by SmartyStreets
                 'Nominatim':        None,       # Nominatim geocoder for OpenStreetMap servers
                 } 

        DIST_FUNC = {'great_circle':'GreatCircleDistance',
                           'vincenty': 'VincentyDistance'}
        DIST_UNIT = {'km':'kilometers',
                           'mi': 'miles',
                           'm': 'meters',
                           'ft': 'feet'}
     
        #/********************************************************************/
        def __init__(self, **kwargs):
            # call geocoder module geopy: https://github.com/geopy/geopy'
            self._gc = None
            coder = kwargs.pop('geocoder', 'GeoNames')
            if coder not in self.CODER.keys():
                raise IOError('geocoder %s not recognised' % coder)
            try:        gc = getattr(geopy.geocoders, coder)   
            except:     raise IOError('module geopy not available')
            key = self.CODER[coder]
            if key is not None:          
                self.client_key = kwargs.pop(key,None)
                kwargs.update({key: self.client_key})
            else:   
                self.client_key = None                
            try:    self._gc = gc(**kwargs)  
            except: raise IOError('geocoder not available')

        #/********************************************************************/
        def __getattr__(self, method):
            # 'im_class': deal with 'im_class' as an instance is NOT callable...
            # '__objclass__': dont' ask for an explanation here: we just want to 
            # pass Sphinx Napoleon... 
            if method in ('im_class','__objclass__'): 
                return getattr(self._gc, '__class__')
            elif method.startswith('__'):  # to avoid some bug of the pylint editor
                try:        return object.__getattribute__(self, method) 
                except:     pass 
            # try:        return object.__getattribute__(self.__call__, method) 
            # except:     pass 
            # finally, what we are really interested in
            try:        return getattr(self._gc, method)
            except:     raise IOError('method %s not implemented' % method)

        # THIS SHOULD NOT BE A CALLABLE!
        #def __call__(self, *args, **kwargs):    pass
            
        #/********************************************************************/
        def update(self, coder, **kwargs): 
            # call method used for updating the default geocoder.
            pass
            # self._gc = None
            if self._gc is None or self._gc.__class__.__name__!=coder:
                gc = getattr(geopy.geocoders, coder) 
                self._gc = gc(**kwargs) 

        #/********************************************************************/
        def distance(self, *args, **kwargs):            
            if args in (None,()):           return
            else:                           locs = list(args)    
            nlocs = len(locs)
            code = kwargs.pop('dist', 'great_circle')
            unit = kwargs.pop('unit', 'km')
            if unit not in self.DIST_UNIT.keys():
                raise IOError('wrong unit for geodesic distance')
            if code not in self.DIST_FUNC.keys():
                raise IOError('wrong code for geodesic distance')
            try:    
                # in order to accept the 'getattr' below, the geopy.distance needs
                # to be loaded in the first place
                import geopy.distance
            except: 
                raise IOError('distance calculation not available')
            code = self.DIST_FUNC[code]
            distance = getattr(geopy.distance, code) 
            cunit = lambda d: getattr(d, self.DIST_UNIT[unit])
            for i in range(nlocs):
                if isinstance(locs[i],str):
                    try:        locs[i] = self.geocode(locs[i])
                    except:     
                        try:        locs[i] = self.geocode(locs[i], reverse=True)
                        except:     raise IOError('unable to find locations; enter lat/long')
                elif not(isinstance(locs[i],(list,tuple)) and len(locs[i])==2):
                    raise IOError('unexpected variable for lat/long')
            dist = np.zeros([nlocs,nlocs])
            np.fill_diagonal(dist, 0.)
            for i in range(nlocs):
                for j in range(i+1,nlocs):
                    dist[i][j] = dist[j][i] = cunit(distance(locs[i],locs[j]))
            if nlocs==2:        dist = dist[1][0]
            return dist

#==============================================================================
# CLASS _googleMapsAPI
# Class emulating googlemaps.GoogleMaps API.
# Available when module googlemaps is installed.
#==============================================================================
try:    
    assert API_SERVICE and googlemaps
except (NameError,AssertionError): 
    class _googleMapsAPI(object):     
        CODER = {}
else:   
    class _googleMapsAPI(googlemaps.Client):
        """Class emulating :class:`googlemaps.Client` API.

        Most of the :class:`googlemaps.Client` methods will be inherited by the
        :class:`OfflineService` class through composition and embedding in container attributes. 
        """

        CODER = {settings.CODER_GOOGLE_MAPS: settings.KEY_GOOGLE}

        #/********************************************************************/
        def __init__(self, **kwargs):
            # call Google Maps API: https://developers.google.com/maps/
            key = kwargs.pop(self.CODER[settings.CODER_GOOGLE_MAPS])
            if key is None or not isinstance(key,str):
                raise IOError('Google client key not recognised')
            self.client_key = key
            super(_googleMapsAPI,self).__init__(self.client_key)

        #/********************************************************************/
        def reverse(self, *args, **kwargs):
            info = kwargs.pop('info', False)
            try:
                geoinfo = self.reverse_geocode(*args, **kwargs) # OLD: address_to_latlng
            except:
                raise IOError('reverse geocoding method not found') 
            if info:
                return geoinfo
            location = geoinfo[0]['address_components']
            return [item['long_name'] for item in location]
                        
         #/********************************************************************/
        def geocode(self, arg, **kwargs):
            info = kwargs.pop('info', False)
            try:
                geoinfo = super(_googleMapsAPI,self).geocode(arg, **kwargs) # OLD: address_to_latlng
            except:
                raise IOError('geocoding method not found') 
            if info:
                return geoinfo
            location = geoinfo[0]['geometry']['location']
            return location['lat'], location['lng']
            
         #/********************************************************************/
        def distance(self, *args, **kwargs):
            info = kwargs.pop('info', False)
            dist, time = kwargs.pop('dist', True), kwargs.pop('time', False)
            res = {}
            try:
                dst_mx = super(_googleMapsAPI,self).distance_matrix(*args, **kwargs) 
            except:
                raise IOError('geocoding method not found') 
            if info:
                res = dst_mx
            else:
                dst_mx = dst_mx['rows'][0]['elements'][0]
                if time:                 
                    res.update({'duration': dst_mx['duration']}) # 'text' or 'value'
                if dist: 
                    res.update({'distance': dst_mx['distance']}) # 'text' or 'value'
            return res

#==============================================================================
# CLASS _googlePlacesAPI
# Class emulating googleplaces.GooglePlaces API.
# Available when module googleplaces is installed.
#==============================================================================
try:    
    assert API_SERVICE and googleplaces
except (NameError,AssertionError): 
    class _googlePlacesAPI(object):  
        CODER = {}
else: 
    class _googlePlacesAPI(googleplaces.GooglePlaces):
        
        CODER = {settings.CODER_GOOGLE_PLACES: settings.KEY_GOOGLE}

        #/********************************************************************/
        def __init__(self, **kwargs):
            # call Google Places API: https://developers.google.com/places
            key = kwargs.pop(self.CODER[settings.CODER_GOOGLE_PLACES])
            if key is None or not isinstance(key,str):
                raise IOError('GOoogle client key not recognised')
            self.client_key = key
            super(_googlePlacesAPI,self).__init__(self.client_key)

        #/********************************************************************/
        geocode = classmethod(googleplaces.geocode_location)
        # nearby_search, text_search, get_place are regular attributes

#==============================================================================
# CLASS APIService
#==============================================================================
     
#%%
class APIService(object):
    """
    """
    
    CODER = dict(_googlePlacesAPI.CODER.items()
                 | _googleMapsAPI.CODER.items() 
                 | _geoCoderAPI.CODER.items()) # we know there is no duplicate, so ok...
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        """Initialisation of a :class:`OfflineService` instance.

            >>> serv = OfflineService(**kwargs)

        Arguments
        ---------
        client_key : str
            key used to connect to the geolocation API, _e.g._:= Google Maps, 
            Google Places, _etc_...
        driver_name : str
            name of the driver used for vector files
        """
        # initial settings
        self.__coder, self.__coder_key = None, ''
        self.__driver, self.__drivername = None, ''
        # read the arguments              
        try:
            assert API_SERVICE is not False
        except:
            raise IOError('OFFLINE service not available')
        self.__coder = kwargs.pop('coder', settings.CODER_GOOGLE_MAPS)
        self.__coder_key  = kwargs.get(self.CODER[self.__coder]) # it is a get!!! maybe None
        self.__drivername   = kwargs.pop('driver_name', settings.DRIVER_NAME)
        if self.__coder in _googleMapsAPI.CODER.keys():
            try:
                # geomapper defined as an instance of _googleMapsAPI class derived
                # from googlemaps.GoogleMaps
                self.__coder = _googleMapsAPI(**kwargs) 
            except:
                raise IOError('Google Maps geocoder not available')
        elif self.__coder in _googlePlacesAPI.CODER.keys():
            try:
                # geolocator defined as an instance of _googlePlacesAPI class
                # derived from googleplaces.GooglePlaces
                self.__coder = _googlePlacesAPI(**kwargs) 
            except:
                raise IOError('Google Places geocoder not available')
        elif self.__coder in _geoCoderAPI.CODER.keys():
            try:
                # geocoder defined as an instance of _geoCoderAPI class derived from 
                # geopy.geocoders
                self.__coder = _geoCoderAPI(geocoder=self.__coder, **kwargs) 
            except:
                raise IOError('geopy geocoder not available')
        try:
            self.__driver = ogr.GetDriverByName(self.driver_name)
        except:
            try:
                self.__driver = ogr.GetDriver(0)
            except:
                raise IOError('driver not available')
            
    #/************************************************************************/
    @property
    def coder(self):
        return self.__coder
    
    @property
    def driver(self):
        return self.__driver
            
    @property
    def coder_key(self):
        return self.__coder_key
    @coder_key.setter#analysis:ignore
    def coder_key(self, key):
        if not isinstance(key, str):
            raise IOError('wrong type for CODER_KEY parameter')
        self.__coder_key = key
            
    @property
    def driver_name(self):
        return self.__driver_name
    @driver_name.setter#analysis:ignore
    def driver_name(self, driver_name):
        if not isinstance(driver_name, str):
            raise IOError('wrong type for DRIVER_NAME parameter')
        self.__driver_name = driver_name
    
    #/************************************************************************/
    def file2layer(self, filename):
        if not isinstance(filename, str):
            raise IOError('wrong type for FILENAME parameter')
        try:
            assert self.driver is not None
        except:
            raise IOError('offline driver not available')
        try:
            data = self.driver.Open(filename, 0) # 0 means read-only
            assert data is not None
        except:
            raise IOError('file %s not open' % filename)
        else:
            if settings.VERBOSE: print('file %s opened' % filename)
        try:
            layer = data.GetLayer()
            assert layer is not None
        except:
            raise IOError('could not get vector layer')
        return layer

    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs):
        coord = [] 
        for p in place:   
            try:
                geocode = self.coder.geocode(p)
                coord.append(geocode[0]['geometry']['location'])
                assert coord is not None
            except:
                coord.append(None)
                if settings.VERBOSE: print('\nCould not retrieve geolocation of %s' % p)
                # continue
            else:
                if settings.VERBOSE: print('%s => %s' % (place, coord))
                # continue
        return coord

    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2vec(self, lat, lng, **kwargs):
        vector = ogr.Geometry(ogr.wkbMultiPoint)
        for i in range(len(lat)):
            try:
                pt = ogr.Geometry(ogr.wkbPoint)
                pt.AddPoint(lng[i], lat[i]) 
            except:
                if settings.VERBOSE is True:
                        print('\nCould not add geolocation')
            else:
                vector.AddGeometry(pt)
        return vector

    #/************************************************************************/
    def vec2id(self, layer, vector):
        answer = [] # will be same lenght as self.vector
        featureCount = layer.GetFeatureCount()
        nutsVerbose('\nNumber of features in %s: %d' % (os.path.basename(NUTSFILE),featureCount))
        # iterate through points
        for i in range(0, self.vector.GetGeometryCount()): # because it is a MULTIPOINT
            pt = self.vector.GetGeometryRef(i)
            #print(pt.ExportToWkt())
            # iterate through polygons in layer
            for j in range(0, featureCount):
                feature = layer.GetFeature(j)
                if feature is None:
                    continue    
                #elif feature.geometry() and feature.geometry().Contains(pt):
                #    Regions.append(feature)
                ft = feature.GetGeometryRef()
                if ft is not None and ft.Contains(pt):
                    answer.append(feature)
            if len(answer)<i+1:    
                answer.append(None)
        return answer

    #/************************************************************************/
    def coord2nuts(self, *args, **kwargs):
        try:
            layer = self.file2layer(kwargs.pop('nuts_file',''))
            assert layer not in (None,[])
        except:
            raise IOError('could not load feature layer')
        try:
            vector = self.coord2vec(*args, **kwargs)
            assert vector not in (None,[])
        except:
            raise IOError('could not load geolocation vector')
        return self.vec2nuts(layer, vector)
    
#==============================================================================
# CLASS Place
#==============================================================================
            
class Place(object):

    def __init__(self, *args, **kwargs):
        try:
            dummy_id = lambda inst, place, **kwargs: place
            place = _geoDecorators.parse_place(dummy_id)(*args, **kwargs)
        except:
            place = None
        try:
            dummy_id = lambda inst, lat, lng, **kwargs: [lat, lng]
            lat, lng = _geoDecorators.parse_coordinate(dummy_id)(*args, **kwargs)
        except:
            lat, lng = None, None
        try:
            assert not(place is None and lat is None and lng is None)
        except:
            raise IOError('no geographical entity parsed to define the place')
        try:
            assert place is None or (lat is None and lng is None)
        except:
            raise IOError('too many geographical entities parsed to define the place')
        self.__place = place
        self.__lat, self.__lng = lat, lng

    @property
    def place(self):
        return self.__place
       
    @property
    def coord(self):
        return self.__coord
    
    def tourl(self):
        return ['+'.join(p.replace(',',' ').split()) for p in self.place]

    def __repr__(self):
        return [','.join(p.replace(',',' ').split()) for p in self.place]

    def tonuts(self, **kwargs):  
        pass


    def geocode(self, **kwargs):   
        """Convert place names to geographic coordinates (default) and reciprocally, 
        depending on the type of input arguments passed.
        
            >>> location = place.geocode(*args, **kwargs)

        Arguments
        ---------
        args : tuple, str
            a tuple representing (lat,Lon) coordinates, or a string representing
            either a place name, or again (lat,Lon) coordinates.
        
        Keyword Arguments
        -----------------        
        reverse : bool  
            set to :literal:`True` when `location` is passed as a tuple of (lat,Lon) so 
            that a place name is reverse; default: :literal:`False`

        Returns
        -------
        location : tuple, str
            a place name or a :data:`(lat,Lon)` tuple.

        Raises
        ------
        IOError:
            when unable to recognize address/location.

        Note
        ----
        It may return no results if it is passed a non-existent address or a lat/lng 
        in a remote location.

        Examples
        --------
        >>> print serv.code('Paris, France')
            (48.856614, 2.3522219)
        >>> paris = serv.code('48.85693, 2.3412', reverse=True)
        >>> print paris
            [u'76 Quai des Orf\xe8vres, 75001 Paris, France', u"Saint-Germain-l'Auxerrois, Paris, France", 
             u'75001 Paris, France', u'1er Arrondissement, Paris, France', u'Paris, France', 
             u'Paris, France', u'\xcele-de-France, France', u'France']
        >>> paris == serv.code(48.85693, 2.3412, reverse=True)
            True
        
        See also
        --------
        :meth:`~OfflineService.reverse`
        """
        service = kwargs.pop('serv',None)
        if service is None: # whatever works...
            try:
                assert GISCO_SERVICE is True 
                service = GISCOService()
            except:
                try:
                    assert API_SERVICE is True 
                    service = APIService()
                except:
                    raise IOError('No service available')
        elif isinstance(service, str):
            if service in GISCOService.CODER:
                service = GISCOService(coder=service)
            elif service in APIService.CODER:
                service = APIService(coder=service)
            else:
                raise IOError('service %s not available' % service)
        if not isinstance(service,(GISCOService,APIService)):
            raise IOError('service not supported')
        for p in self.place:   
            try:
                geocode = service.geocode(p)
                coord = geocode[0]['geometry']['location']
                assert coord is not None
            except:
                print('\nCould not retrieve geolocation of %s' % p)
                continue
            else:
                print('%s => %s' % (place, coord))
        return self.coord
        
    #/************************************************************************/
    # def geocode(self, *args, **kwargs): # specific use
        if args in((),(None,)):
            return
        elif not all([isinstance(a,str) for a in args]):
            if len(args)==1 and isinstance(args[0],(tuple, list)) and len(args[0])==2:
                args = args[0]
            elif not len(args)==2:
                raise IOError('unrecognised input location argument')
            args = ((str(args[0])+', '+str(args[1])), ) 
        else:
            pass
        reverse =  kwargs.pop('reverse', False) # internal dummy
        try:
            if reverse: loc = self.coder.reverse(*args)    
            else:       loc = self.coder.geocode(*args)
            assert loc
        except:     
            raise IOError('unrecognised address/location argument') 
        if not isinstance(loc,(list,tuple)):    
            loc, islist = [loc], False
        else:   islist = True
        if reverse:         loc = [l[0] for l in loc] 
        else:               loc = [l[1] for l in loc] 
        # note that in geopy, the indexing of locations is still supported
        # through the _tuple field and the special __getitem__ method
        return loc if islist else loc[0]
    
     #/************************************************************************/
    def reverse(self, *args):
        """Convert geographic location (passed as a tuple of coordinates or a string 
        with those coordinates). 
        
            >>> place = serv.reverse(*args)
        
        This is nothing else than a (dummy) shortcut to:
        
            >>> place = serv.code(*args, reverse=True)

        Arguments
        ---------
        args: tuple, str
            a tuple or a string representing (lat,Lon) coordinates.

        Returns
        -------
        place : str
            a place name.        

        Examples
        --------
        >>> paris = serv.reverse('48.85693, 2.3412') 
        >>> print paris
            [u'76 Quai des Orf\xe8vres, 75001 Paris, France', u"Saint-Germain-l'Auxerrois, Paris, France", 
             u'75001 Paris, France', u'1er Arrondissement, Paris, France', u'Paris, France', 
             u'Paris, France', u'\xcele-de-France, France', u'France']
        >>> paris == serv.reverse(48.85693, 2.3412)
            True
        """
        # geocode may return no results if it is passed a  
        # non-existent address or a lat/lng in a remote location
        # raise LocationError('unrecognised location argument')          
        return self.geocode(*args, reverse=True)
    
    def distance(self, *args, **kwargs):            
        """Method used for computing pairwise distances between given locations, 
        passed indifferently as places names or geographic coordinates.
        
            >>> D = _geoCoderAPI.distance(*args, **kwargs)
    
        Arguments
        ---------
        args : tuple, str
            a pair of locations represented either as tuple of (lat,Lon) coordinates
            or string of place name.
            
        Keyword Arguments
        -----------------        
        dist : str  
            name of the geo-principle used to estimate the distance: it is any string
            in :literal:`['great_circle','vincenty']`; see :meth:`geopy.distance` method; 
            default to :literal:`'great_circle'`.
        unit : str  
            name of the unit used to return the result: any string in the list
            :literal:`['km','mi','m','ft']`; default to :literal:`'km'`.
            
        Returns
        -------
        D : :class:`np.array`
            matrix of pairwise distances computed in `unit` unit.
        
        Raises
        ------
        IOError:
            when wrong unit/code for geodesic distance or when unable to find/recognize
            locations.
            
        Examples
        --------        
        >>> print _geoCoderAPI.distance((26.062951, -80.238853), (26.060484,-80.207268), 
        ...                             dist='vincenty', unit='m')
            3172.3596179302895
        >>> print _geoCoderAPI.distance((26.062951, -80.238853), (26.060484,-80.207268), 
        ...                             dist='great_circle', unit='km')
            3.167782321855102
        >>> print _geoCoderAPI.distance((26.062951, -80.238853), 'Paris, France', 
        ...                             dist='great_circle', unit='km')
            7338.5353364838438
        """
        pass
    
    
    @property
    def tovector(self):       
        if self.__vector in ([], None):
            location = ogr.Geometry(ogr.wkbMultiPoint)
            for p in self.coord:   
                try:
                    pt = ogr.Geometry(ogr.wkbPoint)
                    pt.AddPoint(self.coord['lng'], self.coord['lat']) 
                except:
                    if settings.VERBOSE is True:
                        print('\nCould not add geolocation')
                else:
                    location.AddGeometry(pt)
            self.__vector = location
        return self.vector
    
    def inlayer(self, layer):
        answer = [] # will be same lenght as self.vector
        featureCount = layer.GetFeatureCount()
        if settings.VERBOSE is True:
            print('\nNumber of features in %s: %d' % (os.path.basename(NUTSFILE),featureCount))
        # iterate through points
        for i in range(0, self.vector.GetGeometryCount()): # because it is a MULTIPOINT
            pt = self.vector.GetGeometryRef(i)
            #print(pt.ExportToWkt())
            # iterate through polygons in layer
            for j in range(0, featureCount):
                feature = layer.GetFeature(j)
                if feature is None:
                    continue    
                #elif feature.geometry() and feature.geometry().Contains(pt):
                #    Regions.append(feature)
                ft = feature.GetGeometryRef()
                if ft is not None and ft.Contains(pt):
                    answer.append(feature)
            if len(answer)<i+1:    
                answer.append(None)
        return answer

        
    #/************************************************************************/
    def place2nuts():
        return
    
    #/************************************************************************/
    def __call__(self, *args, **kwargs):
        return self.place2nuts(*args, **kwargs)
    
class NUTS(object):
    pass    


 #   http://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52
 #   http://europa.eu/webtools/rest/gisco/reverse?lat=2.3514992&lon=48.8566101
 #   http://europa.eu/webtools/rest/gisco/reverse?lat=2&lon=48

#def place2nuts(*args, **kwargs):
#    place = Place(*args, **kwargs)
#    nuts = NUTS(place.tonuts())
#    return nuts
#    
#    
#PLACES      = ['Bremen, Germany', 'Florence, Italy', 'Brussels, Belgium']
#GOOGLE_KEY  = '' # you need to provide your own API key here
#NUTSDIR     = 'ref-nuts-2013-01m'
#NUTSFILE    = 'NUTS_RG_01M_2013_4326_LEVL_2.shp' # region
#
#gmaps = googlemaps.Client(key=GOOGLE_KEY) 
#Locations = ogr.Geometry(ogr.wkbMultiPoint)
#
#try:
#    assert Locations is not None
#except:
#    print('\nCould not retrieve any geolocation')
#    raise IOError
#else:
#    print(Locations.ExportToWkt())
#
#try:
#    driver = ogr.GetDriverByName('ESRI Shapefile')
#    Nuts = driver.Open(os.path.join(NUTSDIR,NUTSFILE), 0) # 0 means read-only
#    assert Nuts is not None
#except:
#    print('\nCould not open %s' % NUTSFILE)
#    print('visit: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip')
#    raise IOError
#else:
#    print('\nOpened %s' % NUTSFILE)
#    print('NUTS help: http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf')
#    
#try:
#    layer = Nuts.GetLayer()
#    assert layer is not None
#except:
#    print('\nCould not get vector layer')
#    raise IOError
#else:
#    featureCount = layer.GetFeatureCount()
#    print('\nNumber of features in %s: %d' % (os.path.basename(NUTSFILE),featureCount))
#    
#Regions = []
#
## iterate through points
#for i in range(0, Locations.GetGeometryCount()): # because it is a MULTIPOINT
#    pt = Locations.GetGeometryRef(i)
#    #print(pt.ExportToWkt())
#    # iterate through polygons in layer
#    for j in range(0, featureCount):
#        feature = layer.GetFeature(j)
#        if feature is None:
#            continue    
#        #elif feature.geometry() and feature.geometry().Contains(pt):
#        #    Regions.append(feature)
#        ft = feature.GetGeometryRef()
#        if ft is not None and ft.Contains(pt):
#            Regions.append(feature)
#    if len(Regions)<i+1:    
#        Regions.append(None)
#
#try:
#    assert not all([region is None for region in Regions])
#except:
#    print('\nNUTS regions (level 2) not found')
#else:
#    print('\nNUTS regions (level 2) identified')
#    for i, place in enumerate(PLACES):
#        items = Regions[i].items()
#        print('%s => NUTS ID: %s - NUTS name: %s' % (place, items['NUTS_ID'],items['NUTS_NAME']))
## will display:
## Bremen, Germany => NUTS ID: DE50 - NUTS name: Bremen
## Florence, Italy => NUTS ID: ITI1 - NUTS name: Toscana
## Brussels, Belgium => NUTS ID: BE10 - NUTS name: Région de Bruxelles-Capitale / Brussels Hoofdstedelijk Gewest	
