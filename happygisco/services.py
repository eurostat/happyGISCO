#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_services

Module for place/location identification and NUTS identifier retrieval.

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      1
--
*since*:        Sat Apr  7 01:46:51 2018

**Description**

Perform offline or online queries in order to define unambiguously geographic 
locations and their NUTS identifiers.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`json`

*optional*:     :mod:`requests`, :mod:`googlemaps`, :mod:`googleplaces`

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

import functools#analysis:ignore

# local imports
from . import settings
from .settings import happyVerbose, happyWarning, _geoDecorators

# requirements
try:                                
    GISCO_SERVICE = True
    import requests # urllib2
except ImportError:                 
    happyWarning('REQUESTS package (https://pypi.python.org/pypi/requests/) not loaded - GISCO ONLINE service will not be accessed')
    GISCO_SERVICE = False
    
try:
    API_SERVICE = True
    import googlemaps
except ImportError:
    API_SERVICE = False
    happyWarning('GOOGLEMAPS package (https://pypi.python.org/pypi/googlemaps/) not loaded')
else:
    print('GOOGLEMAPS help: https://github.com/googlemaps/google-maps-services-python')

try:
    import googleplaces
except ImportError:
    happyWarning('GOOGLEPLACES package (https://github.com/slimkrazy/python-google-places) not loaded')   
else:
    API_SERVICE = True
    print('GOOGLEPLACES help: https://github.com/slimkrazy/python-google-places')

try:
    import geopy
except ImportError:
    happyWarning('GEOPY package (https://github.com/geopy/geopy) not loaded')   
else:
    API_SERVICE = True
    print('GEOPY help: http://geopy.readthedocs.io/en/latest/')
   
try:
    assert geopy or googlemaps or googleplaces
except:
    API_SERVICE = False
    happyWarning('external API service not available')
    
try:                                
    import simplejson as json
except ImportError:
    happyWarning("missing SIMPLEJSON package (https://pypi.python.org/pypi/simplejson/)", ImportWarning)
    try:                                
        import json
    except ImportError: 
        happyWarning("JSON module missing in Python Standard Library", ImportWarning)
        class json:
            def loads(arg):  return '%s' % arg

try:
    import numpy as np
except ImportError:
    pass

