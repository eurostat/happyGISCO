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

# requirements
try:                                
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
      

#==============================================================================
# CLASS __BaseGeoService
#==============================================================================
    
#%%
class __BaseGeoService(object):
    """Base class for geolocation services.
    """
        
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        pass
    
    #/************************************************************************/
    @classmethod
    def parse_place(cls, *args, **kwargs): # specific use
        """Base method to parse and check input place argument.
        """
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
        place = list(place)
        if not all([isinstance(p,str) for p in place]):
            raise IOError('wrong format for input place')
        #else:
        #    place = '+'.join(place.replace(',',' ').split())
        return place

    #/************************************************************************/
    @classmethod
    def parse_coordinate(cls, *args, **kwargs):
        """Base method to parse and check input coordinate arguments.
        """
        coord, lat, lng = None, None, None
        if args not in (None,()):      
            if all([isinstance(a,dict) for a in args]):
                coord = args
            elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                if len(args[0])==2 and all([isinstance(args[0][i],(tuple,list)) for i in (0,1)]):
                    lat, lng = args[0]
                elif all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                    coord = args[0]
            elif len(args) == 1 and isinstance(args[0],(tuple,list)) and len(args[0])==2:
                lat, lng = args[0]
            elif len(args) == 2 and all([isinstance(args[i],(tuple,list)) for i in (0,1)]):    
                lat, lng = args
            else:   
                raise IOError('input arguments not recognised')
        else:   
            coord = kwargs.pop('coord', None)         
            lat = kwargs.pop('lat', None) or kwargs.pop('x', None)
            lng = kwargs.pop('lng', None) or kwargs.pop('y', None)
        try:
            assert not(coord is None and lat is None and lng is None) 
        except:
            raise IOError('no input arguments passed')
        try:
            assert coord is None or (lat is None and lng is None)
        except:
            raise IOError('too many input arguments')
        if coord is not None:
            if not isinstance(coord,(list,tuple)):  
                coord = [coord]
            try:
                lat, lng = [_ for _ in zip(*[(c['lat'], c['lng']) for c in coord])]
            except:
                raise IOError('wrong input arguments passed')
        if lat is None or lng is None:
            raise IOError('wrong geographical coordinates')
        lat, lng = list(lat), list(lng)
        if not len(lat) == len(lng):
            raise IOError('incompatible geographical coordinates')
        return lat, lng

#==============================================================================
# CLASS OnlineService
#==============================================================================
    
#%%
class GISCOService(__BaseGeoService):
    """Class providing geolocation methods based on GISCO online services.
    """
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        """Initialisation of a :class:`OnlineService` instance.

            >>> x = OnlineService(**kwargs)
        """
        self.__session, self.__domain = None, ''
        try:
            assert GISCO_SERVICE is not False
        except:
            raise IOError('ONLINE service not available')
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
        """Download just the header of a URL and return the server's status code.
        """        
        try:
             response = self.__session.head(url)
             response.raise_for_status()
        except:
             raise IOError('wrong request formulated')  
        else:
             status = response.status_code
             response.close()
        return status
    
    #/************************************************************************/
    def get_response(self, url, **kwargs):
        """
        """
        try:
            response = self.__session.get(url)                
        except:
            raise IOError('wrong request formulated')  
        else:
            response.raise_for_status()
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
    def url_location(self, **kwargs):
        """Create a query URL to *NUTS* web service.
        
            >>> url = GISCOService.url_location(**filters)
           
        Keyword Arguments
        -----------------
        filters : dict
            define the parameters for web service.
                
        Returns
        -------
        url : str
            link to NUTS web service to submit the specified 'geocode' query that
            retrieves a geolocation from a place.

        Note
        ----
        The generic url formatting is: domain/api?{filters}
        """
        return self.__build_url(domain=self.domain, query='api', filters=kwargs)
    
    #/************************************************************************/
    def url_nuts(self, **kwargs):
        """Create a query URL to *NUTS* web service.
        
            >>> url = GISCOService.url_nuts(**filters)
           
        Keyword Arguments
        -----------------
        filters : dict
            define the parameters for web service.
                
        Returns
        -------
        url : str
            link to NUTS web service to submit the specified 'NUTS' query that
            identifies the NUTS code of a given geolocation.

        Note
        ----
        The generic url formatting is: domain/nuts/find-nuts.py?{filters}
        """
        return self.__build_url(domain=self.domain, path='nuts', query='find-nuts.py', filters=kwargs)
        
    #/************************************************************************/
    def place2loc(self, *args, **kwargs): # specific use
        place = self.parse_place(*args, **kwargs)
        # place = ['+'.join(p.replace(',',' ').split()) for p in place]
        location = []
        for p in place:
            kwargs.update({'q': p})
            try:
                url = self.url_location(self, **kwargs)
                self.get_status(url)
            except:
                raise IOError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                loc = json.loads(response.text)
                assert loc not in({},None)
            except:
                raise IOError('geolocation of place %s not recognised' % p)
            else:
                location.append(loc)
        return location
        # pprint(location)

    #/************************************************************************/
    def loc2nuts(self, *args, **kwargs):
        """
        """
        kwargs.update({'year': kwargs.pop('year',2013), 
                       'geometry': kwargs.pop('geometry','Y'), 
                       'f': 'JSON'})
        lat, lng = self.parse_coordinate(*args, **kwargs)
        nuts = []
        # Usage: x=<longitude>&y=<latitude>&f=<JSON/XML>&year=<2013/2010/2006>&proj=3035&geometry=<N/Y>
        for i in range(len(lat)):
            kwargs.update({'x': lng[i], 'y': lat[i]})
            try:
                url = self.url_nuts(self, **kwargs)
                self.get_status(url)
            except:
                raise IOError('error NUTS request')
            else:
                response = self.get_response(url)
            try:
                nut = json.loads(response.text)
                assert nut is not None
            except:
                raise IOError('NUTS of location (%s,%s) not recognised' % (lat,lng))
            else:
                nuts.append(nut)
        return nuts

