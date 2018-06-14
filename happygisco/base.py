#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_base

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

Base implementations (generic methods and classes) used trhoughout :mod:`happygisco`.

**Description**
  
**Note**

The :class:`_Decorator` class and its subclasses exposed in this module **can be 
ignored** at the first glance since they are not requested to run the services. 
They are provided here for the sake of an exhaustive documentation.

**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`itertools`, :mod:`functools`, :mod:`collections`

*optional*:     :mod:`requests`

*call*:         :mod:`settings`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat May  5 00:09:56 2018

__all__         = ['_Service', '_Feature', '_Tool', '_Decorator']

# generic import
import os, sys#analysis:ignore
import itertools, functools
import collections#analysis:ignore

# local imports
from happygisco import settings
from happygisco.settings import happyVerbose, happyWarning, happyError, happyType

# requirements
try:                
    SERVICE_AVAILABLE = True                
    import requests # urllib2
except ImportError:                 
    SERVICE_AVAILABLE = False                
    happyWarning('REQUESTS package (https://pypi.python.org/pypi/requests/) not loaded - GISCO ONLINE service will not be accessed')


#%%
#==============================================================================
# CLASS _Service
#==============================================================================

class _Service(object):
    """Base class for web-based geospatial services.
    
    This class is used to defined a web-session and simple connection operations 
    called by a web-service. 
        
    ::
        
       >>> serv = base._Service()
        
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
        """Session property (:data:`getter`/:data:`setter`) of an instance of
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
        
        ::
        
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
        
        ::
        
            >>> serv = base._Service()
            >>> serv.get_status('http://dumb')
                ConnectionError: connection failed
            >>> serv.get_status('http://www.dumbanddumber.com')
                301 
        
        Let us actually check that the status is ok when connecting to |Eurostat| website:
        
        ::
            
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
        
        ::
        
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
        
        ::
            
            >>> serv = base._Service()
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
        
        ::
            
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
        
        ::
            
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
    def build_url(cls, domain=None, **kwargs):
        """Create a complete query URL to be used by a web-service.
        
        ::
        
            >>> url = _Service.build_url(domain, **kwargs)
            
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
        
        ::
            >>> from happygisco.base import _Service
            >>> _Service.build_url(settings.ESTAT_URL,
                                   path='wdds/rest/data/v2.1/json/en',
                                   query='ilc_li03', 
                                   precision=1,
                                   indic_il='LI_R_MD60',
                                   time='2015')
                'http://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/ilc_li03?precision=1&indic_il=LI_R_MD60&time=2015'
        
        Note that another way to call the method is:
        
        ::

            >>> _Service.build_url(domain=settings.ESTAT_URL,
                                   path='wdds/rest/data/v2.1/json/en',
                                   query='ilc_li01', 
                                   **{'precision': 1, 'hhtyp': 'A1', 'time': '2010'})
                'http://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/ilc_li01?precision=1&hhtyp=A1&time=2010'
        
        Similarly, we will be able to access to |GISCO| service (see :meth:`GISCOService.url_geocode`
        below):
         
        ::

            >>> _Service.build_url(domain=settings.GISCO_URL,
                                   query='api', 
                                   **{'q': 'Berlin+Germany', 'limit': 2})
                'http://europa.eu/webtools/rest/gisco/api?q=Berlin+Germany&limit=2'  
        
        See also
        --------
        :meth:`~_Service.get_status`, :meth:`~_Service.get_response`.
        """
        # retrieve parameters/build url
        if domain is None:      domain = kwargs.pop('domain','')
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
# CLASS _Tool
#==============================================================================

class _Tool(object):   
    """Dummy base class for geospatial "tools". 
    """
    pass

#%%
#==============================================================================
# CLASS _Feature
#==============================================================================
            
class _Feature(object):    
    """Base class for geographic features.
    
        >>> feat = base._Feature()
    """

    #/************************************************************************/
    def __init__(self):
        self._coord = None
        self._service, self._tool = None, None
        try:
            assert True
        except:
            happyWarning('tool(s) not available')
        else:
            self._tool = _Tool()
        try:
            assert SERVICE_AVAILABLE
        except:
            happyWarning('web service(s) not available')
        else:
            self._service = _Service()
       
    #/************************************************************************/
    @property
    def service(self):
        """Service property (:data:`getter`) of a :class:`_Feature` instance. 
        A :data:`service` object will be generally a :class:`~happygisco.services.GISCOService` 
        or a :class:`~happygisco.services.APIService` instance.
        """
        return self._service
       
    @property
    def tool(self):
        """Geospatial tool property (:data:`getter`) of a :class:`_Feature` instance.
        A :data:`service` object will be generally a :class:`~happygisco.tools.GDALTool` 
        instance.
        """
        return self._tool
    
    @property
    def coord(self):
        # ignore: this will be overwritten              
        """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`) 
        of a :class:`_Feature` instance.
        """ 
        return self._coord

#%%
#==============================================================================
# CLASS _Decorator
#==============================================================================
    
