#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_services

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _GISCOWIKI: https://webgate.ec.europa.eu/fpfis/wikis/display/GISCO/Geospatial+information+services+for+the+European+Commission+and+other+EU+users
.. |GISCOWIKI| replace:: `GISCO offline wiki <GISCOWIKI_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `Open Street Map <OSM_>`_
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. |Nominatim| replace:: `Nominatim <Nominatim_>`_
.. _NominatimWIKI: https://wiki.openstreetmap.org/wiki/Nominatim
.. |NominatimWIKI| replace:: `NominatimWIKI <NominatimWIKI_>`_
.. _Google_Maps: https://developers.google.com/maps/
.. |Google_Maps| replace:: `Google Maps <Google_Maps_>`_
.. _Google_Places: https://developers.google.com/places/
.. |Google_Places| replace:: `Google Places <Google_Places_>`_
.. _ArcGIS: http://arcgis.com
.. |ArcGIS| replace:: `ArcGIS <ArcGIS_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_
.. _googlemaps: https://pypi.python.org/pypi/googlemaps
.. |googlemaps| replace:: `Google Maps <googlemaps_>`_
.. _googleplaces: https://github.com/slimkrazy/python-google-places
.. |googleplaces| replace:: `Google Places <googleplaces_>`_

Module implementing simple requests to various web-based geographical services, 
including |Eurostat| |GISCO|, |OSM| |Nominatim| and |Google_Maps|.

**Description**

Perform operations using online web-services, *e.g.*:

* query and collection through |GISCO| web-services,
* query and collection through external GIS web-services,
* simple geographical data handling and processing.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`functools`, :mod:`json`

*optional*:     :mod:`requests`, :mod:`geopy`, :mod:`googlemaps`, :mod:`googleplaces`

*call*:         :mod:`settings`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:46:51 2018

__all__         = ['GISCOService', 'APIService', 
                   '_googleMapsAPI', '_googlePlacesAPI', '_geoCoderAPI']

# generic import
import os, sys#analysis:ignore

import functools#analysis:ignore

# local imports
from happygisco import settings
from happygisco.settings import happyVerbose, happyWarning, happyError,  \
                                _geoDecorators, _Types

# requirements
try:                                
    GISCO_SERVICE = True
    OSM_SERVICE = True
    import requests # urllib2
except ImportError:                 
    happyWarning('REQUESTS package (https://pypi.python.org/pypi/requests/) not loaded - GISCO ONLINE service will not be accessed')
    GISCO_SERVICE = False
    OSM_SERVICE = False
    
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

#%%
#==============================================================================
# CLASS _Service
#==============================================================================

class _Service(object):
    """Base class defining a web-session and simple connection operations to be
    used by a web-service. 
       
        >>> serv = services._Service()
    """
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        try:
            self.session = requests.Session()
        except:
            raise happyError('request session not recognised')
        
    #/************************************************************************/
    @property
    def session(self):
        """Session attribute (:data:`getter`/:data:`setter`) of an instance of
        a class :class:`_Service`. `session` is actually an instance of a
        :class:`requests.session.Session` class.
        """ # A session type is :class:`requests.session.Session`.
        return self.__session
    @session.setter#analysis:ignore
    def session(self, session):
        if session is not None and not isinstance(session, requests.sessions.Session):
            raise TypeError('wrong type for SESSION parameter')
        self.__session = session
    
    #/************************************************************************/   
    def get_status(self, url):
        """Retrieve the header of a URL and return the server's status code.
        
            >>> status = serv.get_status(url)
            
        Arguments
        ---------
        url : str
            complete URL name whom status will be checked.
        
        Returns
        -------
        status : int
            response status code.
            
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
                
                * the request is wrongly formulated,
                * the connection fails.
            
        Examples
        --------
        We can see the response status code when connecting to different web-pages
        or services:
        
        >>> serv = services._Service()
        >>> serv.get_status('http://dumb')
            ConnectionError: connection failed
        >>> serv.get_status('http://www.dumbanddumber.com')
            301 
        
        Let us actually check that the status is ok when connecting to |Eurostat| website:
            
        >>> stat = serv.get_status(settings.ESTAT_URL)
        >>> print(stat)
            200
        >>> import requests
        >>> stat == requests.codes.ok
            True
        
        See also
        --------
        :meth:`~_Service.get_response`, :meth:`~_Service.build_url`.
        """ 
        try:
            response = self.session.head(url)
        except requests.ConnectionError:
            raise happyError('connection failed')  
        else:
            happyVerbose('response status from web-service: %s' % response.status_code)
        response.raise_for_status()
        try:
            response.raise_for_status()
        except:
            raise happyError('wrong request formulated')  
        else:
            status = response.status_code
            response.close()
        return status
    
    #/************************************************************************/
    def get_response(self, url):
        """Retrieve the GET response of a URL.
        
            >>> response = serv.get_response(url)
            
        Arguments
        ---------
        url : str
            complete URL name whose response is retrieved.
        
        Returns
        -------
        response : :class:`requests.models.Response`
            response retrieved from the URL.
            
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the request is wrongly formulated,
                * a wrong response is retrieved.
            
        Examples
        --------
        Some simple tests:
            
        >>> serv = services._Service()
        >>> serv.get_response('http://dumb')
            happyError: wrong request formulated
        >>> resp = serv.get_response('http://www.example.com')
        >>> print(resp.text)
            <!doctype html>
            <html>
            <head>
                <title>Example Domain</title>
                <meta charset="utf-8" />
                <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                ...
            
        We can view the server’s response headers when connecting to |Eurostat|
        webpage:
            
        >>> resp = serv.get_response(settings.ESTAT_URL)
        >>> print(resp.headers)
            {   'Date': 'Wed, 18 Apr 2018 11:54:40 GMT', 
                'X-Content-Type-Options': 'nosniff', 
                'X-Frame-Options': 'SAMEORIGIN', 
                'X-XSS-Protection': '1', 
                'Content-Type': 'text/html;charset=UTF-8', 
                'Transfer-Encoding': 'chunked', 
                'Server': 'Europa', 
                'Connection': 'Keep-Alive', 
                'Content-Encoding': 'gzip' }
        
        We can also access the response body as bytes (though that is usually
        adapted to non-text requests):
            
        >>> print(resp.content)
            b'<!DOCTYPE html PUBLIC " ...
        
        See also
        --------
        :meth:`~_Service.get_status`, :meth:`~_Service.build_url`.
        """
        try:
            response = self.session.get(url)                
        except:
            raise happyError('wrong request formulated')  
        else:
            # happyVerbose('response reason from web-service: %s' % response.reason)
            pass
        try:
            response.raise_for_status()
        except:
            raise happyError('wrong response retrieved')  
        return response   
    
    #/************************************************************************/
    @classmethod
    def build_url(cls, *args, **kwargs):
        """Create a complete query URL to be used by a web-service.
        
            >>> url = _Service.build_url(*args, **kwargs)
            
        Arguments
        ---------
        domain : str
            domain of the URL; default: :data:`domain` is left empty.
           
        Keyword Arguments
        -----------------
        protocol : str
            web protocol; default to :data:`settings.DEF_PROTOCOL`, *e.g.* :literal:`http`\ .
        domain : str
            this keyword can be used when :data:`domain` is not passed as a 
            positional argument already.
        path : str
            path completing the domain to form the URL: it will actually be concatenated
            to :data:`domain` so as to form the composite string :data:`domain/path`; hence, 
            :data:`path` could simply be concatenated with :data:`domain` in input already.
        query : str
            query of the URL: it is concatenated to the string :data:`domain/path` so
            as to form the string :data:`domain/path/query?`\ .
        kwargs : dict
            any other keyword argument can be added as further "filters" to the output
            URL, *e.g.* when :data:`{'par': 1}` is passed as an additional keyword argument,
            the string :literal:`par=1` will be concatenated at the end of the URL formed
            by the other parameters.
                
        Returns
        -------
        url : str
            URL uniquely defined by the input parameters; the generic form of :data:`url`
            is :data:`protocol://domain/path/query?filters`, when all parameters above
            are passed.
    
        Example
        -------
        Let us, for instance, build a URL query to *Eurostat* Rest API (just enter 
        the output URL in your browser to check the output):
            
        >>> _Service.build_url(settings.ESTAT_URL,
                               path='wdds/rest/data/v2.1/json/en',
                               query='ilc_li03', 
                               precision=1,
                               indic_il='LI_R_MD60',
                               time='2015')
            'http://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/ilc_li03?precision=1&indic_il=LI_R_MD60&time=2015'
        
        Note that another way to call the method is:

        >>> _Service.build_url(domain=settings.ESTAT_URL,
                               path='wdds/rest/data/v2.1/json/en',
                               query='ilc_li01', 
                               **{'precision': 1, 'hhtyp': 'A1', 'time': '2010'})
            'http://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/ilc_li01?precision=1&hhtyp=A1&time=2010'
        
        Similarly, we will be able to access to |GISCO| service (see :meth:`GISCOService.url_geocode`
        below):
 
        >>> _Service.build_url(domain=settings.GISCO_URL,
                               query='api', 
                               **{'q': 'Berlin+Germany', 'limit': 2})
            'http://europa.eu/webtools/rest/gisco/api?q=Berlin+Germany&limit=2'  
        
        See also
        --------
        :meth:`~_Service.get_status`, :meth:`~_Service.get_response`.
        """
        # retrieve parameters/build url
        if args not in (None,()):       domain = args[0]
        else:                           domain = kwargs.pop('domain','')
        url = domain.strip("/")
        protocol = kwargs.pop('protocol', settings.DEF_PROTOCOL)
        if protocol not in settings.PROTOCOLS:
            raise happyError('web protocol not recognised')
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