#/****************************************************************************/
# CLASS _geoCoderAPI    
# Class emulating :mod:`geopy` API.
# Available when module :mod:`geopy` is installed.
#/****************************************************************************/
try:    
    assert API_SERVICE and geopy
except (NameError,AssertionError): 
    class _geoCoderAPI(object):     
        pass
else:   
    class _geoCoderAPI(object):
        """Class emulating :mod:`geopy` API.

        Inherit all methods from original API.
        
        Most of the :class:`_geoCoderAPI` methods will be inherited by the class
        :class:`OfflineService` through composition and embedding in container 
        attributes. Following, usages are presented using :class:`OfflineService`\ .
        """

        GEOCODERS = {'GoogleV3':         None,   # API authentication is only required for Google Maps Premier customers
                     'Bing':             'key',  # valid Bing Maps API key
                     'GeoNames':         'username', # username required for API access
                     'YahooPlaceFinder': 'key',  # Key provided by Yahoo
                     'OpenMapQuest':     None,       # No API Key is needed by the Nominatim based platform
                     'MapQuest':         'key',  # API key provided by MapQuest
                     'LiveAddress':      'token',# Valid authentication token; LiveAddress geocoder provided by SmartyStreets
                     'Nominatim':        None,       # Nominatim geocoder for OpenStreetMap servers
                     } 

        GEOCODER_DIST  = {'great_circle':'GreatCircleDistance',
                           'vincenty': 'VincentyDistance'}
        DIST_UNIT      = {'km':'kilometers',
                           'mi': 'miles',
                           'm': 'meters',
                           'ft': 'feet'}
     
        #/********************************************************************/
        def __init__(self, **kwargs):
            # call geocoder module geopy: https://github.com/geopy/geopy'
            self._gc = None
            coder = kwargs.pop('geocoder', 'GeoNames')
            if coder not in self.GEOCODERS.keys():
                raise IOError('geocoder %s not recognised' % coder)
            try:        gc = getattr(geopy.geocoders, coder)   
            except:     raise IOError('module geopy not available')
            key = self.GEOCODERS[coder]
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
            if code not in self.GEOCODER_DIST.keys():
                raise IOError('wrong code for geodesic distance')
            try:    
                # in order to accept the 'getattr' below, the geopy.distance needs
                # to be loaded in the first place
                import geopy.distance
            except: 
                raise IOError('distance calculation not available')
            code = self.GEOCODER_DIST[code]
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
        pass
else:   
    class _googleMapsAPI(googlemaps.Client):
        """Class emulating :class:`googlemaps.Client` API.

        Most of the :class:`googlemaps.Client` methods will be inherited by the
        :class:`OfflineService` class through composition and embedding in container attributes. 
        """

        #/********************************************************************/
        def __init__(self, key=None):
            # call Google Maps API: https://developers.google.com/maps/
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
        pass