class _Decorator(object):
    """Class implementing dummy decorators of methods and functions used to parse 
    and check arguments as geographic features, *e.g.* place, coordinates or 
    geometries.
    
    Methods from the :mod:`services` module rely on these classes.
    """
    
    KW_PLACE        = 'place'
    KW_ADDRESS      = 'address'
    KW_CITY         = 'city'
    KW_COUNTRY      = 'country'
    KW_ZIPCODE      = 'zip'
    
    KW_LAT          = 'lat'
    KW_LON          = 'Lon' 
    KW_COORD        = 'coord'
    
    KW_AREA         = 'area'
    
    KW_PROJECTION   = 'proj' 
    
    KW_YEAR         = 'year'
    
    KW_NUTS         = 'nuts' 
    
    KW_FILE         = 'file'
    KW_DATA         = 'data'

    #/************************************************************************/
    @staticmethod
    def _flatten(args):
        #ignore
        """Flatten a list of lists.
        """
        return list(itertools.chain.from_iterable(args))

    #/************************************************************************/
    class __parse(object):
        """Base parsing class for geographic entities. All decorators in 
        :class:`_Decorator` will inherit from this class.
        """
        def __init__(self, func, obj=None, cls=None, method_type='function'):
            self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type 
            setattr(self,'__doc__',object.__getattribute__(func, '__doc__'))
        #def __get__(self, obj, objtype):
        #    # support instance methods
        #    return functools.partial(self.__call__, obj)
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
        def __getattribute__(self, attr_name): 
            # this is the only way found so far to have both the generation of the 
            # documentation for methods and the retrieval of classes' attributes 
            # working together
            if attr_name in ('__init__', '__get__', '__getattribute__', '__call__', '__doc__', 
                             'func', 'obj', 'cls', 'method_type'): 
                return object.__getattribute__(self, attr_name)
            try:
                return getattr(self.func, attr_name)
            except:
                try:
                    return object.__getattribute__(self, attr_name)
                except:
                    pass
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
        def __repr__(self):
            return self.func.__repr__()

    #/************************************************************************/
    class parse_coordinate(__parse):
        """Generic class decorator of functions and methods used to parse place 
        :literal:`(lat,Lon)` coordinates.
        
        ::
        
            >>> new_func = _Decorator.parse_coordinate(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
            
        Keyword arguments
        -----------------
        method_type : str
            type of the method decorated; can be any string from 
            :literal:`['function', 'staticmethod', 'classmethod', 'property','instancemethod']`;
            default is :literal:`'function'`.
        obj : 
            instance whose method is decorated when the decorated function is an
            :literal:`'instancemethod'`; default is :data:`None`.
        cls : 
            class whose method is decorated when the decorated function is any 
            among :literal:`['staticmethod', 'classmethod', 'property','instancemethod']`; 
            default is :data:`None`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts geographic coordinates as 
            positional argument(s), plus some additional keyword arguments (see 
            *Notes* below).
        
        Examples
        --------        
        Some dummy examples:
        
        ::
            
            >>> func = lambda coord, *args, **kwargs: coord
            >>> new_func = _Decorator.parse_coordinate(func)
            >>> new_func(coord=[[1,-1],[2,-2]], order='Ll')
                [[-1, 1], [-2, 2]]
            >>> new_func(**{'lat':[1,2], 'Lon': [-1,-2]})
                [[1, -1], [2, -2]]
            >>> new_func(lat=[1,2], Lon=[-1,-2], order='Ll')
                [[-1, 1], [-2, 2]]
            >>> new_func(**{'y':[1,2], 'x': [-1,-2]})
                [[1, -1], [2, -2]]
            
        Note that the new decorated method also supports the parsing of the coordinates 
        as positional arguments (usage not recommended):
        
        ::
            
            >>> new_func([1,-1])
                [[1,-1]]
            >>> new_func([1,2],[-1,-2])
                [[1, -1], [2, -2]]
            >>> new_func(coord=[[1,-1],[2,-2]])
                [[1, -1], [2, -2]]

        Therefore, things like that should be avoided:
        
        ::

            >>> new_func([[1,-1],[2,-2]], lat=[1,2], Lon=[-1,-2])
                happyError: !!! dont mess up with me - duplicated coordinate argument parsed !!!
            >>> new_func(coord=[[1,-1],[2,-2]], lat=[1,2], Lon=[-1,-2])
                happyError: !!! AssertionError: too many input coordinate arguments !!!
             
        Notes
        -----
        * As per the use  of the :class:`_Decorator` decorating functions in the
          module :mod:`happyGISCO`, the keyword arguments :data:`obj,cls,method_type` 
          can be ignored. 
        * The decorated method/function :data:`new_func` accepts the same :data:`*args` 
          positional arguments as :data:`func` and, in addition to the arguments 
          in :data:`**kwargs` already supported by the input method/function :data:`func`, 
          an extra keyword argument:
              + :data:`order` : a flag used to define the order of the output parsed 
                geographic coordinates; it can be either :literal:`'lL'` for 
                :literal:`(lat,Lon)` order or :literal:`'Ll'` for a :literal:`(Lon,lat)` 
                order; default is :literal:`'lL'`.
        * The output decorated method :data:`new_func` can parse the following keys: 
          :literal:`['lat', 'Lon', 'x', 'y', 'coord']` from any input keyword argument. 
          See the examples above.
           
        See also
        --------
        :meth:`~_Decorator.parse_place`, :meth:`~_Decorator.parse_place_or_coordinate`,
        :meth:`~_Decorator.parse_area`.
        """
        KW_POLYLINE      = 'polyline'
        try:
            if settings.POLYLINE:    import polyline
            else:           polyline = True
            assert polyline
        except:
            polyline = False
            happyWarning('POLYLINE (https://pypi.python.org/pypi/polyline/) not loaded')
        else:
            if settings.POLYLINE:   happyWarning('POLYLINE help: https://github.com/hicsail/polyline')
            pass
        def __call__(self, *args, **kwargs):
            order = kwargs.pop('order', 'lL')
            if not happyType.isstring(order) or not order in ('Ll','lL'):
                raise happyError('wrong order parameter')
            coord, lat, lon, poly = None, None, None, None
            if args not in (None,()):      
                if all([isinstance(a,_Feature) for a in args]):
                    try:
                        coord = [a.coord for a in args]
                    except:
                        raise happyError('parsed coordinates feature not recognised')
                elif all([happyType.ismapping(a) for a in args]):
                    coord = list(args)
                elif len(args) == 1 and happyType.issequence(args[0]):
                    if len(args[0])==2                                      \
                        and all([happyType.issequence(args[0][i]) or not hasattr(args[0][i],'__len__') for i in (0,1)]):
                        lat, lon = args[0]
                    elif all([happyType.ismapping(args[0][i]) for i in range(len(args[0]))]):
                        coord = args[0]
                    elif all([len(args[0][i])==2 for i in range(len(args[0]))]):
                        coord = args[0]
                elif len(args) == 2                                         \
                    and all([happyType.issequence(args[i]) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    lat, lon = args
                else:   
                    raise happyError('input coordinate arguments not recognised')
            if lat is None and lon is None and coord is None:
                coord = kwargs.pop(_Decorator.KW_COORD, None)         
                lat = kwargs.pop(_Decorator.KW_LAT, None) or kwargs.pop('y', None)
                lon = kwargs.pop(_Decorator.KW_LON, None) or kwargs.pop('x', None)
                poly = self.polyline and kwargs.get(_Decorator.parse_coordinate.KW_POLYLINE)
            elif not (kwargs.get(_Decorator.KW_LAT) is None and \
                      kwargs.get(_Decorator.KW_LON) is None and \
                      kwargs.get(_Decorator.KW_COORD) is None):
                raise happyError('don''t mess up with me - duplicated coordinate argument parsed')
            try:
                assert not(coord is None and lat is None and lon is None and poly in (False,None)) 
            except AssertionError:
                raise happyError('no input coordinate arguments passed')
            try:
                assert coord is None or (lat is None and lon is None)
            except AssertionError:
                raise happyError('too many input coordinate arguments')
            if poly not in (False,None):
                # coord = self.polyline.decode(poly)
                return self.func(None, None, **kwargs)
            if not (lat is None and lon is None):
                if not isinstance(lat,(list,tuple)):  
                    lat, lon = [lat,], [lon,]
                if not len(lat) == len(lon):
                    raise happyError('incompatible geographic coordinates')
                coord = [list(_) for _ in zip(lat, lon)]
            elif all([happyType.ismapping(coord[i]) for i in range(len(coord))]):
                coord = [[coord[i].get(_Decorator.KW_LAT), coord[i].get(_Decorator.KW_LON)]     \
                          for i in range(len(coord))]      
            if coord in ([],None):
                raise happyError('wrong geographic coordinates')
            if order != 'lL':                   coord = [_[::-1] for _ in coord] # order = 'Ll'
            if settings.REDUCE_ANSWER and len(coord)==1:    coord = coord[0]
            return self.func(coord, **kwargs)

    #/************************************************************************/
    class parse_place(__parse):
        """Generic class decorator of functions and methods used to parse place
        (topo,geo) names.
        
        ::
        
            >>> new_func = _Decorator.parse_place(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.

        Returns
        -------
        new_func : callable
            the decorated function that now accepts a place as a positional 
            argument.
        
        Examples
        --------
        Very basic parsing examples:
        
        ::
            
            >>> func = lambda place, *args, **kwargs: place
            >>> new_func = _Decorator.parse_place(func)
            >>> new_func(place='Bruxelles, Belgium')
                ['Bruxelles, Belgium']
            >>> new_func(city=['Athens','Heraklion'],country='Hellas')
                ['Athens, Hellas', 'Heraklion, Hellas']
            >>> new_func(**{'address':['72 avenue Parmentier','101 Avenue de la République'], 
                            'city':'Paris', 
                            'country':'France'})
                ['72 avenue Parmentier, Paris, France', 
                '101 Avenue de la République, Paris, France']
            >>> new_func(place=['Eurostat', 'DIGIT', 'EIB'], 
                         city='Luxembourg')
                ['Eurostat, Luxembourg', 'DIGIT, Luxembourg', 'EIB, Luxembourg']
            
        Note that the new decorated method also supports the parsing of the place
        (topo)name as a positional argument (usage not recommended):
        
        ::

            >>> new_func('Athens, Hellas')
                ['Athens, Hellas']

        Therefore, things like that should be avoided:
        
        ::

            >>> new_func('Athens, Hellas', place='Berlin, Germany')
                happyError: !!! dont mess up with me - duplicated place argument parsed !!!
            
        Note
        ----
        The output decorated method :data:`new_func` can parse the following keys: 
        :literal:`['place', 'address', 'city', 'zip', 'country']` from any input 
        keyword argument. See the examples above.
           
        See also
        --------
        :meth:`~_Decorator.parse_coordinate`, :meth:`~_Decorator.parse_place_or_coordinate`,
        :meth:`~_Decorator.parse_area`.
        """ 
        def __call__(self, *args, **kwargs):
            place, address, city, country, zipcode = '', '', '', '', ''
            if args not in (None,()):      
                if all([isinstance(a,_Feature) for a in args]):
                    try:
                        place = [a.place for a in args]
                    except:
                        raise happyError('parsed place feature not recognised')
                elif all([happyType.isstring(a) for a in args]):
                    place = list(args)
                elif len(args) == 1 and happyType.issequence(args[0]):
                    place = args[0]
                else:   
                    raise happyError('input arguments not recognised')
            if place in ('',None):
                place = kwargs.pop(_Decorator.KW_PLACE, None)
                address = kwargs.pop(_Decorator.KW_ADDRESS, None)
                city = kwargs.pop(_Decorator.KW_CITY, None)
                country = kwargs.pop(_Decorator.KW_COUNTRY, None)
                zipcode = kwargs.pop(_Decorator.KW_ZIPCODE, None)                
            elif not (kwargs.get(_Decorator.KW_PLACE) is None and   \
                      kwargs.get(_Decorator.KW_ADDRESS) is None and \
                      kwargs.get(_Decorator.KW_CITY) is None and    \
                      kwargs.get(_Decorator.KW_COUNTRY) is None and \
                      kwargs.get(_Decorator.KW_ZIPCODE) is None):
                raise happyError('don''t mess up with me - duplicated place argument parsed')
            try:
                assert not(place in ('',None) and country in ('',None) and city in ('',None)) 
            except AssertionError:
                raise happyError('no input place arguments passed')
            try:
                assert place in ('',None) or address in ('',None)
            except AssertionError:
                raise happyError('too many place arguments')
            if address not in ('',None):        place = address
            if place in ('',None):              place = []
            if happyType.isstring(place): place = [place,]
            if city not in ('',None):   
                if happyType.isstring(city): 
                    city = [city,]
                if place == []:                 place = city
                else:
                    if len(city) > 1:
                        raise happyError('inconsistent place with multiple cities')
                    place = [', '.join(_) for _ in zip(place, itertools.cycle(city))]
            if zipcode not in ('',None):   
                if happyType.isstring(zipcode):   
                    zipcode = [zipcode,]
                if place == []:                 place = zipcode
                else:
                    if len(zipcode) > 1:
                        raise happyError('inconsistent place with multiple zipcodes')
                    place = [', '.join(_) for _ in zip(place, itertools.cycle(zipcode))]
            if country not in ('',None):   
                if happyType.isstring(country): 
                    country = [country,]
                if place == []:                 place = country
                else:
                    if len(country) > 1:
                        raise happyError('inconsistent place with multiple countries')
                    place = [', '.join(_) for _ in zip(place, itertools.cycle(country))]
            if place in (None,[],''):
                raise happyError('no input arguments passed')
            if settings.REDUCE_ANSWER and len(place)==1:    place = place[0]
            if not all([happyType.isstring(p) for p in place]):
                raise happyError('wrong format for input place')
            return self.func(place, **kwargs)
       
    #/************************************************************************/
    class parse_place_or_coordinate(__parse):
        """Generic class decorator of functions and methods used to parse place 
        :literal:`(lat,Lon)` coordinates or place names.
        
        ::
        
            >>> new_func = _Decorator.parse_place_or_coordinate(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts  :data:`coord` or :data:`lat` 
            and :data:`Lon` as new keyword argument(s) to parse geographic 
            coordinates, plus some additional keyword argument (see *Notes* of
            :meth:`~_Decorator.parse_coordinate` method).
        
        Examples
        --------
        Some dummy examples:
        
        ::
            
            >>> func = lambda *args, **kwargs: [kwargs.get('coord'), kwargs.get('place')]
            >>> new_func = _Decorator.parse_place_or_coordinate(func)
            >>> new_func(lat=[1,2], Lon=[-1,-2])
                [[[1, -1], [2, -2]], None]
            >>> new_func(place='Bruxelles, Belgium')
                [None, ['Bruxelles, Belgium']]
        
        Note
        ----
        The output decorated method :data:`new_func` can parse all of the keys
        already supported by :meth:`~_Decorator.parse_place` and 
        :meth:`~_Decorator.parse_coordinate` from any input keyword argument,
        *i.e.,* :literal:`['lat', 'Lon', 'x', 'y', 'coord', 'place', 'address', 'city', 'zip', 'country']`. 
        See the examples above.
            
        See also
        --------
        :meth:`~_Decorator.parse_place`, :meth:`~_Decorator.parse_coordinate`,
        :meth:`~_Decorator.parse_area`.
        """
        def __call__(self, *args, **kwargs):
            try:
                place = _Decorator.parse_place(lambda p, **kw: p)(*args, **kwargs)
            except:
                place = None
            else:
                kwargs.update({_Decorator.KW_PLACE: place})
            try:
                coord = _Decorator.parse_coordinate(lambda c, **kw: c)(*args, **kwargs)
            except:
                coord = None
            else:
                kwargs.update({_Decorator.KW_COORD: coord})
            try:
                assert not(place in ('',None) and coord in ([],None))
            except:
                raise happyError('no geographic entity parsed to define the place')
            if settings.EXCLUSIVE_ARGUMENTS is True:
                try:
                    assert place in ('',None) or coord in ([],None)
                except:
                    raise happyError('too many geographic entities parsed to define the place')
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_area(__parse):
        """Generic class decorator of functions and methods used to parse either
        :literal:`(lat,Lon)` coordinate(s) or (topo)name(s) from JSON-like dictionary 
        parameters (geometry features) formated according to |GISCO| geometry 
        responses (see |GISCOWIKI|).
        
        ::
        
            >>> new_func = _Decorator.parse_area(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts :data:`area` as a keyword 
            argument to parse geographic coordinates, plus some additional keyword 
            arguments (see *Notes* below).
        
        Examples
        --------
        Some dummy examples:
        
        ::
            
            >>> func = lambda *args, **kwargs: kwargs.get('coord')
            >>> area = {'A': 1, 'B': 2}
            >>> _Decorator.parse_area(func)(area=area)
                happyError: !!! geometry attributes not recognised !!!
            >>> area = {'geometry': {'coordinates': [1, 2], 'type': 'Point'},
                        'properties': {'city': 'somewhere', 
                                       'country': 'some country',
                                       'street': 'sesame street',
                                       'osm_key': 'place'},
                        'type': 'Feature'}
            >>> _Decorator.parse_area(func)(area=area)
                [[2, 1]]
            >>> func = lambda *args, **kwargs: kwargs.get('place')
            >>> _Decorator.parse_area(func)(area=area, filter='place')
                ['sesame street, somewhere, some country']
        
        Also note that the argument can be parsed as a positional argument (usage
        not recommended):
        
        ::
            
            >>> _Decorator.parse_area(func)(area)
                []
            >>> _Decorator.parse_area(func)(area, order='Ll')
                [[1, 2]]

        and an actual one:
        
        ::
            
            >>> serv = services.GISCOService()
            >>> area = serv.place2area(place='Berlin,Germany')
            >>> print(area)
                [{'geometry': {'coordinates': [13.3888599, 52.5170365], 'type': 'Point'},
                  'properties': {'city': 'Berlin', 'country': 'Germany',
                   'name': 'Berlin',
                   'osm_id': 240109189, 'osm_key': 'place', 'osm_type': 'N', 'osm_value': 'city',
                   'postcode': '10117', 'state': 'Berlin'},
                  'type': 'Feature'},
                 {'geometry': {'coordinates': [13.4385964, 52.5198535], 'type': 'Point'},
                  'properties': {'country': 'Germany',
                   'extent': [13.08835, 52.67551, 13.76116, 52.33826],
                   'name': 'Berlin',
                   'osm_id': 62422, 'osm_key': 'place', 'osm_type': 'R', 'osm_value': 'state'},
                  'type': 'Feature'},
                 {'geometry': {'coordinates': [13.393560634296435, 52.51875095], 'type': 'Point'},
                  'properties': {'city': 'Berlin', 'country': 'Germany',
                   'extent': [13.3906703, 52.5200704, 13.3948782, 52.5174944],
                   'name': 'Humboldt University in Berlin Mitte Campus',
                   'osm_id': 120456814, 'osm_key': 'amenity', 'osm_type': 'W', 'osm_value': 'university',
                   'postcode': '10117', 'state': 'Berlin', 'street': 'Dorotheenstraße'},
                  'type': 'Feature'},
                 ...
                  {'geometry': {'coordinates': [13.3869856, 52.5156648], 'type': 'Point'},
                  'properties': {'city': 'Berlin', 'country': 'Germany',
                   'housenumber': '55-57',
                   'name': 'Komische Oper Berlin',
                   'osm_id': 318525456, 'osm_key': 'amenity', 'osm_type': 'N', 'osm_value': 'theatre',
                   'postcode': '10117', 'state': 'Berlin', 'street': 'Behrenstraße'},
                  'type': 'Feature'}]
                    
        We can for instance use the :meth:`parse_area` to parse (filter) the 
        data :data:`area` and retrieve the coordinates:
        
        ::
            
            >>> func = lambda **kwargs: kwargs.get('coord')
            >>> new_func = _Decorator.parse_area(func)
            >>> hasattr(new_func, '__call__')
                True
            >>> new_func(area=area, filter='coord')
                [[52.5170365, 13.3888599], [52.5198535, 13.4385964]]
            >>> new_func(area=area, filter='coord', unique=True, order='Ll')
                [[13.3888599, 52.5170365]]
            
        One can also simlarly retrieve the name of the places:
        
        ::

            >>> func = lambda **kwargs: kwargs.get('place')
            >>> new_func = _Decorator.parse_area(func)
            >>> hasattr(new_func, '__call__')
                True
            >>> new_func(area=area, filter='place')
                ['Berlin, 10117, Germany', 'Germany', 'Dorotheenstraße, Berlin, 10117, Germany',
                'Unter den Linden, Berlin, 10117, Germany', 'Olympischer Platz, Berlin, 14053, Germany', 
                'Sauerbruchweg, Berlin, 10117, Germany', 'Eingangsebene, Berlin, 10557, Germany', 
                'Niederkirchnerstraße, Berlin, 10117, Germany', 'Friedrichstraße, Berlin, 10117, Germany', 
                'Bismarckstraße, Berlin, 10627, Germany', 'Berlin Ostbahnhof, Berlin, 10243, Germany', 
                'Pflugstraße, Berlin, 10115, Germany', 'Unter den Linden, Berlin, 10117, Germany', 
                'Hanne-Sobek-Platz, Berlin, 13357, Germany', 'Behrenstraße, Berlin, 10117, Germany']
            
        Notes
        -----
        * The decorated method/function :data:`new_func` accepts the same :data:`*args` 
          positional arguments as :data:`func` and, in addition to the arguments 
          in `data:`**kwargs` already supported by the input method/function :data:`func`, 
          some extra keyword arguments:              
              + :data:`area` to parse geocoordinates;
              + :data:`filter` - a flag used to define the output of the decorated
                function; it is either :literal:`place` or :literal:`coord`;
              + :data:`unique` - when set to :data:`True`, a single geometry is 
                filtered out, the first available one; default to :data:`False`, 
                hence all geometries are parsed;
              + :data:`order` - a flag used to define the order of the output filtered 
                geographic coordinates; it can be either :literal:`'lL'` for 
                :literal:`(lat,Lon)` order or :literal:`'Ll'` for a :literal:`(Lon,lat)` 
                order; default is :literal:`'lL'`.                    
        * When passed to the decorated method :data:`new_func` with input arguments 
          :data:`*args, **kwargs`, the remaining parameters in :data:`kwargs` are 
          actually filtered out to extract geometry features, say :data:`g`, that 
          are formatted like the JSON :literal:`geometries` output by |GISCO| 
          geocoding web-service (see method :meth:`services.GISCOService.place2area`) 
          and which verify the following match:
          ::             
              g['type']='Feature' and g['geometry']['type']='Point' and g['properties']['osm_key']='place'    
              
        * When extracting the coordinates from a geometry feature, say :data:`g`, 
          output by |GISCO| web-service, the original order in the composite key 
          :data:`g['geometry']['coordinates']` is :literal:`(Lon,lat)`. Note that
          for |OSM| output, the keyword :data:`lat` and :data:`Lon` are directly
          defined.
            
        See also
        --------
        :meth:`~_Decorator.parse_place`, :meth:`~_Decorator.parse_coordinate`,
        :meth:`~_Decorator.parse_place_or_coordinate`, :meth:`~_Decorator.parse_nuts`, 
        :meth:`services.GISCOService.place2area`.
        """
        KW_LAT          = 'lat' # not to be confused with _Decorator.KW_LAT
        KW_LON          = 'lon' # ibid 
        KW_FEATURES     = 'features'
        KW_GEOMETRY     = 'geometry'
        KW_PROPERTIES   = 'properties'
        KW_TYPE         = 'type'
        KW_OSM_KEY      = 'osm_key'
        KW_COORDINATES  = 'coordinates'
        KW_CITY         = 'city' # not to be confused with _Decorator.KW_CITY
        KW_COUNTRY      = 'country' # ibid
        KW_POSTCODE     = 'postcode'
        KW_STATE        = 'state'
        KW_STREET       = 'street'
        KW_EXTENT       = 'extent'
        KW_DISPLAYNAME  = 'display_name'
        def __call__(self, *args, **kwargs):
            filt = kwargs.pop('filter','coord')
            if filt not in ('',None) and not (happyType.isstring(filt) and filt in ('place','coord')):
                raise happyError('wrong "filer" parameter')
            unique = kwargs.pop('unique',False)
            if not isinstance(unique, bool):
                raise happyError('wrong "unique" parameter')
            order = kwargs.pop('order', 'lL')
            if not happyType.isstring(order) or not order in ('Ll','lL'):
                raise happyError('wrong "order" parameter')
            geom = None
            if args not in (None,()): 
                __key_area = False
                if all([isinstance(a,_Feature) for a in args]):
                    try:
                        geom = [a.geometry for a in args]
                    except:
                        raise happyError('parsed geometry feature not recognised')
                elif all([happyType.ismapping(a) for a in args]):
                    geom = args
                elif len(args) == 1 and happyType.issequence(args[0]):
                    if all([happyType.ismapping(args[0][i]) for i in range(len(args[0]))]):
                        geom = args[0]
            if geom is None:
                __key_area = True
                geom = kwargs.pop(_Decorator.KW_AREA, None)                 
            elif not kwargs.get(_Decorator.KW_AREA) is None:
                raise happyError('don''t mess up with me - duplicated geometry argument parsed')
            if geom is None:
                return self.func(*args, **kwargs)
            if happyType.ismapping(geom): 
                geom = [geom,]
            elif not happyType.issequence(geom):
                raise happyError('wrong geometry definition')              
            if not all([happyType.ismapping(g) for g in geom]): 
                raise happyError('wrong formatting/typing of geometry')  
            if filt in ('',None):
                kwargs.update({_Decorator.KW_AREA: geom}) 
            elif filt == 'coord':                            
                try: # geometry is formatted like an OSM output
                    coord = [[float(g[_Decorator.parse_area.KW_LAT]),
                              float(g[_Decorator.parse_area.KW_LON])] for g in geom]
                    assert coord not in ([],None,[None])
                except: # geometry is formatted like a GISCO output
                    coord = [g for g in geom                                                        \
                       if _Decorator.parse_area.KW_GEOMETRY in g                            \
                           and _Decorator.parse_area.KW_PROPERTIES in g                     \
                           and _Decorator.parse_area.KW_TYPE in g                           \
                           and g[_Decorator.parse_area.KW_TYPE]=='Feature'                  \
                           and (not(settings.CHECK_TYPE) or g[_Decorator.parse_area.KW_GEOMETRY][_Decorator.parse_area.KW_TYPE]=='Point')          \
                           and (not(settings.CHECK_OSM_KEY) or g[_Decorator.parse_area.KW_PROPERTIES][_Decorator.parse_area.KW_OSM_KEY]=='place')  \
                       ]
                    #coord = dict(zip(['lon','lat'],                                                 \
                    #                  zip(*[c[self.KW_GEOMETRY][self.KW_COORDINATES] for c in coord])))
                    coord = [_[_Decorator.parse_area.KW_GEOMETRY][_Decorator.parse_area.KW_COORDINATES][::-1]   \
                             for _ in coord]
                if __key_area and coord in ([],None):
                    raise happyError ('geometry attributes not recognised')
                if order != 'lL':   coord = [_[::-1] for _ in coord]
                if unique:          coord = [coord[0],]
                #elif len(coord)==1:          coord = coord[0]
                kwargs.update({_Decorator.KW_COORD: coord}) 
            elif filt == 'place':
                try: # geometry is formatted like an OSM output
                    place = [g[_Decorator.parse_area.KW_DISPLAYNAME] for g in geom]
                    assert place not in ([],[''],None,[None])
                except: # geometry is formatted like an OSM output 
                    place = [g.get(_Decorator.parse_area.KW_PROPERTIES) for g in geom \
                             if _Decorator.parse_area.KW_PROPERTIES in g]
                    place = [', '.join(filter(None, [p.get(_Decorator.parse_area.KW_STREET) or '',
                                        p.get(_Decorator.parse_area.KW_CITY) or '',
                                        '(' + p.get(_Decorator.parse_area.KW_STATE) + ')'               \
                                            if p.get(_Decorator.parse_area.KW_STATE) not in (None,'')   \
                                            and p.get(_Decorator.parse_area.KW_STATE)!=p.get(_Decorator.parse_area.KW_CITY) else '',
                                        p.get(_Decorator.parse_area.KW_POSTCODE) or '',
                                        p.get(_Decorator.parse_area.KW_COUNTRY) or ''])) for p in place] 
                if unique:          place = [place[0],]
                if settings.REDUCE_ANSWER and len(place)==1:    place=place[0]
                kwargs.update({_Decorator.KW_PLACE: place}) 
            return self.func(**kwargs)
        
    #/************************************************************************/
    class parse_nuts(__parse):
        """Generic class decorator of functions and methods used to parse NUTS
        information from JSON-like dictionary parameters formated according to 
        |GISCO| |NUTS| responses (see |GISCOWIKI|).
        
        ::
        
            >>> new_func = _Decorator.parse_nuts(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts a NUTS entry as a positional
            argument (see  *Notes* below).             
        
        Examples
        --------
        Some dummy examples:
        
        ::
            
            >>> func = lambda *args, **kwargs: kwargs.get('nuts')
            >>> nuts = {'A': 1, 'B': 2}
            >>> _Decorator.parse_nuts(func)(nuts)
                []
            >>> _Decorator.parse_nuts(func)(nuts=nuts)
                happyError: !!! NUTS attributes not recognised !!!
            >>> nuts = {'attributes': {'CNTR_CODE': 'EU', 'LEVL_CODE': '0'},
                        'NUTS_NAME': 'EU',
                        'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                        'value': 'EU'}
            >>> [nuts] == _Decorator.parse_nuts(func)(**nuts)
                True
            >>> [nuts] == _Decorator.parse_nuts(func)(nuts=nuts)
                True
        
        and an even dummier one:
        
        ::
            
            >>> serv = services.GISCOService()
            >>> nuts = serv.place2nuts(place='Lisbon,Portugal')
            >>> print(nuts)
                [{'attributes': {'CNTR_CODE': 'PT', 'LEVL_CODE': '0',
                   'NAME_LATN': 'PORTUGAL', 'NUTS_ID': 'PT',
                   'NUTS_NAME': 'PORTUGAL', 'OBJECTID': '28',
                   'SHRT_ENGL': 'Portugal'},
                  'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'PT'},
                 {'attributes': {'CNTR_CODE': 'PT', 'LEVL_CODE': '1',
                   'NAME_LATN': 'CONTINENTE', 'NUTS_ID': 'PT1',
                   'NUTS_NAME': 'CONTINENTE', 'OBJECTID': '113',
                   'SHRT_ENGL': 'Portugal'},
                  'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'PT1'},
                 {'attributes': {'CNTR_CODE': 'PT', 'LEVL_CODE': '2',
                   'NAME_LATN': 'Área Metropolitana de Lisboa', 'NUTS_ID': 'PT17',
                   'NUTS_NAME': 'Área Metropolitana de Lisboa', 'OBJECTID': '376',
                   'SHRT_ENGL': 'Portugal'},
                  'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'PT17'},
                 {'attributes': {'CNTR_CODE': 'PT', 'LEVL_CODE': '3',
                   'NAME_LATN': 'Área Metropolitana de Lisboa', 'NUTS_ID': 'PT170',
                   'NUTS_NAME': 'Área Metropolitana de Lisboa', 'OBJECTID': '1233',
                   'SHRT_ENGL': 'Portugal'},
                  'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'PT170'}]
            >>> res = settings._Decorator.parse_nuts(func)(nuts)
            >>> all([res[i] == nuts[i] for i in range(len(res))])
                True
            >>> settings._Decorator.parse_nuts(func)(nuts, level=2)
                 {'attributes': {'CNTR_CODE': 'PT', 'LEVL_CODE': '2',
                   'NAME_LATN': 'Área Metropolitana de Lisboa', 'NUTS_ID': 'PT17',
                   'NUTS_NAME': 'Área Metropolitana de Lisboa', 'OBJECTID': '376',
                   'SHRT_ENGL': 'Portugal'},
                  'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'PT17'},

        Notes
        -----
        * When passed to the decorated method :data:`new_func` with input arguments 
          :data:`*args, **kwargs`, the parameters :data:`kwargs` are actually filtered 
          out to extract NUTS features, say :data:`g`, that are formatted like 
          the JSON NUTS output by |GISCO| |NUTS| web-service (see method 
          :meth:`services.GISCOService.place2nuts`).
        * Alternatively, the output decorated method :data:`new_func` can parse 
          the following keys: :literal:`['nuts', 'attributes', 'displayFieldName', 'layerId', 'layerName', 'value']` 
          from any input keyword argument. See the examples above.
            
        See also
        --------
        :meth:`~_Decorator.parse_area`, :meth:`services.GISCOService.place2area`, 
        :meth:`~geoDecorators.parse_coordinate`, :meth:`services.GISCOService.coord2nuts`, 
        :meth:`services.GISCOService.place2nuts`.            
        """
        KW_RESULTS      = 'results'
        KW_ATTRIBUTES   = 'attributes'
        KW_FIELDNAME    = 'displayFieldName' 
        KW_LAYERID      = 'layerId'
        KW_LAYERNAME    = 'layerName'
        KW_VALUE        = 'value'
        KW_LEVEL        = 'LEVL_CODE'
        KW_NUTS_ID      = 'NUTS_ID' 
        KW_CNTR_CODE    = 'CNTR_CODE'
        KW_NUTS_NAME    = 'NUTS_NAME' # or 'NAME_LATN' ?
        KW_OBJECTID     = 'OBJECTID'
        def __call__(self, *args, **kwargs):
            level = kwargs.pop('level',None)
            nuts, items = None, {}
            if args not in (None,()):      
                __key_nuts = False
                if all([happyType.ismapping(a) for a in args]):
                    nuts = list(args)
                elif len(args) == 1 and happyType.issequence(args[0]):
                    if all([happyType.ismapping(args[0][i]) for i in range(len(args[0]))]):
                        nuts = args[0]
            if nuts is None:
                __key_nuts = True
                nuts = kwargs.pop(_Decorator.KW_NUTS, {})   
                items = {_Decorator.parse_nuts.KW_ATTRIBUTES:   kwargs.pop(_Decorator.parse_nuts.KW_ATTRIBUTES, None),
                         _Decorator.parse_nuts.KW_FIELDNAME:    kwargs.pop(_Decorator.parse_nuts.KW_FIELDNAME, None),
                         _Decorator.parse_nuts.KW_LAYERID:      kwargs.pop(_Decorator.parse_nuts.KW_LAYERID, None),
                         _Decorator.parse_nuts.KW_LAYERNAME:    kwargs.pop(_Decorator.parse_nuts.KW_LAYERNAME, None),
                         _Decorator.parse_nuts.KW_VALUE:        kwargs.pop(_Decorator.parse_nuts.KW_VALUE, None),
                         _Decorator.parse_nuts.KW_NUTS_NAME:    kwargs.pop(_Decorator.parse_nuts.KW_NUTS_NAME, None),
                         _Decorator.parse_nuts.KW_LEVEL:        kwargs.pop(_Decorator.parse_nuts.KW_LEVEL, None),
                         _Decorator.parse_nuts.KW_NUTS_ID:      kwargs.pop(_Decorator.parse_nuts.KW_NUTS_ID, None),
                         _Decorator.parse_nuts.KW_CNTR_CODE:    kwargs.pop(_Decorator.parse_nuts.KW_CNTR_CODE, None),
                         _Decorator.parse_nuts.KW_OBJECTID:     kwargs.pop(_Decorator.parse_nuts.KW_OBJECTID, None)}
                # note: the following instruction raises a "unhashable type: 'dict'"
                # TypeError
                # items = {(k,v) for (k,v) in list(items.items()) if v is not None}
                # using frozenset instead of list above does not solve the issue
                items = dict([(k,v) for (k,v) in list(items.items()) if v is not None])
            elif not kwargs.get(_Decorator.KW_NUTS) is None:
                raise happyError('don''t mess up with me - duplicated argument parsed')
            try:
                assert not(nuts in ({},None) and all([v in ([],None) for v in items.values()]))
            except AssertionError:
                # raise happyError('no input NUTS parsed')
                return self.func(*args, **kwargs)
            try:
                assert nuts in ({},None) or all([v in ([],None) for v in items.values()])
            except AssertionError:
                raise happyError('too many input file arguments')
            else:
                nuts = items if nuts in ({},None) else nuts
            if nuts in ((),[],None) or                                              \
                (happyType.ismapping(nuts) and all([n in ([],None) for n in nuts.values()])):
                # raise happyError('no NUTS parsed')
                return self.func(*args, **kwargs)
            if happyType.ismapping(nuts):     
                nuts = [nuts,]
            elif not happyType.issequence(nuts):
                raise happyError('wrong NUTS definition')              
            if all([happyType.ismapping(n) for n in nuts]): 
                nuts = [n for n in nuts if _Decorator.parse_nuts.KW_ATTRIBUTES in n]
            if __key_nuts and nuts in ([],None): 
                raise happyError('NUTS attributes not recognised')              
            if level is not None:
                nuts = [n for n in nuts if n[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_LEVEL] == str(level)]
            if settings.REDUCE_ANSWER and len(nuts)==1:    nuts=nuts[0]
            kwargs.update({_Decorator.KW_NUTS: nuts}) 
            return self.func(**kwargs)
 
    #/************************************************************************/
    class parse_projection(__parse):
        """Generic class decorator of functions and methods used to parse a projection
        reference system.
        
        ::
        
            >>> new_func = _Decorator.parse_projection(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts  :data:`proj` as a keyword 
            argument to parse the geographic projection system.
        
        Examples
        --------          
        
        ::
            
            >>> func = lambda *args, **kwargs: kwargs.get('proj')
            >>> _Decorator.parse_projection(func)(proj='dumb')
                happyError: !!! projection dumb not supported !!!
            >>> _Decorator.parse_projection(func)(proj='WGS84')
                4326
            >>> _Decorator.parse_projection(func)(proj='EPSG3857')
                3857
            >>> _Decorator.parse_projection(func)(proj=3857)
                3857
            >>> _Decorator.parse_projection(func)(proj='LAEA')
                3035
                
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`.
        """
        PROJECTION      = {'WGS84': 4326, 4326: 4326,
                           4258: 4258,
                           'EPSG3857': 3857, 3857: 3857, 
                           'LAEA': 3035, 3035: 3035}
        def __call__(self, *args, **kwargs):
            proj = kwargs.pop(_Decorator.KW_PROJECTION, 'WGS84')
            if proj in ('',None):
                return self.func(*args, **kwargs)
            if proj not in list(_Decorator.parse_projection.PROJECTION.keys() \
                | _Decorator.parse_projection.PROJECTION.values()):
                raise happyError('projection %s not supported' % proj)
            kwargs.update({_Decorator.KW_PROJECTION: _Decorator.parse_projection.PROJECTION[proj]})                  
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_year(__parse):
        """Generic class decorator of functions and methods used to parse a 
        reference year for NUTS regulation.
        
        ::
        
            >>> new_func = _Decorator.parse_year(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts  :data:`year` as a keyword 
            argument to parse a reference year (*e.g.*, used in NUTS definition).
        
        Examples
        --------          
        
        ::

            >>> func = lambda *args, **kwargs: kwargs.get('year')
            >>> _Decorator.parse_year(func)(year=2000)
                happyError: !!! year 2000 not supported !!!
            >>> _Decorator.parse_year(func)(year=2013)
                2013

        Note
        ----
        Currently, only years :literal:`[2006, 2010, 2013]` are supported (since
        they are the one currently implemented in |GISCO| NUTS service). 2013 is the
        default. 
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`.
        """
        YEARS      = [2006, 2010, 2013 # 2016 ?
                      ]
        def __call__(self, *args, **kwargs):
            year = kwargs.pop(_Decorator.KW_YEAR, 2013)
            if year in ([],None):
                return self.func(*args, **kwargs)
            if year not in tuple(_Decorator.parse_year.YEARS):
                raise happyError('year %s not supported' % year)
            kwargs.update({_Decorator.KW_YEAR: year})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_file(__parse):
        """Generic class decorator of functions and methods used to parse a 
        filename.
        
        ::
        
            >>> new_func = _Decorator.parse_file(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_Decorator.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts :data:`dir`, :data:`base`, and 
            :data:`file` as a keyword argument to parse the complete full path of
            a file. 
        
        Examples
        --------          
        
        ::

            >>> func = lambda *args, **kwargs: kwargs.get('file')
            >>> _Decorator.parse_file(func)(file='test.txt')
                test.txt
            >>> _Decorator.parse_file(func)(dir='/home/sweet/home/',base='test.txt')
                '/home/sweet/home/test.txt'
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`.
        """
        KW_DIRNAME      = 'dir'
        KW_BASENAME     = 'base'
        KW_FILENAME     = 'file'
        def __call__(self, *args, **kwargs):
            dirname, basename, filename = None, None, None
            if args not in (None,()):      
                if len(args) == 1 and happyType.issequence(args[0]):
                    if len(args[0])==2 and all([happyType.isstring(args[0][i]) for i in (0,1)]):
                        dirname, basename = args[0]
                    elif all([isinstance(args[0][i],str) for i in range(len(args[0]))]):
                        filename = args[0]
                elif len(args) == 1 and happyType.isstring(args[0]) and len(args[0])==2:
                    dirname, basename = args[0]
                elif len(args) == 2                                         \
                    and all([happyType.isstring(args[i]) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    dirname, basename = args
                else:   
                    raise happyError('input file arguments not recognised')
            if not (dirname is None and basename is None) or            \
                    (kwargs.get(_Decorator.parse_file.KW_DIRNAME) is None and  \
                     kwargs.get(_Decorator.parse_file.KW_BASENAME) is None and \
                     kwargs.get(_Decorator.parse_file.KW_FILENAME) is None):
                raise happyError('don''t mess up with me - duplicated argument parsed')
            else:   
                dirname = kwargs.pop(_Decorator.parse_file.KW_DIRNAME, '')         
                basename = kwargs.pop(_Decorator.parse_file.KW_BASENAME, '')
                filename = kwargs.pop(_Decorator.parse_file.KW_FILENAME, '')
            try:
                assert not(filename in ('',None) and basename in ('',None))
            except AssertionError:
                raise happyError('no input file arguments passed')
            try:
                assert filename in ('',None) or basename in ('',None)
            except AssertionError:
                raise happyError('too many input file arguments')
            if filename in ('',None):
                try:
                    filename = os.path.join(os.path.realpath(dirname or ''), basename)
                except:
                    raise happyError('wrong input file argument passed')
            if not happyType.isstring(filename):
                filename = [filename,]
            kwargs.update({_Decorator.KW_FILE: filename})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_route(__parse):
        """Generic class decorator of functions and methods used to parse a route.
            
        Note
        ----
        ! Not yet implemented !
        """
        KW_CODE         = 'code'
        KW_ROUTES       = 'routes'
        KW_WAYPOITNS    = 'waypoints'
        def __call__(self, *args, **kwargs):
            pass
    
#%%
#==============================================================================
# CLASS _Memoized
#==============================================================================
    
class _Memoized(object):
    """Decorator caching a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        key = str(args) + str(kwargs)
        #key = args
        #if not isinstance(args, collections.Hashable):
        #    # uncacheable (a list, for instance): better to not cache than blow up.
        #    return self.func(*args, **kwargs)
        if not key in self.cache:
            self.cache[key] = self.func(*args, **kwargs)
        return self.cache[key]

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    
    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)