#%%
#==============================================================================
# CLASS OSMService
#==============================================================================
    
class OSMService(_Service):
    """Class providing conversion methods and geocoding tools that run the |Nominatim| 
    online web-service of the |OSM| API.
       
        >>> serv = services.OSMService(**kwargs)
            
    Keyword arguments
    -----------------
    domain : str
        domain of |OSM| web-services hosted by |OSM|; default is :data:`settings.OSM_URL`,
        *e.g.* an URL domain like :literal:`'nominatim.openstreetmap.org'`. 
 
    Attributes
    ----------     
    CODER :
        coder dictionary defining the connection to |OSM| based web-service
        set to {:data:`settings.CODER_OSM`: :data:`settings.KEY_OSM` }, *e.g*
        :literal:`{'OSM': None}`.
    """
    
    CODER = {settings.CODER_OSM: settings.KEY_OSM}
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        try:
            assert OSM_SERVICE is not False
        except:
            raise happyError('GISCO service not available')
        super(OSMService, self).__init__(**kwargs)
        self.domain = kwargs.pop('domain', settings.OSM_URL) 

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Generate the query URL for |Nominatim| geocoding web-service (from toponame to
        geocoordinate).
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`format, json_callback, accept-language, extratags, namedetails, q, street, city, county, state, country, postalcode, countrycodes, viewbox, bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson, polygon_kml, polygon_svg`, and :data:`polygon_text`;
            see |NominatimWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *geocode* results (*i.e.*, geocoordinates) 
            associated to a given place using |Nominatim| web-service; the generic form of 
            :data:`url` is :literal:`domain/search?{filters}` with :literal:`filters` the 
            filters passed through :data:`kwargs`.
        
        Example
        -------
        Let us create a simple URL for querying the geolocation of a toponame:
            
        >>> serv = services.OSMService()
        >>> serv.url_geocode(q='Paris+France', format='json')
            'https://nominatim.openstreetmap.org/search?q=Paris+France&format=json'
        
        See also
        --------
        :meth:`~OSMService.url_reverse`, :meth:`~OSMService.url_route`, 
        :meth:`~OSMService.url_transform`, :meth:`_Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https')
        query = kwargs.pop('query', 'search')
        keys = kwargs.pop('keys',
                          ['format', 'json_callback', 'accept-language', 'extratags', 'namedetails', 
                           'q', 'street', 'city', 'county', 'state', 'country', 'postalcode', 'countrycodes', 
                           'viewbox', 'bounded', 'addressdetails', 'email', 'limit', 'dedupe', 'debug', 
                           'polygon_geojson', 'polygon_kml', 'polygon_svg', 'polygon_text']
                          )
        happyVerbose('\n            * '.join(['input filters used for geocoding service :',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=protocol,
                             domain=self.domain, 
                             query=query, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for |Nominatim| reverse geocoding web-service (from 
        geocoordinate to toponame).
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`lat, lon, format, json_callback, accept-language, extratags, email, osm_type, osm_id, zoom, addressdetails, polygon_geojson, polygon_kml, polygon_svg`, and :data:`polygon_text`;
            see |NominatimWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *reverse geocode* results (*i.e.*, 
            toponame) associated to given geocoordinates using |Nominatim| web-service; 
            the generic form of :data:`url` is :literal:`domain/reverse?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        We can generate the URL for querying the toponame associated to a given
        geolocation:

        >>> serv = services.OSMService()
        >>> serv.url_reverse(lon=10, lat=52)
            'https://nominatim.openstreetmap.org/reverse?lon=10&lat=52'
        
        See also
        --------
        :meth:`~OSMService.url_geocode`, :meth:`~OSMService.url_route`, 
        :meth:`~OSMService.url_transform`, :meth:`_Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https')
        query = kwargs.pop('query', 'reverse')
        keys = kwargs.pop('keys',
                          ['format', 'json_callback', 'accept-language', 'extratags', 'email', 
                           'osm_type', 'osm_id', 'lat', 'lon', 'zoom', 'addressdetails', 
                           'polygon_geojson', 'polygon_kml', 'polygon_svg', 'polygon_text']
                          )
        happyVerbose('\n            * '.join(['input filters used for reverse geocoding service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=protocol,
                             domain=self.domain, 
                             query=query, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    def _place2geom(self, place, **kwargs): 
        """Iterable version of :meth:`~OSMService.place2geom`.
        """
        place = ['+'.join(p.replace(',',' ').split()) for p in place]
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt is not None:
            kwargs.update({'format':fmt or 'json'})
        for p in place:
            kwargs.update({'q': p})
            try:
                url = self.url_geocode(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in({},None)
            except:
                raise happyError('geolocation for place %s not loaded' % p)
            try:
                assert key is not None
            except AssertionError:
                try:
                    assert data != [] 
                except:
                    raise happyError('geolocation for place %s not recognised' % p)  
                else:
                    pass
            else:
                try:
                    assert key in data and data[key] != [] 
                except AssertionError:
                    raise happyError('geolocation for place %s with key %s not recognised' % (p,key))  
                else:
                    data = data.get(key)
            yield data if _Types.ismapping(data) or len(data)>1 else data[0]

    #/************************************************************************/
    #@_geoDecorators.parse_place
    #def place2geom(self, place, **kwargs): 
    #    place = ['+'.join(p.replace(',',' ').split()) for p in place]
    #    geom = []
    #    fmt = kwargs.pop('format','')
    #    if fmt is not None:
    #        kwargs.update({'format':fmt or 'json'})
    #    for p in place:
    #        kwargs.update({'q': p})
    #        try:
    #            url = self.url_geocode(**kwargs)
    #            assert self.get_status(url) is not None
    #        except:
    #            raise happyError('error geolocation request')
    #        else:
    #            response = self.get_response(url)
    #        try:
    #            data = json.loads(response.text)
    #            assert data not in({},None)
    #        except:
    #            raise happyError('geolocation for place %s not loaded' % p)
    #        try:
    #            assert data != [] 
    #        except:
    #            raise happyError('geolocation for place %s not recognised' % p)      
    #        else:
    #            geom.append(data if len(data)>1 else data[0])
    #    return geom if len(geom)>1 else geom[0]
    @_geoDecorators.parse_place
    def place2geom(self, place, **kwargs):
        """Retrieve the geographical information associated to a given place as a
        geometry object using |OSM| service.
        
            >>> geom = serv.place2geom(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, namedetails, street, city, county, state, country, postalcode, countrycodes, viewbox, bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson, polygon_kml, polygon_svg, polygon_text`;
            are accepted; see :meth:`~OSMService.url_geocode`.
        
        Returns
        -------
        geom : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input olace(s) in :data:`place`, one for each 
            place mentioned.
                  
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
                
        Examples
        --------
        We will retrieve the geolocation of Berlin, Germany:
        
        >>> berlin = 'Berlin, Germany'
        
        For that purpose, we can build the desired |OSM| URL:
        
        >>> serv = services.OSMService()
        >>> serv.url_geocode(place=berlin) 
            'https://nominatim.openstreetmap.org/search?format=json&q=Berlin+Germany'
        
        though the method :meth:`place2geom` enables us to run the operation all
        in once: 

        >>> serv.place2geom(berlin, format='json')
            [{'boundingbox': ['52.3570365', '52.6770365', '13.2288599', '13.5488599'],
               'class': 'place',
              'display_name': 'Berlin, 10117, Deutschland',
              'icon': 'https://nominatim.openstreetmap.org/images/mapicons/poi_place_city.p.20.png',
              'importance': 0.31553744940772,
              'lat': '52.5170365',
              'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
              'lon': '13.3888599',
              'osm_id': '240109189', 'osm_type': 'node',
              'place_id': '226584215',
              'type': 'city'},
             {'boundingbox': ['52.33826', '52.67551', '13.08835', '13.76116'],
              'class': 'boundary',
              'display_name': 'Berlin, Deutschland',
              'icon': 'https://nominatim.openstreetmap.org/images/mapicons/poi_boundary_administrative.p.20.png',
              'importance': 0.31553744940772,
              'lat': '52.5198535',
              'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
              'lon': '13.4385964',
              'osm_id': '62422', 'osm_type': 'relation',
              'place_id': '178741737',
              'type': 'administrative'},
             ...
             {'boundingbox': ['52.4186824', '52.4187824', '13.1963552', '13.1964552'],
              'class': 'tourism',
              'display_name': 'Berlin, A 115, Nikolassee, Steglitz-Zehlendorf, Berlin, 14109, Deutschland',
              'icon': 'https://nominatim.openstreetmap.org/images/mapicons/tourist_art_gallery2.p.20.png',
              'importance': 0.11025,
              'lat': '52.4187324',
              'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
              'lon': '13.1964052',
              'osm_id': '1069490670', 'osm_type': 'node',
              'place_id': '11522486',
              'type': 'artwork'}]  
            
        See also
        --------
        :meth:`~OSMService.coord2place`, :meth:`~OSMService.place2coord`, 
        :meth:`~OSMService.url_geocode`, :meth:`~GISCOService.place2geom`, 
        :meth:`_Service.get_status`, :meth:`_Service.get_response`.
        """
        unique = kwargs.pop('unique',False)
        geom = []
        [geom.append(data if len(data)>1 and unique is False else data[0]) for data in self._place2geom(place, **kwargs)]
        return geom if len(geom)>1 else geom[0]
       
    #/************************************************************************/
    def _coord2geom(self, coord, **kwargs): 
        """Iterable version of :meth:`~OSMService.coord2geom`.
        """
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt is not None:
            kwargs.update({'format':fmt or 'json'})
        for i in range(len(coord)):
            kwargs.update({'lat': coord[i][0], 'lon': coord[i][1]})
            try:
                url = self.url_reverse(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in ({},None)
            except:
                raise happyError('place for geolocation %s not loaded' % coord[i])
            try:
                assert key is not None
            except AssertionError:
                try:
                    assert data != [] 
                except:
                    raise happyError('place for geolocation %s not recognised' % coord[i])  
                else:
                    pass
            else:
                try:
                    assert key in data and data[key] != [] 
                except AssertionError:
                    raise happyError('place for geolocation %s and key %s not recognised' % (coord[i], key))  
                else:
                    data = data.get(key)
            yield data if not _Types.ismapping(data) or len(data)>1 else data[0]
       
    #/************************************************************************/
    #@_geoDecorators.parse_coordinate
    #def coord2geom(self, lat, lon, **kwargs): # specific use
    #    geom = []
    #    for i in range(len(lat)):
    #        kwargs.update({'lat': lat[i], 'lon': lon[i]})
    #        try:
    #            url = self.url_reverse(**kwargs)
    #            assert self.get_status(url) is not None
    #        except:
    #            raise happyError('error geolocation request')
    #        else:
    #            response = self.get_response(url)
    #        try:
    #            data = json.loads(response.text)
    #            assert data not in({},None)
    #        except:
    #            raise happyError('place for geolocation (%s,%s) not loaded' % (lat[i], lon[i]))
    #        try:
    #            assert _geoDecorators.parse_geometry.KW_FEATURES in data     \
    #                and data[_geoDecorators.parse_geometry.KW_FEATURES] != []
    #        except:
    #            raise happyError('place for geolocation (%s,%s) not recognised' % (lat[i], lon[i]))      
    #        else:
    #            p = data.get(_geoDecorators.parse_geometry.KW_FEATURES)
    #            geom.append(p if len(p)>1 else p[0])
    #    return geom[0] if len(geom)==1 else geom
    @_geoDecorators.parse_coordinate
    def coord2geom(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographical coordinates using |OSM| service.
        
            >>>  place = serv.coord2geom(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, email, osm_type, osm_id, zoom, addressdetails, polygon_geojson, polygon_kml, polygon_svg, polygon`
            are accepted; see :meth:`~OSMService.url_reverse`.
        
        Returns
        -------
        geom : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input geographical coordinate(s) in :data:`coord`, 
            one for each coordinate listed.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
        >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
        >>> serv = services.OSMService()
        >>> serv.url_reverse(coord=berlin) 
            'https://nominatim.openstreetmap.org/reverse?format=json&lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2geom` does everything at once:
        
        >>> serv.coord2geom(berlin, format='json')
            {'address': {'address29': 'Douglas',
              'city': 'Berlin',
              'city_district': 'Mitte',
              'country': 'Deutschland', 'country_code': 'de',
              'neighbourhood': 'Spandauer Vorstadt',
              'postcode': '10117',
              'road': 'Unter den Linden',
              'state': 'Berlin',
              'suburb': 'Mitte'},
             'boundingbox': ['52.517222', '52.517422', '13.388877', '13.389077'],
             'display_name': 'Douglas, Unter den Linden, Spandauer Vorstadt, Mitte, Berlin, 10117, Deutschland',
             'lat': '52.517322',
             'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
             'lon': '13.388977',
             'osm_id': '1818862993', 'osm_type': 'node',
             'place_id': '18439434'}
        
        See also
        --------
        :meth:`~OSMService.place2coord`, :meth:`~OSMService.url_reverse`, 
        :meth:`_Service.get_status`, :meth:`_Service.get_response`.
        """
        place = []
        [place.append(data if len(data)>1 else data[0]) for data in self._coord2geom(coord, **kwargs)]
        return place[0] if len(place)==1 else place

    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs):
        """Retrieve the geographical coordinates of a given place provided by 
        its (topo)name.
        
            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, namedetails, street, city, county, state, country, postalcode, countrycodes, viewbox, bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson, polygon_kml, polygon_svg`, and :data:`polygon_text`
            are accepted; see :meth:`~OSMService.url_geocode`.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`False`, hence all geometries are parsed.
        order : str
            a flag used to define the order of the output geographical coordinates; 
            it can be either :literal:`'lL'` for :literal:`(lat,Lon)` order or 
            :literal:`'Ll'` for a :literal:`(lon,lat)` order; default is :literal:`'lL'`.            
            
        Returns
        -------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.

        Examples
        --------
        We can easily retrieve the geolocations associated to well-known places:
        
        >>> serv=services.OSMService()
        >>> serv.place2coord('Berlin, Germany')
            [[52.5170365, 13.3888599],
             [52.5198535, 13.4385964],
             [54.0363605, 10.4461313],
             [54.405119, 9.4319966],
             [52.5034002, 13.3386373],
             [52.5129535, 13.3299651],
             [52.5208803, 13.4107774],
             [47.984547, 10.1865807],
             [52.4758015, 13.3248541],
             [52.4187324, 13.1964052]]        
        >>> serv.place2coord('Roma, Italy', order='Ll', unique=True)
            [12.4829321, 41.8933203]
            
        Note
        ----
        This method simply "decorates" the method :meth:`~OSMService._place2geom`
        with :meth:`_geoDecorators.parse_geometry`.
            
        See also
        --------
        :meth:`~OSMService.place2geom`, :meth:`~OSMService.coord2place`,
        :meth:`GISCOService.place2coord`.
        """
        unique = kwargs.pop('unique',False)
        order = kwargs.pop('order','lL')
        coord = []
        func = lambda **kw: [kw.get('coord')]
        [coord.append(data if len(data)>1 else data[0])                     \
             for g in self._place2geom(place, **kwargs)                     \
             for data in _geoDecorators.parse_geometry(func)(g, filter='coord', order=order, unique=unique)]
        return coord if len(coord)>1 else coord[0]

    @_geoDecorators.parse_coordinate
    def coord2place(self, coord, **kwargs):
        """Retrieve the geographical coordinates of a given place provided by 
        its (topo)name.
        
            >>> place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, namedetails, street, city, county, state, country, postalcode, countrycodes, viewbox, bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson, polygon_kml, polygon_svg`, and :data:`polygon_text`
            are accepted; see :meth:`~OSMService.url_geocode`.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`False`, hence all geometries are parsed.
            
        Returns
        -------
        place : str, list[str]
            place (topo) name(s).

        Examples
        --------
        Let us see whether we can identify some places through their geolocations:
            
        >>> serv=services.OSMService()
        >>> serv.coord2place([41.8933203, 12.4829321])
            'Statua equestre di Marco Aurelio, Piazza del Campidoglio, Municipio Roma I, Roma, RM, LAZ, 00186, Italia'        
        >>> serv.coord2place([55.6867243, 12.5700724])
            '3A, Øster Farimagsgade, Indre Østerbro, Frederiksstaden, København, Københavns Kommune, Region Hovedstaden, 1353, Danmark'
            
        Note
        ----
        This method simply "decorates" the method :meth:`~OSMService._coord2geom`
        with :meth:`_geoDecorators.parse_geometry`.
            
        See also
        --------
        :meth:`~OSMService.coord2geom`, :meth:`~OSMService.place2coord2`,
        :meth:`GISCOService.coord2place`.
        """
        unique = kwargs.pop('unique',False)
        place =[]
        func = lambda **kw: [kw.get('place')]
        [place.append(data if len(data)>1 else data[0])                     \
             for g in self._coord2geom(coord, **kwargs)                     \
             for data in _geoDecorators.parse_geometry(func)(g, filter='place', unique=unique)]
        return place if len(place)>1 else place[0]

