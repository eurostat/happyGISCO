#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_settings

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `OpenStreetMap <OSM_>`_
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
.. |GDAL| replace:: `GDAL <GDAL_>`_
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

The classes exposed in this module (*e.g.*, logging classes :class:`happyVerbose`,
:class:`happyWarning`, :class:`happyError` and decorator class :class:`_geoDecorators`
and its subclasses) **can be ignored** at the first glance since they are not requested
to run the services. They are provided here for the sake of an exhaustive documentation.

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Mar 31 21:54:08 2018

import os, sys#analysis:ignore
import inspect#analysis:ignore

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
                (self.errtype, 
                 ' ' if self.errtype and self.errcode else '',
                 self.errcode,
                 ': ' if (self.errtype or self.errcode) and (self.errmsg or self.expr) else '',
                 self.errmsg, 
                 ' ' if self.errmsg and self.expr else '',
                 self.expr #[' ' + self.expr if self.expr else '']
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
"""Dummy |OSM| key: connection to |OSM| web-services does not require authentication.
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
   
   
#%%
#==============================================================================
# CLASS _geoDecorators
#==============================================================================
    
class _geoDecorators(object):
    """Class implementing dummy decorators used to parse and check place and coordinate 
    arguments, but not only, to generic methods, *e.g.* the methods of the geoservice 
    classes.
    """
    
    KW_PLACE        = 'place'
    KW_LAT          = 'lat'
    KW_LON          = 'lon'
    KW_COORD        = 'coord'
    KW_PROJECTION   = 'proj' 
    KW_NUTS         = 'nuts' 
    
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
    class parse_place(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with place (topo,geo) names to functions and methods.
        """
        def __call__(self, *args, **kwargs):
            if args not in (None,()):      
                if all([isinstance(a,str) for a in args]):
                    place = list(args)
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    place = args[0]
                else:   
                    raise IOError('input arguments not recognised')
            else:                           
                place = kwargs.pop(_geoDecorators.KW_PLACE, None)
            if place in (None,[],''):
                raise IOError('no input arguments passed')
            if not isinstance(place,(list,tuple)):
                place = [place,]
            if not all([isinstance(p,str) for p in place]):
                raise IOError('wrong format for input place')
            return self.func(place, **kwargs)

    #/************************************************************************/
    class parse_coordinate(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lon)` geographical coordinates to functions and methods.
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
            coord, lat, lon, poly = None, None, None, None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = list(args)
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2                                      \
                        and all([isinstance(args[0][i],(tuple,list)) or not hasattr(args[0][i],'__len__') for i in (0,1)]):
                        lat, lon = args[0]
                    elif all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
                elif len(args) == 1 and isinstance(args[0],(tuple,list)) and len(args[0])==2:
                    lat, lon = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],(tuple,list)) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    lat, lon = args
                else:   
                    raise IOError('input coordinate arguments not recognised')
            else:   
                coord = kwargs.pop(_geoDecorators.KW_COORD, None)         
                lat = kwargs.pop(_geoDecorators.KW_LAT, None) or kwargs.pop('x', None)
                lon = kwargs.pop(_geoDecorators.KW_LON, None) or kwargs.pop('y', None)
                poly = self.polyline and kwargs.get(self.KW_POLYLINE)
            try:
                assert not(coord is None and lat is None and lon is None and poly in (False,None)) 
            except AssertionError:
                raise IOError('no input coordinate arguments passed')
            try:
                assert coord is None or (lat is None and lon is None)
            except AssertionError:
                raise IOError('too many input coordinate arguments')
            if poly not in (False,None):
                # coord = self.polyline.decode(poly)
                return self.func(None, None, **kwargs)
            #if coord is not None:
            #    if not isinstance(coord,(list,tuple)):  
            #        coord = [coord]
            #    try:
            #        assert all(['lat' in c and 'lon' in c for c in coord])
            #    except AssertionError:
            #        raise IOError('wrong dictionary keys for input coordinate argument')
            #    try:
            #        lat, lon = [_ for _ in zip(*[(c['lat'], c['lon']) for c in coord])]
            #    except:
            #        raise IOError('wrong input coordinate argument passed')
            if not (lat is None or lon is None):
                if not isinstance(lat,(list,tuple)):  
                    lat, lon = [lat,], [lon,]
                if not len(lat) == len(lon):
                    raise IOError('incompatible geographical coordinates')
                coord = [_ for _ in zip(lat, lon)]
                if order != 'lL':   coord = [_[::-1] for _ in coord]
            if coord in ([],None):
                raise IOError('wrong geographical coordinates')
            return self.func(coord, **kwargs)
       
    #/************************************************************************/
    class parse_place_or_coordinate(__parse):
        """
        """
        def __call__(self, *args, **kwargs):
            try:
                place = _geoDecorators.parse_place(lambda p, **kw: p)(*args, **kwargs)
            except:
                place = None
            else:
                kwargs.update({_geoDecorators.KW_PLACE: place})
            try:
                coord = _geoDecorators.parse_coordinate(lambda l, L, **kw: [l, L])(*args, **kwargs)
            except:
                coord = None
            else:
                kwargs.update({_geoDecorators.KW_COORD: coord})
            try:
                assert not(place in ('',None) and coord in ([],None))
            except:
                raise IOError('no geographical entity parsed to define the place')
            try:
                assert place in ('',None) or coord in ([],None)
            except:
                raise IOError('too many geographical entities parsed to define the place')
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_nuts(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with |NUTS| information stored in |GISCO|-like formatted dictionary (from 
        JSON response) to functions and methods.
        
        Examples
        --------
        >>> func = lambda *args, **kwargs: kwargs.get('nuts')
        >>> nuts = _geoDecorators.parse_nuts(func)(attributes='A', layerId=5, LEVL_CODE=2)
        """
        KW_RESULTS      = 'results'
        KW_ATTRIBUTES   = 'attributes'
        KW_FIELDNAME    = 'displayFieldName' 
        KW_LAYERID      = 'layerId'
        KW_LAYERNAME    = 'layerName'
        KW_VALUE        = 'value'
        KW_LEVEL        = 'LEVL_CODE'
        KW_NUTS_ID      = 'NUTS_ID' # nuts[self.KW_FIELDNAME]
        KW_CNTR_CODE    = 'CNTR_CODE'
        KW_NUTS_NAME    = 'NUTS_NAME'
        KW_OBJECTID     = 'OBJECTID'
        def __call__(self, *args, **kwargs):
            level = kwargs.pop('level',None)
            nuts, items = None, {}
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    nuts = list(args)
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        nuts = args[0]
            else:   
                nuts = kwargs.pop(_geoDecorators.KW_NUTS, {})   
                items = {self.KW_ATTRIBUTES: kwargs.pop(self.KW_ATTRIBUTES, None),
                         self.KW_FIELDNAME: kwargs.pop(self.KW_FIELDNAME, None),
                         self.KW_LAYERID: kwargs.pop(self.KW_LAYERID, None),
                         self.KW_LAYERNAME: kwargs.pop(self.KW_LAYERNAME, None),
                         self.KW_VALUE: kwargs.pop(self.KW_VALUE, None)}
            try:
                assert not(nuts in ({},None) and all([v in ([],None) for v in items.values()]))
            except AssertionError:
                # raise IOError('no input NUTS parsed')
                return self.func(None, *args, **kwargs)
            try:
                assert nuts in ({},None) or all([v in ([],None) for v in items.values()])
            except AssertionError:
                raise IOError('too many input file arguments')
            else:
                nuts = items if nuts in ({},None) else nuts
            if nuts in ((),[],None) or                                              \
                (isinstance(nuts,dict) and all([n in ([],None) for n in nuts.values()])):
                # raise IOError('no NUTS parsed')
                return self.func(*args, **kwargs)
            if not isinstance(nuts,(list,tuple)):
                nuts = [nuts,]
            if not all([isinstance(n,dict) and self.KW_ATTRIBUTES in n for n in nuts]): 
                raise IOError('NUTS attributes not recognised')
            if level is not None:
                nuts = [n for n in nuts if n[self.KW_ATTRIBUTES][self.KW_LEVEL] == str(level)]
            # kwargs.update({_geoDecorators.KW_NUTS: nuts})
            # return self.func(**kwargs)
            return self.func(nuts, **kwargs)

    #/************************************************************************/
    class parse_geometry(__parse):
        """Generic class decorator of functions and methods used to parse 
        :literal:`(lat,lon)` geographical coordinates from JSON-like dictionary 
        parameters formated according to |GISCO| geometry responses (see |GISCOWIKI|).
        
            >>> new_func = parse_geometry(func)
        
        Arguments
        ---------
        func : callable
            the function to decorate that accepts, say, the input parameters :data:`*args, **kwargs`.
        unique : bool
            when set to :data:`True`, only one geometry is filtered out, the first
            available; default to :data:`False`.
        order : str
            flag used to define the order of the output filtered geographical 
            coordinates; it can be either :literal:`'lL'` for :literal:`(lat,lon)` 
            order or :literal:`'Ll'` for a :literal:`(lon,lat)` order; default 
            is :literal:`'lL'`.
        
        Returns
        -------
        new_func : callable
            the decorated function that now accepts the input parameters :data:`coord`
            as new keyword argument.
        
        Examples
        --------
        Some dummy examples:
            
        >>> func = lambda **kwargs: kwargs.get('coord')
        >>> geom = {'A': 1, 'B': 2}
        >>> _geoDecorators.parse_geometry(func)(geom)
            []
        >>> geom = {'geometry': {'coordinates': [1, 2], 'type': 'Point'},
                    'properties': {'osm_key': 'place'},
                    'type': 'Feature'}
        >>> _geoDecorators.parse_geometry(func)(coord=geom)
            [2, 1]
        >>> _geoDecorators.parse_geometry(func)(geom, order='Ll')
            [2, 1]
        
        and an actual one:
            
        >>> serv = services.GISCOService()
        >>> geom = serv.place2geom(place='Berlin,Germany')
        >>> print(geom)
            [{'geometry': {'coordinates': [13.3888599, 52.5170365], 'type': 'Point'},
              'properties': {'city': 'Berlin',
               'country': 'Germany',
               'name': 'Berlin',
               'osm_id': 240109189, 'osm_key': 'place', 'osm_type': 'N', 'osm_value': 'city',
               'postcode': '10117',
               'state': 'Berlin'},
              'type': 'Feature'},
             {'geometry': {'coordinates': [13.4385964, 52.5198535], 'type': 'Point'},
              'properties': {'country': 'Germany',
               'extent': [13.08835, 52.67551, 13.76116, 52.33826],
               'name': 'Berlin',
               'osm_id': 62422, 'osm_key': 'place', 'osm_type': 'R', 'osm_value': 'state'},
              'type': 'Feature'},
             {'geometry': {'coordinates': [13.393560634296435, 52.51875095],
               'type': 'Point'},
              'properties': {'city': 'Berlin',
               'country': 'Germany',
               'extent': [13.3906703, 52.5200704, 13.3948782, 52.5174944],
               'name': 'Humboldt University in Berlin Mitte Campus',
               'osm_id': 120456814, 'osm_key': 'amenity', 'osm_type': 'W', 'osm_value': 'university',
               'postcode': '10117',
               'state': 'Berlin',
               'street': 'Dorotheenstraße'},
              'type': 'Feature'},
             ...
              {'geometry': {'coordinates': [13.3869856, 52.5156648], 'type': 'Point'},
              'properties': {'city': 'Berlin',
               'country': 'Germany',
               'housenumber': '55-57',
               'name': 'Komische Oper Berlin',
               'osm_id': 318525456, 'osm_key': 'amenity', 'osm_type': 'N', 'osm_value': 'theatre',
               'postcode': '10117',
               'state': 'Berlin',
               'street': 'Behrenstraße'},
              'type': 'Feature'}]
                    
        We can for instance use the :meth:`parse_geometry` to parse (filter) the 
        data :data:`geom`:
            
        >>> func = lambda **kwargs: kwargs.get('coord')
        >>> _geoDecorators.parse_geometry(func)(geom)
            [[52.5170365, 13.3888599], [52.5198535, 13.4385964]]
        >>> _geoDecorators.parse_geometry(func)(geom, unique=True, order='Ll')
            [13.3888599, 52.5170365]
            
        Note
        ----
        When passed to the decorated method :data:`new_func`, the input :data:`kwargs` 
        are actually filtered out to extract features, say :data:`g`, that are formatted 
        like the JSON geometries output by |GISCO| web-service and which verify the
        following match:
        
            ```
            g['type']='Feature' g['geometry']['type']='Point' and g['properties']['osm_key']='place'
            ```
        """
        KW_FEATURES     = 'features'
        KW_GEOMETRY     = 'geometry'
        KW_PROPERTIES   = 'properties'
        KW_TYPE         = 'type'
        KW_OSM_KEY      = 'osm_key'
        KW_COORDINATES  = 'coordinates'
        def __call__(self, *args, **kwargs):
            unique = kwargs.pop('unique',False)
            order = kwargs.pop('order', 'lL')
            coord = None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
            else:   
                coord = kwargs.pop(_geoDecorators.KW_COORD, None)        
            if coord is not None:
                if isinstance(coord,(list,tuple)) and all([isinstance(c,dict) for c in coord]):      
                    coord = [c for c in coord                                                      \
                       if self.KW_GEOMETRY in c and self.KW_PROPERTIES in c and self.KW_TYPE in c   \
                       and c[self.KW_TYPE]=='Feature'                                               \
                       and (not(CHECK_TYPE) or c[self.KW_GEOMETRY][self.KW_TYPE]=='Point')          \
                       and (not(CHECK_OSM_KEY) or c[self.KW_PROPERTIES][self.KW_OSM_KEY]=='place')  \
                       ]
                    #coord = dict(zip(['lon','lat'],                                                 \
                    #                  zip(*[c[self.KW_GEOMETRY][self.KW_COORDINATES] for c in coord])))
                    coord = [_[self.KW_GEOMETRY][self.KW_COORDINATES] for _ in coord]
                    if order == 'lL':   coord = [_[::-1] for _ in coord]
                    if unique or len(coord)==1:          coord = coord[0]
                kwargs.update({_geoDecorators.KW_COORD: coord}) 
                return self.func(**kwargs)
            else:
                return self.func(*args, **kwargs)
        
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
            if proj in ('',None):
                return self.func(None,*args, **kwargs)
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
            if year in ([],None):
                return self.func(None, *args, **kwargs)
            print(self.YEARS)
            if year not in tuple(self.YEARS):
                raise IOError('year %s not supported' % year)
            kwargs.update({'year': year})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_file(__parse):
        """
        """
        def __call__(self, *args, **kwargs):
            dirname, basename, filename = None, None, None
            if args not in (None,()):      
                if len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2 and all([isinstance(args[0][i],str) for i in (0,1)]):
                        dirname, basename = args[0]
                    elif all([isinstance(args[0][i],str) for i in range(len(args[0]))]):
                        filename = args[0]
                elif len(args) == 1 and isinstance(args[0],str) and len(args[0])==2:
                    dirname, basename = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],str) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    dirname, basename = args
                else:   
                    raise IOError('input file arguments not recognised')
            else:   
                dirname = kwargs.pop('dir', '')         
                basename = kwargs.pop('base', '')
                filename = kwargs.pop('file', '')
            try:
                assert not(filename in ('',None) and basename in ('',None))
            except AssertionError:
                raise IOError('no input file arguments passed')
            try:
                assert filename in ('',None) or basename in ('',None)
            except AssertionError:
                raise IOError('too many input file arguments')
            if filename is None:
                try:
                    filename = os.path.join(os.path.realpath(dirname or ''), basename)
                except:
                    raise IOError('wrong input file argument passed')
            if not isinstance(filename,str):
                filename = [filename,]
            return self.func(filename, **kwargs)

    #/************************************************************************/
    class parse_route(__parse):
        """
        """
        KW_CODE         = 'code'
        KW_ROUTES       = 'routes'
        KW_WAYPOITNS    = 'waypoints'
        def __call__(self, *args, **kwargs):
            pass
    



