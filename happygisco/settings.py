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

Basic definitions for the use of various geolocation web-services.

**Description**

This module contains some basic definitions (classes and variables) that are used
for:

* query and collection through |Eurostat| |GISCO| webservices,
* query and collection through external GIS webservices,
* simple geographical data handling and processing.

**Note**

The classes exposed in this module (*e.g.*, type class :class:`_Types`, logging 
classes :class:`happyVerbose`, :class:`happyWarning`, :class:`happyError` and 
decorator class :class:`_geoDecorators` and its subclasses) **can be ignored** 
at the first glance since they are not requested to run the services. They are 
provided here for the sake of an exhaustive documentation.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`itertools`, :mod:`collection`, :mod:`six`, :mod:`inspect`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Mar 31 21:54:08 2018

import os, sys#analysis:ignore
import inspect#analysis:ignore
import itertools, collections
import six

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
    >>> happyVerbose('The more we talk, we less we do...', verb=True);
        [verbose] - The more we talk, we less we do...
    """
    def __init__(self, msg, expr=None, verb=True):    
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
# GLOBAL VARIABLES
#==============================================================================

PACKAGE             = "happygisco"

PROTOCOLS           = ('http', 'https', 'ftp')
"""Recognised protocols (APIs, bulk downloads,...).
"""
DEF_PROTOCOL        = 'http'
PROTOCOL            = DEF_PROTOCOL
"""Default protocol used by the APIs.
"""
LANGS               = ('en','de','fr')
"""Languages supported by this package.
"""
DEF_LANG            = 'en'
"""Default language used when launching |Eurostat| |GISCO| API.
"""

EC_URL              = 'ec.europa.eu'
"""European Commission URL.
"""
ESTAT_DOMAIN        = 'eurostat'
"""|Eurostat| domain under European Commission URL.
"""
ESTAT_URL           = '%s://%s/%s' % (PROTOCOL, EC_URL, ESTAT_DOMAIN)
"""|Eurostat| complete URL.
"""

EC_DOMAIN           = 'europa.eu'
"""European Commission web-service domain.
"""
GISCO_DOMAIN        = 'webtools/rest/gisco/'
"""|GISCO| web-service domain under European Commission URL.
"""
GISCO_URL           = '%s/%s' % (EC_DOMAIN, GISCO_DOMAIN)
"""|GISCO| web-service complete URL.
"""
GISCO_ARCGIS        = 'webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/'
"""|GISCO| |ArcGIS| server.
"""
CODER_GISCO         = 'gisco'
"""Identifier of |GISCO| geocoder.
"""
KEY_GISCO           = None
"""Dummy |GISCO| key. It is set to :data:`None` since connection to |GISCO| web-services does
not require authentication.
"""

OSM_URL             = 'nominatim.openstreetmap.org/'
"""
|OSM| web-service complete URL.
"""
CODER_OSM         = 'osm'
"""Identifier of |OSM| geocoder.
"""
KEY_OSM           = None
"""
Dummy |OSM| key (connection to |OSM| web-services does not require authentication).
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

CODER_LIST          = [CODER_GISCO, CODER_GOOGLE, CODER_GOOGLE_MAPS, CODER_GOOGLE_PLACES]
"""List of geocoders available.
"""
CODER_PROJ          = {CODER_GISCO: 'WGS84',
                       CODER_GOOGLE: 'EPSG3857',
                       CODER_GOOGLE_MAPS: 'EPSG3857', 
                       CODER_GOOGLE_PLACES: 'EPSG3857'}
"""Geographical projections available through the different geocoders.
"""

DRIVER_NAME         = 'ESRI Shapefile'
"""|GDAL| driver name.
"""             
   
POLYLINE            = False
"""
Boolean flag set to import the package :mod:`polylines` that will enable you to 
generate polylines (see the `package website <https://pypi.python.org/pypi/polyline/>`_). 
Not really necessary to generate the routes.
"""

VERBOSE             = True

REDUCE_ANSWER       = False # !!! used for testing purpose: do not change !!!
   
   
#%%
#==============================================================================
# CLASS _Types
#==============================================================================
    
class _Types(object):
    """Class implementing various dummy types' checking.
    """
    
    #/************************************************************************/
    @classmethod
    def typename(cls, inst): 
        """Return the class name of a given instance: nothing else than 
        :literal:`instance.__class__.__name__`\ .  
    
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
            return _Types.typename(inst) == str_cls
        except:
            raise happyError('class not recognised')
    
    #/************************************************************************/
    @classmethod
    def isstring(cls, arg):
        """Check whether an argument is a string.
        
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
        return (isinstance(arg, collections.Sequence) and not _Types.isstring(arg))
    
    #/************************************************************************/
    @classmethod
    def ismapping(cls, arg):
        """Check whether an argument is a dictionary.
        
            >>> ans = _Types.ismapping(arg)
      
        Arguments
        ---------
        arg : 
            any input to test
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is an instance of the 
            :class:`collections.Mapping` class.
        """
        return (isinstance(arg, collections.Mapping))