#%%
#==============================================================================
# CLASS GISCOService
#==============================================================================
    
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
        self.session = requests.Session()
        self.domain = kwargs.pop('domain', settings.GISCO_URL)
        self.arcgis = kwargs.pop('arcgis', settings.GISCO_ARCGIS)

    #/************************************************************************/
    @property
    def domain(self):
        """
        """
        return self.__domain
    @domain.setter#analysis:ignore
    def domain(self, domain):
        if domain is not None and not isinstance(domain, str):
            raise IOError('wrong type for DOMAIN parameter')
        self.__domain = domain or ''
        
    #/************************************************************************/
    @property
    def session(self):
        """
        """
        return self.__session
    @session.setter#analysis:ignore
    def session(self, session):
        if session is not None and not isinstance(session, requests.sessions.Session):
            raise IOError('wrong type for SESSION parameter')
        self.__session = session
    
    #/************************************************************************/   
    def get_status(self, url):
        """Retrieve the header of a URL and return the server's status code.
        """ 
        try:
            response = self.session.head(url)
        except requests.ConnectionError:
            raise IOError('connection failed')  
        else:
            happyVerbose('response status from web-service: %s' % response.status_code)
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
            # happyVerbose('response reason from web-service: %s' % response.reason)
            pass
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
            url = "%s/%s" % (url, kwargs.pop('query'))
        if kwargs != {}:
            #_izip_replicate = lambda d : [(k,i) if isinstance(d[k], (tuple,list))        \
            #        else (k, d[k]) for k in d for i in d[k]]
            _izip_replicate = lambda d : [[(k,i) for i in d[k]] if isinstance(d[k], (tuple,list))        \
                else (k, d[k])  for k in d]          
            filters = '&'.join(['{k}={v}'.format(k=k, v=v) for (k, v) in _izip_replicate(kwargs)])
            # filters = '&'.join(map("=".join,kwargs.items()))
            sep = '?'
            try:        
                last = url.rsplit('/',1)[1]
            except:     
                pass
            else:
                if any([last.endswith(c) for c in ('?', '/')]):     sep = ''
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
        The generic url formatting is: {domain}/api?{filters}
        
        Example
        -------
        >>> print GISCOService.url_geocode(place='paris, France')
            'http://europa.eu/webtools/rest/gisco/api?q=paris+France'
        """
        keys = ['q', 'lat', 'lon', 'distance_sort', 'limit', 'osm_tag', 'lang']
        happyVerbose('\n            * '.join(['input filters used for geocoding service :',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.__build_url(domain=self.domain, 
                               query='api', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
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
        The generic url formatting is: {domain}/reverse?{filters}.
        
        Example
        -------
        >>> print GISCOService.url_reverse(lon=10, lat=52)
            'http://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52'
        """
        keys = ['lat', 'lon', 'radius', 'distance_sort', 'limit', 'lang']
        happyVerbose('\n            * '.join(['input filters used for reverse geocoding service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.__build_url(domain=self.domain, 
                               query='reverse', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    def url_route(self, **kwargs):
        """
        http(s)://europa.eu/webtools/rest/gisco/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219?overview=false
        """
        keys = ['overview', ] # ?
        happyVerbose('\n            * '.join(['input filters used for routing service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        coordinates = kwargs.pop('coordinates','')
        polyline = kwargs.pop(_geoDecorators.parse_coordinate.KW_POLYLINE,None)
        polyline = 'polyline(' + polyline + ')' if polyline else ''
        url = self.__build_url(domain=self.domain, 
                               query='route/v1/driving/%s' % coordinates or polyline, 
                               **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        # test: 
        # url_route(lat=[13.388860, 13.397634, 13.428555],lon=[52.517037,52.529407,52.523219])
    #/************************************************************************/
    def url_transform(self, **kwargs):
        """

        Note
        ----
        The generic url formatting is: {arcgis}/Utilities/Geometry/GeometryServer/project?{filters}.
        
        Example
        -------
        >>> print GISCOService.url_reverse(lon=10, lat=52)
        https://webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/Utilities/Geometry/GeometryServer/project?inSR=4326&outSR=3035&geometries=-9.1630%2C38.7775&transformation=&transformForward=true&f=json
        """
        keys = ['inSR', 'outSR', 'geometries', 'transformation', 'transformForward', 'f'] # ?
        url = self.__build_url(domain=self.arcgis, 
                               query='Utilities/Geometry/GeometryServer/project', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
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
        happyVerbose('\n            * '.join(['input filters used for NUTS identification service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.__build_url(domain=self.domain, 
                               path='nuts', 
                               query='find-nuts.py', 
                               **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2geom(self, place, **kwargs): 
        """
        """
        place = ['+'.join(p.replace(',',' ').split()) for p in place]
        geom = []
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
                geom.append(c if len(c)>1 else c[0])
        return geom if len(geom)>1 else geom[0]
        
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs): # specific use
        """
        """
        geom = self.place2geom(place, **kwargs)
        return _geoDecorators.parse_geometry(lambda **kw: [kw.get('lat'), kw.get('lon')])(geom)
       
    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2place(self, lat, lon, **kwargs): # specific use
        """
        """
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
                happyWarning('NUTS of location (%s,%s) not loaded' % (lat[i], lon[i]))
                nuts.append(None)
            try:
                # assert 'results' in data and data['results'] != [] 
                assert _geoDecorators.parse_nuts.KW_RESULTS in data     \
                    and data[_geoDecorators.parse_nuts.KW_RESULTS] != []
            except:
                happyWarning('NUTS of location (%s,%s) not recognised' % (lat[i], lon[i]))      
                nuts.append(None)
            else:
                n = data.get(_geoDecorators.parse_nuts.KW_RESULTS)
                nuts.append(n if len(n)>1 else n[0])
        return nuts[0] if len(nuts)==1 else nuts

    #/************************************************************************/
    @_geoDecorators.parse_year
    @_geoDecorators.parse_projection
    @_geoDecorators.parse_place
    def place2nuts(self, place, **kwargs): # specific use
        lat, lon = self.place2coord(place, **kwargs)
        nuts = self.coord2nuts(lat, lon, **kwargs)
        return nuts[0] if len(nuts)==1 else nuts
        #res = _geoDecorators.parse_nuts(lambda **kw: kw.get('nuts'))(nuts, **kwargs)
        #return res[0] if len(res)==1 else res

    #/************************************************************************/
    def geomtrans(self, *args, **kwargs):
        pass

    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2route(self, lat, lon, **kwargs):
        routes, waypoints = None, None
        if not (lat in([],None) or lon in ([],None)):
            coordinates = ';'.join([','.join([str(l), str(L)]) for (l,L) in zip(lat,lon)])
        elif kwargs.get():
            coordinates = kwargs.pop(_geoDecorators.parse_coordinate.KW_POLYLINE)
        kwargs.update({'coordinates': coordinates})
        try:
            url = self.url_route(**kwargs)
            assert self.get_status(url) is not None
        except:
            raise IOError('error route request')
        else:
            response = self.get_response(url)
        pass
        try:
            data = json.loads(response.text)
            assert data is not None
        except:
            raise IOError('route not available')
        try:
            assert _geoDecorators.parse_route.KW_CODE in data       \
                and data[_geoDecorators.parse_route.KW_CODE].upper() == "OK"
        except:
            raise IOError('route  not recognised')      
        else:
            routes = data.get(_geoDecorators.parse_route.KW_ROUTES)
            waypoints = data.get(_geoDecorators.parse_route.KW_WAYPOITNS)
        return routes[0], waypoints
    
#%%
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
        """Initialisation of a :class:`APIService` instance.

            >>> serv = APIService(**kwargs)

        Arguments
        ---------
        coder : str
            identifier of the geocoder, _e.g._ _Google Maps_, _Google Places_, 
            _etc_... used for geolocation queries.
        key/token/username : str
            key (depending on the :literal:`coder actually chosen) used to connect 
            to the geolocation API.
        """
        # initial settings
        self.__coder, self.__coder_key = None, ''
        try:
            assert API_SERVICE is not False
        except:
            raise IOError('external API service not available')
        # read the arguments              
        self.__coder = kwargs.pop('coder', settings.CODER_GOOGLE_MAPS)
        self.__coder_key  = kwargs.get(self.CODER[self.__coder]) # it is a get!!! maybe None
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
            
    #/************************************************************************/
    @property
    def coder(self):
        return self.__coder
            
    @property
    def coder_key(self):
        return self.__coder_key
    @coder_key.setter#analysis:ignore
    def coder_key(self, key):
        if not isinstance(key, str):
            raise IOError('wrong type for CODER_KEY parameter')
        self.__coder_key = key

    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs):
        """
        """
        coord = [] 
        for p in place:   
            try:
                lat, lon = self.coder.geocode(p)
                assert lat not in ([],None) and lon not in ([],None)
                coord.append([lat,lon])
            except:
                coord.append(None)
                happyVerbose('\ncould not retrieve geolocation of %s' % p)
                # continue
            else:
                # happyVerbose('%s => %s' % (p, coord))
                pass
        return coord #{'lat':lat, 'lon': lon}

    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2place(self, lat, lon, **kwargs):
        """
        """
        places = self.coder.reverse(lat, lon)
        places = [] 
        for i in range(len(lat)):   
            try:
                p = self.coder.reverse(lat[i],lon[i])
                assert p not in ('',None)
                places.append(p)
            except:
                places.append(None)
                happyVerbose('\ncould not retrieve place name for geolocation %s' % (lat[i],lon[i]))
                # continue
            else:
                # happyVerbose('%s => %s' % (p, coord))
                pass
        return places 


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
