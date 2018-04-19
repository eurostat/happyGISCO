#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. services

Module implementing simple requests to various web-based geographical services, 
including |Eurostat| |GISCO|, |OSM| |Nominatim| and |GMaps|.

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

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `OpenStreetMap <OSM_>`_
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. |Nominatim| replace:: `Nominatim <Nominatim_>`_
.. _googlemaps: https://pypi.python.org/pypi/googlemaps
.. |googlemaps| replace:: `Google Maps <googlemaps_>`_
.. _googleplaces: https://github.com/slimkrazy/python-google-places
.. |googleplaces| replace:: `Google Places <googleplaces_>`_
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
from happygisco.settings import happyVerbose, happyWarning, happyError, _geoDecorators

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

#%%
#==============================================================================
# CLASS _Service
#==============================================================================

class _Service(object):
    """
    .. Links
    
    .. _Eurostat: http://ec.europa.eu/eurostat/web/main
    .. |Eurostat| replace:: `Eurostat <Eurostat_>`_
    .. _GISCO: http://ec.europa.eu/eurostat/web/gisco
    .. |GISCO| replace:: `GISCO <GISCO_>`_

    Base class defining a web-session and simple connection operations to be
    used by a web-service. 
       
        >>> serv = services._Service()
            
    Returns
    -------
    serv : :class:`requests.session.Session`
        a web session used to connect to external URLs.
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
        a class :class:`_Service`\ . 
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
        We can check the response status code when connecting to different web-pages/serving:
        
        >>> serv = _Service()
        >>> serv.get_status('http://dumb')
        ConnectionError: connection failed
        >>> serv.get_status('http://www.dumbanddumber.com')
        301 
        
        Let us check that the status is ok when connecting to |Eurostat| website:
            
        >>> stat = serv.get_status(settings.ESTAT_URL)
        >>> print(stat)
        200
        >>> import requests
        >>> stat == requests.codes.ok
        True
        
        See also
        --------
        :meth:`get_response`, :meth:`build_url`.
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
            
        >>> serv = _Service()
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
            'Content-Encoding': 'gzip'}
        
        We can also access the response body as bytes (though that is usually
        adapted to non-text requests):
            
        >>> print(resp.content)
        b'<!DOCTYPE html PUBLIC " ...
        
        See also
        --------
        :meth:`get_status`, :meth:`build_url`.
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
        :meth:`get_status`, :meth:`get_response`.
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
    """
    .. Links
    
    .. _Eurostat: http://ec.europa.eu/eurostat/web/main
    .. |Eurostat| replace:: `Eurostat <Eurostat_>`_
    .. _GISCO: http://ec.europa.eu/eurostat/web/gisco
    .. |GISCO| replace:: `GISCO <GISCO_>`_
    .. _GISCOWIKI: https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=GISCO&postingDay=2016%2F1%2F20&title=Background+Services+at+the+EC+cooperate+level+in+production+in+four+projections
    .. |GISCOWIKI| replace:: `GISCOWIKI <GISCOWIKI_>`_
    .. _OSM: https://www.openstreetmap.org
    .. |OSM| replace:: `OpenStreetMap <OSM_>`_
    .. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
    .. |Nominatim| replace:: `Nominatim <Nominatim_>`_
    .. _googlemaps: https://pypi.python.org/pypi/googlemaps
    .. |googlemaps| replace:: `Google Maps <googlemaps_>`_
    .. _googleplaces: https://github.com/slimkrazy/python-google-places
    .. |googleplaces| replace:: `Google Places <googleplaces_>`_
    .. _geopy: https://github.com/geopy/geopy
    .. |geopy| replace:: `geopy <geopy_>`_
    .. _PyGeoTools: https://github.com/jfein/PyGeoTools/blob/master/geolocation.py
    .. |PyGeoTools| replace:: `PyGeoTools <PyGeoTools_>`_

    """
    pass

#%%
#==============================================================================
# CLASS GISCOService
#==============================================================================
    
class GISCOService(_Service):
    """
    .. Links
    
    .. _Eurostat: http://ec.europa.eu/eurostat/web/main
    .. |Eurostat| replace:: `Eurostat <Eurostat_>`_
    .. _GISCO: http://ec.europa.eu/eurostat/web/gisco
    .. |GISCO| replace:: `GISCO <GISCO_>`_
    .. _GISCOWIKI: https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=GISCO&postingDay=2016%2F1%2F20&title=Background+Services+at+the+EC+cooperate+level+in+production+in+four+projections
    .. |GISCOWIKI| replace:: `GISCOWIKI <GISCOWIKI_>`_
    .. _OSM: https://www.openstreetmap.org
    .. |OSM| replace:: `OpenStreetMap <OSM_>`_
    .. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
    .. |Nominatim| replace:: `Nominatim <Nominatim_>`_
    .. _googlemaps: https://pypi.python.org/pypi/googlemaps
    .. |googlemaps| replace:: `Google Maps <googlemaps_>`_
    .. _googleplaces: https://github.com/slimkrazy/python-google-places
    .. |googleplaces| replace:: `Google Places <googleplaces_>`_
    .. _geopy: https://github.com/geopy/geopy
    .. |geopy| replace:: `geopy <geopy_>`_
    .. _PyGeoTools: https://github.com/jfein/PyGeoTools/blob/master/geolocation.py
    .. |PyGeoTools| replace:: `PyGeoTools <PyGeoTools_>`_

    Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
       
        >>> serv = GISCOService(**kwargs)
            
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
        """Domain attribute (:data:`getter`/:data:`setter`) of an instance of
        a class :class:`_Service`\ . 
        """ # A domain type is :class:`str`.
        return self.__domain
    @domain.setter#analysis:ignore
    def domain(self, domain):
        if domain is not None and not isinstance(domain, str):
            raise TypeError('wrong type for DOMAIN parameter')
        self.__domain = domain or ''

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Generate the query URL for the geocoding web-service (from toponame to
        geocoordinate).
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`q, lat, lon, distance_sort, limit, osm_tag`, and :literal:`lang`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *geocode* results (*i.e.*, geocoordinates) 
            associated to a given place using |GISCO| web-service; the generic form of 
            :data:`url` is :literal:`domain/api?{filters}` with :literal:`filters` the 
            filters passed through :data:`kwargs`\ .
        
        Example
        -------
        Let us create a simple URL for querying the geolocation of a toponame:
            
        >>> serv = GISCOService()
        >>> serv.url_geocode(q='Paris+France')
        'http://europa.eu/webtools/rest/gisco/api?q=Paris+France'
        
        See also
        --------
        :meth:`url_reverse`, :meth:`url_route`, :meth:`url_transform`, :meth:`url_nuts`,
        :meth:`~_Service.build_url`.
        """
        keys = ['q', 'lat', 'lon', 'distance_sort', 'limit', 'osm_tag', 'lang']
        happyVerbose('\n            * '.join(['input filters used for geocoding service :',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(domain=self.domain, 
                             query='api', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for the reverse geocoding web-service (from 
        geocoordinate to toponame).
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :literal:`lat, lon, radius, distance_sort, limit`, and :literal:`lang`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *reverse geocode* results (*i.e.*, 
            toponame) associated to given geocoordinates using |GISCO| web-service; 
            the generic form of :data:`url` is :literal:`domain/reverse?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`\ .
       
        Example
        -------
        We can generate the URL for querying the toponame associated to a given
        geolocation:

        >>> serv = GISCOService()
        >>> serv.url_reverse(lon=10, lat=52))
        'http://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52'
        
        See also
        --------
        :meth:`url_geocode`, :meth:`url_route`, :meth:`url_transform`, :meth:`url_nuts`,
        :meth:`~_Service.build_url`.
        """
        keys = ['lat', 'lon', 'radius', 'distance_sort', 'limit', 'lang']
        happyVerbose('\n            * '.join(['input filters used for reverse geocoding service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(domain=self.domain, 
                             query='reverse', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    def url_route(self, **kwargs):
        """
        http(s)://europa.eu/webtools/rest/gisco/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219?overview=false
        
        See also
        --------
        :meth:`url_geocode`, :meth:`url_reverse`, :meth:`url_transform`, :meth:`url_nuts`,
        :meth:`~_Service.build_url`.
        """
        keys = ['overview', ] # ?
        happyVerbose('\n            * '.join(['input filters used for routing service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        coordinates = kwargs.pop('coordinates','')
        polyline = kwargs.pop(_geoDecorators.parse_coordinate.KW_POLYLINE,None)
        polyline = 'polyline(' + polyline + ')' if polyline else ''
        url = self.build_url(domain=self.domain, 
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
        
        See also
        --------
        :meth:`url_geocode`, :meth:`url_reverse`, :meth:`url_route`, :meth:`url_nuts`,
        :meth:`~_Service.build_url`.
        """
        keys = ['inSR', 'outSR', 'geometries', 'transformation', 'transformForward', 'f'] # ?
        url = self.build_url(domain=self.arcgis, 
                             query='Utilities/Geometry/GeometryServer/project', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
    
    #/************************************************************************/
    @_geoDecorators.parse_projection
    def url_nuts(self, **kwargs):
        """Create a query URL to be submitted to the GISCO (simple) web-service 
        for NUTS codes identification.
        
            >>> url = GISCOService.url_nuts(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            define the parameters for web-service; allowed parameters are: 
            :literal:`x, y, f, year, proj`, and :literal:`geometry`\ .
            
        Returns
        -------
        url : str
            link to NUTS web service to submit the specified 'NUTS' query that
            identifies the NUTS code of a given geolocation.
            the generic url formatting is: domain/nuts/find-nuts.py?{filters}
            
        Usage
        -----
        x=<lon>&y=<lat>&f=<JSON/XML>&year=<2013/2010/2006>&proj=3035&geometry=<N/Y>
        
        See also
        --------
        :meth:`url_geocode`, :meth:`url_reverse`, :meth:`url_route`, :meth:`url_transform`,
        :meth:`~_Service.build_url`.
        """
        keys = ['x', 'y', 'f', 'year', 'proj', 'geometry']
        happyVerbose('\n            * '.join(['input filters used for NUTS identification service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(domain=self.domain, 
                             path='nuts', 
                             query='find-nuts.py', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2geom(self, place, **kwargs): 
        """
        
            >>>  = serv.(, **kwargs)

        Argument
        --------
        
        Keyword arguments
        -----------------
        
        Returns
        -------
            
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
        
        See also
        --------
        :meth:`place2coord`, :meth:`coord2place`, :meth:`coord2nuts`, :meth:`place2nuts`, 
        :meth:`coord2route`, :meth:`url_geocode`, :meth:`~_Service.get_response`.
        """
        place = ['+'.join(p.replace(',',' ').split()) for p in place]
        geom = []
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
                assert 'features' in data and data['features'] != [] 
            except:
                raise happyError('geolocation for place %s not recognised' % p)      
            else:
                c = data.get('features')
                geom.append(c if len(c)>1 else c[0])
        return geom if len(geom)>1 else geom[0]
        
    #/************************************************************************/
    @_geoDecorators.parse_place
    def place2coord(self, place, **kwargs): # specific use
        """
        
            >>>  coord = serv.place2coord(place, **kwargs)

        Argument
        --------
        place : str or list[str]
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        coord :
        
        See also
        --------
        :meth:`place2geom`, :meth:`coord2place`, :meth:`coord2nuts`, :meth:`place2nuts`, 
        :meth:`coord2route`.
        """
        geom = self.place2geom(place, **kwargs)
        return _geoDecorators.parse_geometry(lambda **kw: [kw.get('lat'), kw.get('lon')])(geom)
       
    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2place(self, lat, lon, **kwargs): # specific use
        """
        
            >>>  place = serv.coord2place(lat, lon, **kwargs)

        Arguments
        ---------
        lat,lon : float, list[float]
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        place : str, list[str]
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
        
        See also
        --------
        :meth:`place2coord`, :meth:`place2geom`, :meth:`coord2nuts`, :meth:`place2nuts`, 
        :meth:`coord2route`, :meth:`url_reverse`, :meth:`~_Service.get_response`.
        """
        place = []
        for i in range(len(lat)):
            kwargs.update({'lat': lat[i], 'lon': lon[i]})
            try:
                url = self.url_reverse(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in({},None)
            except:
                raise happyError('place for geolocation (%s,%s) not loaded' % (lat[i], lon[i]))
            try:
                assert _geoDecorators.parse_geometry.KW_FEATURES in data     \
                    and data[_geoDecorators.parse_geometry.KW_FEATURES] != []
            except:
                raise happyError('place for geolocation (%s,%s) not recognised' % (lat[i], lon[i]))      
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
        
            >>> nuts = serv.(lat, lon, **kwargs)

        Arguments
        ---------
        lat,lon : float, list(float)
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        
        Raises
        ------
        ~settings.happyError
            error is raised in the case the NUTS request is wrongly formulated.
        
        See also
        --------
        :meth:`place2geom`, :meth:`place2coord`, :meth:`place2nuts`, :meth:`coord2route`,
        :meth:`coord2place`, :meth:`url_nuts`, :meth:`~_Service.get_response`.
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
                raise happyError('error NUTS request')
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
        """
            >>> nuts = serv.place2nuts(place, **kwargs)

        Argument
        --------
        place : str or list[str]
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        nuts :
                 
        See also
        --------
        :meth:`place2coord`, :meth:`coord2nuts`, :meth:`place2geom`, :meth:`coord2place`, 
        :meth:`coord2route`, :meth:`url_geocode`, :meth:`~_Service.get_response`.
        """
        lat, lon = self.place2coord(place, **kwargs)
        nuts = self.coord2nuts(lat, lon, **kwargs)
        return nuts[0] if len(nuts)==1 else nuts
        #res = _geoDecorators.parse_nuts(lambda **kw: kw.get('nuts'))(nuts, **kwargs)
        #return res[0] if len(res)==1 else res

    #/************************************************************************/
    @_geoDecorators.parse_coordinate
    def coord2route(self, lat, lon, **kwargs):
        """
            >>>  route = serv.coord2route(lat, lon, **kwargs)

        Argument
        --------
        lat,lon : list[float]
        
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
        :meth:`place2geom`, :meth:`place2coord`, :meth:`coord2place`, :meth:`coord2nuts`, 
        :meth:`place2nuts`, :meth:`url_route`, :meth:`~_Service.get_response`.
        """
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
        
        Most of the :class:`geopy.geocoders` methods will be inherited by the class
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
        """Class emulating :class:`~googlemaps.Client` API (whenever the package 
        |googlemaps| is available).

        Inherit many methods from original API.

        Most of the :class:`googlemaps.Client` methods will be inherited by the
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
        """
        """

#==============================================================================
# CLASS APIService
#==============================================================================
     
#%%
class APIService(_Service):
    """
    .. Links
    
    .. _Eurostat: http://ec.europa.eu/eurostat/web/main
    .. |Eurostat| replace:: `Eurostat <Eurostat_>`_
    .. _GISCO: http://ec.europa.eu/eurostat/web/gisco
    .. |GISCO| replace:: `GISCO <GISCO_>`_
    .. _GISCOWIKI: https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=GISCO&postingDay=2016%2F1%2F20&title=Background+Services+at+the+EC+cooperate+level+in+production+in+four+projections
    .. |GISCOWIKI| replace:: `GISCOWIKI <GISCOWIKI_>`_
    .. _OSM: https://www.openstreetmap.org
    .. |OSM| replace:: `OpenStreetMap <OSM_>`_
    .. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
    .. |Nominatim| replace:: `Nominatim <Nominatim_>`_
    .. _googlemaps: https://pypi.python.org/pypi/googlemaps
    .. |googlemaps| replace:: `Google Maps <googlemaps_>`_
    .. _googleplaces: https://github.com/slimkrazy/python-google-places
    .. |googleplaces| replace:: `Google Places <googleplaces_>`_
    .. _geopy: https://github.com/geopy/geopy
    .. |geopy| replace:: `geopy <geopy_>`_
    .. _PyGeoTools: https://github.com/jfein/PyGeoTools/blob/master/geolocation.py
    .. |PyGeoTools| replace:: `PyGeoTools <PyGeoTools_>`_


    Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
       
        >>> serv = APIService(**kwargs)
            
    Keyword arguments
    -----------------
    domain : str
        domain of |OSM| web-services hosted by |GISCO|; default is :data:`settings.GISCO_URL`,
        *e.g.* an URL domain like :literal:`'europa.eu/webtools/rest/gisco/'`\ . 
    coder : str
        coder selection.
    key : str
 
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
        
        Raises
        ------
        
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
    def coord2place(self, lat, lon, **kwargs):
        """Associate a (list of) toponame(s) with a (set of) given geographical
        coordinates.
        
            >>>  = serv.(, **kwargs)

        Argument
        --------
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        
        Raises
        ------
        
        See also
        --------
        :meth:``\ .
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