#%%
#==============================================================================
# CLASS _geoDecorators
#==============================================================================
    
class _geoDecorators(object):
    """Class implementing dummy decorators of methods and functions used to parse 
    and check arguments as geographical features, *e.g.* place, coordinates or 
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
    
    KW_GEOM         = 'geom'
    
    KW_PROJECTION   = 'proj' 
    
    KW_YEAR         = 'year'
    
    KW_NUTS         = 'nuts' 
    
    KW_FILE         = 'file'

    #/************************************************************************/
    @staticmethod
    def _flatten(args):
        #ignore
        """Flatten a list of lists.
        """
        return list(itertools.chain.from_iterable(args))

    #/************************************************************************/
    class __parse(object):
        """Base parsing class for geographical entities. All decorators in 
        :class:`_geoDecorators` will inherit from this class.
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
        
            >>> new_func = _geoDecorators.parse_coordinate(func)
        
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
            :literal`'instancemethod'`; default is :data:`None`.
        cls : 
            class whose method is decorated when the decorated function is any 
            among :literal`['staticmethod', 'classmethod', 'property','instancemethod']; 
            default is :data:`None`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts geographical coordinates as 
            positional argument(s), plus an additional keyword argument (see 
            *Notes* below).
        
        Examples
        --------        
        Some dummy examples:
            
        >>> func = lambda coord, *args, **kwargs: coord
        >>> new_func = _geoDecorators.parse_coordinate(func)
        >>> new_func([1,-1])
            [[1,-1]]
        >>> new_func([1,2],[-1,-2])
            [[1, -1], [2, -2]]
        >>> new_func(coord=[[1,-1],[2,-2]])
            [[1, -1], [2, -2]]
        >>> new_func(coord=[[1,-1],[2,-2]], order='Ll')
            [[-1, 1], [-2, 2]]
        >>> new_func(**{'lat':[1,2], 'Lon': [-1,-2]})
            [[1, -1], [2, -2]]
        >>> new_func(lat=[1,2], Lon=[-1,-2], order='Ll')
            [[-1, 1], [-2, 2]]
        >>> new_func(**{'y':[1,2], 'x': [-1,-2]})
            [[1, -1], [2, -2]]

        Also be aware:

        >>> new_func([[1,-1],[2,-2]], lat=[1,2], Lon=[-1,-2])
            happyError: !!! dont mess up with me - duplicated argument parsed !!!
        >>> new_func(coord=[[1,-1],[2,-2]], lat=[1,2], Lon=[-1,-2])
            happyError: !!! AssertionError: too many input coordinate arguments !!!
             
        Notes
        -----
        * As per their use in the module :mod:`happyGISCO` of the :class:`_geoDecorators` 
          decorating functions, the keyword arguments :data:`obj,cls,method_type` 
          can be ignored. 
        * The decorated method/function :data:`new_func` accepts the same :data:`*args` 
          positional arguments as :data:`func` and, in addition to the arguments 
          already in `data:`**kwargs`, one extra keyword argument:
              + :data:`order` : a flag used to define the order of the output parsed 
                geographical coordinates; it can be either :literal:`'lL'` for 
                :literal:`(lat,Lon)` order or :literal:`'Ll'` for a :literal:`(Lon,lat)` 
                order; default is :literal:`'lL'`.
        * The output decorated method :data:`new_func` can parse the following keys: 
          :literal:`['lat', 'Lon', 'x', 'y', 'coord']` from any input keyword argument. 
          See the examples above.
           
        See also
        --------
        :meth:`~_geoDecorators.parse_place`, :meth:`~_geoDecorators.parse_place_or_coordinate`,
        :meth:`~_geoDecorators.parse_geometry`.
        """
        KW_POLYLINE      = 'polyline'
        try:
            if POLYLINE:    import polyline
            else:           polyline = True
            assert polyline
        except:
            polyline = False
            happyWarning('POLYLINE (https://pypi.python.org/pypi/polyline/) not loaded')
        else:
            if POLYLINE:   happyWarning('POLYLINE help: https://github.com/hicsail/polyline')
            pass
        def __call__(self, *args, **kwargs):
            order = kwargs.pop('order', 'lL')
            if not _Types.isstring(order) or not order in ('Ll','lL'):
                raise happyError('wrong order parameter')
            coord, lat, lon, poly = None, None, None, None
            if args not in (None,()):      
                if all([_Types.ismapping(a) for a in args]):
                    coord = list(args)
                elif len(args) == 1 and _Types.issequence(args[0]):
                    if len(args[0])==2                                      \
                        and all([_Types.issequence(args[0][i]) or not hasattr(args[0][i],'__len__') for i in (0,1)]):
                        lat, lon = args[0]
                    elif all([_Types.ismapping(args[0][i]) for i in range(len(args[0]))]):
                        coord = args[0]
                    elif all([len(args[0][i])==2 for i in range(len(args[0]))]):
                        coord = args[0]
                elif len(args) == 2                                         \
                    and all([_Types.issequence(args[i]) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    lat, lon = args
                else:   
                    raise happyError('input coordinate arguments not recognised')
            if lat is None and lon is None and coord is None:
                coord = kwargs.pop(_geoDecorators.KW_COORD, None)         
                lat = kwargs.pop(_geoDecorators.KW_LAT, None) or kwargs.pop('y', None)
                lon = kwargs.pop(_geoDecorators.KW_LON, None) or kwargs.pop('x', None)
                poly = self.polyline and kwargs.get(_geoDecorators.parse_coordinate.KW_POLYLINE)
            elif not (kwargs.get(_geoDecorators.KW_LAT) is None and \
                      kwargs.get(_geoDecorators.KW_LON) is None and \
                      kwargs.get(_geoDecorators.KW_COORD) is None):
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
                    raise happyError('incompatible geographical coordinates')
                coord = [list(_) for _ in zip(lat, lon)]
            elif all([_Types.ismapping(coord[i]) for i in range(len(coord))]):
                coord = [[coord[i].get(_geoDecorators.KW_LAT), coord[i].get(_geoDecorators.KW_LON)]     \
                          for i in range(len(coord))]      
            if coord in ([],None):
                raise happyError('wrong geographical coordinates')
            if order != 'lL':                   coord = [_[::-1] for _ in coord] # order = 'Ll'
            if REDUCE_ANSWER and len(coord)==1:    coord = coord[0]
            return self.func(coord, **kwargs)

    #/************************************************************************/
    class parse_place(__parse):
        """Generic class decorator of functions and methods used to parse place
        (topo,geo) names.
        
            >>> new_func = _geoDecorators.parse_place(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.

        Returns
        -------
        new_func : callable
            the decorated function that now accepts a place as a positional 
            argument.
        
        Examples
        --------
        Very basic parsing examples:
            
        >>> func = lambda place, *args, **kwargs: place
        >>> new_func = _geoDecorators.parse_place(func)
        >>> new_func('Athens, Hellas')
            ['Athens, Hellas']
        >>> new_func(place='Bruxelles, Belgium')
            ['Bruxelles, Belgium']
        >>> new_func(city=['Athens','Heraklion'],country='Hellas')
            ['Athens, Hellas', 'Heraklion, Hellas']
        >>> new_func(**{'address':['72 avenue Parmentier','101 Avenue de la République'], 
                        'city':'Paris', 
                        'country':'France'})
            ['72 avenue Parmentier, Paris, France', 
            '101 Avenue de la République, Paris, France']
        >>> new_func(place=['Eurostat', 'DIGIT', 'EIB']], 
                     city='Luxembourg')
            ['Eurostat, Luxembourg', 'DIGIT, Luxembourg', 'EIB, Luxembourg']
            
        Note
        ----
        The output decorated method :data:`new_func` can parse the following keys: 
        :literal:`['place', 'address', 'city', 'zip', 'country']` from any input 
        keyword argument. See the examples above.
           
        See also
        --------
        :meth:`~_geoDecorators.parse_coordinate`, :meth:`~_geoDecorators.parse_place_or_coordinate`,
        :meth:`~_geoDecorators.parse_geometry`.
        """ 
        def __call__(self, *args, **kwargs):
            place, address, city, country, zipcode = '', '', '', '', ''
            if args not in (None,()):      
                if all([_Types.isstring(a) for a in args]):
                    place = list(args)
                elif len(args) == 1 and _Types.issequence(args[0]):
                    place = args[0]
                else:   
                    raise happyError('input arguments not recognised')
            if place in ('',None):
                place = kwargs.pop(_geoDecorators.KW_PLACE, None)
                address = kwargs.pop(_geoDecorators.KW_ADDRESS, None)
                city = kwargs.pop(_geoDecorators.KW_CITY, None)
                country = kwargs.pop(_geoDecorators.KW_COUNTRY, None)
                zipcode = kwargs.pop(_geoDecorators.KW_ZIPCODE, None)                
            elif not (kwargs.get(_geoDecorators.KW_PLACE) is None and   \
                      kwargs.get(_geoDecorators.KW_ADDRESS) is None and \
                      kwargs.get(_geoDecorators.KW_CITY) is None and    \
                      kwargs.get(_geoDecorators.KW_COUNTRY) is None and \
                      kwargs.get(_geoDecorators.KW_ZIPCODE) is None):
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
            if _Types.isstring(place): place = [place,]
            if city not in ('',None):   
                if _Types.isstring(city): 
                    city = [city,]
                if place == []:                 place = city
                else:
                    if len(city) > 1:
                        raise happyError('inconsistent place with multiple cities')
                    place = [', '.join(_) for _ in zip(place, itertools.cycle(city))]
            if zipcode not in ('',None):   
                if _Types.isstring(zipcode):   
                    zipcode = [zipcode,]
                if place == []:                 place = zipcode
                else:
                    if len(zipcode) > 1:
                        raise happyError('inconsistent place with multiple zipcodes')
                    place = [', '.join(_) for _ in zip(place, itertools.cycle(zipcode))]
            if country not in ('',None):   
                if _Types.isstring(country): 
                    country = [country,]
                if place == []:                 place = country
                else:
                    if len(country) > 1:
                        raise happyError('inconsistent place with multiple countries')
                    place = [', '.join(_) for _ in zip(place, itertools.cycle(country))]
            if place in (None,[],''):
                raise happyError('no input arguments passed')
            if REDUCE_ANSWER and len(place)==1:    place = place[0]
            if not all([_Types.isstring(p) for p in place]):
                raise happyError('wrong format for input place')
            return self.func(place, **kwargs)
       
    #/************************************************************************/
    class parse_place_or_coordinate(__parse):
        """Generic class decorator of functions and methods used to parse place 
        :literal:`(lat,Lon)` coordinates or place names.
        
            >>> new_func = _geoDecorators.parse_place_or_coordinate(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts  :data:`coord` or :data:`lat` 
            and :data:`Lon` as new keyword argument(s) to parse geographical 
            coordinates, plus some additional keyword argument (see *Notes* of
            :meth:`~_geoDecorators.parse_coordinate` method).
        
        Examples
        --------
        Some dummy examples:
            
        >>> func = lambda *args, **kwargs: [kwargs.get('coord'), kwargs.get('place')]
        >>> new_func = _geoDecorators.parse_place_or_coordinate(func)
        >>> new_func(lat=[1,2], Lon=[-1,-2])
            [[[1, -1], [2, -2]], None]
        >>> new_func(place='Bruxelles, Belgium')
            [None, ['Bruxelles, Belgium']]
        
        Note
        ----
        The output decorated method :data:`new_func` can parse all of the keys
        already supported by :meth:`~_geoDecorators.parse_place` and 
        :meth:`~_geoDecorators.parse_coordinate` from any input keyword argument,
        *i.e.,* :literal:`['lat', 'Lon', 'x', 'y', 'coord', 'place', 'address', 'city', 'zip', 'country']`. 
        See the examples above.
            
        See also
        --------
        :meth:`~_geoDecorators.parse_place`, :meth:`~_geoDecorators.parse_coordinate`,
        :meth:`~_geoDecorators.parse_geometry`.
        """
        def __call__(self, *args, **kwargs):
            try:
                place = _geoDecorators.parse_place(lambda p, **kw: p)(*args, **kwargs)
            except:
                place = None
            else:
                kwargs.update({_geoDecorators.KW_PLACE: place})
            try:
                coord = _geoDecorators.parse_coordinate(lambda c, **kw: c)(*args, **kwargs)
            except:
                coord = None
            else:
                kwargs.update({_geoDecorators.KW_COORD: coord})
            try:
                assert not(place in ('',None) and coord in ([],None))
            except:
                raise happyError('no geographical entity parsed to define the place')
            try:
                assert place in ('',None) or coord in ([],None)
            except:
                raise happyError('too many geographical entities parsed to define the place')
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_geometry(__parse):
        """Generic class decorator of functions and methods used to parse either
        :literal:`(lat,Lon)` coordinate(s) or (topo)name(s) from JSON-like dictionary 
        parameters (geometry features) formated according to |GISCO| geometry 
        responses (see |GISCOWIKI|).
        
            >>> new_func = _geoDecorators.parse_geometry(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts :data:`coord` as a keyword 
            argument to parse geographical coordinates, plus some additional keyword 
            arguments (see *Notes* below).
        
        Examples
        --------
        Some dummy examples:
            
        >>> func = lambda *args, **kwargs: kwargs.get('coord')
        >>> geom = {'A': 1, 'B': 2}
        >>> _geoDecorators.parse_geometry(func)(geom)
            []
        >>> _geoDecorators.parse_geometry(func)(geom=geom)
            happyError: !!! geometry attributes not recognised !!!
        >>> geom = {'geometry': {'coordinates': [1, 2], 'type': 'Point'},
                    'properties': {'city': 'somewhere', 
                                   'country': 'some country',
                                   'street': 'sesame street',
                                   'osm_key': 'place'},
                    'type': 'Feature'}
        >>> _geoDecorators.parse_geometry(func)(geom=geom)
            [[2, 1]]
        >>> _geoDecorators.parse_geometry(func)(geom, order='Ll')
            [[1, 2]]
        >>> func = lambda *args, **kwargs: kwargs.get('place')
        >>> _geoDecorators.parse_geometry(func)(geom=geom, filter='place')
            ['sesame street, somewhere, some country']
        
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
             {'geometry': {'coordinates': [13.393560634296435, 52.51875095],
               'type': 'Point'},
              'properties': {'city': 'Berlin', 'country': 'Germany',
               'extent': [13.3906703, 52.5200704, 13.3948782, 52.5174944],
               'name': 'Humboldt University in Berlin Mitte Campus',
               'osm_id': 120456814, 'osm_key': 'amenity', 'osm_type': 'W', 'osm_value': 'university',
               'postcode': '10117', 'state': 'Berlin',
               'street': 'Dorotheenstraße'},
              'type': 'Feature'},
             ...
              {'geometry': {'coordinates': [13.3869856, 52.5156648], 'type': 'Point'},
              'properties': {'city': 'Berlin', 'country': 'Germany',
               'housenumber': '55-57',
               'name': 'Komische Oper Berlin',
               'osm_id': 318525456, 'osm_key': 'amenity', 'osm_type': 'N', 'osm_value': 'theatre',
               'postcode': '10117', 'state': 'Berlin',
               'street': 'Behrenstraße'},
              'type': 'Feature'}]
                    
        We can for instance use the :meth:`parse_geometry` to parse (filter) the 
        data :data:`geom` and retrieve the coordinates:
            
        >>> func = lambda **kwargs: kwargs.get('coord')
        >>> new_func = _geoDecorators.parse_geometry(func)
        >>> hasattr(new_func, '__call__')
            True
        >>> new_func(geom, filter='coord')
            [[52.5170365, 13.3888599], [52.5198535, 13.4385964]]
        >>> new_func(geom, filter='coord', unique=True, order='Ll')
            [[13.3888599, 52.5170365]]
            
        One can also simlarly retrieve the name of the places:

        >>> func = lambda **kwargs: kwargs.get('place')
        >>> new_func = _geoDecorators.parse_geometry(func)
        >>> hasattr(new_func, '__call__')
            True
        >>> new_func(geom, filter='place')
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
          already in `data:`**kwargs`, some extra keyword arguments:              
              + :data:`geom` to parse geocoordinates;
              + :data:`filter` - a flag used to define the output of the decorated
                function; it is either :literal:`place` or :literal:`coord`;
              + :data:`unique` - when set to :data:`True`, a single geometry is 
                filtered out, the first available one; default to :data:`False`, 
                hence all geometries are parsed;
              + :data:`order` - a flag used to define the order of the output filtered 
                geographical coordinates; it can be either :literal:`'lL'` for 
                :literal:`(lat,Lon)` order or :literal:`'Ll'` for a :literal:`(Lon,lat)` 
                order; default is :literal:`'lL'`.    
        * When passed to the decorated method :data:`new_func` with input arguments 
          :data:`*args, **kwargs`, the remaining parameters in :data:`kwargs` are 
          actually filtered out to extract geometry features, say :data:`g`, that 
          are formatted like the JSON :literal:`geometries` output by |GISCO| 
          geocoding web-service (see method :meth:`services.GISCOService.place2geom`) 
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
        :meth:`~_geoDecorators.parse_place`, :meth:`~_geoDecorators.parse_coordinate`,
        :meth:`~_geoDecorators.parse_place_or_coordinate`, :meth:`~_geoDecorators.parse_nuts`, 
        :meth:`services.GISCOService.place2geom`.
        """
        KW_LAT          = 'lat' # not to be confused with _geoDecorators.KW_LAT
        KW_LON          = 'lon' # ibid 
        KW_FEATURES     = 'features'
        KW_GEOMETRY     = 'geometry'
        KW_PROPERTIES   = 'properties'
        KW_TYPE         = 'type'
        KW_OSM_KEY      = 'osm_key'
        KW_COORDINATES  = 'coordinates'
        KW_CITY         = 'city' # not to be confused with _geoDecorators.KW_CITY
        KW_COUNTRY      = 'country' # ibid
        KW_POSTCODE     = 'postcode'
        KW_STATE        = 'state'
        KW_STREET       = 'street'
        KW_DISPLAYNAME  = 'display_name'
        def __call__(self, *args, **kwargs):
            filt = kwargs.pop('filter','coord')
            if filt not in ('',None) and not (_Types.isstring(filt) and filt in ('place','coord')):
                raise happyError('wrong "filer" parameter')
            unique = kwargs.pop('unique',False)
            if not isinstance(unique, bool):
                raise happyError('wrong "unique" parameter')
            order = kwargs.pop('order', 'lL')
            if not _Types.isstring(order) or not order in ('Ll','lL'):
                raise happyError('wrong "order" parameter')
            geom = None
            if args not in (None,()): 
                __key_geom = False
                if all([_Types.ismapping(a) for a in args]):
                    geom = args
                elif len(args) == 1 and _Types.issequence(args[0]):
                    if all([_Types.ismapping(args[0][i]) for i in range(len(args[0]))]):
                        geom = args[0]
            if geom is None:
                __key_geom = True
                geom = kwargs.pop(_geoDecorators.KW_GEOM, None)                 
            elif not kwargs.get(_geoDecorators.KW_GEOM) is None:
                raise happyError('don''t mess up with me - duplicated geometry argument parsed')
            if geom is None:
                return self.func(*args, **kwargs)
            if _Types.ismapping(geom): 
                geom = [geom,]
            elif not _Types.issequence(geom):
                raise happyError('wrong geometry definition')              
            if not all([_Types.ismapping(g) for g in geom]): 
                raise happyError('wrong formatting/typing of geometry')  
            if filt in ('',None):
                kwargs.update({_geoDecorators.KW_GEOM: geom}) 
            elif filt == 'coord':                            
                try: # geometry is formatted like an OSM output
                    coord = [[float(g[_geoDecorators.parse_geometry.KW_LAT]),
                              float(g[_geoDecorators.parse_geometry.KW_LON])] for g in geom]
                    assert coord not in ([],None,[None])
                except: # geometry is formatted like a GISCO output
                    coord = [g for g in geom                                                        \
                       if _geoDecorators.parse_geometry.KW_GEOMETRY in g                            \
                           and _geoDecorators.parse_geometry.KW_PROPERTIES in g                     \
                           and _geoDecorators.parse_geometry.KW_TYPE in g                           \
                           and g[_geoDecorators.parse_geometry.KW_TYPE]=='Feature'                  \
                           and (not(CHECK_TYPE) or g[_geoDecorators.parse_geometry.KW_GEOMETRY][_geoDecorators.parse_geometry.KW_TYPE]=='Point')          \
                           and (not(CHECK_OSM_KEY) or g[_geoDecorators.parse_geometry.KW_PROPERTIES][_geoDecorators.parse_geometry.KW_OSM_KEY]=='place')  \
                       ]
                    #coord = dict(zip(['lon','lat'],                                                 \
                    #                  zip(*[c[self.KW_GEOMETRY][self.KW_COORDINATES] for c in coord])))
                    coord = [_[_geoDecorators.parse_geometry.KW_GEOMETRY][_geoDecorators.parse_geometry.KW_COORDINATES][::-1]   \
                             for _ in coord]
                if __key_geom and coord in ([],None):
                    raise happyError ('geometry attributes not recognised')
                if order != 'lL':   coord = [_[::-1] for _ in coord]
                if unique:          coord = [coord[0],]
                #elif len(coord)==1:          coord = coord[0]
                kwargs.update({_geoDecorators.KW_COORD: coord}) 
            elif filt == 'place':
                try: # geometry is formatted like an OSM output
                    place = [g[_geoDecorators.parse_geometry.KW_DISPLAYNAME] for g in geom]
                    assert place not in ([],[''],None,[None])
                except: # geometry is formatted like an OSM output 
                    place = [g.get(_geoDecorators.parse_geometry.KW_PROPERTIES) for g in geom \
                             if _geoDecorators.parse_geometry.KW_PROPERTIES in g]
                    place = [', '.join(filter(None, [p.get(_geoDecorators.parse_geometry.KW_STREET) or '',
                                        p.get(_geoDecorators.parse_geometry.KW_CITY) or '',
                                        '(' + p.get(_geoDecorators.parse_geometry.KW_STATE) + ')'               \
                                            if p.get(_geoDecorators.parse_geometry.KW_STATE) not in (None,'')   \
                                            and p.get(_geoDecorators.parse_geometry.KW_STATE)!=p.get(_geoDecorators.parse_geometry.KW_CITY) else '',
                                        p.get(_geoDecorators.parse_geometry.KW_POSTCODE) or '',
                                        p.get(_geoDecorators.parse_geometry.KW_COUNTRY) or ''])) for p in place] 
                if unique:          place = [place[0],]
                if REDUCE_ANSWER and len(place)==1:    place=place[0]
                kwargs.update({_geoDecorators.KW_PLACE: place}) 
            return self.func(**kwargs)
        
    #/************************************************************************/
    class parse_nuts(__parse):
        """Generic class decorator of functions and methods used to parse NUTS
        information from JSON-like dictionary parameters formated according to 
        |GISCO| |NUTS| responses (see |GISCOWIKI|).
        
            >>> new_func = _geoDecorators.parse_nuts(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts a NUTS entry as a positional
            argument (see  *Notes* below).             
        
        Examples
        --------
        Some dummy examples:
            
        >>> func = lambda *args, **kwargs: kwargs.get('nuts')
        >>> nuts = {'A': 1, 'B': 2}
        >>> _geoDecorators.parse_nuts(func)(nuts)
            []
        >>> _geoDecorators.parse_nuts(func)(nuts=nuts)
            happyError: !!! NUTS attributes not recognised !!!
        >>> nuts = {'attributes': {'CNTR_CODE': 'EU', 'LEVL_CODE': '0'},
                    'NUTS_NAME': 'EU',
                    'displayFieldName': 'NUTS_ID', 'layerId': 2, 'layerName': 'NUTS_2013',
                    'value': 'EU'}
        >>> [nuts] == _geoDecorators.parse_nuts(func)(**nuts)
            True
        >>> [nuts] == _geoDecorators.parse_nuts(func)(nuts=nuts)
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
        >>> res = settings._geoDecorators.parse_nuts(func)(nuts)
        >>> all([res[i] == nuts[i] for i in range(len(res))])
            True
        >>> settings._geoDecorators.parse_nuts(func)(nuts, level=2)
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
        :meth:`~_geoDecorators.parse_geometry`, :meth:`services.GISCOService.place2geom`, 
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
        KW_NUTS_NAME    = 'NUTS_NAME'
        KW_OBJECTID     = 'OBJECTID'
        def __call__(self, *args, **kwargs):
            level = kwargs.pop('level',None)
            nuts, items = None, {}
            if args not in (None,()):      
                __key_nuts = False
                if all([_Types.ismapping(a) for a in args]):
                    nuts = list(args)
                elif len(args) == 1 and _Types.issequence(args[0]):
                    if all([_Types.ismapping(args[0][i]) for i in range(len(args[0]))]):
                        nuts = args[0]
            if nuts is None:
                __key_nuts = True
                nuts = kwargs.pop(_geoDecorators.KW_NUTS, {})   
                items = {_geoDecorators.parse_nuts.KW_ATTRIBUTES:   kwargs.pop(_geoDecorators.parse_nuts.KW_ATTRIBUTES, None),
                         _geoDecorators.parse_nuts.KW_FIELDNAME:    kwargs.pop(_geoDecorators.parse_nuts.KW_FIELDNAME, None),
                         _geoDecorators.parse_nuts.KW_LAYERID:      kwargs.pop(_geoDecorators.parse_nuts.KW_LAYERID, None),
                         _geoDecorators.parse_nuts.KW_LAYERNAME:    kwargs.pop(_geoDecorators.parse_nuts.KW_LAYERNAME, None),
                         _geoDecorators.parse_nuts.KW_VALUE:        kwargs.pop(_geoDecorators.parse_nuts.KW_VALUE, None),
                         _geoDecorators.parse_nuts.KW_NUTS_NAME:    kwargs.pop(_geoDecorators.parse_nuts.KW_NUTS_NAME, None),
                         _geoDecorators.parse_nuts.KW_LEVEL:        kwargs.pop(_geoDecorators.parse_nuts.KW_LEVEL, None),
                         _geoDecorators.parse_nuts.KW_NUTS_ID:      kwargs.pop(_geoDecorators.parse_nuts.KW_NUTS_ID, None),
                         _geoDecorators.parse_nuts.KW_CNTR_CODE:    kwargs.pop(_geoDecorators.parse_nuts.KW_CNTR_CODE, None),
                         _geoDecorators.parse_nuts.KW_OBJECTID:     kwargs.pop(_geoDecorators.parse_nuts.KW_OBJECTID, None)}
                # note: the following instruction raises a "unhashable type: 'dict'"
                # TypeError
                # items = {(k,v) for (k,v) in list(items.items()) if v is not None}
                # using frozenset instead of list above does not solve the issue
                items = dict([(k,v) for (k,v) in list(items.items()) if v is not None])
            elif not kwargs.get(_geoDecorators.KW_NUTS) is None:
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
                (_Types.ismapping(nuts) and all([n in ([],None) for n in nuts.values()])):
                # raise happyError('no NUTS parsed')
                return self.func(*args, **kwargs)
            if _Types.ismapping(nuts):     
                nuts = [nuts,]
            elif not _Types.issequence(nuts):
                raise happyError('wrong NUTS definition')              
            if all([_Types.ismapping(n) for n in nuts]): 
                nuts = [n for n in nuts if _geoDecorators.parse_nuts.KW_ATTRIBUTES in n]
            if __key_nuts and nuts in ([],None): 
                raise happyError('NUTS attributes not recognised')              
            if level is not None:
                nuts = [n for n in nuts if n[_geoDecorators.parse_nuts.KW_ATTRIBUTES][_geoDecorators.parse_nuts.KW_LEVEL] == str(level)]
            if REDUCE_ANSWER and len(nuts)==1:    nuts=nuts[0]
            kwargs.update({_geoDecorators.KW_NUTS: nuts}) 
            return self.func(**kwargs)
 
    #/************************************************************************/
    class parse_projection(__parse):
        """Generic class decorator of functions and methods used to parse a projection
        reference system.
        
            >>> new_func = _geoDecorators.parse_projection(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts  :data:`proj` as a keyword 
            argument to parse the geographical projection system.
        
        Examples
        --------          
        >>> func = lambda *args, **kwargs: kwargs.get('proj')
        >>> _geoDecorators.parse_projection(func)(proj='dumb')
            happyError: !!! projection dumb not supported !!!
        >>> _geoDecorators.parse_projection(func)(proj='WGS84')
            4326
        >>> _geoDecorators.parse_projection(func)(proj='EPSG3857')
            3857
        >>> _geoDecorators.parse_projection(func)(proj=3857)
            3857
        >>> _geoDecorators.parse_projection(func)(proj='LAEA')
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
            proj = kwargs.pop(_geoDecorators.KW_PROJECTION, 'WGS84')
            if proj in ('',None):
                return self.func(*args, **kwargs)
            if proj not in list(_geoDecorators.parse_projection.PROJECTION.keys() \
                | _geoDecorators.parse_projection.PROJECTION.values()):
                raise happyError('projection %s not supported' % proj)
            kwargs.update({_geoDecorators.KW_PROJECTION: _geoDecorators.parse_projection.PROJECTION[proj]})                  
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_year(__parse):
        """Generic class decorator of functions and methods used to parse a 
        reference year for NUTS regulation.
        
            >>> new_func = _geoDecorators.parse_year(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts  :data:`year` as a keyword 
            argument to parse a reference year (*e.g.*, used in NUTS definition).
        
        Examples
        --------          
        >>> func = lambda *args, **kwargs: kwargs.get('year')
        >>> _geoDecorators.parse_year(func)(year=2000)
            happyError: !!! year 2000 not supported !!!
        >>> _geoDecorators.parse_year(func)(year=2013)
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
            year = kwargs.pop(_geoDecorators.KW_YEAR, 2013)
            if year in ([],None):
                return self.func(*args, **kwargs)
            if year not in tuple(_geoDecorators.parse_year.YEARS):
                raise happyError('year %s not supported' % year)
            kwargs.update({_geoDecorators.KW_YEAR: year})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_file(__parse):
        """Generic class decorator of functions and methods used to parse a 
        filename.
        
            >>> new_func = _geoDecorators.parse_file(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input arguments 
            :data:`*args, **kwargs`.
        
        Keyword arguments
        -----------------
        method_type,obj,cls : 
            see :meth:`~_geoDecorators.parse_coordinate`.
                
        Returns
        -------
        new_func : callable
            the decorated function that now accepts :data:`dir`, :data:`base`, and 
            :data:`file` as a keyword argument to parse the complete full path of
            a file. 
        
        Examples
        --------          
        >>> func = lambda *args, **kwargs: kwargs.get('file')
        >>> _geoDecorators.parse_file(func)(file='test.txt')
            test.txt
        >>> _geoDecorators.parse_file(func)(dir='/home/sweet/home/',base='test.txt')
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
                if len(args) == 1 and _Types.issequence(args[0]):
                    if len(args[0])==2 and all([_Types.isstring(args[0][i]) for i in (0,1)]):
                        dirname, basename = args[0]
                    elif all([isinstance(args[0][i],str) for i in range(len(args[0]))]):
                        filename = args[0]
                elif len(args) == 1 and _Types.isstring(args[0]) and len(args[0])==2:
                    dirname, basename = args[0]
                elif len(args) == 2                                         \
                    and all([_Types.isstring(args[i]) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    dirname, basename = args
                else:   
                    raise happyError('input file arguments not recognised')
            if not (dirname is None and basename is None) or            \
                    (kwargs.get(_geoDecorators.KW_DIRNAME) is None and  \
                     kwargs.get(_geoDecorators.KW_BASENAME) is None and \
                     kwargs.get(_geoDecorators.KW_FILENAME) is None):
                raise happyError('don''t mess up with me - duplicated argument parsed')
            else:   
                dirname = kwargs.pop(_geoDecorators.parse_file.KW_DIRNAME, '')         
                basename = kwargs.pop(_geoDecorators.parse_file.KW_BASENAME, '')
                filename = kwargs.pop(_geoDecorators.parse_file.KW_FILENAME, '')
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
            if not _Types.isstring(filename):
                filename = [filename,]
            kwargs.update({_geoDecorators.KW_FILE: filename})                  
            return self.func(**kwargs)

    #/************************************************************************/
    class parse_route(__parse):
        """Generic class decorator of functions and methods used to parse a 
        route.
            
        Note
        ----
        !!! Currently not yet implemented !!!
        """
        KW_CODE         = 'code'
        KW_ROUTES       = 'routes'
        KW_WAYPOITNS    = 'waypoints'
        def __call__(self, *args, **kwargs):
            pass
    

