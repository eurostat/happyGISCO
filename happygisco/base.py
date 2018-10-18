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

The classes :class:`_Decorator` and :class:`_NestedDict` exposed in this module, 
as well as their respective subclasses  **can be ignored** in a first instance 
since they are not requested to run the services. They are provided here for the 
sake of an exhaustive documentation.

**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`io`, :mod:`asyncio`, :mod:`itertools`, :mod:`functools`, :mod:`collections`, :mod:`time`, :mod:`hashlib`, :mod:`zipfile`, :mod:`copy`, :mod:`json`

*optional*:     :mod:`datetime`, :mod:`requests`,  :mod:`requests_cache`,  :mod:`cachecontrol`, :mod:`aiohttp`, :mod:`aiofiles`, :mod:`chardet`, :mod:`zipstream` 

*call*:         :mod:`settings`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat May  5 00:09:56 2018

__all__         = ['_Service', '_Feature', '_Tool', '_Decorator', '_NestedDict']

#%%
#==============================================================================
# IMPORT STATEMENTS
#==============================================================================

# import modules from Python Standard Library
import os, sys, io
import itertools, functools, collections
import inspect
import asyncio

import time
import hashlib, urllib
import shutil
import copy, zipfile
#import abc

# local (absolute) imports
from happygisco import happyVerbose, happyWarning, happyError, happyType, happyDeprecated
from happygisco import REDUCE_ANSWER, EXCLUSIVE_ARGUMENTS
from happygisco import settings

# another standard import
try:                                
    import datetime
except ImportError:          
    happyWarning("missing DATETIME module in Python Standard Library", ImportWarning)
    class datetime:
        class timedelta: 
            def __init__(self,arg): return arg

# requirements

try:
    import aiohttp
except:
    ASYNCIO_AVAILABLE = False
    happyWarning("missing AIOHTTP package (visit https://github.com/aio-libs/aiohttp)", ImportWarning)
    class aiohttp():
        class ClientResponse():
            pass
else:
    SERVICE_AVAILABLE = True                
    ASYNCIO_AVAILABLE = True
    happyVerbose('AIOHTTP help: https://aiohttp.readthedocs.io/en/latest/')
    try:
        import aiofiles
    except:
        happyVerbose('AIOFILES help: https://pypi.org/project/aiofiles/')
    else:
        happyWarning("missing AIOFILES package (visit https://pypi.org/project/aiofiles/)", ImportWarning)
  
ASYNCIO_AVAILABLE = False

try:                
    assert ASYNCIO_AVAILABLE is False                             
    import requests # urllib2
except (AssertionError,ImportError) as e:
    if e == ImportError:
        SERVICE_AVAILABLE = False                
        happyWarning('missing REQUESTS package (https://pypi.python.org/pypi/requests/) - GISCO ONLINE service will not be accessed')
    class requests():
        class Response():
            pass
else:
    SERVICE_AVAILABLE = True                

try:   
    assert ASYNCIO_AVAILABLE is False                              
    import requests_cache 
except (AssertionError,ImportError) as e:
    REQUESTS_CACHE_INSTALLED = False
    if e == ImportError:
        happyWarning("missing REQUESTS_CACHE package (https://pypi.python.org/pypi/requests-cache)", ImportWarning)
else:
    REQUESTS_CACHE_INSTALLED = True
    happyVerbose('REQUESTS_CACHE help: http://requests-cache.readthedocs.io/en/latest/')
    
try:                                
    assert ASYNCIO_AVAILABLE is False                              
    import cachecontrol#analysis:ignore
except (AssertionError,ImportError) as e:
    CACHECONTROL_INSTALLED = False
    if e == ImportError:
        happyWarning("missing CACHECONTROL package (visit https://pypi.python.org/pypi/requests-cache)", ImportWarning)
    class CacheControl():
        pass
    class FileCache():
        pass
else:
    CACHECONTROL_INSTALLED = True
    happyVerbose('CACHECONTROL help: https://cachecontrol.readthedocs.io/en/latest/')
    from cachecontrol import CacheControl
    from cachecontrol.caches import FileCache
    try:
        import fasteners#analysis:ignore
        #import lockfile#deprecated
    except ImportError:  
        happyWarning("missing FASTENERS package (https://pypi.org/project/fasteners/)", ImportWarning)
    
try:                                
    JSON_INSTALLED = True
    import simplejson as json
except ImportError:
    happyWarning("missing SIMPLEJSON package (https://pypi.python.org/pypi/simplejson/)", ImportWarning)
    try:
        import json
    except ImportError:
        JSON_INSTALLED = False
        happyWarning("JSON module missing in Python Standard Library", ImportWarning)
        class json:
            def loads(arg):  return '%s' % arg

try:                                
    import chardet
except ImportError:  
    CHARDET_INSTALLED = False
    happyWarning("missing CHARDET package (visit https://pypi.org/project/chardet/)", ImportWarning)