#%%
#==============================================================================
# CLASS GISCOService
#==============================================================================
    
class GISCOService(OSMService):
    """Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
       
        >>> serv = services.GISCOService(**kwargs)
            
    Keyword arguments
    -----------------
    domain : str
        domain of |OSM| web-services hosted by |GISCO|; default is :data:`settings.GISCO_URL`,
        *e.g.* an URL domain like :literal:`'europa.eu/webtools/rest/gisco/'`\ . 
    arcgis : str
        domain of |ArcGIS| web-services hosted by |GISCO|; default is :data:`settings.GISCO_ARCGIS`,
        *e.g.* an URL domain like :literal:`'webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/'`\ .
 
    Attributes
    ----------     
    CODER :
        coder dictionary defining the connection to |GISCO| based web-service
        set to {:data:`settings.CODER_GISCO`: :data:`settings.KEY_GISCO` }, *e.g*
        :literal:`{'gisco': None}` since there is currently no authentication 
        requested.
    """
    
    CODER = {settings.CODER_GISCO: settings.KEY_GISCO}
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        try:
            assert GISCO_SERVICE is not False
        except:
            raise happyError('GISCO service not available')
        super(GISCOService, self).__init__(**kwargs)
        self.domain = kwargs.pop('domain', settings.GISCO_URL) 
        self.arcgis = kwargs.pop('arcgis', settings.GISCO_ARCGIS)

    #/************************************************************************/
    @property
    def domain(self):
        """Domain attribute (:data:`getter`/:data:`setter`) defining the domain
        URL, *e.g.* :data:`settings.GISCO_URL`, of an instance of this class. 
        """ # A domain type is :class:`str`.
        return self.__domain
    @domain.setter#analysis:ignore
    def domain(self, domain):
        if domain is not None and not _Types.isstring(domain):
            raise TypeError('wrong type for DOMAIN parameter')
        self.__domain = domain or ''

    #/************************************************************************/
    @property
    def arcgis(self):
        """Domain attribute (:data:`getter`/:data:`setter`) defining the ArcGIS
        URL, *e.g.* :data:`settings.GISCO_ARCGIS`, of the an instance of this class. 
        """ # A domain type is :class:`str`.
        return self.__arcgis
    @arcgis.setter#analysis:ignore
    def arcgis(self, arcgis):
        if arcgis is not None and not _Types.isstring(arcgis):
            raise TypeError('wrong type for ARCGIS parameter')
        self.__arcgis = arcgis or ''

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Generate the query URL for |GISCO| geocoding web-service (from toponame 
        to geocoordinate).
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`q, lat, lon, distance_sort, limit, osm_tag`, and :data:`lang`;
            see |GISCOWIKI| on *background services* for more details.
        nominatim : bool
            flag set to :data:`True` when |Nominatim| geocoding service shall be 
            used; default is :data:`False`.
                
        Returns
        -------
        url : str
            URL used to return the adequate *geocode* results (*i.e.*, geocoordinates) 
            associated to a given place using |GISCO| web-service; the generic form of 
            :data:`url` is :literal:`{domain}/api?{filters}` with :literal:`filters` 
            the filters passed through :data:`kwargs`.
        
        Example
        -------
        Let us create a simple URL for querying the geolocation of a toponame:
            
        >>> serv = services.GISCOService()
        >>> serv.url_geocode(q='Paris+France')
            'http://europa.eu/webtools/rest/gisco/api?q=Paris+France'
            
        Note
        ----
        This method overrides the *super* method :meth:`OSMService.url_geocode`.
        
        See also
        --------
        :meth:`~GISCOService.url_reverse`, :meth:`~GISCOService.url_route`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_nuts`,
        :meth:`OSMService.url_geocode`.
        """
        nominatim = kwargs.pop('nominatim', False)
        kwargs.update({'keys': ['q', 'lat', 'lon', 'distance_sort', 'limit', 'osm_tag', 'lang'],
                       'path': 'nominatim' if nominatim else '',
                       'query': 'search.php' if nominatim else 'api',
                       'protocol': 'http'}
            )
        return super(GISCOService, self).url_geocode(**kwargs)
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for |GISCO| reverse geocoding web-service (from 
        geocoordinate to toponame).
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`lat, lon, radius, distance_sort, limit`, and :data:`lang`;
            see |GISCOWIKI| on *background services* for more details.
        nominatim : bool
            flag set to :data:`True` when |Nominatim| reverse service shall be 
            used; default is :data:`False`.
                
        Returns
        -------
        url : str
            URL used to return the adequate *reverse geocode* results (*i.e.*, 
            toponame) associated to given geocoordinates using |GISCO| web-service; 
            the generic form of :data:`url` is :literal:`{domain}/reverse?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        We can generate the URL for querying the toponame associated to a given
        geolocation:

        >>> serv = services.GISCOService()
        >>> serv.url_reverse(lon=10, lat=52)
            'http://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52'
            
        Note
        ----
        This method overrides the *super* method :meth:`OSMService.url_reverse`.
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_route`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_nuts`,
        :meth:`OSMService.url_reverse`.
        """
        nominatim = kwargs.pop('nominatim', False)
        kwargs.update({'keys': ['lat', 'lon', 'radius', 'distance_sort', 'limit', 'lang'],
                       'path': 'nominatim' if nominatim else '',
                       'query': 'reverse.php' if nominatim else 'reverse',
                       'protocol': 'http'}
            )
        return super(GISCOService, self).url_reverse(**kwargs)

    #/************************************************************************/
    def url_route(self, **kwargs):
        """Generate the query URL for |GISCO| routing web-service (from a list of
        geocoordinates to a route).
        
            >>> url = serv.url_route(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`coordinates, polyline, overview`, and :data:`???`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *routing* results associated to a list
            of given geocoordinates using |GISCO| web-service; 
            the generic form of :data:`url` is 
            :literal:`{domain}/route/v1/driving/{coordinates}?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        Let us generate the URL for querying the route going through a series of
        geolocations:

        >>> serv = services.GISCOService()
        >>> serv.url_route(coordinates='13.388860,52.517037;13.397634,52.529407;13.428555,52.523219')
            'https://europa.eu/webtools/rest/gisco/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOServiceurl_nuts`,
        :meth:`_Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https') # actually not necessary, http works as well  
        keys = ['overview', ] # ?
        happyVerbose('\n            * '.join(['input filters used for routing service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        coordinates = kwargs.pop('coordinates','')
        polyline = kwargs.pop(_geoDecorators.parse_coordinate.KW_POLYLINE,None)
        polyline = 'polyline(' + polyline + ')' if polyline else ''
        url = self.build_url(protocol=protocol,
                             domain=self.domain, 
                             query='route/v1/driving/%s' % coordinates or polyline, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        # test: 
        # url_route(lat=[13.388860, 13.397634, 13.428555],lon=[52.517037,52.529407,52.523219])

    #/************************************************************************/
    def url_transform(self, **kwargs):
        """Generate the query URL for |GISCO| projection tranform web-service (from 
        a geocoordinate in a given projection reference system to its transformation
        in another projection reference system)
        
            >>> url = serv.url_transform(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`inSR, outSR, geometries, transformation, transformForward` and :data:`f`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *projection* results of a given
            geocoordinate using |GISCO| web-service; the generic form of :data:`url` 
            is :literal:`{arcgis}/Utilities/Geometry/GeometryServer/project?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        We can generate the URL for querying the tranform of a given geolocation
        from *WGS84* projection system to *LAEA*:

        >>> serv = services.GISCOService()
        >>> serv.url_transform(inSR=4326, outSR=3035, f='json',
                               geometries='-9.1630,38.7775')
            'https://webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/Utilities/Geometry/GeometryServer/project?inSR=4326&outSR=3035&geometries=-9.1630,38.7775&f=json'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_route`, :meth:`~GISCOService.url_nuts`,
        :meth:`_Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https')  
        keys = ['inSR', 'outSR', 'geometries', 'transformation', 'transformForward', 'f'] # ?
        happyVerbose('\n            * '.join(['input filters used for tranform service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=protocol,
                             domain=self.arcgis, 
                             query='Utilities/Geometry/GeometryServer/project', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    @_geoDecorators.parse_projection
    def url_nuts(self, **kwargs):
        """Create a query URL to be submitted to the |GISCO| (simple) web-service 
        for NUTS codes identification.
        
            >>> url = serv.url_nuts(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`x, y, f, year, proj` and :data:`geometry`; see |GISCOWIKI| 
            on *background services* for more details.
            
        Returns
        -------
        url : str
            URL used to return the adequate *NUTS* results from a given
            geocoordinate using |GISCO| web-service; the generic form of :data:`url` 
            is :literal:`{domain}/nuts/find-nuts.py?{filters}` with :literal:`filters` 
            the filters passed through :data:`kwargs`.
            
        Example
        -----
        Let us build the URL that will allow us to identify the NUTS actually 
        associated with Berlin, Germany:

        >>> serv = services.GISCOService()
        >>> serv.url_nuts(y=52.5170365, x=13.3888599, f='JSON', proj=4326)
            'http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py?y=52.5170365&x=13.3888599&f=JSON&proj=4326'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_route`, :meth:`~GISCOService.url_transform`,
        :meth:`_Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'http')  
        keys = ['x', 'y', 'f', 'year', 'proj', 'geometry']
        happyVerbose('\n            * '.join(['input filters used for NUTS identification service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        # note that the service is case sensitive as f is concerned
        kwargs.update({'f': kwargs.get('f','JSON').upper()}) # let us avoid stupid mistakes
        url = self.build_url(protocol=protocol,
                             domain=self.domain, 
                             path='nuts', 
                             query='find-nuts.py', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        
    #/************************************************************************/
    def _place2geom(self, place, **kwargs): 
        """Iterable version of :meth:`~GISCOService.place2geom`.
        """
        kwargs.update({'key': _geoDecorators.parse_geometry.KW_FEATURES})
        #return super(GISCOService,self)._place2geom(place, **kwargs)
        for g in super(GISCOService,self)._place2geom(place, **kwargs):
            yield g
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2geom(self, place, **kwargs): 
        """Retrieve geographical information) associated to a given place as a
        geometry using |GISCO| service.
        
            >>>  = serv.place2geom(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[lat, lon, distance_sort, limit, osm_tag, lang]`
            are accepted; see :meth:`~GISCOService.url_geocode`.
        
        Returns
        -------
        geom : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input :data:`place`, one for each place 
            mentioned.
                  
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
                
        Example
        -------
        The method returns the complete list of geometries output by the web-servive:
            
        >>> serv = services.GISCOService()
        >>> serv.place2geom('Madrid, Spain')
            [{'geometry': {'coordinates': [-3.7035825, 40.4167047], 'type': 'Point'},
              'properties': {'country': 'Spain',
               'extent': [-3.8889539, 40.6437293, -3.5179163, 40.3119774],
               'name': 'Madrid',
               'osm_id': 5326784, 'osm_key': 'place', 'osm_type': 'R', 'osm_value': 'city',
               'postcode': '28001',
               'state': 'Community of Madrid'},
              'type': 'Feature'},
             {'geometry': {'coordinates': [-3.7715627754518115, 40.5248319],
               'type': 'Point'},
              'properties': {'country': 'Spain',
               'extent': [-4.5790058, 41.1657381, -3.0529852, 39.8845834],
               'name': 'Community of Madrid',
               'osm_id': 349055, 'osm_key': 'boundary', 'osm_type': 'R', 'osm_value': 'administrative'},
              'type': 'Feature'},
              {'geometry': {'coordinates': [-3.8275783867014415, 40.738663599999995],
               'type': 'Point'},
              'properties': {'country': 'Spain',
               'extent': [-4.3409302, 41.1657381, -3.3946285, 40.3119774],
               'name': 'Archidiócesis de Madrid',
               'osm_id': 6932541, 'osm_key': 'boundary', 'osm_type': 'R', 'osm_value': 'religious_administration',
               'state': 'Community of Madrid'},
              'type': 'Feature'},
              ...
               {'geometry': {'coordinates': [-3.690692008891012, 40.41147845],
               'type': 'Point'},
              'properties': {'city': 'Madrid', 'country': 'Spain',
               'extent': [-3.6925997, 40.4126075, -3.6889179, 40.4097313],
               'housenumber': '2',
               'name': 'Royal Botanical Garden of Madrid',
               'osm_id': 15244804, 'osm_key': 'leisure', 'osm_type': 'W', 'osm_value': 'garden',
               'postcode': '28014',
               'state': 'Community of Madrid',
               'street': 'Plaza Murillo'},
              'type': 'Feature'}]
        
        Note
        ----
        This method overrides :meth:`OSMService.get_response` by further providing 
        the :literal:`features` key that will be extracted from the output geometry 
        dictionary(ies).
        
        See also
        --------
        :meth:`~GISCOService.place2coord`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2nuts`, :meth:`~GISCOService.place2nuts`, 
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.url_geocode`, 
        :meth:`OSMService.place2geom`, :meth:`_Service.get_response`.
        """
        kwargs.update({'key': _geoDecorators.parse_geometry.KW_FEATURES})
        return super(GISCOService,self).place2geom(place=place, **kwargs)
        
    #/************************************************************************/
    #@_geoDecorators.parse_place
    #def _place2coord(self, place, **kwargs): 
    #    for g in super(GISCOService,self)._place2coord(place, **kwargs):
    #        yield g
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs): # specific use
        """Retrieve the geographical coordinates of a given place provided by 
        its (topo)name using |GISCO| service.
        
            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[lat, lon, distance_sort, limit, osm_tag, lang]`
            are accepted; see :meth:`~GISCOService.url_geocode`.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`False`, hence all geometries are parsed.
        order : str
            a flag used to define the order of the output geographical coordinates; 
            it can be either :literal:`'lL'` for :literal:`(lat,Lon)` order or 
            :literal:`'Ll'` for a :literal:`(lon,lat)` order; default is :literal:`'lL'`.            
            
        Returns
        -------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.

        Examples
        --------
        We can easily retrieve the geolocations associated to well-known places:
        
        >>> serv=services.GISCOService()
        >>> serv.place2coord('Berlin, Germany')
            [[52.5170365, 13.3888599], [52.5198535, 13.4385964]]        
        >>> serv.place2coord('Roma, Italy', order='Ll', unique=True)
            [10.4584101, 44.5996045]
            
        Note
        ----
        This method simply overrides the method :meth:`~OSMService.place2geom`.
           
        See also
        --------
        :meth:`~OSMService.place2coord`, :meth:`~GISCOService.place2geom`, 
        :meth:`~GISCOService.coord2place`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`.
        """
        return super(GISCOService,self).place2coord(place=place, **kwargs)

    #/************************************************************************/
    def _coord2geom(self, coord, **kwargs): 
        """Iterable version of :meth:`~GISCOService.coord2geom`.
        """
        kwargs.update({'key': _geoDecorators.parse_geometry.KW_FEATURES})
        #return super(GISCOService,self)._place2geom(place, **kwargs)
        for g in super(GISCOService,self)._coord2geom(coord, **kwargs):
            yield g
    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2geom(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographical coordinates using |GISCO| service.
        
            >>>  place = serv.coord2geom(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[radius, distance_sort, limit, lang]` are accepted; 
            see :meth:`~GISCOService.url_reverse`.
        
        Returns
        -------
        geom : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input geographical coordinate(s) in :data:`coord`, 
            one for each coordinate listed.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
        >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
        >>> serv = services.OSMService()
        >>> serv.url_reverse(coord=berlin) 
            'https://nominatim.openstreetmap.org/reverse?format=json&lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2geom` does everything at once:
        
        >>> serv.coord2geom(berlin, format='json')
            {'address': {'address29': 'Douglas',
              'city': 'Berlin',
              'city_district': 'Mitte',
              'country': 'Deutschland', 'country_code': 'de',
              'neighbourhood': 'Spandauer Vorstadt',
              'postcode': '10117',
              'road': 'Unter den Linden',
              'state': 'Berlin',
              'suburb': 'Mitte'},
             'boundingbox': ['52.517222', '52.517422', '13.388877', '13.389077'],
             'display_name': 'Douglas, Unter den Linden, Spandauer Vorstadt, Mitte, Berlin, 10117, Deutschland',
             'lat': '52.517322',
             'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
             'lon': '13.388977',
             'osm_id': '1818862993', 'osm_type': 'node',
             'place_id': '18439434'}
        
        See also
        --------
        :meth:`~OSMService.place2coord`, :meth:`~OSMService.url_reverse`, 
        :meth:`_Service.get_status`, :meth:`_Service.get_response`.
        """
        kwargs.update({'key': _geoDecorators.parse_geometry.KW_FEATURES})
        return super(GISCOService,self).coord2geom(coord=coord, **kwargs)
      
    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2place(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographical coordinates using |OSM| service.
        
            >>>  place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[radius, distance_sort, limit, lang]` are accepted; 
            see :meth:`~GISCOService.url_reverse`.
        
        Returns
        -------
        place : str, list[str]
            place (topo)name(s) identifying the input geolocation(s) in :data:`coord`.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
        >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
        >>> serv = services.GISCOService()
        >>> serv.url_reverse(lat=berlin[0], lon=berlin[1])
            'http://europa.eu/webtools/rest/gisco/reverse?lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2place` does everything at once:
        
        >>> serv.coord2place(berlin, format='json')
            'Caroline-von-Humboldt-Weg, Berlin, 10117, Germany'
        
        See also
        --------
        :meth:`~OSMService.coord2place`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`, 
        :meth:`~GISCOService.url_reverse`.
        """
        kwargs.update({'key': _geoDecorators.parse_geometry.KW_FEATURES})
        return super(GISCOService,self).coord2place(coord=coord, **kwargs)

    #/************************************************************************/
    def _coord2nuts(self, coord, **kwargs):
        """Iterable version of :meth:`~GISCOService.coord2nuts`.
        """
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt is not None:
            kwargs.update({'f':fmt or 'JSON'})
        kwargs.update({#'year': kwargs.pop('year',2013), 
                       # 'proj': kwargs.pop('proj',4326),
                       'geometry': kwargs.pop('geometry','N')
                       })
        for i in range(len(coord)):
            kwargs.update({'x': coord[i][1], 'y': coord[i][0]})
            try:
                url = self.url_nuts(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error NUTS request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in ({},None)
            except:
                happyError('NUTS for location %s not loaded' % coord[i])
            try:
                assert key is not None
            except AssertionError:
                try:
                    assert data != [] 
                except:
                    raise happyError('NUTS for geolocation %s not recognised' % coord[i])  
                else:
                    pass
            else:
                try:
                    assert key in data and data[key] != [] 
                except AssertionError:
                    raise happyError('NUTS for geolocation %s and key %s not recognised' % (coord[i], key))  
                else:
                    data = data.get(key)
            yield data if not _Types.ismapping(data) or len(data)>1 else data[0]

    #/************************************************************************/
    @_geoDecorators.parse_year
    @_geoDecorators.parse_projection
    @_geoDecorators.parse_geometry
    @_geoDecorators.parse_coordinate
    def coord2nuts(self, coord, **kwargs):
        """Retrieve the various |NUTS| geometries (all levels) associated to given 
        geolocation(s) provided as geographical :literal:`(lat,Lon)` coordinates.
        
            >>> nuts = serv.coord2nuts(coord, **kwargs)

        Arguments
        ---------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographical 
            coordinates.
        
        Keyword arguments
        -----------------
        level : int
            integer in [0,3] defining the classification level of the NUTS geometry 
            to return, if not all (default when :data:`level` is :data:`None`).
        
        Returns
        -------
        nuts : dict, list[dict]
            a (list of) dictionary(ies) representing NUTS geometries.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the case the NUTS request is wrongly formulated.
            
        Examples
        --------
        We can easily retrieve all NUTS geometry associated to Rome, Italia from its
        geocoordinates:
            
        >>> serv.coord2nuts([41.8933203,12.4829321])
            [{'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '0',
               'NAME_LATN': 'ITALIA', 'NUTS_ID': 'IT', 'NUTS_NAME': 'ITALIA',
               'OBJECTID': '17',
               'SHRT_ENGL': 'Italy'},
              'displayFieldName': 'NUTS_ID',
              'layerId': 2, 'layerName': 'NUTS_2013',
              'value': 'IT'},
             {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '1',
               'NAME_LATN': 'CENTRO (IT)', 'NUTS_ID': 'ITI', 'NUTS_NAME': 'CENTRO (IT)',
               'OBJECTID': '94',
               'SHRT_ENGL': 'Italy'},
              'displayFieldName': 'NUTS_ID',
              'layerId': 2, 'layerName': 'NUTS_2013',
              'value': 'ITI'},
             {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2',
               'NAME_LATN': 'Lazio', 'NUTS_ID': 'ITI4', 'NUTS_NAME': 'Lazio',
               'OBJECTID': '330',
               'SHRT_ENGL': 'Italy'},
              'displayFieldName': 'NUTS_ID',
              'layerId': 2, 'layerName': 'NUTS_2013',
              'value': 'ITI4'},
             {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '3',
               'NAME_LATN': 'Roma', 'NUTS_ID': 'ITI43', 'NUTS_NAME': 'Roma',
               'OBJECTID': '1053',
               'SHRT_ENGL': 'Italy'},
              'displayFieldName': 'NUTS_ID',
              'layerId': 2, 'layerName': 'NUTS_2013',
              'value': 'ITI43'}]  
            
        If we are interested in one level only instead:
        
        >>> serv.coord2nuts([41.8933203,12.4829321], level=2)
            {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2',
              'NAME_LATN': 'Lazio', 'NUTS_ID': 'ITI4', 'NUTS_NAME': 'Lazio',
              'OBJECTID': '330',
              'SHRT_ENGL': 'Italy'},
             'displayFieldName': 'NUTS_ID',
             'layerId': 2, 'layerName': 'NUTS_2013',
             'value': 'ITI4'}        
        
        See also
        --------
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`,
        :meth:`~GISCOService.coord2place`, :meth:`~GISCOService.url_nuts`, 
        :meth:`_Service.get_response`.
        """
        level = kwargs.pop('level',None)
        kwargs.update({'key': _geoDecorators.parse_nuts.KW_RESULTS})
        nuts = []        
        #[nuts.append(data if len(data)>1 else data[0]) for data in self._coord2nuts(coord, **kwargs)]
        func = lambda **kw: [kw.get('nuts')]
        [nuts.append(data if len(data)>1 else data[0])                     \
             for g in self._coord2nuts(coord, **kwargs)                     \
             for data in _geoDecorators.parse_nuts(func)(g, level=level)]
        return nuts[0] if len(nuts)==1 else nuts


    #/************************************************************************/
    @_geoDecorators.parse_year
    @_geoDecorators.parse_projection
    @_geoDecorators.parse_place
    def place2nuts(self, place, **kwargs): # specific use
        """
            >>> nuts = serv.place2nuts(place, **kwargs)

        Arguments
        ---------
        place : str or list[str]
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        nuts :
                 
        See also
        --------
        :meth:`~GISCOService.place2coord`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.url_geocode`, 
        :meth:`_Service.get_response`.
        """
        lat, lon = self.place2coord(place, **kwargs)
        nuts = self.coord2nuts(lat, lon, **kwargs)
        return nuts[0] if len(nuts)==1 else nuts
        #res = _geoDecorators.parse_nuts(lambda **kw: kw.get('nuts'))(nuts, **kwargs)
        #return res[0] if len(res)==1 else res

    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2route(self, coord, **kwargs):
        """
            >>>  route = serv.coord2route(coord, **kwargs)

        Arguments
        ---------
        coord : list[float]
        
        Keyword arguments
        -----------------
        route : 
        
        Returns
        -------
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the route request is wrongly formulated,
                * the route is not available,                
                * the route is not recognised.
       
        See also
        --------
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.coord2place`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.url_route`, 
        :meth:`_Service.get_response`.
        """
        routes, waypoints = None, None
        if not coord in([],None):
            coordinates = ';'.join([','.join([str(l), str(L)]) for (l,L) in coord])
        elif kwargs.get():
            coordinates = kwargs.pop(_geoDecorators.parse_coordinate.KW_POLYLINE)
        kwargs.update({'coordinates': coordinates})
        try:
            url = self.url_route(**kwargs)
            assert self.get_status(url) is not None
        except:
            raise happyError('error route request')
        else:
            response = self.get_response(url)
        pass
        try:
            data = json.loads(response.text)
            assert data is not None
        except:
            raise happyError('route not available')
        try:
            assert _geoDecorators.parse_route.KW_CODE in data       \
                and data[_geoDecorators.parse_route.KW_CODE].upper() == "OK"
        except:
            raise happyError('route  not recognised')      
        else:
            routes = data.get(_geoDecorators.parse_route.KW_ROUTES)
            waypoints = data.get(_geoDecorators.parse_route.KW_WAYPOITNS)
        return routes[0], waypoints

    #/************************************************************************/
    def geomtrans(self, *args, **kwargs):
        pass
    
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

        CODER = {'GoogleV3':         None,   # API authentication is only required for Google Maps Premier customers
                 'Bing':             'key',  # valid Bing Maps API key
                 'GeoNames':         'username', # username required for API access
                 'YahooPlaceFinder': 'key',  # Key provided by Yahoo
                 'OpenMapQuest':     None,       # No API Key is needed by the Nominatim based platform
                 'MapQuest':         'key',  # API key provided by MapQuest
                 'LiveAddress':      'token',# Valid authentication token; LiveAddress geocoder provided by SmartyStreets
                 'Nominatim':        None,       # Nominatim geocoder for OpenStreetMap servers
                 } 
     
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
                
_geoCoderAPI.__doc__ =                                                      \
        """Class emulating :mod:`geopy` API (whenever the package |geopy| is available).

        Inherit all methods from original API.
        
        Most of the :class:`geopy.geocoders` methods are inherited by the class
        :class:`~services.APIService` through composition and embedding in container 
        attributes. 
        """

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

_googleMapsAPI.__doc__ =                                                    \
        """Class emulating :class:`googlemaps.Client` API (whenever the package 
        |googlemaps| is available).

        Inherit many methods from original API.

        Most of the :class:`googlemaps.Client` methods are inherited by the
        :class:`~services.APIService` class through composition and embedding 
        in container attributes. 
        """

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

_googlePlacesAPI.__doc__ =                                                  \
        """Class emulating :class:`googleplaces.GooglePlaces` API (whenever the 
        package |googleplaces| is available).

        Inherit most methods from original API.

        Most of the :class:`googleplaces.GooglePlaces` methods are inherited by the
        :class:`~services.APIService` class through composition and embedding 
        in container attributes. 
        """

#%%
#==============================================================================
# CLASS APIService
#==============================================================================
     
class APIService(_Service):
    """Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
       
        >>> serv = services.APIService(**kwargs)
            
    Keyword arguments
    -----------------
    domain : str
        domain of |OSM| web-services hosted by |GISCO|; default is :data:`settings.GISCO_URL`,
        *e.g.* an URL domain like :literal:`'europa.eu/webtools/rest/gisco/'`\ . 
    coder : str
        identifier of the geocoder, *e.g.* |Google_Maps|, |Google_Places|, 
        *etc*... used for geolocation queries.
    key/token/username : str
        key (depending on the :data:`coder` actually chosen) used to connect 
        to the geolocation API.
 
    Attributes
    ----------     
    CODER :
        coder dictionary defining the connection to |GISCO| based web-service
        set to {:data:`settings.CODER_GISCO`: :data:`settings.KEY_GISCO` }, *e.g*
        :literal:`{'gisco': None}` since there is currently no authentication 
        requested.
    """
    
    CODER = dict(_googlePlacesAPI.CODER.items()
                 | _googleMapsAPI.CODER.items() 
                 | _geoCoderAPI.CODER.items()) # we know there is no duplicate, so ok to use | ...
    
    #/************************************************************************/
    def __init__(self, **kwargs):
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
        """Coder attribute (:data:`getter`) of a :class:`APIService` instance. 
        A `coder` type is a either :class:`~happygisco.services._googlePlacesAPI`,  
        or a :class:`~happygisco.services._googleMapsAPI`, or  
        :class:`~happygisco.services._geoCoderAPI` object.
        """
        return self.__coder
            
    @property
    def coder_key(self):
        """Service attribute (:data:`getter`/:data:`setter`) of a :class:`APIService` 
        instance. 
        A `coder_key` type is a :class:`str` object.
        """
        return self.__coder_key
    @coder_key.setter#analysis:ignore
    def coder_key(self, key):
        if not isinstance(key, str):
            raise IOError('wrong type for CODER_KEY parameter')
        self.__coder_key = key

    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs):
        """Retrieve the geographical coordinates associated to a (a list of) 
        toponame(s).
        
            >>> coord = serv.place2coord(place, **kwargs)

        Argument
        --------
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        
        See also
        --------
        :meth:``\ .
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
    def coord2place(self, coord, **kwargs):
        """Associate a (list of) toponame(s) with a (set of) given geographical
        coordinates.
        
            >>>  = serv.(coord, **kwargs)

        Arguments
        ---------
        coord : 
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        
        See also
        --------
        :meth:``.
        """
        #places = self.coder.reverse(coord[0], coord[1])
        places = [] 
        for i in range(len(coord)):   
            try:
                p = self.coder.reverse(coord[i][0],coord[i][1])
                assert p not in ('',None)
                places.append(p)
            except:
                places.append(None)
                happyVerbose('\ncould not retrieve place name for geolocation %s' % coord[i])
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