else: 
    class _googlePlacesAPI(googleplaces.GooglePlaces):
        
        #/********************************************************************/
        def __init__(self, key=None):
            # call Google Places API: https://developers.google.com/places
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
class APIService(__BaseGeoService):
    """
    """
    
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
        self.coder_key    = kwargs.pop('coder_key', settings.GOOGLE_KEY)
        self.driver_name   = kwargs.pop('driver_name', settings.DRIVER_NAME)
        try:
            # geocoder defined as an instance of _geoCoderAPI class derived from 
            # geopy.geocoders
            geocoder = kwargs.get('geocoder') # settings.GOOGLE_CODER
            self.__coder = _geoCoderAPI(key=self.coder_key, geocoder=geocoder) 
        except:
            try:
                # geomapper defined as an instance of _googleMapsAPI class derived
                # from googlemaps.GoogleMaps
                self.__coder = _googleMapsAPI(key=self.coder_key) 
            except:
                try:
                    # geolocator defined as an instance of _googlePlacesAPI class
                    # derived from googleplaces.GooglePlaces
                    self.__coder = _googlePlacesAPI(key=self.coder_key) 
                except:
                    raise IOError('geocoder not available')
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
    def geocode(self, *args, **kwargs): # specific use
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
    def place2loc(self, *args, **kwargs):
        place = self.parse_place(*args, **kwargs)
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
    def loc2vec(self, *args, **kwargs):
        lat, lng = self.parse_coordinate(*args, **kwargs)
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
    def vec2nuts(self, layer, vector):
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
    def loc2nuts(self, *args, **kwargs):
        filename = kwargs.pop('nuts_file','')
        return self.vec2nuts(self.file2layer(filename), 
                             self.loc2vec(self, *args, **kwargs))
    
#==============================================================================
# CLASS PLACE
#==============================================================================
        
class Place(object):

    def __init__(self, *args, **kwargs):
        try:
            place = __BaseGeoService.parse_place(*args, **kwargs)
        except:
            place = None
        try:
            lat, lng = __BaseGeoService.parse_coordinate(*args, **kwargs)
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
        if self.__coord in ([], None):   
            service = ServiceGIS(**kwargs)
            try:
                assert online is True or OFFLINE is not False
            except:
                raise IOError('OFFLINE service not available')
            try:
                assert online is False or ONLINE is not False
            except:
                raise IOError('ONLINE webservice not available')
            for p in self.place:   
                try:
                    geocode = gmaps.geocode(p)
                    coord = geocode[0]['geometry']['location']
                    assert coord is not None
                except:
                    print('\nCould not retrieve geolocation of %s' % p)
                    continue
                else:
                    print('%s => %s' % (place, coord))
        return self.coord
    
class Location(__BaseGeoEntity):
    
    def __init__(self, *args, **kwargs):
        self.__coord = []
        self.__vector = None
        return
       
    @property
    def coord(self):
        return self.__coord
       
    @property
    def vector(self):
        return self.__vector
       
    def reverse():
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

def place2nuts(*args, **kwargs):
    place = Place(*args, **kwargs)
    nuts = NUTS(place.tonuts())
    return nuts
    
    
PLACES      = ['Bremen, Germany', 'Florence, Italy', 'Brussels, Belgium']
GOOGLE_KEY  = '' # you need to provide your own API key here
NUTSDIR     = 'ref-nuts-2013-01m'
NUTSFILE    = 'NUTS_RG_01M_2013_4326_LEVL_2.shp' # region

gmaps = googlemaps.Client(key=GOOGLE_KEY) 
Locations = ogr.Geometry(ogr.wkbMultiPoint)

try:
    assert Locations is not None
except:
    print('\nCould not retrieve any geolocation')
    raise IOError
else:
    print(Locations.ExportToWkt())

try:
    driver = ogr.GetDriverByName('ESRI Shapefile')
    Nuts = driver.Open(os.path.join(NUTSDIR,NUTSFILE), 0) # 0 means read-only
    assert Nuts is not None
except:
    print('\nCould not open %s' % NUTSFILE)
    print('visit: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip')
    raise IOError
else:
    print('\nOpened %s' % NUTSFILE)
    print('NUTS help: http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf')
    
try:
    layer = Nuts.GetLayer()
    assert layer is not None
except:
    print('\nCould not get vector layer')
    raise IOError
else:
    featureCount = layer.GetFeatureCount()
    print('\nNumber of features in %s: %d' % (os.path.basename(NUTSFILE),featureCount))
    
Regions = []

# iterate through points
for i in range(0, Locations.GetGeometryCount()): # because it is a MULTIPOINT
    pt = Locations.GetGeometryRef(i)
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
            Regions.append(feature)
    if len(Regions)<i+1:    
        Regions.append(None)

try:
    assert not all([region is None for region in Regions])
except:
    print('\nNUTS regions (level 2) not found')
else:
    print('\nNUTS regions (level 2) identified')
    for i, place in enumerate(PLACES):
        items = Regions[i].items()
        print('%s => NUTS ID: %s - NUTS name: %s' % (place, items['NUTS_ID'],items['NUTS_NAME']))
# will display:
# Bremen, Germany => NUTS ID: DE50 - NUTS name: Bremen
# Florence, Italy => NUTS ID: ITI1 - NUTS name: Toscana
# Brussels, Belgium => NUTS ID: BE10 - NUTS name: Région de Bruxelles-Capitale / Brussels Hoofdstedelijk Gewest	