else:
    CHARDET_INSTALLED = True
    happyVerbose('CHARDET help: https://chardet.readthedocs.io/en/latest')

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
    
    # session/service parameters
    KW_SESSION      = 'session'
    KW_CACHING      = '_caching_'
    KW_CACHE        = 'cache_store'
    KW_EXPIRE       = 'expire_after'
    KW_FORCE        = '_force_download_' 
    KW_BACKEND      = 'cache_backend'
    
    KW_REST_URL     = 'rest_url'
    KW_CACHE_URL    = 'cache_url'
    KW_MAP_URL      = 'map_url'
    KW_ARCGIS       = 'arcgis'
    
    KW_CODER        = 'coder'
    
    KW_PROJECTION   = 'proj'  # 'projection'
    KW_LAT          = 'lat'
    KW_LON          = 'Lon' 
    KW_COORD        = 'coord'
    
    KW_PLACE        = 'place'
    KW_ADDRESS      = 'address'
    KW_CITY         = 'city'
    KW_COUNTRY      = 'country'
    KW_ZIPCODE      = 'zip'
    
    KW_LOCATION     = 'location' 
    KW_NUTS         = 'nuts' 
    KW_AREA         = 'area'
    
    KW_CENTER       = 'center'
    KW_ZOOM         = 'zoom'
      
    # input vector data
    KW_DATA         = 'data'
    KW_CONTENT      = 'content'
    KW_RESPONSE     = 'resp'
    KW_INFO         = 'info'
    KW_LAYER        = 'layer'
    KW_FILE         = 'file'
    KW_URL          = 'url'
    KW_DOMAIN       = 'domain'
    KW_FEATURE      = 'feat' # 'feature' 
    
    KW_SOURCE       = 'source'
    KW_CODE         = 'code'
    KW_UNIT         = 'unit' 
        
    # dimensions
    KW_YEAR         = 'year'
    KW_IFORMAT      = 'ifmt'
    KW_OFORMAT      = 'ofmt'
    KW_SCALE        = 'scale'
    KW_GEOMETRY     = 'geom' # 'geometry' 
    KW_LEVEL        = 'level'
    KW_SIZE         = 'size'
    KW_VECTOR       = 'vector' 
    
    KW_NAME         = 'name'
    KW_ID           = 'id'
    KW_TILE         = 'tile'
    KW_ATTR         = 'attr' # 'attribution'
              
    KW_ORDER        = 'order'
    KW_KEYS         = 'keys'
    KW_VALUES       = 'values'
    KW_FORCE_LIST   = '_force_list_'
    
    KW_NO_WIDGET    = '_no_widget_'

    #/************************************************************************/
    class __base(object):
        """Base parsing class for geographic entities. All decorators in 
        :class:`_Decorator` will inherit from this class.
        """
        def __init__(self, func, obj=None, cls=None, method_type='function',
                     **kwargs):
            self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type
            setattr(self, '__doc__', object.__getattribute__(func, '__doc__'))
            # ...
            self._key = kwargs.pop('_key_',None)
            try:    
                assert self._key is None or isinstance(self._key,str)  
            except: 
                raise happyError('wrong type for KEY argument')         
            self._parse_cls = kwargs.pop('_parse_cls_',None)
            if self._parse_cls is not None and not happyType.issequence(self._parse_cls):
                self._parse_cls = [self._parse_cls,]
            try:
                assert self._parse_cls is None or (happyType.issequence(self._parse_cls)    \
                    and all([isinstance(c,type) for c in self._parse_cls]))
            except:
                raise happyError('wrong type for PARSE_CLS argument')   
            if '_values_' in kwargs:
                self._values = kwargs.pop('_values_')
                if self._values is not None and not happyType.ismapping(self._values):
                    self._values = {v:v for v in self._values}
                try:
                    assert self._values is None or happyType.ismapping(self._values)
                except:
                    raise happyError('wrong type for VALUES argument')         
            if '_key_default_' in kwargs:
                self._key_default = kwargs.pop('_key_default_')
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
                             'func', 'obj', 'cls', 'method_type',
                             '_parse_cls', '_key', '_values', '_key_default'): 
                return object.__getattribute__(self, attr_name)
            try:
                # func = object.__getattribute__(self, 'func')
                return getattr(self.func, attr_name)
            except:
                try:
                    return object.__getattribute__(self, attr_name)
                except:
                    pass
        #def __call__(self, *args, **kwargs):
        #    return self.func(*args, **kwargs)
        def __call__(self, *args, **kwargs):  
            if self._key is not None:     
                try:
                    assert hasattr(self,'_key_default')
                except:
                    value = kwargs.pop(self._key, None)
                else:
                    value = kwargs.pop(self._key, self._key_default)
                try:
                    assert value is None or self._parse_cls is None or \
                        any([isinstance(value,c) for c in self._parse_cls])
                except:
                    raise happyError('wrong format for %s argument' % self._key.upper())
                else:
                    if value is None:
                        return self.func(*args, **kwargs)
                if self._values is not None:
                    try:
                        # could check: list,tuple in self._parse_cls
                        _all_values = happyType.seqflatten(list(self._values.items()))
                        assert (happyType.issequence(value) and set(value).difference(set(_all_values))==set())   \
                            or value in _all_values
                    except:
                        raise happyError('wrong value for %s argument - %s not supported' % (self._key.upper(), value))
                    else:
                        if happyType.issequence(value):
                            value = [self._values[v] if v in self._values.keys() else v for v in value]
                        elif value in self._values.keys():
                            value = self._values[value]
                kwargs.update({self._key: value}) 
            return self.func(*args, **kwargs)
    def __repr__(self):
            return self.func.__repr__()

    #/************************************************************************/
    class parse_coordinate(__base):
        """Class decorator of functions and methods used to parse place :literal:`(lat,Lon)` 
        coordinates.
        
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
            
            >>> new_func([1,-1])
                [[1,-1]]
            >>> new_func([1,2],[-1,-2])
                [[1, -1], [2, -2]]
            >>> new_func(coord=[[1,-1],[2,-2]])
                [[1, -1], [2, -2]]

        Therefore, things like that should be avoided:

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
        :meth:`~_Decorator.parse_geometry`.
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
            if args not in ((None,),()):      
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
                # return self.func(*args, **kwargs)
                raise ValueError('no input coordinate arguments passed')
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
            elif happyType.issequence(coord) \
                    and not any([hasattr(coord[i],'__len__') for i in range(len(coord))]):
                coord = [coord]
            if coord in ([],None):
                raise happyError('wrong geographic coordinates')
            if order != 'lL':                   coord = [_[::-1] for _ in coord] # order = 'Ll'
            if REDUCE_ANSWER and len(coord)==1:    coord = coord[0]
            return self.func(coord, **kwargs)

    #/************************************************************************/
    class parse_place(__base):
        """Class decorator of functions and methods used to parse place (topo,geo) 
        names.
        
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

            >>> new_func('Athens, Hellas')
                ['Athens, Hellas']

        Therefore, things like that should be avoided:

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
        :meth:`~_Decorator.parse_geometry`.
        """ 
        def __call__(self, *args, **kwargs):
            place, address, city, country, zipcode = '', '', '', '', ''
            if args not in ((None,),()):      
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
                # return self.func(*args, **kwargs)
                raise ValueError('no input place arguments passed')
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
            if REDUCE_ANSWER and len(place)==1:    place = place[0]
            if not all([happyType.isstring(p) for p in place]):
                raise happyError('wrong format for input place')
            return self.func(place, **kwargs)
       
    #/************************************************************************/
    class parse_place_or_coordinate(__base):
        """Class decorator of functions and methods used to parse place :literal:`(lat,Lon)` 
        coordinates or place names.
        
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
        :meth:`~_Decorator.parse_geometry`.
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
                # return self.func(*args, **kwargs)
                raise ValueError('no geographic entity parsed to define the place')
            if EXCLUSIVE_ARGUMENTS is True:
                try:
                    assert place in ('',None) or coord in ([],None)
                except:
                    raise happyError('too many geographic entities parsed to define the place')
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_geometry(__base):
        """Class decorator of functions and methods used to parse either :literal:`(lat,Lon)` 
        coordinate(s) or (topo)name(s) from JSON-like dictionary parameters (geometry 
        features) formated according to |GISCO| geometry responses (see |GISCOWIKI|).
        
            >>> new_func = _Decorator.parse_geometry(func)
        
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
            the decorated function that now accepts :data:`geom` as a keyword 
            argument to parse geographic coordinates, plus some additional keyword 
            arguments (see *Notes* below).
        
        Examples
        --------
        Some dummy examples:
            
            >>> func = lambda *args, **kwargs: kwargs.get('geom')
            >>> geom = {'A': 1, 'B': 2}
            >>> _Decorator.parse_geometry(func)(geom=geom)
                happyError: !!! geometry attributes not recognised !!!
            >>> geom = {'geometry': {'coordinates': [1, 2], 'type': 'Point'},
                        'properties': {'city': 'somewhere', 
                                       'country': 'some country',
                                       'street': 'sesame street',
                                       'osm_key': 'place'},
                        'type': 'Feature'}
            >>> _Decorator.parse_geometry(func)(geom=geom)
                [[2, 1]]
            >>> func = lambda *args, **kwargs: kwargs.get('place')
            >>> _Decorator.parse_geometry(func)(geom=geom, filter='place')
                ['sesame street, somewhere, some country']
        
        Also note that the argument can be parsed as a positional argument (usage
        not recommended):
            
            >>> _Decorator.parse_geometry(func)(geom)
                []
            >>> _Decorator.parse_geometry(func)(geom, order='Ll')
                [[1, 2]]

        and an actual one:
            
            >>> serv = services.GISCOService()
            >>> geom = serv.place2geom(place='Berlin,Germany')
            >>> print(geom)
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
                    
        We can for instance use the :meth:`parse_geometry` to parse (filter) the 
        data :data:`geom` and retrieve the coordinates:
            
            >>> func = lambda **kwargs: kwargs.get('coord')
            >>> new_func = _Decorator.parse_geometry(func)
            >>> hasattr(new_func, '__call__')
                True
            >>> new_func(geom=geom, filter='coord')
                [[52.5170365, 13.3888599], [52.5198535, 13.4385964]]
            >>> new_func(geom=geom, filter='coord', unique=True, order='Ll')
                [[13.3888599, 52.5170365]]
            
        One can also similarly retrieve the name of the places:

            >>> func = lambda **kwargs: kwargs.get('place')
            >>> new_func = _Decorator.parse_geometry(func)
            >>> hasattr(new_func, '__call__')
                True
            >>> new_func(geom=geom, filter='place')
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
              + :data:`geom` to parse a geometry;
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
        KW_NAME         = 'name'
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
            if args not in ((None,),()): 
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
                geom = kwargs.pop(_Decorator.KW_GEOMETRY, None)                 
            elif not kwargs.get(_Decorator.KW_GEOMETRY) is None:
                raise happyError('don''t mess up with me - duplicated geometry argument parsed')
            if geom is None:
                # raise ValueError('not input geometry parsed')              
                return self.func(*args, **kwargs)
            if happyType.ismapping(geom): 
                geom = [geom,]
            elif not happyType.issequence(geom):
                raise happyError('wrong geometry definition')              
            if not all([happyType.ismapping(g) for g in geom]): 
                raise happyError('wrong formatting/typing of geometry')  
            if filt in ('',None):
                kwargs.update({_Decorator.KW_GEOMETRY: geom}) 
            elif filt == 'coord':                            
                try: # geometry is formatted like an OSM output
                    coord = [[float(g[_Decorator.parse_geometry.KW_LAT]),
                              float(g[_Decorator.parse_geometry.KW_LON])] for g in geom]
                    assert coord not in ([],None,[None])
                except: # geometry is formatted like a GEOJSON output
                    coord = [g for g in geom                                                    \
                       if _Decorator.parse_geometry.KW_GEOMETRY in g                            \
                           and _Decorator.parse_geometry.KW_PROPERTIES in g                     \
                           and _Decorator.parse_geometry.KW_TYPE in g                           \
                           and g[_Decorator.parse_geometry.KW_TYPE]=='Feature'                  \
                       ]
                    _coord = [c for c in coord                                              \
                              if (not(settings.CHECK_TYPE) or c[_Decorator.parse_geometry.KW_GEOMETRY][_Decorator.parse_geometry.KW_TYPE]=='Point')]
                    try:    assert _coord != []
                    except: pass
                    else:
                        coord = _coord
                        _coord = [c for c in coord                                              \
                                  if (not(settings.CHECK_OSM_KEY) or c[_Decorator.parse_geometry.KW_PROPERTIES][_Decorator.parse_geometry.KW_OSM_KEY]=='place')]
                        try:    assert _coord != []
                        except: pass
                        else:   coord = _coord                       
                    #coord = dict(zip(['lon','lat'],                                                 \
                    #                  zip(*[c[self.KW_GEOMETRY][self.KW_COORDINATES] for c in coord])))
                    coord = [_[_Decorator.parse_geometry.KW_GEOMETRY][_Decorator.parse_geometry.KW_COORDINATES][::-1]   \
                             for _ in coord]
                if __key_area and coord in ([],None):
                    raise happyError ('geometry attributes not recognised')
                if order != 'lL':   coord = [_[::-1] for _ in coord]
                if unique:          coord = [coord[0],]
                #elif len(coord)==1:          coord = coord[0]
                kwargs.update({_Decorator.KW_COORD: coord}) 
            elif filt == 'place':
                try: # geometry is formatted like an OSM output
                    place = [g[_Decorator.parse_geometry.KW_DISPLAYNAME] for g in geom]
                    assert place not in ([],[''],None,[None])
                except: # geometry is formatted like an OSM output 
                    place = [g.get(_Decorator.parse_geometry.KW_PROPERTIES) for g in geom \
                             if _Decorator.parse_geometry.KW_PROPERTIES in g]
                    place = [', '.join(filter(None, [p.get(_Decorator.parse_geometry.KW_STREET) or '',
                                        p.get(_Decorator.parse_geometry.KW_CITY) or '',
                                        '(' + p.get(_Decorator.parse_geometry.KW_STATE) + ')'               \
                                            if p.get(_Decorator.parse_geometry.KW_STATE) not in (None,'')   \
                                            and p.get(_Decorator.parse_geometry.KW_STATE)!=p.get(_Decorator.parse_geometry.KW_CITY) else '',
                                        p.get(_Decorator.parse_geometry.KW_POSTCODE) or '',
                                        p.get(_Decorator.parse_geometry.KW_COUNTRY) or ''])) \
                            or p.get(_Decorator.parse_geometry.KW_NAME) or '' for p in place] 
                if unique:          place = [place[0],]
                if REDUCE_ANSWER and len(place)==1:    place=place[0]
                kwargs.update({_Decorator.KW_PLACE: place}) 
            return self.func(**kwargs)
        
    #/************************************************************************/
    class parse_nuts(__base):
        """Class decorator of functions and methods used to parse information content
        from JSON-like dictionary parameters (*e.g.*, formated according to |GISCO| 
        |NUTS| responses: see |GISCOWIKI|).
        
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
            the decorated function that now accepts a JSON-like entry as a positional
            argument (see  *Notes* below).             
        
        Examples
        --------
        Some dummy examples:
            
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
            >>> res = _Decorator.parse_nuts(func)(nuts)
            >>> all([res[i] == nuts[i] for i in range(len(res))])
                True
            >>> _Decorator.parse_nuts(func)(nuts, level=2)
                 {'attributes': {'CNTR_CODE': 'PT', 'LEVL_CODE': '2',
                   'NAME_LATN': 'Área Metropolitana de Lisboa', 'NUTS_ID': 'PT17',
                   'NUTS_NAME': 'Área Metropolitana de Lisboa', 'OBJECTID': '376',
                   'SHRT_ENGL': 'Portugal'},
                  'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'PT17'},

        Notes
        -----
        * When parsed to the decorated method :data:`new_func` with input arguments 
          :data:`*args, **kwargs`, the parameters :data:`kwargs` are actually filtered 
          out to extract NUTS features, say :data:`g`, that are formatted like 
          the JSON NUTS output by |GISCO| |NUTS| web-service (see method 
          :meth:`services.GISCOService.place2nuts`).
        * Alternatively, the output decorated method :data:`new_func` can parse 
          the following keys: :literal:`['nuts', 'attributes', 'displayFieldName', 'layerId', 'layerName', 'value']` 
          from any input keyword argument. See the examples above.
            
        See also
        --------
        :meth:`~_Decorator.parse_geometry`, :meth:`services.GISCOService.place2area`, 
        :meth:`~geoDecorators.parse_coordinate`, :meth:`services.GISCOService.coord2nuts`, 
        :meth:`services.GISCOService.place2nuts`.            
        """
        # GDAL like dictionaries
        KW_PROPERTIES   = 'properties'
        KW_GEOMETRY     = 'geometry'
        KW_FEATURES     = 'features'
        KW_TYPE         = 'type' 
        KW_CRS          = 'crs' 
        KW_NAME         = 'name'
        KW_COORDINATES  = 'coordinates'
        # GISCO-like dictionaries
        KW_RESULTS      = 'results'
        KW_ATTRIBUTES   = 'attributes'
        KW_FIELDNAME    = 'displayFieldName' 
        KW_LAYERID      = 'layerId'
        KW_LAYERNAME    = 'layerName'
        KW_VALUE        = 'value'
        KW_LEVEL        = 'LEVL_CODE'
        KW_FID          = 'FID'
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
                items = { # GDAL like dictionaries
                        _Decorator.parse_nuts.KW_PROPERTIES:    kwargs.pop(_Decorator.parse_nuts.KW_PROPERTIES, None),
                         _Decorator.parse_nuts.KW_GEOMETRY:     kwargs.pop(_Decorator.parse_nuts.KW_GEOMETRY, None),
                         _Decorator.parse_nuts.KW_FEATURES:     kwargs.pop(_Decorator.parse_nuts.KW_FEATURES, None),
                         _Decorator.parse_nuts.KW_TYPE:         kwargs.pop(_Decorator.parse_nuts.KW_TYPE, None),
                         _Decorator.parse_nuts.KW_CRS:          kwargs.pop(_Decorator.parse_nuts.KW_CRS, None),
                         _Decorator.parse_nuts.KW_NAME:         kwargs.pop(_Decorator.parse_nuts.KW_NAME, None),
                         # GISCO-like dictionaries
                         _Decorator.parse_nuts.KW_ATTRIBUTES:   kwargs.pop(_Decorator.parse_nuts.KW_ATTRIBUTES, None),
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
                # raise ValueError('no input NUTS parsed')
                return self.func(*args, **kwargs)
            try:
                assert nuts in ({},None) or all([v in ([],None) for v in items.values()])
            except AssertionError:
                raise happyError('too many input NUTS arguments')
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
                try:
                    nuts = [n for n in nuts \
                            if _Decorator.parse_nuts.KW_ATTRIBUTES in n or _Decorator.parse_nuts.KW_PROPERTIES in n]
                except:
                    nuts = {}
            if __key_nuts and nuts in ([],None): 
                raise happyError('NUTS attributes not recognised')              
            if level is not None:
                if not happyType.issequence(level):
                    level = [level,]
                level = [str(l) for l in level]
                try:
                    nuts = [n for n in nuts                 \
                            if n[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_LEVEL] in level]
                except:
                    try :
                        nuts = [n for n in nuts             \
                                if n[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_LEVEL] in level]                    
                    except:
                        nuts = {}
            if REDUCE_ANSWER and len(nuts)==1:    nuts=nuts[0]
            kwargs.update({_Decorator.KW_NUTS: nuts}) 
            return self.func(**kwargs)
  
    #/************************************************************************/
    class parse_route(__base):
        """Class decorator of functions and methods used to parse a route.
            
        Note
        ----
        ! Not yet implemented !
        """
        KW_CODE         = 'code'
        KW_ROUTES       = 'routes'
        KW_WAYPOITNS    = 'waypoints'
        def __call__(self, *args, **kwargs):
            pass

    #/************************************************************************/
    class parse_file(__base):
        """Class decorator of functions and methods used to parse a filename.
        
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

            >>> func = lambda *args, **kwargs: kwargs.get('file')
            >>> _Decorator.parse_file(func)(file='test.txt')
                test.txt
            >>> _Decorator.parse_file(func)(dir='/home/sweet/home/',base='test.txt')
                '/home/sweet/home/test.txt'
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_url`.
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
                    elif all([happyType.isstring(args[0][i]) for i in range(len(args[0]))]):
                        filename = args[0]
                elif len(args) == 1 and happyType.isstring(args[0]):
                    filename = args[0]
                elif len(args) == 2                                         \
                    and all([happyType.isstring(args[i]) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    dirname, basename = args
                else:   
                    raise happyError('input file argument(s) not recognised')
            if dirname is None and basename is None and filename is None:   
                dirname = kwargs.pop(_Decorator.parse_file.KW_DIRNAME, '')         
                basename = kwargs.pop(_Decorator.parse_file.KW_BASENAME, '')
                filename = kwargs.pop(_Decorator.parse_file.KW_FILENAME, '')
            elif not (kwargs.get(_Decorator.parse_file.KW_DIRNAME) is None and       \
                      kwargs.get(_Decorator.parse_file.KW_BASENAME) is None and      \
                      kwargs.get(_Decorator.parse_file.KW_FILENAME) is None):
                raise happyError('don''t mess up with me - duplicated argument parsed')
            try:
                assert not(filename in ('',None) and basename in ('',None))
            except AssertionError:
                # raise ValueError('no input file arguments passed')
                return self.func(*args, **kwargs)
            try:
                assert filename in ('',None) or basename in ('',None)
            except AssertionError:
                raise happyError('too many input file arguments parsed')
            if filename in ('',None):
                try:
                    filename = os.path.join(os.path.realpath(dirname or ''), basename)
                except:
                    raise happyError('wrong input file argument(s) parsed')
            if not happyType.issequence(filename):
                filename = [filename,]
            kwargs.update({_Decorator.KW_FILE: filename})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_url(__base):
        """Class decorator of functions and methods used to parse a url.
        
            >>> new_func = _Decorator.parse_url(func)
        
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
            the decorated function that now accepts  :data:`url` as a keyword 
            argument to parse a simple URL; the URL must support any of the
            protocols :literal:`'http', 'https'`, or :literal:`'ftp'`, as listed 
            in :data:`settings.PROTOCOLS`.
        
        Examples
        --------          

            >>> func = lambda *args, **kwargs: kwargs.get('url')
            >>> _Decorator.parse_url(func)(url=0)
                happyError: !!! wrong format for URL argument !!!
            >>> _Decorator.parse_url(func)(url='dumb')
                happyError: !!! wrong value for URL argument - level 'dumb' not supported !!!
            >>> _Decorator.parse_url(func)(url='http://dumb.com')
                ['http://dumb.com']
            >>> _Decorator.parse_url(func)('http://dumb1.com', 'https://dumb2.com')
                ['http://dumb1.com', 'https://dumb2.com']
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_file`.
        """
        def __call__(self, *args, **kwargs):
            url = None
            if args not in (None,()):  
                if len(args) == 1:
                    if happyType.isstring(args[0]):
                        url = list(args)
                    elif happyType.issequence(args[0]) \
                            and all([happyType.isstring(args[0][i]) for i in range(len(args[0]))]):
                        url = args[0]
                elif all([happyType.isstring(args[i]) for i in range(len(args))]):
                    url = list(args)
                else:   
                    raise happyError('input URL argument(s) not recognised')
            if not(url is None or kwargs.get(_Decorator.KW_URL) is None):
                raise happyError('don''t mess up with me - duplicated argument parsed')
            elif url is None:
                url = kwargs.pop(_Decorator.KW_URL, '')
            try:
                assert url not in ('',None,[])
            except AssertionError:
                # raise ValueError('no input URL argument passed')
                return self.func(*args, **kwargs)
            if not happyType.issequence(url):
                url = [url,]
            try:
                assert all([any([u.startswith(s) for s in settings.PROTOCOLS]) \
                            for u in url])
            except:
                raise happyError('wrong value for %s argument - url %s not supported' % (_Decorator.KW_URL.upper(), url))
            kwargs.update({_Decorator.KW_URL: url})                  
            return self.func(*args, **kwargs)
 
    #/************************************************************************/
    @classmethod
    def _parse_class(cls, parse_cls, key, **_kwargs):
        """Generic method that enables defining a class decorator of functions 
        and methods that can parse any parameter of a given class.
        
            >>> decorator = _Decorator._parse_class(parse_cls, key, 
                                                    _values_=None, _key_default_=None)
        
        Arguments
        ---------
        parse_cls : class
            a custom class that is the type of the parsed argument.
        key : str
            keyword argument used to parse the argument.
        
        Keyword arguments
        -----------------
        _values_ : dict,list
            list of values accepted for the key; can be a list or a dictionary;
            in the latter case, the argument parsed will be mapped to its
            corresponding value in the dictionary; default is :literal:`None`.
        _key_default_ : 
            default value parsed for the :data:`key` parameter.
            
        Returns
        -------
        decorator : :class:`_Decorator.__base)`
            A parsing class that can be used to decorate any method or function
            that accepts :data:`key` as a keyword argument to parse an argument 
            of type :data:`myclass`.
            
        Examples
        --------
        Let say for instance we want to parse a :class:`str` argument that can 
        take values in :literal:`['a','b','c']` only with a :literal:`dummy_key`
        key:
            
            >>> key = 'dummy_key'
            >>> parse_cls = str
            >>> values = ['a', 'b', 'c']
            >>> func = lambda *args, **kwargs: kwargs.get(key)
            
        we then use:
                
            >>> decorator = _Decorator._parse_class(parse_cls, key, _values_=values)
            >>> decorator(func)(dummy_key=0)
                happyError: !!! AssertionError: wrong format for DUMMY_KEY argument !!!
            >>> decorator(func)(dummy_key='dumb')
                happyError: !!! wrong value for DUMMY_KEY argument - 'dumb' not supported !!!
            >>> decorator(func)(dummy_key='a')
                'a'
                
        what if we use a dictionary for :data:`values` instead:
                
            >>> values = {'a':1, 'b':2, 'c':3}
            >>> decorator = _Decorator._parse_class(parse_cls, key, _values_=values)
            >>> decorator(func)(dummy_key='b')
                2
        """
        class parse_class(_Decorator.__base):
            def __init__(self, *args, **kwargs):
                kwargs.update({'_parse_cls_': parse_cls, '_key_': key})
                if '_values_' in _kwargs:
                    kwargs.update({'_values_': _kwargs.get('_values_')})
                if '_key_default_' in _kwargs:
                    kwargs.update({'_key_default_': _kwargs.get('_key_default_')})
                super(parse_class,self).__init__(*args, **kwargs)
        return parse_class

    #/************************************************************************/
    class parse_year(__base):
        """Class decorator of functions and methods used to parse a reference 
        year for NUTS regulation.
        
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
            argument to parse a reference year (*e.g.*, used in NUTS definition);
            currently, only years :literal:`2006, 2010, 2013` and :literal:`2016` 
            are supported (though 2016 is not yet implemented in |GISCO| NUTS 
            service). 
        
        Examples
        --------          
        This can be used to parse years of implementation of NUTS regulation:
    
            >>> func = lambda *args, **kwargs: kwargs.get('year')
            >>> _Decorator.parse_year(func)(year=2000)
                happyError: !!! wrong value for YEAR argument - year 2000 not supported !!!
            >>> _Decorator.parse_year(func)(year=2010)
                2010
                
        Note that it forces to parse a non-empty :data:`year` parameter:
            
            >>> _Decorator.parse_year(func)()
                2013
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_scale`,
        :meth:`~geoDecorators.parse_iformat`, :meth:`~geoDecorators.parse_vector`,
        :meth:`~geoDecorators.parse_projection`, :meth:`~geoDecorators.parse_level`.
        """
        def __init__(self, *args, **kwargs):
            kwargs.update({'_parse_cls_':   [int, list], 
                           '_key_':         _Decorator.KW_YEAR, 
                           '_values_':      settings.GISCO_YEARS,
                           '_key_default_': settings.DEF_GISCO_YEAR})
            super(_Decorator.parse_year, self).__init__(*args, **kwargs)

    #/************************************************************************/
    class parse_projection(__base):
        """Class decorator of functions and methods used to parse a projection
        reference system.
        
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
            argument to parse the geographic projection system; the currently 
            supported projections are :literal:`'WGS84','ETRS89','LAEA'` and 
            :literal:`'EPSG3857'` or their equivalent EPSG codes (4326, 4258, 3857 
            and 3035 respectively), *e.g* the ones listed in 
            :data:`settings.GISCO_PROJECTIONS`.
        
        Examples
        --------          
        It can be used to check that the projection is actually one of those accepted 
        by |GISCO| services:
            
            >>> func = lambda *args, **kwargs: kwargs.get('proj')
            >>> _Decorator.parse_projection(func)(proj='dumb')
                happyError: !!! AssertionError: wrong value for PROJ argument - projection dumb not supported !!!
            >>> _Decorator.parse_projection(func)(proj='WGS84')
                4326
            >>> _Decorator.parse_projection(func)(proj='EPSG3857')
                3857
            >>> _Decorator.parse_projection(func)(proj=3857)
                3857
            >>> _Decorator.parse_projection(func)(proj='LAEA')
                3035
                
        Note also that the default projection can be parsed:
            
            >>> _Decorator.parse_projection(func)()
                4326
                
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_year`,
        :meth:`~geoDecorators.parse_scale`, :meth:`~geoDecorators.parse_vector`,
        :meth:`~geoDecorators.parse_iformat`, :meth:`~geoDecorators.parse_level`.
        """
        ## PROJECTION      = dict(happyType.seqflatten([[(k,v), (v,v)] for k,v in settings.GISCO_PROJECTIONS.items()]))
        def __init__(self, *args, **kwargs):
            kwargs.update({'_parse_cls_':   [int, str, list], 
                           '_key_':         _Decorator.KW_PROJECTION, 
                           '_values_':      settings.GISCO_PROJECTIONS,
                           '_key_default_': settings.DEF_GISCO_PROJECTION})
            super(_Decorator.parse_projection,self).__init__(*args, **kwargs)
        #pass
       
    #/************************************************************************/
    class parse_iformat(__base):
        """Class decorator of functions and methods used to parse a vector format.
        
            >>> new_func = _Decorator.parse_iformat(func)
        
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
            the decorated function that now accepts :data:`fmt` as a keyword 
            argument to parse a vector format (*e.g.*, for downloading datasets);
            the supported vector formats (*i.e.* parsed to :data:`fmt`) are 
            :literal:`'shp','geojson','topojson','gdb'` and :literal:`'pbf'`, *e.g.* 
            any of those listed in :data:`settings.GISCO_FORMATS`. 
        
        Examples
        --------     
        The formats supported by |GISCO| are parsed/checked through the call to
        this class:

            >>> func = lambda *args, **kwargs: kwargs.get('fmt')
            >>> _Decorator.parse_iformat(func)(fmt='1)
                happyError: !!! wrong format for FMT argument !!!
            >>> _Decorator.parse_iformat(func)(fmt='csv')
                happyError: !!! wrong value for FMT argument - vector format 'csv' not supported !!!
            >>> _Decorator.parse_iformat(func)(fmt='geojson')
                'geojson'
            >>> _Decorator.parse_iformat(func)(fmt='topojson')
                'json'          
            >>> _Decorator.parse_iformat(func)(fmt='shapefile')
                'shx'
                
        A default format shall be parsed as well:
            
            >>> _Decorator.parse_iformat(func)()
                'geojson'
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_year`,
        :meth:`~geoDecorators.parse_scale`, :meth:`~geoDecorators.parse_vector`,
        :meth:`~geoDecorators.parse_projection`, :meth:`~geoDecorators.parse_level`.
        """
        def __init__(self, *args, **kwargs):
            _kwargs = {'shapefile': 'shx'} # we cheat...
            _kwargs.update(settings.GISCO_FORMATS.copy()) 
            kwargs.update({'_parse_cls_':   [str, list], 
                           '_key_':         _Decorator.KW_IFORMAT, 
                           '_values_':      _kwargs,
                           '_key_default_': settings.DEF_GISCO_FORMAT})
            super(_Decorator.parse_iformat,self).__init__(*args, **kwargs)
       
    #/************************************************************************/
    class parse_vector(__base):
        """Class decorator of functions and methods used to parse a spatial typology, 
        as defined by |GISCO|.
        
            >>> new_func = _Decorator.parse_vector(func)
        
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
            the decorated function that now accepts :data:`vector` as a keyword 
            argument to parse a feature type (*e.g.*, used when downloading |GISCO| 
            datasets); the supported vector formats (*i.e.*, parsed to :data:`vector`) 
            are :literal:`'region','label'` and :literal:`'line'` (or :literal:`'boundary'`, 
            *e.g.* those listed in :data:`settings.GISCO_VECTORS`.   
        
        Examples
        --------          

            >>> func = lambda *args, **kwargs: kwargs.get('vector')
            >>> _Decorator.parse_vector(func)(vector='1)
                happyError: !!! wrong format for GEOMETRY argument !!!
            >>> _Decorator.parse_vector(func)(vector='polygon')
                happyError: !!! wrong value for GEOMETRY argument - geometry 'polygon' not supported !!!
            >>> _Decorator.parse_vector(func)(vector='region')
                'RN'
            >>> _Decorator.parse_vector(func)(vector='line')
                'BN'
            >>> _Decorator.parse_vector(func)(vector='LB')
                'LB'
            
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_year`,
        :meth:`~geoDecorators.parse_scale`, :meth:`~geoDecorators.parse_iformat`,
        :meth:`~geoDecorators.parse_projection`, :meth:`~geoDecorators.parse_level`.
        """
        def __init__(self, *args, **kwargs):
            kwargs.update({'_parse_cls_':   [str, list], 
                           '_key_':         _Decorator.KW_VECTOR, 
                           '_values_':      settings.GISCO_VECTORS,
                           '_key_default_': settings.DEF_GISCO_VECTOR})
            super(_Decorator.parse_vector,self).__init__(*args, **kwargs)
   
    #/************************************************************************/
    class parse_scale(__base):
        """Class decorator of functions and methods used to parse a scale resolution 
        unit, as defined by |GISCO|.
        
            >>> new_func = _Decorator.parse_scale(func)
        
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
            the decorated function that now accepts  :data:`scale` as a keyword 
            argument to parse a scale/resolution unit (*e.g.*, used in NUTS definition);
            the supported scale parameters are :literal:`'01m','03m','10m','20m','60m'`, 
            *e.g.* those listed in :data:`settings.GISCO_SCALES`, as well as the
            corresponding digital units (1, 3, 10, 20 and 60 respectively).
        
        Examples
        --------          
        The representation scales implemented in |GISCO| vector datasets are parsed
        thanks to this class:

            >>> func = lambda *args, **kwargs: kwargs.get('scale')
            >>> _Decorator.parse_scale(func)(scale=45)
                happyError: !!! wrong value for SCALE argument - scale resolution 45 not supported !!!
            >>> _Decorator.parse_scale(func)(scale=1)
                '01m'
            >>> _Decorator.parse_scale(func)(scale='20m')
                '20m'
            >>> _Decorator.parse_scale(func)(scale='6')
                '60m'
            
        A default scale is automatically parsed:
            
            >>> _Decorator.parse_scale(func)()
                '01m'

        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_year`,
        :meth:`~geoDecorators.parse_level`, :meth:`~geoDecorators.parse_iformat`,
        :meth:`~geoDecorators.parse_projection`, :meth:`~geoDecorators.parse_vector`.
        """
        def __init__(self, *args, **kwargs_):
            kwargs_.update({'_parse_cls_':  [int, str, list], 
                           '_key_':         _Decorator.KW_SCALE, 
                           '_values_':      settings.GISCO_SCALES,
                           '_key_default_': settings.DEF_GISCO_SCALE})
            super(_Decorator.parse_scale,self).__init__(*args, **kwargs_)
    
    #/************************************************************************/
    class parse_level(__base):
        """Class decorator of functions and methods used to parse a level for |NUTS| 
        units.
        
            >>> new_func = _Decorator.parse_level(func)
        
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
            the decorated function that now accepts  :data:`level` as a keyword 
            argument to parse a NUTS level; the supported levels are 
            :literal:`0,1,2,3`, as listed in :data:`settings.GISCO_LEVELS`.
        
        Examples
        --------          
        All current NUTS levels can parsed/checked using this class:

            >>> func = lambda *args, **kwargs: kwargs.get('level')
            >>> _Decorator.parse_level(func)(level='dumb')
                happyError: !!! wrong format for LEVEL argument !!!
            >>> _Decorator.parse_level(func)(level=4)
                happyError: !!! wrong value for LEVEL argument - level 4 not supported !!!
            >>> _Decorator.parse_level(func)(level=1)
                1

        It also supports the parsing of multiple levels:
            
            >>> _Decorator.parse_level(func)(level=[0,1,2])
                [0,1,2]
                
        and forces the parsing of one default level at level:
            
            >>> _Decorator.parse_level(func)()
                0
                
        See also
        --------
        :meth:`~geoDecorators.parse_coordinate`, :meth:`~geoDecorators.parse_year`,
        :meth:`~geoDecorators.parse_scale`, :meth:`~geoDecorators.parse_iformat`,
        :meth:`~geoDecorators.parse_projection`, :meth:`~geoDecorators.parse_vector`.
        """
        def __init__(self, *args, **kwargs):
            kwargs.update({'_parse_cls_':   [int, str, list], # list of levels 
                           '_key_':         _Decorator.KW_LEVEL, 
                           '_values_':      settings.GISCO_LEVELS + ['ALL',],
                           '_key_default_': settings.DEF_GISCO_LEVEL})
            super(_Decorator.parse_level,self).__init__(*args, **kwargs)
            
    
    #/************************************************************************/
    @classmethod
    def parse_default(cls, dimensions, **kwargs):
        """Class method decorator defining default parsing arguments.
        
            >>> decorator = parse_default(dimensions, **kwargs)
            >>> new_func = decorator(func)
            
        Arguments
        ---------
        dimensions : str, list
            a list of dimensions defining parsing parameters for which default
            values have been set; see for instance the dimensions provided in the
            variable :data:`settings.GISCO_DATA_DIMENSIONS`.
            
        Keyword arguments
        -----------------
        _force_list_ : bool
            flag set to :literal:`True` so as to force the output default value(s) 
            to be of the type :obj:`list`; default: :data:`_force_list_=False`.
            
        Returns
        -------
        decorator : 
            a method decorator that parse a dictionary of default values for all 
            the parsing parameters listed in the :data:`dimensions` list; all other
            keyword arguments are preserved.
            
        Examples
        --------
        The class returns a decorator:
        
            >>> _Decorator.parse_default('DUMB')
                Traceback (most recent call last):
                ...
                happyError: !!! AttributeError: dimension DUMB not recognised !!!
            >>> _Decorator.parse_default('PLACE')
                Traceback (most recent call last):
                ...
                happyError: !!! AssertionError: no input place arguments passed !!!
            >>> _Decorator.parse_default('PROJECTION')
                happygisco.base._Decorator.parse_default.<locals>.decorator
                
        It can be used to decorate any method accepting keyword arguments:

            >>> @_Decorator.parse_default('SOURCE')
            ... def func(*args,**kwargs):
            ...     print(kwargs)
            >>> func()
                {}
            >>> @_Decorator.parse_default('PROJECTION')
            ... def func(*args,**kwargs):
            ...     print(kwargs)
            >>> func(key = 'dumb')
                {key = 'dumb', 'proj': 4326}    
            >>> @_Decorator.parse_def_kwargs(['LEVEL','SCALE'])
            ... def func(*args,**kwargs):
            ...     print(kwargs)
            >>> func(key = 0, level = -1, scale = 'dumb')
                {'key': 0, 'level': 0, 'scale': '60m'}
                
        The use of the :data:`_force_list_` keyword argument can help reformat the 
        output default values into list:
            
            >>> @_Decorator.parse_default(settings.GISCO_DATA_DIMENSIONS, _force_list_=True)
            ... def func(*args,**kwargs):
            ...     print(kwargs)
            >>> func()
                {'fmt': ['geojson'], 'level': [0], 'proj': [4326], 'scale': ['60m'], 'vector': ['RG'], 'year': [2013]}                
        
        Note in particular that, in order to retrieve, all at once, the dictionary 
        of |GISCO| default dimension parameters, one can run:
            
            >>> defkw = _Decorator.parse_default(settings.GISCO_DATA_DIMENSIONS)(lambda **kw: kw)
            >>> defkw()
                {'fmt': 'geojson', 'level': 0, 'proj': 4326, 'scale': '60m', 'vector': 'RG', 'year': 2013}                
        
        Note
        ----
        * For each dimension :data:`dim` in the input list :data:`dimensions`, both
          a variable :data:`KW_<dim>` and a parsing method :data:`parse_<dim>` need 
          to be defined in the class :class:`_Decorator`.
        * The parsing methods :data:`parse_<dim>` need to define default values when 
          no keyword argument is parsed.
          
        See also
        --------
        :meth:`~_Decorator.parse_year`, :meth:`~_Decorator.parse_projection`, 
        :meth:`~_Decorator.parse_iformat`, :meth:`~_Decorator.parse_vector`, 
        :meth:`~_Decorator.parse_scale`, :meth:`~_Decorator.parse_level`, 
        :meth:`~_Decorator.parse_projection`. 
        """
        __force_list = kwargs.pop(_Decorator.KW_FORCE_LIST, False)
        try:
            assert happyType.isstring(dimensions) or happyType.issequence(dimensions)
        except:
            raise happyError('wrong format for DIMENSIONS arguments')
        else:
            if not happyType.issequence(dimensions):
                dimensions = [dimensions,]           
        def_kwargs = {}
        for dim in dimensions:
            try:
                key = getattr(cls, 'KW_' + dim)
            except:
                raise happyError('dimension %s not recognised' % dim)
            try:
                dim = dim.lower()
                parse = getattr(cls, 'parse_' + dim)
            except:
                # raise happyError('parse method parse_%s not recognised' % dim)
                happyVerbose('parse method parse_%s not recognised' % dim)
                continue # pass 
            try:
                func = lambda *a, **kw: [kw.get(key)]
                if __force_list is True:
                    def_kwargs.update({key: parse(func)()})
                else:
                    val = parse(func)()
                    def_kwargs.update({key: val[0] if val is not None and happyType.issequence(val) and len(val)==1 \
                                            else val})
            except:
                raise happyError('error while parsing dimension %s' % dim)
        # return def_kwargs
        class decorator(cls.__base):
            def __call__(self, *args, **_kwargs):  
                _kwargs.update(def_kwargs)
                return self.func(*args, **_kwargs)
        return decorator
         
#_Decorator.parse_year =                         \
#    _Decorator._parse_class(int, _Decorator.KW_YEAR, 
#                            _values_=settings.GISCO_YEARS, _key_default_= settings.DEF_GISCO_YEAR)
#_Decorator.parse_projection =                   \
#    _Decorator._parse_class([int,str], _Decorator.KW_PROJECTION, 
#                            _values_=settings.GISCO_PROJECTIONS, _key_default_=settings.DEF_GISCO_PROJECTION)
#_Decorator.parse_iformat =                       \
#    _Decorator._parse_class(str, _Decorator.KW_FORMAT, _values_=settings.GISCO_FORMATS)
#_Decorator.parse_vector =                      \
#    _Decorator._parse_class(str, _Decorator.KW_GEOMETRY, 
#                            _values_=settings.GISCO_GEOMETRIES, _key_default_=settings.DEF_GISCO_GEOMETRY)
#_Decorator.parse_scale =                        \
#    _Decorator._parse_class([int,str], _Decorator.KW_SCALE, 
#                            _values_=settings.GISCO_SCALES, _key_default_=settings.DEF_GISCO_SCALE)
#_Decorator.parse_level =                        \
#    _Decorator._parse_class([int, list], _Decorator.KW_LEVEL, 
#                            _values_=settings.GISCO_LEVELS, _key_default_=settings.DEF_GISCO_NUTSLEVE)
#_Decorator.parse_layer =                        \
#    _Decorator._parse_class(ogr.Layer, _Decorator.KW_LAYER)
#_Decorator.parse_vector =                        \
#    _Decorator._parse_class(ogr.Feature, _Decorator.KW_VECTOR)
        

#%%
#==============================================================================
# CLASS _CachedResponse
#==============================================================================

try:
    assert SERVICE_AVAILABLE is True
except:
    class _CachedResponse(object):
        #doc-ignore
        pass 
else:
    class _CachedResponse(requests.Response):
        """Generic class used for representing a cached response.
            
            >>> resp = base._CachedResponse(resp, url, path='')
        """ 
        # why not derive this class from aiohttp.ClientResponse in the case
        # ASYNCIO_AVAILABLE is True? actually, we refer here to aiohttp doc,
        # namely http://docs.aiohttp.org/en/stable/client_reference.html:
        #   "User never creates the instance of ClientResponse class but gets 
        #   it from API calls"
        __attrs__ = requests.Response.__attrs__ + ['_cache_path', 'cache_store']
        def __init__(self, *args, **kwargs):
            r, url = args
            path = kwargs.pop('path','')
            try:
                assert happyType.isstring(url) and happyType.isstring(path) \
                    and isinstance(r,(bytes,requests.Response,aiohttp.ClientResponse))
            except:
                raise happyError('parsed initialising parameters not recognised')
            super(_CachedResponse,self).__init__()
            self.url = url
            self._cache_path = self.cache_store = path
            if isinstance(r,bytes):
                self.reason, self.status_code = "OK", 200
                self._content, self._content_consumed = r, True           
            elif isinstance(r,(requests.Response,aiohttp.ClientResponse)):
                # self.__response = r
                for attr in r.__dict__:
                    setattr(self, attr, getattr(r, attr))
            # self._encoding = ?
        def __repr__(self):
            return '<Response [%s]>' % (self.status_code)
                 
#%%
#==============================================================================
# CLASS _Service
#==============================================================================

class _Service(object):
    """Base class for web-based geospatial services.
    
    This class is used to defined a web-session and simple connection operations 
    called by a web-service. 
        
       >>> serv = base._Service()        
    """
    
    RESPONSE_FORMATS = ['resp', 'zip', 'raw', 'text', 'stringio', 'content', 'bytes', 'bytesio', 'json']
    ZIP_OPERATIONS  = ['extract', 'extractall', 'getinfo', 'namelist', 'read', 'infolist']
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        self.__session           = None
        self.__cache_store       = True
        self.__expire_after      = None # datetime.deltatime(0)
        self.__cache_backend     = None
        # update with keyword arguments passed
        if kwargs != {}:
            attrs = (_Decorator.KW_CACHE,_Decorator.KW_EXPIRE,_Decorator.KW_FORCE)
            for attr in list(set(attrs).intersection(kwargs.keys())):
                setattr(self, '%s' % attr, kwargs.pop(attr))
        # determine appropriate setting for a given session, taking into account
        # the explicit setting on that request, and the setting in the session. 
        self.__cache_backend = 'File'
        if isinstance(self.__cache_store, bool):
            self.__cache_store = self.__default_cache() if self.cache_store else None
        # determine appropriate setting for a given session, taking into account
        # the explicit setting on that request, and the setting in the session.
        if ASYNCIO_AVAILABLE is False:            
            try:
                # whether requests_cache is defined or not, no matter
                self.__session = requests.Session()
                # session = requests.session(**kwargs)
            except:
                raise happyError('wrong requests setting - SESSION not initialised')
            if CACHECONTROL_INSTALLED is True and self.cache_store is not None:
                try:
                    if self.expire_after is None or int(self.expire_after) > 0:
                        cache_store = FileCache(os.path.abspath(self.cache_store))  
                    else:
                        cache_store = FileCache(os.path.abspath(self.cache_store), forever=True)
                except:
                    pass
                else:
                    self.__session = CacheControl(self.session, cache_store)
            try:
                assert self.session is not None
            except:
                raise happyError('wrong definition for SESSION parameters - SESSION not initialised')
        else:
            self.__session = None
        
    #/************************************************************************/
    @property
    def session(self):
        """Session property (:data:`getter`/:data:`setter`) of an instance of
        a class :class:`_Service`. :data:`session` is itself an instance of a
        :class:`requests.session.Session` class.
        """ # A session type is :class:`requests.session.Session`.
        return self.__session
    @session.setter#analysis:ignore
    def session(self, session):
        if session is not None and not isinstance(session, requests.sessions.Session, aiohttp.client.ClientSession):
            raise happyError('wrong type for SESSION parameter')
        self.__session = session
    
    #/************************************************************************/
    @property
    def cache_store(self):
        """Cache property (:data:`getter`/:data:`setter`) of an instance of
        a class :class:`_Service`. :data:`cache_store` is set to the physical 
        location (*i.e.* on the drive) of the repository used to cache the 
        downloaded datasets/responses.
        """
        return self.__cache_store
    @cache_store.setter
    def cache_store(self, cache_store):
        if not(cache_store is None or isinstance(cache_store, (str,bool))):
            raise happyError('wrong type for %s parameter' % _Decorator.KW_CACHE.upper())
        else:
            #if cache_store not in (False,'',None) and requests_cache is None and CACHECONTROL_INSTALLED is False:
            #    raise happyError('caching not supported in the absence of modules requests_cache and cachecontrol')                
            pass
        self.__cache_store = cache_store
    
    #/************************************************************************/
    @property
    def cache_backend(self):
        return self.__cache_backend
    # note: no setter ... 

    #/************************************************************************/
    @property
    def expire_after(self):
        """Expiration property (:data:`getter`/:data:`setter`) of an instance of
        a class :class:`_Service`. :data:`expire_after` represents the time after
        which datasets downloaded and cached through this instance shall be 
        downloaded again.
        """
        return self.__expire_after
    @expire_after.setter
    def expire_after(self, expire_after):
        if expire_after is None or isinstance(expire_after, (int, datetime.timedelta)) \
                and (int(expire_after)>=0 or expire_after==-1):
            self.__expire_after = expire_after
        elif not isinstance(expire_after, (int, datetime.timedelta)):
            raise happyError('wrong type for %s parameter' % _Decorator.KW_EXPIRE.upper())
        #elif isinstance(expire_after, int) and expire_after<0:
        #    raise happyError('wrong time setting for %s parameter' % _Decorator.KW_EXPIRE.upper())
        
    #/************************************************************************/   
    def __get_status(self, url):
        # sequential implementation of get_status
        try:
            response = self.session.head(url)
        except requests.ConnectionError:
            raise happyError('connection failed - a Connection error occurred')  
        except requests.HTTPError:
            raise happyError('request failed - an HTTP error occurred.')  
        else:
            status = response.status_code
        try:
            name = settings.HTTP_ERROR_STATUS[status]['name']
            desc = settings.HTTP_ERROR_STATUS[status]['desc']
        except KeyError:
            name = desc = 'Unknown error'#analysis:ignore
        happyVerbose('response status from web-service: %s ("%s")' % (status,name))
        try:
            response.raise_for_status()
        except:
            raise happyError('wrong request - %s status ("%s") returned' % (status,name))  
        else:
            response.close()
        return status

    #/************************************************************************/
    async def __aio_get_status(self, session, url):
        # asynchronous implementation of get_status
        try:
            response = await session.head(url)
        except Exception as e: # aiohttp.ClientConnectionError:
            raise happyError('connection failed', errtype=e)  
        else: 
            status = response.status
        try:
            name = settings.HTTP_ERROR_STATUS[status]['name']
            desc = settings.HTTP_ERROR_STATUS[status]['desc']
        except KeyError:
            name = desc = 'Unknown error'#analysis:ignore
        happyVerbose('response status from web-service: %s ("%s")' % (status,name))
        async with response:
            try:
                response.raise_for_status()
            except:
                raise happyError('wrong request - %s status ("%s") returned' % (status,name))  
                #happyVerbose('response status from web-service: %s' % status)
        return status
        
    #/************************************************************************/ 
    @_Decorator.parse_url
    def get_status(self, *url, **kwargs):
        """Retrieve the header of a URL and return the server's status code.
        
            >>> status = serv.get_status(*url)
            
        Arguments
        ---------
        url : str
            complete URL name(s) whom status will be checked.
        
        Returns
        -------
        status : int
            response status code(s).
            
        Raises
        ------
        happyError
            error is raised in the cases:
                
                * the request is wrongly formulated,
                * the connection fails.
            
        Examples
        --------
        We can see the response status code when connecting to different web-pages
        or services:
        
            >>> serv = base._Service()
            >>> serv.get_status('http://dumb')
                Cannot connect to host dumb:80 ssl:None [nodename nor servname provided, or not known]: connection failed
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
            assert _Decorator.KW_URL in kwargs
        except:
            pass
        else:
            url = kwargs.pop(_Decorator.KW_URL)
        #if len(urls)==1 and happyType.issequence(urls[0]):
        #    urls = urls[0]
        #try:
        #    assert all([happyType.isstring(url) for url  in urls])
        #except:
        #    raise happyError('wrong type for input URLs')
        if ASYNCIO_AVAILABLE is False:
            try:
                status = [self.__get_status(u) for u in url]
            except happyError as e:
                raise happyError(errtype=e) # 'sequential status extraction error'
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop() # event loop
            async def aio_get_all_status(loop, url):
                async with aiohttp.ClientSession(loop=loop, raise_for_status=True) as session:
                    # tasks to do
                    tasks = [self.__aio_get_status(session, u) for u in url]
                    # gather task responses
                    return await asyncio.gather(*tasks, return_exceptions=True) 
            try:
                future = asyncio.ensure_future(aio_get_all_status(loop, url)) 
                # future = loop.create_task(aio_get_all_status(urls))
                status = loop.run_until_complete(future) # loop until done
                # status = future.result()
            except happyError as e:
                raise happyError(errtype=e) # 'asynchronous status extraction error'
            finally:
                loop.close()  
        status = [s if isinstance(s,int) else -1 for s in status]
        return status if status in ([],None) or len(status)>1 else status[0]

    #/************************************************************************/
    @staticmethod
    def __default_cache():
        #ignore-doc
        # create default pathname for cache directory depending on OS platform.
        # inspired by `Python` package `mod:wbdata`: default path defined for 
        # `property:path` property of `class:Cache` class.
        platform = sys.platform
        if platform.startswith("win"): # windows
            basedir = os.getenv("LOCALAPPDATA",os.getenv("APPDATA",os.path.expanduser("~")))
        elif platform.startswith("darwin"): # Mac OS
            basedir = os.path.expanduser("~/Library/Caches")
        else:
            basedir = os.getenv("XDG_CACHE_HOME",os.path.expanduser("~/.cache"))
        return os.path.join(basedir, settings.PACKAGE)    

    #/************************************************************************/
    @staticmethod
    def __build_cache(url, cache_store):
        #ignore-doc
        # build unique filename from URL name and cache directory, e.g. using 
        # hashlib encoding.
        # :param url:
        # :param cache_store:
        # :returns: a unique pathname representing the input URL
        pathname = url.encode('utf-8')
        try:
            pathname = hashlib.md5(pathname).hexdigest()
        except:
            pathname = pathname.hex()
        return os.path.join(cache_store or './', pathname)

    #/************************************************************************/
    @staticmethod
    def __is_cached(pathname, time_out): # note: we check a path here
        #ignore-doc
        if not os.path.exists(pathname):
            resp = False
        elif time_out is None:
            resp = True
        elif time_out < 0:
            resp = True
        elif time_out == 0:
            resp = False
        else:
            cur = time.time()
            mtime = os.stat(pathname).st_mtime
            happyVerbose("%s - last modified: %s" % (pathname,time.ctime(mtime)))
            resp = cur - mtime < time_out
        return resp
    
    #/************************************************************************/
    @_Decorator.parse_url
    def is_cached(self, *url, **kwargs):
        """Check whether a URL has been already cached.
        
        Returns
        -------
        ans : bool, list[bool] 
            True if the input URL(s) can be retrieved from the disk (cache).,
        """
        try:
            assert _Decorator.KW_URL in kwargs
        except:
            pass
        else:
            url = kwargs.pop(_Decorator.KW_URL)
        cache_store = kwargs.get(_Decorator.KW_CACHE) or self.cache_store or True
        if isinstance(cache_store, bool) and cache_store is True:
            cache_store = self.__default_cache()
        expire_after = kwargs.get(_Decorator.KW_EXPIRE) or self.expire_after
        ans = [self.__is_cached(self.__build_cache(u, cache_store), expire_after) 
                for u in url]
        return ans if len(ans)>1 else ans[0]
    
    #/************************************************************************/
    @staticmethod
    def __clean_cache(pathname, time_expiration): # note: we clean a path here
        #ignore-doc
        if not os.path.exists(pathname):
            resp = False
        elif time_expiration is None or time_expiration <= 0:
            resp = True
        else:
            cur = time.time()
            mtime = os.stat(pathname).st_mtime
            happyVerbose("%s - last modified: %s" % (pathname,time.ctime(mtime)))
            resp = cur - mtime >= time_expiration
        if resp is True:
            happyVerbose("removing disk file %s" % pathname)
            if os.path.isfile(pathname):
                os.remove(pathname)
            elif os.path.isdir(pathname):
                shutil.rmtree(pathname) 
            
    #/************************************************************************/
    @_Decorator.parse_url
    def clean_cache(self, *url, **kwargs):
        """Clean a cached file or a cached repository.

        Examples
        --------
        
            >>> serv = services.GISCOService()
            >>> serv.clean_cache()
            
        To be sure, one can enfore the :data:`expire_after` parameter:
            
            >>> serv.clean_cache(expire_after=0)
            
        """
        try:
            assert _Decorator.KW_URL in kwargs
        except:
            pass
        else:
            url = kwargs.pop(_Decorator.KW_URL,None)
        cache_store = kwargs.get(_Decorator.KW_CACHE) or self.cache_store or True
        if isinstance(cache_store, bool) and cache_store is True:
            cache_store = self.__default_cache()
        expire_after = kwargs.get(_Decorator.KW_EXPIRE) or self.expire_after
        if url in ((),None):
            pathnames = os.scandir(cache_store) 
        else:
            pathnames = [self.__build_cache(u, cache_store) for u in url]
        for pathname in pathnames:
            if pathname.is_dir():
                self.__clean_cache(pathname, expire_after)
        #try:
        #    os.rmdir(cache_store)
        #except OSError:
        #    pass # the directory was not empty
        if url in ((),None):
            shutil.rmtree(cache_store) 
                        
    #/************************************************************************/
    def __sync_cache_response(self, url, force_download, cache_store, expire_after):
        # sequential implementation of cache_response
        pathname = self.__build_cache(url, cache_store)
        is_cached = self.__is_cached(pathname, expire_after)
        if force_download is True or is_cached is False or cache_store in (None,False):
            response = self.session.get(url)
            content = response.content
            if cache_store not in (None,False):
                # write "content" to a given pathname
                with open(pathname, 'wb') as f:
                    f.write(content)
        else:
            # read "content" from a given pathname.
            with open(pathname, 'rb') as f:
                content = f.read()
        return content, pathname

    #/************************************************************************/
    async \
    def __async_cache_response(self, session, url, force_download, cache_store, expire_after):
        # asynchronous implementation of cache_response
        pathname = self.__build_cache(url, cache_store)
        is_cached = self.__is_cached(pathname, expire_after)
        if force_download is True or is_cached is False or cache_store in (None,False):
            response = await session.get(url)
            content = await response.content.read()
            if cache_store not in (None,False):
                try:
                    assert aiofiles
                except:  # we loose the benefits of the async ... but ok
                    print('__async open')
                    with open(pathname, 'wb') as f:
                        f.write(content)
                else:
                    async with aiofiles.open(pathname, 'wb') as f:
                        await f.write(content)
        else:
            try:
                assert aiofiles
            except:
                with open(pathname, 'rb') as f:
                    content = f.read() 
            else:
                async with aiofiles.open(pathname, 'rb') as f:
                    content = await f.read() 
        return content, pathname
    
    #/************************************************************************/
    @_Decorator.parse_url
    def cache_response(self, *url, **kwargs):
        """Download URL from internet and store the downloaded content into 
        <cache>/file.
        If <cache>/file already exists, it returns content from disk.
        
            >>> page = serv.cache_response(url, cache_store=False, 
                                           _force_download_=False, _expire_after_=-1)
        """
        try:
            assert _Decorator.KW_URL in kwargs
        except:
            pass
        else:
            url = kwargs.pop(_Decorator.KW_URL)
        #if len(urls)==1 and happyType.issequence(urls[0]):
        #    urls = urls[0]
        #try:
        #    assert all([happyType.isstring(url) for url  in urls])
        #except:
        #    raise happyError('wrong type for input URLs')
        cache_store = kwargs.get(_Decorator.KW_CACHE) or self.cache_store or False
        if isinstance(cache_store, bool) and cache_store is True:
            cache_store = self.__default_cache()
        # create cache directory only the fist time it is needed
        if cache_store not in (False, None):
            if not os.path.exists(cache_store):
                os.makedirs(cache_store)
            elif not os.path.isdir(cache_store):
                raise happyError('cache %s is not a directory' % cache_store)
        force_download = kwargs.get(_Decorator.KW_FORCE) or False
        if not isinstance(force_download, bool):
            raise happyError('wrong type for %s parameter' % _Decorator.KW_FORCE.upper())
        expire_after = kwargs.get(_Decorator.KW_EXPIRE) or self.expire_after
        if ASYNCIO_AVAILABLE is False:
            try:
                resp, path = zip(*[self.__sync_cache_response(u, force_download, cache_store, expire_after)              \
                                        for u in url])
            except happyError as e:
                raise happyError(errtype=e) # 'sequential status extraction error'
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop() # event loop
            async def async_cache_all_response(loop, url):
                async with aiohttp.ClientSession(loop=loop, raise_for_status=True) as session:
                    # tasks to do
                    tasks = [self.__async_cache_response(session, u,
                                                         force_download, cache_store, expire_after)         \
                                for u in url]
                    # gather task responses
                    return await asyncio.gather(*tasks, return_exceptions=True) 
            try:
                future = asyncio.ensure_future(async_cache_all_response(loop, url)) 
                # future = loop.create_task(aio_get_all_status(urls))
                resp, path = zip(*loop.run_until_complete(future)) # loop until done
                # status = future.result()
            except happyError as e:
                raise happyError(errtype=e) # 'asynchronous status extraction error'
            finally:
                loop.close()             
        return (resp, path) if resp in ([],None) or len(resp)>1 else (resp[0], path[0])

    #/************************************************************************/
    def __sync_get_response(self, url, force_download, caching, cache_store, expire_after, **kwargs):
        if caching is False or cache_store is None:
            try:
                if REQUESTS_CACHE_INSTALLED is True:
                    with requests_cache.disabled():
                        resp = self.session.get(url)    
                else:
                    resp = self.session.get(url)                
            except:
                raise happyError('wrong request formulated') 
        else: 
            path = ''
            try:
                if CACHECONTROL_INSTALLED is True:
                    resp = self.session.get(url)                
                    path = cache_store
                elif REQUESTS_CACHE_INSTALLED is True:
                    with requests_cache.enabled(cache_store, **kwargs):
                        resp = self.session.get(url)  
                    path = cache_store
                else:
                    resp, path = self.__sync_cache_response(url, force_download, cache_store, expire_after)
            except:
                raise happyError('wrong request formulated')  
            else:
                resp = _CachedResponse(resp, url, path=path)
        try:
            assert resp is not None
        except:
            raise happyError('wrong response retrieved')  
        return resp

    #/************************************************************************/
    async \
    def __async_get_response(self, session, url, force_download, caching, cache_store, expire_after):
        if caching is False or cache_store is None:
            try:
                resp = await session.get(url)                
            except:
                raise happyError('wrong request formulated') 
        else: 
            try:
                resp, path = await self.__async_cache_response(session, url, force_download, cache_store, expire_after)
            except:
                raise happyError('wrong request formulated')  
            else:
                print('url=%s' % url)
                resp = _CachedResponse(resp, url, path=path)
        try:
            assert resp is not None
            # yield from response.raise_for_status()
        except:
            raise happyError('wrong response retrieved')  
        return resp
    
    #/************************************************************************/
    @_Decorator.parse_url
    def get_response(self, *url, **kwargs):
        """Retrieve the GET response of a URL.
        
            >>> response = serv.get_response(*url, **kwargs)
            
        Arguments
        ---------
        url : str
            complete URL name(s) whose response(s) is(are) retrieved.
            
        Keyword arguments
        -----------------
        cache_store : str
            physical location (*i.e.* on the drive) of the repository used to 
            cache the datasets/responses to be downloaded; when not set, the
            internal :data:`~_Service.cache_store` location already set for the 
            service is used.
        _expire_after_ : int,datetime
            time after which the already cached datasets shall be downloaded again; 
            when not set, the internal :data:`~_Service.expire_after` value already 
            set for the service is used.
        _force_download_ : bool
            flag set to force the downloading of the datasets/responses even if
            those are already cached, and independently of the value of the
            :data:`_expire_after_` argument above; default: :data:`_force_download_=False`.
        _caching_ : bool
            flag set to actually use caching when fetching the response; default: 
            :data:`_caching_=True`, the cache is used and downloaded datasets/responses
            are stored on the disk.
            
        Returns
        -------
        response : :class:`requests.models.Response`
            response(s) fetched from the input :data:`url` addresses.
            
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the request is wrongly formulated,
                * a bad response is retrieved.
            
        Examples
        --------
        Some simple tests:
            
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
            assert _Decorator.KW_URL in kwargs
        except:
            pass
        else:
            url = kwargs.pop(_Decorator.KW_URL)
        caching = kwargs.pop(_Decorator.KW_CACHING, True)
        cache_store = kwargs.pop(_Decorator.KW_CACHE,None) or self.cache_store or False
        if isinstance(cache_store, bool) and cache_store is True:
            cache_store = self.__default_cache()
        # create cache directory only the fist time it is needed
        if cache_store not in (False, None):
            if not os.path.exists(cache_store):
                os.makedirs(cache_store)
            elif not os.path.isdir(cache_store):
                raise happyError('cache %s is not a directory' % cache_store)
        force_download = kwargs.pop(_Decorator.KW_FORCE, False)
        if not isinstance(force_download, bool):
            raise happyError('wrong type for %s parameter' % _Decorator.KW_FORCE.upper())
        expire_after = kwargs.get(_Decorator.KW_EXPIRE) or self.expire_after
        #expire_after = kwargs.pop(_Decorator.KW_EXPIRE,None) or self.expire_after or 0
        if isinstance(cache_store, bool) and cache_store is True:
            cache_store = self.__default_cache()
        if ASYNCIO_AVAILABLE is False:
            try:
                response = [self.__sync_get_response(u, force_download, caching, cache_store, expire_after)              \
                            for u in url]
            except happyError as e:
                raise happyError(errtype=e) # 'sequential status extraction error'
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop() # event loop
            async def async_get_all_response(loop, url):
                async with aiohttp.ClientSession(loop=loop, raise_for_status=True) as session:
                    # tasks to do
                    tasks = [self.__async_get_response(session, u, force_download, caching, cache_store, expire_after)  \
                             for u in url]
                    # gather task responses
                    return await asyncio.gather(*tasks, return_exceptions=True) 
            try:
                future = asyncio.ensure_future(async_get_all_response(loop, url)) 
                # future = loop.create_task(aio_get_all_status(urls))
                response = loop.run_until_complete(future) # loop until done
                # status = future.result()
            except happyError as e:
                raise happyError(errtype=e) # 'asynchronous status extraction error'
            finally:
                loop.close()             
        return response if response in ([],None) or len(response)>1 else response[0]
    
    #/************************************************************************/
    def __sync_read_response(self, response, **kwargs):
        if not _Decorator.KW_OFORMAT in kwargs:
            try:
                url = response.url
            except:
                fmt = 'json'
            else:
                fmt = 'zip' if any([url.endswith(z) for z in ('zip','gzip','gz')]) else 'json'
        else:
            fmt = kwargs.pop(_Decorator.KW_OFORMAT, None)
        if fmt in (None,'resp','response'):
            return response
        try:
            assert fmt is None or happyType.isstring(fmt)
        except:
            raise happyError('wrong format for %s parameter' % _Decorator.KW_OFORMAT.upper()) 
        else:
            fmt = fmt.lower()
        try:
            assert fmt in ['jsontext', 'jsonbytes'] + self.RESPONSE_FORMATS # only for developers
        except:
            raise happyError('wrong value for FMT parameter - must be in %s' % self.RESPONSE_FORMATS) 
        else:
            if fmt == 'content':
                fmt = 'bytes'
        if fmt.startswith('json'):
            try:
                assert fmt not in ('jsontext', 'jsonbytes')
                data = response.json()
            except:
                try:
                    assert fmt != 'jsonbytes'
                    data = response.text
                except:
                    try:
                        data = response.content 
                    except:
                        raise happyError('error JSON-encoding of response')
                    else:
                        fmt = 'jsonbytes' # force
                else:
                    fmt = 'jsontext' # force
            else:
                return data
        elif fmt == 'raw':
            try:
                data = response.raw
            except:
                raise happyError('error accessing ''raw'' attribute of response')
        elif fmt in ('text', 'stringio'):
            try:
                data = response.text
            except:
                raise happyError('error accessing ''text'' attribute of response')
        elif fmt in ('bytes', 'bytesio', 'zip'):
            try:
                data = response.content 
            except:
                raise happyError('error accessing ''content'' attribute of response')
        if fmt == 'stringio':
            try:
                data = io.StringIO(data)
            except:
                raise happyError('error loading StringIO data')
        elif fmt in ('bytesio', 'zip'):
            try:
                data = io.BytesIO(data)
            except:
                raise happyError('error loading BytesIO data')
        elif fmt == 'jsontext':
            try:
                data = json.loads(data)
            except:
                raise happyError('error JSON-encoding of str text')
        elif fmt == 'jsonbytes':                
                try:
                    data = json.loads(data.decode())
                except:
                    try:            
                        assert CHARDET_INSTALLED is True
                        data = json.loads(data.decode(chardet.detect(data)["encoding"]))
                    except:
                        raise happyError('error JSON-encoding of bytes content')
        if fmt != 'zip':
            return data 
        # deal with special case
        operators = [op for op in self.ZIP_OPERATIONS if op in kwargs.keys()] 
        try:
            assert operators in ([],[None]) or sum([1 for op in operators]) == 1
        except:
            raise happyError('only one operation supported per call')
        else:
            if operators in ([],[None]):
                operator = 'extractall'
                kwargs.update({operator: self.cache_store})
            else:
                operator = operators[0] 
        members, path = None, None
        if operator in ('extract', 'getinfo', 'read'):
            members = kwargs.pop(operator, None)
        elif operator == 'extractall':
            path = kwargs.pop('extractall', None)
        else: # elif operator in ('infolist','namelist'):
            try:
                assert kwargs.get(operator) not in (False,None)
            except:
                raise happyError('no operation parsed')
        if operator.startswith('extract'):
            happyWarning('data extracted from zip file will be physically stored on local disk')
        if members is not None and not happyType.issequence(members):
            members = [members,]
        with zipfile.ZipFile(data) as zf:
            #if not zipfile.is_zipfile(zf): # does not work
            #    raise happyError('file not recognised as zip file')    
            if operator in  ('infolist','namelist'):
                return getattr(zf, operator)()
            elif members is not None:
                if not all([m in zf.namelist() for m in members]):
                    raise happyError('impossible to retrieve member file(s) from zipped data')
            if operator in ('extract', 'getinfo', 'read'):
                data = [getattr(zf, operator)(m) for m in members]
                return data if data in ([],[None]) or len(data)>1 else data[0]
            elif operator == 'extractall':
                return zf.extractall(path=path)    

    #/************************************************************************/
    async \
    def __async_read_response(self, response, **kwargs):
        if not _Decorator.KW_OFORMAT in kwargs:
            try:
                url = response.url
            except:
                fmt = 'json'
            else:
                fmt = 'zip' if any([url.endswith(z) for z in ('zip','gzip','gz')]) else 'json'
        else:
            fmt = kwargs.pop(_Decorator.KW_OFORMAT, None)
        if fmt in (None,'resp','response'):
            return response
        try:
            assert fmt is None or happyType.isstring(fmt)
        except:
            raise happyError('wrong format for %s parameter' % _Decorator.KW_OFORMAT.upper()) 
        else:
            fmt = fmt.lower()
        try:
            assert fmt in ['jsontext', 'jsonbytes'] + self.RESPONSE_FORMATS # only for developers
        except:
            raise happyError('wrong value for FMT parameter - must be in %s' % self.RESPONSE_FORMATS) 
        else:
            if fmt == 'content':
                fmt = 'bytes'
        if fmt.startswith('json'):
            try:
                assert fmt not in ('jsontext', 'jsonbytes')
                data = await response.json()
            except:
                try:
                    assert fmt != 'jsonbytes'
                    data = await response.text
                except:
                    try:
                        data = await response.content 
                    except:
                        raise happyError('error JSON-encoding of response')
                    else:
                        fmt = 'jsonbytes' # force
                else:
                    fmt = 'jsontext' # force
            else:
                return data
        elif fmt == 'raw':
            try:
                data = await response.raw
            except:
                raise happyError('error accessing ''raw'' attribute of response')
        elif fmt in ('text', 'stringio'):
            try:
                data = await response.text
            except:
                raise happyError('error accessing ''text'' attribute of response')
        elif fmt in ('bytes', 'bytesio', 'zip'):
            try:
                data = await response.content 
            except:
                raise happyError('error accessing ''content'' attribute of response')
        if fmt == 'stringio':
            try:
                data = await io.StringIO(data)
            except:
                raise happyError('error loading StringIO data')
        elif fmt in ('bytesio', 'zip'):
            try:
                data = await io.BytesIO(data)
            except:
                raise happyError('error loading BytesIO data')
        elif fmt == 'jsontext':
            try:
                data = await json.loads(data)
            except:
                raise happyError('error JSON-encoding of str text')
        elif fmt == 'jsonbytes':                
                try:
                    data = json.loads(data.decode())
                except:
                    try:            
                        assert CHARDET_INSTALLED is True
                        data = await json.loads(data.decode(chardet.detect(data)["encoding"]))
                    except:
                        raise happyError('error JSON-encoding of bytes content')
        if fmt != 'zip':
            return data 
        # deal with special case
        operators = [op for op in self.ZIP_OPERATIONS if op in kwargs.keys()] 
        try:
            #assert set(kwargs.keys()).difference(set(self.ZIP_OPERATIONS)) == set()
            assert operators in ([],[None]) or sum([1 for op in operators]) == 1
        except:
            raise happyError('only one operation supported per call')
        else:
            if operators in ([],[None]):
                operator = 'extractall'
                kwargs.update({operator: self.cache_store})
            else:
                operator = operators[0] 
        members, path = None, None
        if operator in ('extract', 'getinfo', 'read'):
            members = kwargs.pop(operator, None)
        elif operator == 'extractall':
            path = kwargs.pop('extractall', None)
        else: # elif operator in ('infolist','namelist'):
            try:
                assert kwargs.get(operator) not in (False,None)
            except:
                raise happyError('no operation parsed')
        if operator.startswith('extract'):
            happyWarning('data extracted from zip file will be physically stored on local disk')
        if members is not None and not happyType.issequence(members):
            members = [members,]
        # whatever comes next is actually not asynchronous
        async with zipfile.ZipFile(data) as zf:
            #if not zipfile.is_zipfile(zf): # does not work
            #    raise happyError('file not recognised as zip file')    
            if operator in  ('infolist','namelist'):
                return await getattr(zf, operator)()
            elif members is not None:
                if not all([m in zf.namelist() for m in members]):
                    raise happyError('impossible to retrieve member file(s) from zipped data')
            if operator in ('extract', 'getinfo', 'read'):
                data = await [getattr(zf, operator)(m) for m in members]
                return data if data in ([],[None]) or len(data)>1 else data[0]
            elif operator == 'extractall':
                return await zf.extractall(path=path)    

    #/************************************************************************/
    @_Decorator._parse_class((_CachedResponse, aiohttp.ClientResponse, requests.Response), _Decorator.KW_RESPONSE)
    def read_response(self, *response, **kwargs):
        """Read the response of a given request.
        
            >>> data = serv.read_response(*response, **kwargs)
            
        Arguments
        ---------
        response : :class:`_CachedResponse`,:class:`requests.Response`,:class:`aiohttp.ClientResponse`,
            response(s) from an online request.
            
        Keyword arguments
        -----------------
        ofmt : str
        kwargs :
            
        Returns
        -------
        data : 
            data associated to the input argument :data:`response`, formatted 
            according to what is parsed through the keyword arguments.
            
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the input keyword parameters are wrongly set,
                * there is an error in reading the response,
                * there is an error in encoding the response.
             
        Examples
        --------      

        See also
        --------
        :meth:`~_Service.read_url`.
        """
        try:
            assert _Decorator.KW_RESPONSE in kwargs
        except:
            pass
        else:
            response = kwargs.pop(_Decorator.KW_RESPONSE)
        if ASYNCIO_AVAILABLE is False:
            try:
                data = [self.__sync_read_response(resp, **kwargs) for resp in response]
            except happyError as e:
                raise happyError(errtype=e) # 'sequential status extraction error'
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop() # event loop
            async def async_read_all_response(loop, response):
                # tasks to do
                tasks = [self.__async_read_response(resp, **kwargs) for resp in response]
                # gather task responses
                return await asyncio.gather(*tasks, return_exceptions=True) 
            try:
                future = asyncio.ensure_future(async_read_all_response(loop, response)) 
                # future = loop.create_task(aio_get_all_status(urls))
                data = loop.run_until_complete(future) # loop until done
                # status = future.result()
            except happyError as e:
                raise happyError(errtype=e) # 'asynchronous status extraction error'
            finally:
                loop.close()             
        return data if data in ([],None) or len(data)>1 else data[0]
    
    #/************************************************************************/
    @_Decorator.parse_url
    def read_url(self, *url, **kwargs):
        """Returns the (possibly formatted) response of a given URL.
        
            >>> data = serv.read_url(*url, **kwargs)
            
        Arguments
        ---------
        url : str
            complete URL name(s) from which data will be fetched.
            
        Keyword arguments
        -----------------
        kwargs :
            see keyword arguments of :meth:`~_Service.read_response` method.
            
        Returns
        -------
        data : 
            data fetched from the input :data:`url`, formatted according to what 
            is parsed through the keyword arguments.
            
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * there is a wrong URL status,
                * data cannot be loaded.
             
        Examples
        --------
        
        Note
        ----
        A mix of sequential/asynchronous implementations... 

        See also
        --------
        :meth:`~_Service.get_status`, :meth:`~_Service.get_response`, 
        :meth:`~_Service.read_response`.
        """
        try:
            assert _Decorator.KW_URL in kwargs
        except:
            pass
        else:
            url = kwargs.pop(_Decorator.KW_URL)
        try:
            assert self.get_status(url) is not None
        except happyError as e:
            raise happyError(errtype=e)
        except:
            raise happyError('error API request - wrong URL status')
        try:
            response = self.get_response(url, **kwargs)
        except happyError as e:
            raise happyError(errtype=e)
        except:
            raise happyError('URL data for %s not loaded' % url)
        return self.read_response(response, **kwargs)
            
    #/************************************************************************/
    @classmethod
    def build_url(cls, domain=None, **kwargs):
        """Create a complete query URL to be used by a web-service.
        
            >>> url = _Service.build_url(domain, **kwargs)
            
        Arguments
        ---------
        domain : str
            domain of the URL; default: :data:`domain` is left empty.
           
        Keyword arguments
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
    
        Examples
        --------
        Let us, for instance, build a URL query to *Eurostat* Rest API (just enter 
        the output URL in your browser to check the output):
            
            >>> from happygisco.base import _Service
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
        if domain is None:      domain = kwargs.pop('domain','')
        url = domain.strip("/")
        protocol = kwargs.pop('protocol', settings.DEF_PROTOCOL)
        if protocol not in settings.PROTOCOLS:
            raise happyError('web protocol not recognised')
        if not url.startswith(protocol):  
            url = "%s://%s" % (protocol, url)
        path = kwargs.pop('path','')  
        if path not in (None,''):
            url = "%s/%s" % (url, path)
        query = kwargs.pop('query','')
        if query not in (None,''):      
            url = "%s/%s" % (url, query)
        if kwargs != {}:
            #_izip_replicate = lambda d : [(k,i) if isinstance(d[k], (tuple,list))        \
            #        else (k, d[k]) for k in d for i in d[k]]
            _izip_replicate = lambda d : [[(k,i) for i in d[k]] if isinstance(d[k], (tuple,list))        \
                else (k, d[k])  for k in d]          
            # filters = '&'.join(['{k}={v}'.format(k=k, v=v) for (k, v) in _izip_replicate(kwargs)])
            filters = urllib.parse.urlencode(_izip_replicate(kwargs))
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
    #__metaclass__  = abc.ABCMeta
    pass


#%%
#==============================================================================
# CLASS _Feature
#==============================================================================
            
class _Feature(object):    
    """Base class for geographic features.
    
        >>> feat = base._Feature()
    """
    #__metaclass__  = abc.ABCMeta

    #/************************************************************************/
    def __init__(self):
        self.__coord, self.__projection = None, None
        self.__service, self.__mapping, self.__transform = None, None, None
        try:
            self.__transform = _Tool()
            self.__mapping = _Tool()
        except:
            happyWarning('transform/mapping tool(s) not available')
        try:
            self.__service = _Service()
        except:
            happyWarning('web service(s) not available')
       
    #/************************************************************************/
    @property
    #@abc.abstractmethod
    def service(self):
        """Service property (:data:`getter`) of a :class:`_Feature` instance. 
        The :data:`service` property returns an object as an instance of the
        :class:`~happygisco.services.GISCOService` or :class:`~happygisco.services.APIService`
        classes.
        """
        return self.__service
    @service.setter
    def service(self, service):
        self.__service = service
        
    #/************************************************************************/
    @property
    #@abc.abstractmethod
    def transform(self):
        """Geospatial transform property (:data:`getter`) of a :class:`_Feature` instance.
        The :data:`transform` property returns an object as an instance of the 
        :class:`~happygisco.tools.GDALTransform` class.
        """
        return self.__transform
    @transform.setter
    def transform(self, transform):
        self.__transform = transform
       
    #/************************************************************************/
    @property
    #@abc.abstractmethod
    def mapping(self):
        """Geospatial mapping property (:data:`getter`) of a :class:`_Feature` instance.
        The :data:`mapping` property returns an object as an instance of the
        :class:`~happygisco.tools.FoliumMap` class.
        """
        return self.__mapping
    @mapping.setter
    def mapping(self, mapping):
        self.__mapping = mapping
     
    #/************************************************************************/
    @property
    #@abc.abstractmethod
    def projection(self):
        """Projection property (:data:`getter`) of a :class:`_Feature` instance.
        """ 
        return self.__projection
    @projection.setter
    def projection(self, proj):
        self.__projection = proj

    #/************************************************************************/
    @property
    #@abc.abstractmethod
    def coord(self):
        # ignore: this will be overwritten              
        """Pair of :literal:`(lat,Lon)` geographic coordinates (:data:`getter`/:data:`setter`) 
        of a :class:`_Feature` instance.
        """ 
        return self.__coord
    @coord.setter
    def coord(self, coord):
        self.__coord = coord        
        
    #/************************************************************************/
    @property
    def coordinates(self):                                              
        """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`) of 
        a :class:`_Feature` instance.
        """ 
        pass
        
    #/************************************************************************/
    @property
    def Lon(self):                                                       
        """Longitude property (:data:`getter`) of a :class:`_Feature` instance. 
        A :data:`Lon` type is (a list of) :class:`float`.
        """
        pass

    #/************************************************************************/
    @property
    def lat(self): 
        """Latitude property (:data:`getter`) of a :class:`_Feature` instance. 
        A :data:`lat` type is (a list of) :class:`float`.
        """
        pass
    

#%%
#==============================================================================
# CLASS _NestedDict
#==============================================================================

class _NestedDict(dict):
    """A dictionary-like structure that enables nested indexing of the dictionary 
    contents and merging of multiply nested dictionaries along given dimensions. 
    
        >>> dnest = _NestedDict(*args, **kwargs)
        >>> dnest = _NestedDict(mapping, **kwargs)
        >>> dnest = _NestedDict(iterables, **kwargs)

    Arguments
    ---------
    mapping :
        (an)other dictionar(y)ies; optional.
    iterables :
        (an)other iterable object(s) in a form of key-value pair(s) where keys should 
        be immutable; optional.

    Keyword arguments
    -----------------
    order : list
        provides the depth order of the dimensions in the output dictionary;
        default: :data:`order` is :data:`None` and is ignored and the order
        of the dimensions in the output dictionary depends on their extraction
        as (key,value) items; unless the input :data:`dict` is an instance of 
        the :class:`collections.OrderedDict` class, it is highly recommended 
        to use this keyword argument.
    values : list,tuple
    _nested_ : dict
    
    Returns
    -------
    dnest : dict
        a empty nested dictionary whose (key,value) pairs are defined and
        ordered according to the arguments :data:`dic` and :data:`order`; say
        for instance that :data:`dic = {'dim1': 0, 'dim2': [1, 2]}, then:
            
            * :data:`happyType.mapnest(dic)` returns :data:`nestdic={0: {1: {}, 2: {}}}`. 
            * :data:`happyType.mapnest(dic, order=['dim2', 'dim1'])` returns :data:`nestdic={1: {0: {}}, 2: {0: {}}}`. 
    
    Examples
    --------
    
    Examples
    --------
    Note the initialisation that completely differs from a "normal" :obj:`dict`
    data structure:
        
        >>> dic = _NestedDict({'a': 1, 'b': 2})
        >>> dic
            {1: {2: {}}}
        >>> dic.order
            ['a', 'b']
        >>> dic.dimensions
            OrderedDict([('a', [1]), ('b', [2])])
        >>> dic = _NestedDict([('a',1),('b',2)])
        >>> dic
            {'a': {'b': {}, 2: {}}, 1: {'b': {}, 2: {}}}
        >>> dic.order
            [0, 1]
        >>> dic.dimensions
        
        >>> _NestedDict(a=1, b=2)
            {'a': 1, 'b': 2}
        
    However, in addition the data structure enables nested key settings, like adding a numeric key:
        
        >>> dic = {'a': [1,2], 'b': [3,4]}
        >>> _NestedDict(dic)
            {1: {3: {}, 4: {}}, 2: {3: {}, 4: {}}}
        >>> _NestedDict(dic, order = ['b', 'a'])
            {3: {1: {}, 2: {}}, 4: {1: {}, 2: {}}}
        >>> dic = collections.OrderedDict({'b': [3,4], 'a': [1,2]})
        >>> _NestedDict(dic)
            {3: {1: {}, 2: {}}, 4: {1: {}, 2: {}}}
        >>> _NestedDict(dic, values=[None])
            {3: {1: None, 2: None}, 4: {1: None, 2: None}}
        >>> _NestedDict(dic, values=[10,20,30,40])
            {3: {1: 10, 2: 20}, 4: {1: 30, 2: 40}}
                
    Note
    ----
    See also `Python` module :mod:`AttrDict` that handles complex dictionary data 
    structures (source available `here <https://github.com/bcj/AttrDict>`_).
    
    See also
    --------
    :meth:`happyType.ismapping`.
    """

    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        self.__order = []
        self.__xlen = {}
        # self.__dimensions = {}
        self.__cursor = 0
        self.__dimensions = {}
        if args in ((),({},),(None,)) and kwargs == {}:
            super(_NestedDict, self).__init__({})
            return
        order = kwargs.get(_Decorator.KW_ORDER) or True
        try:
            assert order is None or isinstance(order,bool) or happyType.issequence(order)
        except:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_ORDER.upper())            
        dic = kwargs.pop('_nested_', {})
        try:
            assert dic in (None,{}) or args in ((),(None,))
        except:
            raise happyError('incompatible positional arguments with _NESTED_ keyword argument')            
        if dic in (None,{}):
            try:
                dic, dimensions = self._deepcreate(*args, **kwargs)
            except:
                raise happyError('error creating nested dictionary')
        else:
            try:
                depth = max(list(self.__depth(dic).values()))
                ndim = len(order) if order is not None else depth
                dimensions = dict(zip(range(ndim), [[]]*len(range(ndim))))
            except:
                raise happyError('error setting nested dictionary')
        super(_NestedDict, self).__init__(dic)
        self.__dimensions = dimensions
        if order is not False:
            self.__order = order if order is not True else list(dimensions.keys())
        else:
            self.__order = [str(i) for i in range(len(dimensions))]
        self.__xlen = {k: len(v) if happyType.issequence(v) else 1 for k,v in dimensions.items()}
        values = kwargs.pop(_Decorator.KW_VALUES, None)
        if values is None:
            return
        elif not happyType.issequence(values):    
            values= [values,]
        try:
            assert len(values)==1 or len(values) == self.xlen()
        except:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_VALUES.upper())            
        else:
            if len(values)==1:      
                values = values * self.xlen()
        try:
            self.xupdate(*zip(self.xkeys(**{_Decorator.KW_FORCE_LIST: True}), values))
        except:
            raise happyError('error loading dictionary values')
            
    #/************************************************************************/
    def __getattr__(self, attr): 
        # ugly trick here... 
        if attr in inspect.getmembers(self.__class__, predicate=inspect.ismethod):#analysis:ignore
            return object.__getattribute__(self, attr)
        try:
            xkeys = self.xkeys(**{_Decorator.KW_FORCE_LIST: True})
            xvalues = [getattr(v, attr) for v in self.xvalues(**{_Decorator.KW_FORCE_LIST: True})]
            # res = [getattr(v, attr) for v in self.xvalues(**{_Decorator.KW_FORCE_LIST: True})]
        except:
            raise AttributeError('attribute %s not recognised' % attr)
        if len(xkeys)>1:
            try:
                cls = self.__class__
                res = cls(list(zip(xkeys, xvalues)))
            except:
                raise AttributeError('wrong nested data structure' % attr)
        else:
            res = xvalues if xvalues in ([],[None],None) or (happyType.issequence(xvalues) and len(xvalues)>1) \
            else xvalues[0]
        return res 
    
    #/************************************************************************/
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    #/************************************************************************/
    def __deepcopy__(self, memo):
        cls = self.__class__
        # return cls(copy.deepcopy(dict(self)), order=self.order)
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
    
    #/************************************************************************/
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                assert self.order == other.order
                #assert self.xkeys() == other.xkeys()
                #assert self.xvalues() == other.xvalues()
                assert self.__dict__ == other.__dict__
            except:
                return False
            else:
                return True
        else:
            return False

    #/************************************************************************/
    def __iter__(self):
        return self
    
    #/************************************************************************/
    def __next__(self):
        if self.__cursor >= self.xlen():
            self.__cursor = 0
            raise StopIteration
        _next = list(self.xvalues())[self.__cursor]
        self.__cursor += 1
        return _next

    #/************************************************************************/
    def __repr__(self):
        rep = super(_NestedDict, self).__repr__()
        try:
            assert False
            return rep.replace("'","\"") # does actually make no sense
        except:
            return rep
        
    #/************************************************************************/
    def __str__(self):
        if self.xlen() == 1:
            val = self.xvalues(**self.dimensions)
        if self.xlen() > 1 or val in (None,[],{},''):
            return super(_NestedDict, self).__str__()
        else:
            return "%s" % val

    #/************************************************************************/
    @property
    def order(self):
        # return list(self.__dimensions.keys())
        return self.__order

    @property
    def dimensions(self):
        """Dimensions property (:data:`getter`/:data:`setter`) of a :class:`_NestedDict`
        instance.
        """
        #ndim = len(self.order)
        #dic = dict(zip(range(ndim),[[]]*ndim))
        #def recurse(items, depth):
        #    for k, v in items:
        #        if dic[depth] in ([],None):     dic[depth] = [k,]
        #        else:                           dic[depth].append(k)
        #        dic[depth] = list(set(dic[depth]))
        #        if happyType.ismapping(v):
        #            recurse(v.items(), depth+1)
        #recurse(self.items(), 0)
        #return collections.OrderedDict((self.order[k],v) for k,v in list(dic.items()))
        return collections.OrderedDict({k : v[0] if happyType.issequence(v) and len(v)==1 else v    \
                                        for k,v in self.__dimensions.items()})
    @dimensions.setter
    def dimensions(self, dimensions):
        if not (dimensions is None or happyType.ismapping(dimensions)):
            raise happyError('wrong type for DIMENSIONS parameter')
        self.__dimensions = dimensions
        
    @classmethod
    @happyDeprecated('use depth property instead', run=True)
    def __depth(self, dic):
        depth = {}
        def recurse(v, i):
            if happyType.ismapping(v):
                yield from recurse(v.values(), i+1)
            else:
                yield i
        depth.update({k: list(recurse(v, 1))[0] for k,v in dic.items()})
        return depth

    @property
    def depth(self):
        # return len(self.dimensions) #-1
        return len(self.order) #-1

    #/************************************************************************/
    @classmethod
    def _deepcreate(cls, *args, **kwargs):
        """Initialise a deeply nested dictionary from input (dimension,key) pairs
        parsed as dictionary or list, or (key,value) pairs parsed as a list of 
        items.
        
            >>> new_dnest, dimensions = _NestedDict._deepcreate(*args, **kwargs)
            
        Arguments
        ---------
        
        Keyword arguments
        -----------------
        
        Returns
        -------
        new_dnest : dict
        dim : collections.OrderedDict
        
        Examples
        --------
        it is useful to initialise a data structure as an empty nested dictionary:
        
            >>> _NestedDict._deepcreate(a=1, b=2)
                ({1: {2: {}}}, 
                OrderedDict([('a', 1), ('b', 2)]))
            >>> d = {'a': [1,2], 'b': [3,4,5]}
            >>> _NestedDict._deepcreate(d)
                ({1: {3: {}, 4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}},
                 OrderedDict([('a', [1, 2]), ('b', [3, 4, 5])]))
            >>> _NestedDict._deepcreate(d, order=['b','a'])
                ({3: {1: {}, 2: {}}, 4: {1: {}, 2: {}}, 5: {1: {}, 2: {}}},
                 OrderedDict([('b', [3, 4, 5]), ('a', [1, 2])]))
            >>> l1 = (('a',[1,2]), ('b',[3,4,5]))
            >>> _NestedDict._deepcreate(l1)
                ({1: {3: {}, 4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}},
                 OrderedDict([('a', [1, 2]), ('b', [3, 4, 5])]))
            >>> _NestedDict._deepcreate(l1, order=['b','a'])
                ({3: {1: {}, 2: {}}, 4: {1: {}, 2: {}}, 5: {1: {}, 2: {}}},
                 OrderedDict([('b', [3, 4, 5]), ('a', [1, 2])]))
            >>> l2 = ([1,2], [3,4,5])
            >>> _NestedDict._deepcreate(l2)
                ({1: {3: {}, 4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}},
                 OrderedDict([(0, [1, 2]), (1, [3, 4, 5])])) 
                
        while it is also possible to fill it in with values:
            
            >>> items = [(('a',1,'x'), 1), (('a',2,'y'), 2),
                         (('b',1,'y'), 3), (('b',2,'z'), 4),
                         (('b',1,'x'), 5)]
            >>> _NestedDict._deepcreate(items)
                ({'a': {1: {'x': 1}, 2: {'y': 2}}, 'b': {1: {'x': 5, 'y': 3}, 2: {'z': 4}}},
                 OrderedDict([(0, ['a', 'b']), (1, [1, 2]), (2, ['y', 'z', 'x'])])
        
        See also
        --------
        :meth:`~_NestedDict._deepmerge`, :meth:`~_NestedDict._deepinsert`.
        """
        order = kwargs.pop(_Decorator.KW_ORDER, None)
        try:
            assert order is None or isinstance(order, bool) or happyType.issequence(order)
        except:
            raise happyError('wrong type/value for %s keyword argument' % _Decorator.KW_ORDER.upper())
        if args in ((),(None,)):
            if kwargs == {}:
                return collections.OrderedDict()
            else:
                args = kwargs.items()
        try:
            assert (len(args)==1 and happyType.ismapping(args[0]))          \
                or all([happyType.issequence(a) for a in args])
        except:
            raise happyError('wrong format for input arguments')
        else:
            if len(args)==1: # and, obviously: happyType.ismapping(args[0])) 
                args = args[0]
        try:
            assert not happyType.ismapping(args) or all([happyType.issequence(v) for v in args.values()])
        except:
            raise happyError('wrong format for input nesting dictionary - impossible to resolve dimension ambiguity without []')
        #if happyType.ismapping(args):
        #    if order is True:
        #        order =  list(args.keys())
        #    if order is not None:
        #        args = sorted(args.items(), key = lambda t: order.index(t[0]))
        #    args = collections.OrderedDict(args)
        #    if order is None and order is not False: # that should actually never happen at this stage
        #        order =  list(args.keys())
        #    [args.update({k: [v,] for k,v in args.items() if not happyType.issequence(v)})]            
        #    value = {} # None
        #    dimensions = collections.OrderedDict(dict(zip(order,[None]*len(order))))
        #    try:
        #        for attr in order[::-1]:
        #            argattr = args[attr]
        #            if type(argattr)==tuple:    argattr = list(argattr)
        #            dic = {a: copy.deepcopy(value) for a in argattr} 
        #            dimensions.update({attr: argattr.copy()})
        #            value = dic
        #    except TypeError:
        #        raise happyError('input dictionary argument not supported')
        #elif all([happyType.issequence(a[0]) for a in args]):  
        #    if order is None or isinstance(order,bool):
        #        order = list(range(len(args[0][0])))
        #    attrs = [list(set(a[0][i] for a in args)) for i in range(len(order))]
        #    dimensions = dict(zip(order, attrs))
        #    if order is not False:
        #        dimensions = collections.OrderedDict(dimensions)
        #    dic = {}
        #    try:
        #        for item in args:
        #            d = {item[0][-1]: item[1]}
        #            for key in item[0][:-1][::-1]:
        #                d = {key: d.copy()}
        #            cls._deepmerge(dic, d, in_place=True)
        #    except TypeError:
        #        raise happyError('input item arguments not supported')
        #try:
        #    assert dic
        #except:
        #    dic, dimensions = {}, {}
        #return dic, dimensions   
        if happyType.ismapping(args):
            args = list(args.items())
        if not all([len(a)==2 for a in args]):
            args = [(str(i),a) for i,a in enumerate(args)]
        if all([happyType.issequence(a[0]) for a in args]):
            if order is None or isinstance(order,bool):
                order = [str(i) for i in range(len(args[0][0]))]
            dimensions = collections.OrderedDict(zip(order, 
                              [list(set(v)) for v in zip(*[a[0] for a in args])]))
        else: 
            dimensions = collections.OrderedDict(args)
            if order is None:
                order = [a[0] for a in args]
            try:
                keys = list(itertools.product(*[item[1] for item in args]))
            except:
                try:
                    keys = list(itertools.product(*[[item[1]] for item in args]))
                except:
                    keys = list(itertools.product(*args[1]))                    
            args = list(zip(keys, [{}] * len(keys)))
        return cls._deepinsert({}, args), dimensions
        
    #/************************************************************************/
    @classmethod
    def _deepmerge(cls, *dics, **kwargs):
        """Deep merge (recursively) an arbitrary number of (nested or not) dictionaries.
    
            >>> new_dnest = _NestedDict._deepmerge(*dics, **kwargs)
            
        Arguments
        ---------
        dics : dict
            an arbitrary number of (possibly nested) dictionaries.
            
        Keyword arguments
        -----------------
        in_place : bool
            flag set to update the first dictionary from the input list :data:`dicts`
            of dictionaries; default: :data:`in_place=False`.

        Returns
        -------
        new_dnest : dict
            say that only two dictionaries are parsed, :data:`d1` and :data:`d2`
            through :data:`dics` (in this order); first, :data:`d1` is "deep"-copied 
            into :data:`new_dnest` (we consider the default case :data:`in_place=False`), 
            then for each :data:`k,v` in :data:`d2`: 
                
                * if :data:`k` doesn't exist in :data:`new_dnest`, it is deep copied 
                  from :data:`d2` into :data:`new_dic`;
            
            otherwise: 
                
                * if :data:`v` is a list, :data:`new_dnest[k]` is extended with :data:`d2[k]`,
                * if :data:`v` is a set, :data:`new_dnest[k]` is updated with :data:`v`,
                * if :data:`v` is a dict, it is recursively "deep"-updated,
    
        Examples
        --------
        The method can be used to deep-merge dictionaries storing many different
        data structures:

            >>> d1 = {1: 2, 3: 4, 10: 11}
            >>> d2 = {1: 6, 3: 7}
            >>> _NestedDict._deepmerge(d1, d2)
                {1: [2, 6], 3: [4, 7], 10: 11}
            >>> d1 = {1: 2, 3: {4: {5:6, 7:8}, 9:10}, 11: 12}
            >>> d2 = {1: -2, 3: {4: {-5:{-6:-7}}}, 8:-9}
            >>> _NestedDict._deepmerge(d1, d2)
                {1: [2, -2], 3: {4: {-5: {-6: -7}, 5: 6, 7: 8}, 9: 10}, 8: -9, 11: 12}
            >>> d1 = {'a': {'b': {'x': '1', 'y': '2'}}}
            >>> d2 = {'a': {'c': {'gg': {'m': '3'},'xx': '4'}}}
            >>> _NestedDict._deepmerge(d1, d2, in_place = True)
            >>> print(d1)
                {'a': {'b': {'x': '1','y': '2'}, 'c': {'gg': {'m': '3'}, 'xx': '4'}}}
                
        Note
        ----
        This code is adapted from F.Boender's original source code available at
        `this address <https://www.electricmonk.nl/log/2017/05/07/merging-two-python-dictionaries-by-deep-updating/>`_
        under a *MIT* license.
        
        See also
        --------
        :meth:`~_NestedDict._deepcreate`, :meth:`~_NestedDict._deepinsert`,
        :meth:`~_NestedDict.xupdate`.
        """ 
        in_place = kwargs.pop('in_place', False)
        try:
            assert isinstance(in_place, bool)
        except:
            raise happyError('wrong format/value for IN_PLACE keyword argument')
        try:
            assert all([happyType.ismapping(dic) for dic in dics])
        except:
            raise happyError('wrong format/value for input arguments')
        def recurse(target, src):
            for k, v in src.items():
                #if happyType.issequence(v):  
                #    if k in target:         target[k].extend(v)
                #    else:                   target[k] = copy.deepcopy(v)
                #elif happyType.ismapping(v):  
                #    if k in target:         recurse(target[k], v)
                #    else:                   target[k] = copy.deepcopy(v)
                #elif type(v) == set:
                #    if k in target:         target[k].update(v.copy())
                #    else:                   target[k] = v.copy()
                #else:
                #    if k in target:     
                #        if type(target[k]) == tuple:        target.update({k: list(target[k])})
                #        elif not type(target[k]) == list:   target[k] = [target[k],]
                #        target[k].append(v)
                #    else:
                #        target[k] = copy.copy(v)
                if k in target:     
                    if type(v)!=type(target[k]):
                        if type(target[k]) == tuple:        
                            target.update({k: list(target[k])})
                        elif type(target[k]) != list:   
                            target[k] = [target[k],]    
                    elif not(happyType.ismapping(target[k]) or happyType.issequence(target[k])):
                        target[k] = [target[k],]                        
                #elif type(v)!=type(target[k]):              target[k] = []
                if happyType.issequence(v): 
                    if k in target:                         
                        try:
                            target[k].extend(v)
                        except:
                            target[k] = target[k] + v
                    else:                                   
                        target[k] = copy.deepcopy(v)
                elif happyType.ismapping(v):  
                    if k in target:         
                        recurse(target[k], v)
                    else:                   
                        target[k] = copy.deepcopy(v)
                elif type(v) == set:
                    if k in target:                         
                        try:
                            target[k].update(v.copy())
                        except:
                            target[k].append(v)
                    else:                                   
                        target[k] = v.copy()
                else:
                    if k in target:                         
                        target[k].append(v)
                    else:
                        try:
                           target[k] = copy.copy(v)   
                        except:
                            target[k] = v
        def reduce(*dics):
            if in_place is False:
                dd = copy.deepcopy(dics[0])
                functools.reduce(recurse, (dd,) + dics[1:])
            else:
                dd = None
                functools.reduce(recurse, dics)
            return dd # or dicts[0]
        return reduce(*dics)

    #/************************************************************************/
    @classmethod
    def _deepinsert(cls, dic, *items, **kwargs):
        """Deep merge (recursively) a (nested or not) dictionary with items.
    
            >>> new_dnest = _NestedDict._deepinsert(dic, *items, **kwargs)
            
        Arguments
        ---------
        dic : dict
            a (possibly nested) dictionary.
        items : tuple,list
            items of the form :literal:`(key,value)` pairs
            
        Keyword arguments
        -----------------
        in_place : bool
            flag set to update the first dictionary from the input list :data:`dicts`
            of dictionaries; default: :data:`in_place=False`.

        Returns
        -------
        new_dnest : dict
            
        Examples
        --------
        First simple examples:
            
            >>> _NestedDict._deepinsert({}, (1,2))
                {1: 2}
            >>> _NestedDict._deepinsert({}, (1,2), (3,4))
                {1: 2, 3: 4}
            >>> _NestedDict._deepinsert({}, ((1,2),(3,4)))
                {1: {2: (3, 4)}}                
            >>> _NestedDict._deepinsert({}, ((1, 2), 3), ((4, 5), 6))
                {1: {2: 3}, 4: {5: 6}}
        
        Note the various way/syntax items can be parsed, and the different possible 
        outputs:
            
            >>> _NestedDict._deepinsert({}, (1,2), (1,3) )
                {1: 3} # the last inserted
            >>> _NestedDict._deepinsert({}, (1,2), (3,(4,5)) )
                {1: 2, 3: (4, 5)}
            >>> _NestedDict._deepinsert({}, (1,2), ((3,4),5) )
                {1: 2, 3: {4: 5}}
            >>> _NestedDict._deepinsert({}, ((1,2)), (3,(4,5)) )
                {1: 2, 3: (4, 5)}
            >>> _NestedDict._deepinsert({}, (((1,2)), (3,(4,5))) )
                {1: {2: (3, (4, 5))}}
            >>> _NestedDict._deepinsert({}, (((1,2)), (3,4)), (5,6))
                {1: {2: (3, 4)}, 5: 6}
            >>> _NestedDict._deepinsert({}, (1,(2,(3,4),(5,6),7)) )
                {1: (2, (3, 4), (5, 6), 7)}

        The method can be used to deep-insert items into a (possibly nested) dictionary
        data structure:

            >>> d = {1: 6, 3: 7, 10: 11}
            >>> items = ((1,2), (3,4))
            >>> _NestedDict._deepinsert(d, items)
                {1: {2: (3, 4)}, 3: 7, 10: 11}
            >>> _NestedDict._deepinsert(d, *items)
                1: 2, 3: 4, 10: 11}
            >>> items2 = ((1,2), ((3,4,5),6), ((3,4,7),8), ((3,4,9),10), (11,12))
            >>> d2 = {1: -2, 3: {4: {-5:{-6:-7}}}, 8:-9}
            >>> _NestedDict._deepinsert(d2, *items2)
                {1: 2, 3: {4: {-5: {-6: -7}, 5: 6, 7: 8, 9: 10}}, 8: -9, 11: 12}
        
        The keyword argument :data:`in_place` can be used for in-place update:
            
            >>> items = ((1,2), (3,(4,5)))
            >>> d = {}
            >>> _NestedDict._deepinsert(d, items, in_place=True)
            >>> print(d)
                {1: {2: (3, (4, 5))}}
            >>> d = {}
            >>> _NestedDict._deepinsert(d, *items, in_place=True)
            >>> print(d)
                {1: 2, 3: (4, 5)}
            >>> items = [(('a',1,'x'), 1), (('a',2,'y'), 2),
                         (('b',1,'y'), 3), (('b',2,'z'), 4),
                         (('b',1,'x'), 5)]
            >>> d = {}
            >>> _NestedDict._deepinsert(d, items, in_place=True)
            >>> print(d)
                {'a': {1: {'x': 1}, 2: {'y': 2}}, 'b': {1: {'x': 5, 'y': 3}, 2: {'z': 4}}}
        
        See also
        --------
        :meth:`~_NestedDict._deepcreate`, :meth:`~_NestedDict._deepmerge`, 
        :meth:`~_NestedDict.xupdate`.
        """
        in_place = kwargs.pop('in_place', False)
        try:
            assert isinstance(in_place, bool)
        except:
            raise happyError('wrong format/value for IN_PLACE keyword argument')
        try:
            assert happyType.ismapping(dic) and all([happyType.issequence(item) for item in items])
        except:
            raise happyError('wrong format/value for input arguments')
        # we speculate a lot here... probably not the best way...
        if len(items)==1:
            if not(happyType.issequence(items[0]) and len(items[0])==2)     \
                    or all([happyType.issequence(i) and happyType.issequence(i[0]) for i in items[0]]):
                items = items[0]
            else:
                pass
        try:
            assert len(items)==2 or all([len(item)==2 for item in items])
        except:
            raise happyError('wrong format/value for item arguments')
        def recurse(target, src):
            key, v = src
            k = key[0] if happyType.issequence(key) else key
            if happyType.issequence(key) and len(key)>1: 
                if k not in target:         
                    target[k] = None
                if not happyType.ismapping(target[k]):
                    #if type(target[k]) == tuple:        target.update({k: list(target[k])})
                    #elif not type(target[k]) == list:   target[k] = [target[k],]
                    temp = {}
                    recurse(temp, (key[1:],v))
                    target[k] = temp                    
                else:    
                    recurse(target[k], (key[1:],v))
            else:
                #if k in target:     
                #    if type(v)!=type(target[k]):
                #        if type(target[k]) == tuple:        
                #            target.update({k: list(target[k])})
                #        elif not type(target[k]) == list:   
                #            target[k] = [target[k],]    
                #    elif not(happyType.ismapping(target[k]) or happyType.issequence(target[k])):
                #        target[k] = [target[k],]                        
                ##elif type(v)!=type(target[k]):              target[k] = []
                if happyType.issequence(v): 
                    target[k] = v #copy.deepcopy(v)
                elif happyType.ismapping(v):  
                    target[k] = copy.deepcopy(v)
                elif type(v) == set:
                    target[k] = v.copy()
                else:
                    try:
                       target[k] = copy.copy(v)   
                    except:
                        target[k] = v
        dd = None
        if in_place is False:
            dd = copy.deepcopy(dic)
        for item in items:
            recurse(dd if dd is not None else dic, item)
        return dd 

    #/************************************************************************/
    def _deepsearch(self, attr, *arg, **kwargs):
        """
        """
        try:
            assert attr in ('get', 'keys', 'dimensions', 'values')
        except:
            raise happyError('wrong parsed attribute')
        try:
            assert self.order is not None
        except:
            raise happyError('dimensions not supported with unordered dictionary')
        try:
            assert set(kwargs.keys()).difference(set(self.order)) == set()
        except:
            raise happyError('parsed dimensions are not recognised')  
        order = self.order.copy()
        if attr == 'keys':
            if arg not in ((),([],),(None,)):
                dic = dict(self.items())
                for dim in order:
                    if dim!=arg[0]:        dic = list(dic.values())[0]
                    else:                   break
                return list(dic.keys())
            else:
                pass
        elif attr == 'get':
            while True:
                if order[-1] not in kwargs.keys():
                    order.pop(-1)
                else:
                    break
        else:
            pass
        val = [self.copy()] 
        for i, dim in enumerate(order):
            val = happyType.seqflatten([list(v.items()) for v in val])
            if dim in kwargs.keys():
                keys = kwargs.get(dim)
                if not happyType.issequence(keys):
                    keys = [keys,]
                [val.remove(v) for v in list(val) if v[0] not in keys]
            if attr == 'keys' and i == len(order)-1:
                val = [v[0] for v in val]
            else:
                val = [v[1] for v in val]
        return val[0] if happyType.issequence(val) and len(val)==1 else val
    
    #/************************************************************************/
    @classmethod
    @happyDeprecated('use generic method _deepmerge instead', run=True)
    def __nestmerge(cls, *dicts):
        #ignore-doc
        """Recursively merge an arbitrary number of nested dictionaries.
    
            >>> new_dnest = _NestedDict.__nestmerge(*dicts)
            
        Arguments
        ---------
        dicts : dict
            an arbitrary number of (possibly nested) dictionaries.
    
        Examples
        --------

            >>> d1 = {'a': {'b': {'x': '1', 'y': '2'}}}
            >>> d2 = {'a': {'c': {'gg': {'m': '3'},'xx': '4'}}}
            >>> happyType.__nestmerge(d1, d2)
                {'a': {'b': {'x': '1','y': '2'}, 'c': {'gg': {'m': '3'}, 'xx': '4'}}}
        """    
        keys = set(k for d in dicts for k in d)    
        def vals(key):
            withkey = (d for d in dicts if key in d.keys())
            return [d[key] for d in withkey]    
        def recurse(*values):
            if isinstance(values[0], dict):
                return cls.__nestmerge(*values)
            if len(values) == 1:
                return values[0]
            raise happyError("Multiple non-dictionary values for a key.")    
        return dict((key, recurse(*vals(key))) for key in keys)  
            

    #/************************************************************************/
    @classmethod
    def _deepreorder(cls, dic, **kwargs):
        """Reorder a deeply nested dictionary.
        
            >>> new_dnest = _NestedDict._deepreorder(dic, **kwargs)
            
        Example
        -------
        
            >>> d = {'a': [1,2], 'b': [3,4,5]}
            >>> r = _NestedDict(d, values = list(range(6)))
            >>> print(r)
                {1: {3: 0, 4: 1, 5: 2}, 2: {3: 3, 4: 4, 5: 5}}
            >>> _NestedDict._deepreorder(r, order= ['b', 'a'])
                {3: {1: 0, 2: 3}, 4: {1: 1, 2: 4}, 5: {1: 2, 2: 5}}
            >>> _NestedDict._deepreorder(r, order= ['b', 'a'], in_place=True)
            >>> print(r)
                {3: {1: 0, 2: 3}, 4: {1: 1, 2: 4}, 5: {1: 2, 2: 5}}
        """
        in_place = kwargs.pop('in_place', False)
        try:
            assert isinstance(in_place, bool)
        except:
            raise happyError('wrong format/value for IN_PLACE keyword argument')
        try:
            assert happyType.ismapping(dic)
        except:
            raise happyError('wrong type/value for input argument')
        order = kwargs.pop(_Decorator.KW_ORDER, None)
        try:
            assert order is None or isinstance(order,bool) or happyType.issequence(order)
        except:
            raise happyError('wrong type/value for %s keyword argument' % _Decorator.KW_ORDER.upper())
        else:
            if order is None:
                happyVerbose('nothing to do')
                return dic
        try:
            inorder = getattr(dic, _Decorator.KW_ORDER)
        except AttributeError:
            inorder = list(dic.keys())
        try:
            assert set(order) == set(inorder) # assert set(order).difference(set(inorder)) == set()
        except:
            raise happyError('keys parsed as %s keyword argument not present in input dictionary' % _Decorator.KW_ORDER.upper())
        else:
            if order == inorder:
                happyVerbose('new order key equal to the original one')
                return dic
        xkeys, xvalues = dic.xkeys(), dic.xvalues()
        newxkeys = [sorted(key, key=lambda x: order.index(inorder[key.index(x)])) for key in xkeys]
        # new_xitems = [(sorted(item[0], key=lambda t: order.index(inorder[item[0].index(t)])), item[1]) for item in xitems]
        newxitems = zip(newxkeys, xvalues)
        if in_place is True:
            # dic = _NestedDict(newxitems, order = order) 
            [dic.pop(k) for k in list(dic.keys())]
            # [dic.xpop(k) for k in xkeys]
            dic.xupdate(list(newxitems))
            try:
                dic.order = order # let's make sure this works with any derived class
            except:
                try:
                    setattr(dic, '_NestedDict__order', order) # let's make sure this works with any derived class
                except:
                    pass
            return
        else:
            return cls(list(newxitems), order = order)   

    #/************************************************************************/
    @classmethod
    def _deepest(cls, dic, item='values'):
        """Extract the deepest keys, values or both (items) from a nested dictionary.
            
            >>> l = _NestedDict._deepest(dic, item='values')
            
        Arguments
        ---------
        dic : dict
            a (possibly nested) dictionary.
            
        Keyword arguments
        -----------------
        item : str
            flag used to define the deepest items to extract from the input dictionary
            :data:`dic`; it can be :literal:`keys`, :literal:`values` or :literal:`items`
            to represent both; default is :literal:`values`, hence the deepest values
            are extracted.

        Returns
        -------
        l : list
            contains the deepest keys, values or items extracted from :data:`dic`,
            depending on the keyword argument :data:`item`.
    
        Examples
        --------
            
            >>> d = {4:1, 6:2, 7:{8:3, 9:4, 5:{10:5}, 2:6, 6:{2:7, 1:8}}}
            >>> _NestedDict._deepest(d)
                [1, 2, 3, 4, 5, 6, 7, 8]
            >>> _NestedDict._deepest(d, item='keys')
                [4, 6, 8, 9, 10, 2, 2, 1]
            >>> _NestedDict._deepest(d, item='items')
                [(4, 1), (6, 2), (8, 3), (9, 4), (10, 5), (2, 6), (2, 7), (1, 8)]
        """
        try:
            assert happyType.ismapping(dic) 
        except:
            raise happyError('wrong format/value for input argument')
        try:
            assert item in (None,'') or item in ('items','keys','values')
        except:
            raise happyError('wrong format/value for ITEM argument')
        if isinstance(dic, cls):
            depth = dic.depth
        else:
            depth = -1
        def recurse(d, inc):
            for k, v in d.items():
                if depth>0 and inc<depth and happyType.ismapping(v) and v!={}:
                    yield from recurse(v, inc+1)
                else:
                    if item=='items':           yield (k, v)
                    elif item=='keys':          yield k
                    elif item=='values':        yield v
        return list(recurse(dic, 1))
    
    #/************************************************************************/
    def xget(self, *args, **kwargs):
        """Retrieve value from deep nested dictionary.
        
            >>> val = dnest.xget(*args, **kwargs)
        
        Examples
        --------
        """
        __force_list = kwargs.pop(_Decorator.KW_FORCE_LIST, False)
        if args in ((),(None,)) and kwargs=={}:
            return self._deepest(self, item='values')
        if args!=():
            if len(args)>1 or happyType.issequence(args[0]):
                if len(args)==1:    args = args[0]
                kwargs.update({k: v for k,v in zip(self.order, args)})
        if kwargs == {}:
            return super(_NestedDict, self).get(*args)
        # let us check the complexive lenght of the dimensions that have been left out
        xlen = self.xlen(list(set(self.order).difference(set(kwargs))))
        if happyType.ismapping(xlen):
            xlen = functools.reduce(lambda x, y: x*y, xlen.values())
        def deep_get(dic):
            rdic = copy.deepcopy(dic)
            while happyType.ismapping(rdic):
                rdic = list(rdic.values())[0]
            return rdic
        res = self._deepsearch('get', *args, **kwargs)
        return res if __force_list is True or res is None or xlen>1 else deep_get(res)

    #/************************************************************************/
    def pop(self, *args):
        """
        """
        if args in ((),(None,)):
            raise TypeError('pop expected at least 1 arguments, got 0')
        key = args[0]
        dimensions, order = self.dimensions, self.order
        order = order or [str(i) for i in range(len(dimensions))]
        try:
            dimensions[order[0]].remove(key)
        except:
            dimensions[order[0]] = set([dimensions[order[0]]]).difference(set([key]))
        #.update({order[0]: list(dimensions[order[0]]).remove(key)})
        if dimensions[order[0]] == []:
            dimensions = collections.OrderedDict()
        super(_NestedDict,self).pop(*args)
        
    #/************************************************************************/
    def xpop(self, *arg):
        """Pop values out of deep nested dictionary.
        
            >>> dnest.xpop(*arg)
        
        Examples
        --------
        
            >>> d = {'a': [1,2], 'b': [3,4,5]}
            >>> r = _NestedDict(d)
            >>> print(r)
                {1: {3: {}, 4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}}
            >>> r.xpop([1,3])
                {}
            >>> print(r)
                {1: {4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}}
        """
        try:
            assert len(arg)==1 and (happyType.isnumeric(arg[0]) or happyType.issequence(arg[0]))
        except:
            raise happyError('wrong format/value for ITEM to delete')
        else:
            arg = arg[0]
            if not happyType.issequence(arg):
                arg = [arg,]
        d = self
        try:
            for i, item in enumerate(arg):
                if i<len(arg)-1:     d = d[item]
        except KeyError:
            raise happyError('deep keys not known')
        dimensions, order = self.dimensions, self.order
        if dimensions != {}:
            order = order or [str(i) for i in range(len(dimensions))]
            for i, item in enumerate(arg[::-1]):
                if dimensions[order[i]] == [arg]:
                    dimensions.pop(arg)
                    order.remove(arg)
                else:
                    break
        return d.pop(item)

    #/************************************************************************/
    def update(self, *arg, **kwargs):
        newkeys = []
        if arg not in ((),(None,)):
            newkeys += list(arg[0].keys())
        if kwargs != {}:
            newkeys += list(kwargs.keys())
        dimensions, order = self.dimensions, self.order
        order = order or [str(i) for i in range(len(dimensions))]
        try:
            assert set(newkeys).difference(set(dimensions[order[0]])) == set()
        except:
            self.dimensions.update({order[0]: list(set(dimensions[order[0]] + newkeys))})
        super(_NestedDict,self).update(*arg, **kwargs)

    #/************************************************************************/
    def xupdate(self, *arg, **kwargs):
        """Update a deep nested dictionary.
        
            >>> dnest.xupdate(*arg, **kwargs)
        
        Examples
        --------
        
            >>> d = {'a': [1,2], 'b': [3,4,5]}
            >>> r = _NestedDict(d)
            >>> print(r)
                {1: {3: {}, 4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}}
            >>> r.xupdate(((1,3),5))
            >>> print(r)
                {1: {3: 5, 4: {}, 5: {}}, 2: {3: {}, 4: {}, 5: {}}}
            >>> r.xupdate(((1,4),10), ((2,4),15))
            >>> print(r)
                {1: {3: 5, 4: 10, 5: {}}, 2: {3: {}, 4: 15, 5: {}}}
            >>> r.xupdate(20, a=2, b=3)
            >>> print(r)
                {1: {3: 5, 4: 10, 5: {}}, 2: {3: 20, 4: 15, 5: {}}}
                
            >>> d = _NestedDict()
            >>> items = ((1,2), (3,(4,5)))
            >>> d.xupdate(items)
            >>> print(d)
                {1: 2, 3: (4, 5)}
            >>> d = _NestedDict()
            >>> items = [(('a',1,'x'), 1), (('a',2,'y'), 2),
                        (('b',1,'y'), 3), (('b',2,'z'), 4),
                        (('b',1,'x'), 5)]
            >>> d.xupdate(items)
            >>> print(d)
                {'a': {1: {'x': 1}, 2: {'y': 2}}, 'b': {1: {'x': 5, 'y': 3}, 2: {'z': 4}}}
            
        """
        if arg in((),(None,)) and kwargs == {}:
            return 
        try:
            len(arg) == 1 or len(arg)==2
        except:
            raise happyError('wrong type/value for input argument')
        try:
            assert kwargs == {} or not happyType.ismapping(arg) 
        except:
            raise happyError('no keyword argument requested with input dictionary argument')
        try:
            assert kwargs != {} or happyType.issequence(arg) 
        except:
            raise happyError('items and keyword arguments incompatible when updating')                    
        #if kwargs == {}:
        #    try:
        #        xkeys = [a[0] for a in arg]
        #        xvalues = [a[1] for a in arg]
        #    except:
        #        xkeys, xvalues = arg  
        #    else:
        #        if len(xkeys)==1:
        #            xkeys, xvalues = xkeys[0], xvalues[0]
        #else:
        #    kwargs.update({_Decorator.KW_FORCE_LIST: True})
        #    xkeys = self.xkeys(**kwargs)
        #    xvalues = arg
        #if not happyType.issequence(xvalues):
        #    xkeys, xvalues = [xkeys,], [xvalues,] 
        #try:
        #    assert (len(xvalues)==1 or len(xvalues)==len(xkeys))            \
        #        and all([len(k)==len(self.order) for k in xkeys])
        #except:
        #    raise happyError('wrong number of assignments in dictionary')
        #else:
        #    if len(xvalues)==1 and len(xkeys)>1:
        #        xvalues = xvalues * len(xkeys)
        #for i, xk in enumerate(xkeys):
        #    rdic = self
        #    try:    
        #        for j, x in enumerate(xk):
        #            if j<len(xk)-1:     rdic = rdic[x]
        #    except:
        #        raise happyError('key %s not found' % x)
        #    else:
        #        rdic.update({x: xvalues[i]})
        dimensions, order= self.dimensions.copy(), self.order
        if kwargs != {}:
            kwargs.update({_Decorator.KW_FORCE_LIST: True})
            arg = list(zip(self.xkeys(**kwargs),arg)) 
        if happyType.issequence(arg): 
            if len(arg)==1:
                arg = arg[0]
            try:
                keys = zip(*[a[0] for a in arg])
            except: 
                try:
                    keys = [[a[0]] for a in arg]
                except:
                    keys = arg[0]
            else:
                keys = [list(set(k)) for k in keys]
            if order is None or dimensions == {}:
                dimensions = collections.OrderedDict([(str(i),k) for i,k in enumerate(keys)])
            else:
                dimensions = collections.OrderedDict(zip(dimensions.keys(),
                                                         list(dimensions.values()) + list(keys)))
            self._deepinsert(self, arg, in_place=True)
        elif happyType.ismapping(arg):
            if isinstance(arg,self.__class__):
                [dimensions.update({k: dimensions.get(k,[])+v}) for k,v in arg.items()]
            # elif isinstance(arg,(dict,collections.OrderedDict)): pass
            self._deepmerge(self, arg, in_place=True)        
        self.dimensions = dimensions
        return

    #/************************************************************************/
    def keys(self, *arg, **kwargs):
        """Retrieve deepest (outmost) keys from a nested dictionary.
        
            >>> keys = dnest.keys(**kwargs)
        """
        try:
            assert arg in ((),([],),(None,)) or kwargs == {}
        except:
            raise happyError('both argument or keyword arguments cannot be accepted simultaneously')
        if arg in ((),([],),(None,)) and kwargs == {}:
            return super(_NestedDict, self).keys()
        else:
            return self._deepsearch('keys', *arg, **kwargs)

    #/************************************************************************/
    def xkeys(self, **kwargs):
        """Retrieve composed nested keys from a nested dictionary.
        
            >>> keys = dnest.xkeys(**kwargs)
            
        Examples
        --------
        
            >>> dic = {'a': [1,2], 'b': [3,4,5], 'c':[6,7,8,9]}
            >>> res = _NestedDict(dic, order = ['b', 'c', 'a'])
            >>> res.xkeys()
                [(3, 6, 1), (3, 6, 2), (3, 7, 1), (3, 7, 2), (3, 8, 1), (3, 8, 2), (3, 9, 1), (3, 9, 2),
                 (4, 6, 1), (4, 6, 2), (4, 7, 1), (4, 7, 2), (4, 8, 1), (4, 8, 2), (4, 9, 1), (4, 9, 2),
                 (5, 6, 1), (5, 6, 2), (5, 7, 1), (5, 7, 2), (5, 8, 1), (5, 8, 2), (5, 9, 1), (5, 9, 2)]
            >>> res.xkeys(c=7)
                [(3, 7, 1), (3, 7, 2), (4, 7, 1), (4, 7, 2), (5, 7, 1), (5, 7, 2)]
            >>> res.xkeys(c=7, a=2)
                [(3, 7, 2), (4, 7, 2), (5, 7, 2)]
        """
        #if kwargs=={}:
        #    return self._deepest(self, item='keys')
        __force_list = kwargs.pop(_Decorator.KW_FORCE_LIST, False)
        try:
            assert set(kwargs.keys()).difference(set(self.order)) == set()
        except:
            raise happyError('parsed dimensions are not recognised')  
        dimensions = [[dim] if not happyType.issequence(dim) else dim
                      for dim in [self.dimensions[k] for k in self.order]]
        xkeys = list(itertools.product(*dimensions))
        if xkeys in ([],[None,]):
            return []
        if kwargs != {}:
            for i, dim in enumerate(self.order):
                if dim in kwargs.keys():
                    keys = kwargs.get(dim)
                    if not happyType.issequence(keys):
                        keys = [keys,]
                    [xkeys.remove(k) for k in list(xkeys) if k[i] not in keys]
        return xkeys if __force_list is True or xkeys in ([],None) or len(xkeys)>1 else xkeys[0]
    
    #/************************************************************************/
    def values(self, *arg, **kwargs):
        """Retrieve (outmost) end-values of nested dictionary.
        
            >>> values = dnest.values(*arg, **kwargs)
        """
        try:
            assert arg in ((),([],),(None,)) or kwargs == {}
        except:
            raise happyError('both argument or keyword arguments cannot be accepted simultaneously')
        try:
            assert arg in ((),([],),(None,)) or happyType.issequence(arg[0])
        except:
            raise happyError('wrong format/values for input argument')
        if arg != ():
            kwargs.update({k: v for k,v in zip(self.order, arg[0])})
        if kwargs == {}:
            return super(_NestedDict, self).values()
        return self._deepsearch('values', **kwargs)
    
    #/************************************************************************/
    def xvalues(self, **kwargs):
        """Retrieve nested values of nested dictionary.
        
            >>> values = dnest.xvalues(*arg, **kwargs)
            
        Examples
        --------
        
            >>> dic = {'a':[1,2], 'b':[4,5]}
            >>> ord = ['a', 'b']
            >>> val = [{1:{2:3}}, {4:{5:6}, 7:{8:{9:10}}}, [11,12], 13]
            >>> nd = _NestedDict(dic, values=val, order=ord)
            >>> print(nd)
                {1: {4: {1: {2: 3}}, 5: {4: {5: 6}, 7: {8: {9: 10}}}}, 2: {4: [11, 12], 5: 13}}
            >>> values = nd.xvalues()
            >>> values == val
                True
        """
        __force_list = kwargs.pop(_Decorator.KW_FORCE_LIST, False)
        if kwargs=={}:
            values = self._deepest(self, item='values')
        else:
            values = []
            kwargs.update({_Decorator.KW_FORCE_LIST: True})
            for xk in self.xkeys(**kwargs):
                rdic = self.copy() # copy.deepcopy(self)
                for x in xk:
                    if x not in rdic:
                        rdic.update({x: {}})
                    rdic = rdic[x]
                values.append(rdic)
        if values == []: values = None
        return values if __force_list is True or values in ([],None) or len(values)>1 else values[0]

    #/************************************************************************/
    def items(self, **kwargs):
        """Retrieve items of nested dictionary.
        
            >>> items = dnest.items(**kwargs)
        """
        if kwargs == {}:
            return super(_NestedDict, self).items()
        return list(zip(itertools.cycle(self.keys(**kwargs)),
                        self.values(**kwargs)))
    
    #/************************************************************************/
    def xitems(self, **kwargs):
        """Retrieve nested items of nested dictionary.
        
            >>> items = dnest.xitems(**kwargs)

        Examples
        --------
        
            >>> dic = {'a': [1,2], 'b': [3,4,5], 'c': [6,7,8,9]}
            >>> r = _NestedDict(dic, order = ['b', 'c', 'a'])
            >>> print(r)
                {3: {6: {1: {}, 2: {}}, 7: {1: {}, 2: {}}, 8: {1: {}, 2: {}}, 9: {1: {}, 2: {}}},
                 4: {6: {1: {}, 2: {}}, 7: {1: {}, 2: {}}, 8: {1: {}, 2: {}}, 9: {1: {}, 2: {}}},
                 5: {6: {1: {}, 2: {}}, 7: {1: {}, 2: {}}, 8: {1: {}, 2: {}}, 9: {1: {}, 2: {}}}}
            >>> r.xitems(b=4)
                [((4, 6, 1), {}), ((4, 6, 2), {}), ((4, 7, 1), {}), ((4, 7, 2), {}),
                 ((4, 8, 1), {}), ((4, 8, 2), {}), ((4, 9, 1), {}), ((4, 9, 2), {})]
            >>> r.xitems(c=6, a=2)
                [((3, 6, 2), {}), ((4, 6, 2), {}), ((5, 6, 2), {})]        
        """
        kwargs.update({_Decorator.KW_FORCE_LIST: True})
        return list(zip(self.xkeys(**kwargs), self.xvalues(**kwargs)))
    
    #/************************************************************************/
    def xlen(self, *arg):
        """Retrieve depth lenght of the various dimensions of a nested dictionary.
        
            >>> len = dnest.xlen(*arg)

        
        Examples
        --------
        
            >>> dic = {'a': [1,2], 'b': [3,4,5], 'c': [6,7,8,9]}
            >>> r = _NestedDict(dic, order = ['b', 'c', 'a'])
            >>> print(r)
                {3: {6: {1: {}, 2: {}}, 7: {1: {}, 2: {}}, 8: {1: {}, 2: {}}, 9: {1: {}, 2: {}}},
                 4: {6: {1: {}, 2: {}}, 7: {1: {}, 2: {}}, 8: {1: {}, 2: {}}, 9: {1: {}, 2: {}}},
                 5: {6: {1: {}, 2: {}}, 7: {1: {}, 2: {}}, 8: {1: {}, 2: {}}, 9: {1: {}, 2: {}}}}
            >>> r.xlen('a')
                2
            >>> r.xlen('a','b','c')
                {'a': 2, 'b': 3, 'c': 4}
            >>> r.xlen()
                24
        """
        if arg in ((),([],),(None,)):
            dimensions = self.order
        elif happyType.issequence(arg[0]):
            dimensions = arg[0]
        else:
            dimensions = arg
        try:
            assert set(dimensions).difference(set(self.order)) == set()
        except:
            raise happyError('wrong type/value for input argument')
        try:    
            xlen = {k: v for k,v in self.__xlen.items() if k in dimensions}
        except:
            xlen = {}
            dic = [self.__dict__]
            for dim in self.order:
                if dim in dimensions:
                    xlen.update({dim: len(dic[0].keys())})
                dic = list(dic[0].values())
        if arg == ():
            return functools.reduce(lambda x,y: x*y, xlen.values())
        else:
            return xlen if len(xlen)>1 else list(xlen.values())[0]

    #/************************************************************************/
    def reorder(self, order):
        """Reorder the nested structure of a nested dictionary.
        
            >>> dnest.reorder(order)
        
        Example
        -------
        
            >>> d = {'a': [1,2], 'b': [3,4,5]}
            >>> r = _NestedDict(d, values = list(range(6)))
            >>> r.order
                ['a', 'b']
            >>> print(r)
                {1: {3: 0, 4: 1, 5: 2}, 2: {3: 3, 4: 4, 5: 5}}
            >>> r.reorder(['b', 'a'])
            >>> print(r)
                {3: {1: 0, 2: 3}, 4: {1: 1, 2: 4}, 5: {1: 2, 2: 5}}
            >>> r.order
                ['b', 'a']
        """
        try:
            assert order is None or happyType.issequence(order)
        except:
            raise happyError('wrong argument for %s attribute' % _Decorator.KW_ORDER)
        # reassign self.__dimensions
        if self.order not in (None,[],()) and self.order != order:
            self._deepreorder(self, order=order, in_place=True)

    #/************************************************************************/
    def merge(self, *dics, **kwargs):
        order = self.order
        def umerge(dic):
            try:
                dorder = dic.order
                assert order not in (False,None)
            except:
                pass
            else:
                ndic = None
                norder = sorted([o for o in dorder if o in order], key=lambda x: order.index(x))     \
                    + [o for o in dorder if o not in order]
                if norder != dorder:
                    ndic = dic._deepreorder(norder)
                self._deepmerge(self.__dict__, ndic or dic, in_place=True)
        functools.reduce(umerge, dics) 
    
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
        """Return the function's docstring.
        """
        return self.func.__doc__
    
    def __get__(self, obj, objtype):
        """Support instance methods.
        """
        return functools.partial(self.__call__, obj)

