#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_features

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _NUTS: http://ec.europa.eu/eurostat/web/nuts/background
.. |NUTS| replace:: `NUTS <NUTS_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `Open Street Map <OSM_>`_
.. _Google_Maps: https://developers.google.com/maps/
.. |Google_Maps| replace:: `Google Maps <Google_Maps_>`_
.. _Google_Places: https://developers.google.com/places/
.. |Google_Places| replace:: `Google Places <Google_Places_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_

Module for place/location features definition and description.

**Description**

The module :mod:`features` describes the main classes for the representation of 
place/location entities, as well as generic area geometries and common |NUTS| regions. 
Some basic geographic operations are associated to the different entities through 
the definition of dedicated methods.
    
**Dependencies**

*require*      :mod:`os`, :mod:`sys`, :mod:`functools`

*optional*:     :mod:`json`, :mod:`osgeo`

*call*         :mod:`settings`, :mod:`base`, :mod:`tools`, :mod:`services`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:34:07 2018

__all__         = ['Location', 'Area', 'NUTS']

# generic import
import os, sys#analysis:ignore

import functools#analysis:ignore

# from typing import Dict, Tuple, List

# local (absolute) imports
from happygisco import happyWarning, happyVerbose, happyError, happyType
from happygisco import settings
#from happygisco import base
from happygisco.base import SERVICE_AVAILABLE, ASYNCIO_AVAILABLE, JSON_INSTALLED#analysis:ignore
from happygisco.base import _Feature, _CachedResponse, _Decorator, _NestedDict
from happygisco import tools     
from happygisco.tools import GDAL_TOOL, GEOPANDAS_TOOL, FOLIUM_TOOL, LEAFLET_TOOL, WIDGET_TOOL
#from happygisco.tools import GDALTransform, LeafMap
from happygisco import services     
from happygisco.services import GISCO_SERVICE, API_SERVICE
#from happygisco.services import GISCOService, APIService
   
# requirements
try:
    assert ASYNCIO_AVAILABLE                             
except:
    import requests # urllib2
    class aiohttp():
        class ClientResponse():
            pass
else:
    import aiohttp
    class requests():
        class codes():
            ok = 200
        class Response():
            pass

try:    
    assert JSON_INSTALLED
except AssertionError:
    class json:
        def loads(arg):  return '%s' % arg
else:
    try:                          
        import simplejson as json
    except ImportError:
        import json

try:
    assert GDAL_TOOL
except AssertionError:
    # we want the decorators used in NUTS to run...
    class ogr():
        class Feature():
            pass
        class Layer():
            pass
else:
    from osgeo import ogr
        
try:
    assert GEOPANDAS_TOOL
except AssertionError:
    pass
else:
    import geopandas
    
try:
    assert LEAFLET_TOOL
except AssertionError:
    try:
        assert FOLIUM_TOOL
    except AssertionError:
        pass
    else:
        import folium#analysis:ignore
else:
    import ipyleaflet#analysis:ignore
    
try:
    assert WIDGET_TOOL
except AssertionError:
    pass
else:
    import ipywidgets # as widgets
    

#%%
#==============================================================================
# ENLARGE YOUR _Feature
#==============================================================================
            
# let us complement the definition of _Feature

#/****************************************************************************/
def __projection(inst, proj):
    if proj is None:
        pass
    elif not (happyType.isstring(proj) or happyType.isnumeric(proj)):
        raise happyError('wrong type for PROJ property')
    elif not proj in happyType.seqflatten(list(settings.GISCO_PROJECTIONS.items())):
        raise happyError('projection PROJ not recognised')
    inst._Feature__projection = proj
_Feature.projection = _Feature.projection.setter(__projection)

def __lat(inst):
    try:
        lat = inst.coord[0]
    except:
        try:
            lat = inst.coord.get(_Decorator.KW_LAT)
        except:  # AttributeError
            raise happyError('coordinates parameter not set')
    return lat if lat is None or happyType.isnumeric(lat) or len(lat)>1 else lat[0]
try:
    _Feature.lat = property(__lat) 
except:
    pass

def __Lon(inst):
    try:
        Lon = inst.coord[1]
    except:
        try:
            Lon = inst.coord.get(_Decorator.KW_LON)
        except:  # AttributeError
            raise happyError('coordinates parameter not set')
    return Lon if Lon is None or happyType.isnumeric(Lon) or len(Lon)>1 else Lon[0]
try:
    _Feature.Lon = property(__Lon) 
except:
    pass
    
def __coordinates(inst):  
    try:            
        return [_ for _ in zip(inst.lat, inst.Lon)]
    except:
        return [inst.lat, inst.Lon]
try:
    _Feature.coordinates = property(__coordinates) 
except:
    pass

def __service(inst, service):
    if not (service is None or isinstance(service,(services.GISCOService, services.APIService, services.OSMService))):
        raise happyError('wrong type for SERVICE property')
    inst._Feature__service = service # we override the private attribute here
try:
    _Feature.service = _Feature.service.setter(__service)
except:
    pass

def __transform(inst, transform):
    if not (transform is None or isinstance(transform,tools.GDALTransform)):
        raise happyError('wrong type for TRANSFORM property')
    inst._Feature__transform = transform
try:
    _Feature.transform = _Feature.transform.setter(__transform)
except:
    pass
 
def __mapping(inst, mapping):
    if not (mapping is None or isinstance(mapping,tools.LeafMap)): # ipyleaflet.Map, folium.Map
        raise happyError('wrong type for MAPPING property')
    inst._Feature__mapping = mapping
try:
    _Feature.mapping = _Feature.mapping.setter(__mapping)
except:
    pass
  
#/****************************************************************************/
def __init(inst, *args, **kwargs):
    try:
        assert API_SERVICE or GISCO_SERVICE
    except:
        happyWarning('external API and GISCO services not available')
    else:
        coder = kwargs.pop(_Decorator.KW_CODER, settings.CODER_GISCO)
        proj = kwargs.pop(_Decorator.KW_PROJECTION, None)
        if coder is None: # whatever works
            try:
                assert GISCO_SERVICE is True
                inst.service = services.GISCOService(coder=coder)
            except:
                try:
                    assert API_SERVICE is True
                    inst.service = services.APIService(coder=coder)
                except:
                    raise IOError('no service available')
        elif isinstance(coder,str):
            if coder in services.GISCOService.CODER:
                inst.service = services.GISCOService(coder=coder)
            elif coder in services.APIService.CODER:
                inst.service = services.APIService(coder=coder)
            else:
                raise IOError('service %s not available' % coder)
        if proj is None:
            try:
                proj = settings.CODER_PROJECTIONS[coder]
            except:
                proj = settings.DEF_GISCO_PROJECTION
        inst.projection = proj
        #if not isinstance(inst.service,(services.GISCOService,services.APIService)):
        #    raise IOError('service %s not supported' % coder)
    try:
        assert GDAL_TOOL
    except:
        happyWarning('GDAL transform utilities not available')
    else:
        try:
            _kwargs = kwargs.copy()
        except:
            happyWarning('basic transform available')
            inst.mapping = tools.GDALTransform()
        else:
            inst.transform = tools.GDALTransform(**_kwargs)
    try:
        assert LEAFLET_TOOL
    except:
        happyWarning('folium mapping services not available')
    else:
        try:
            _kwargs = inst.service.tile_info(**kwargs)
            if kwargs.pop(_Decorator.KW_TILE,None) == 'osmec':
                _kwargs.update({'_keep_base_': True})
        except:
            happyWarning('basic mapping available')
            inst.mapping = tools.LeafMap()
        else:
            inst.mapping = tools.LeafMap(**_kwargs)
try:
    _Feature.__init__ = __init
except:
    pass
     
#%%
#==============================================================================
# CLASS Location
#==============================================================================
            
class Location(_Feature):
    """Generic class used so to define a geolocation, *e.g.* a (topo)name or a 
    set of geographic coordinates.
        
        >>> loc = features.Location(*args, **kwargs)
    
    Arguments
    ---------
    place : str, tuple[str]
        a string defining a location name, *e.g.* of the form :literal:`locality, country`,
        for instance :literal:`Paris, France`; possibly left empty, so as to consider the 
        keyword argument :data:`place` in :data:`kwargs`, otherwise ignored.
    coord : float, tuple[float]
        a pair of (tuple of) floats, defining the :literal:`(lat,Lon)` coordinates,
        for instance 48.8566 and 2.3515 to locate Paris; possibly left empty, so as 
        to consider the keyword argument :literal:`place` in :data:`kwargs`.
        
    Keyword arguments
    -----------------
    radius : float
        accuracy radius around the geolocation :data:`coord` (or :data:`place`); 
        default: :data:`radius` is set to 0.001km, *i.e.* 1m.
    """

    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def __init__(self, *args, **kwargs):
        self.__place, self.__coord, self.__geom = [''], [], []
        self.__nuts = None
        # kwargs.pop('order',None)
        super(Location,self).__init__(*args, **kwargs)
        self.place = kwargs.pop(_Decorator.KW_PLACE, None)
        self.coord = kwargs.pop(_Decorator.KW_COORD, None)
        # set additional parameters... only PROJECTION so far
        defkw = _Decorator.parse_default(['PROJECTION'])(lambda **kw: kw)()
        for key in defkw.keys(): 
            attr = kwargs.pop(key, defkw.get(key))
            try:
                assert attr not in (None,[],{},'')
            except: pass
            else:
                setattr(self, key, attr) # may raise an Error

    #/************************************************************************/
    @property
    def place(self):
        """Place property (:data:`getter/setter`/:data:`setter`) of a :class:`Location` 
        instance. A `place` type is  (a list of) :class:`str`.
        """
        if self.__place in ('',[''],None):
            try:
                place = self.reverse()
            except:     
                raise happyError('place not found') 
            else:
                self.__place = place
        return self.__place if self.__place in ('',None) or len(self.__place)>1     \
            else self.__place[0]    
    @place.setter
    def place(self,place):
        try:
            assert place is not None
            place = _Decorator.parse_place(lambda p: p)(place)
        except AssertionError:
            return
        except:
            raise happyError('unrecognised address/location argument') 
        if not happyType.issequence(place):
            place = [place,]
        self.__place = place

    #/************************************************************************/
    @property
    def coord(self):
        """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`/:data:`setter`) 
        of a :class:`Location` instance.
        """ 
        if self.__coord in ([],[None,None],None):
            try:
                coord = self.geocode(unique=True)
            except:     
                raise happyError('coordinates not found') 
            else:
                self.__coord = coord
        return self.__coord if self.__coord is None or len(self.__coord)>1  \
            else self.__coord[0]    
    @coord.setter
    def coord(self,coord):
        try:
            assert coord is not None
            coord = _Decorator.parse_coordinates(lambda c: c)(coord)
        except AssertionError:
            return
        except:
            raise happyError('unrecognised coordinates argument') 
        if not happyType.issequence(coord):
            coord = [coord,]
        self.__coord = coord
        
    #/************************************************************************/
    def __get_geometry(self, **kwargs):
        #ignore-doc
        # build a vector geometry upon the geographical coordinates represented
        # by this instance. 
        try:
            return self.transform.coord2geom(self.coord, **kwargs)
        except:     
            raise happyError('unable to build a vector geometry upon given coordinates') 
    
    #/************************************************************************/
    def __get_nuts(self, **kwargs):
        #ignore-doc
        # find NUTS identifier associated to the geolocations of the current
        # :class:`Location` instance.
        #    >>> nuts = self.whichnuts(**kwargs)
        try:        
            assert GDAL_TOOL and isinstance(self.transform, tools.GDALTransform)
            feat = self.transform.coord2feat(self.coord, **kwargs)
        except:
            try:        
                assert GISCO_SERVICE and isinstance(self.service, services.GISCOService)
                feat = self.service.coord2nuts(self.coord, **kwargs)
            except:
                happyError('error while identifying NUTS')
        if feat in (None,[]):
            return feat
        elif not happyType.issequence(feat):
            feat = [feat,]
        try:
            nuts = [f[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_ID] for f in feat]
        except:
            try:
                nuts = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_FID]  for f in feat]
            except:
                try:
                    nuts = [ff[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_FID] \
                                 for f in feat                                         \
                                 for ff in f[_Decorator.parse_nuts.KW_FEATURES]]                          
                except:
                    nuts = feat # geom = geom.ExportToJson()
        return nuts if len(nuts)>1 else nuts[0] 
    
    #/************************************************************************/
    @property
    def nuts(self):
        """NUTS property (:data:`getter`) of a :class:`Location` instance.
        This is the identifier of the NUTS actually containing this instance.
        """ 
        if self.__nuts in ([],None):
            try:
                nuts = self.__get_nuts()
            except:     
                pass
            else:
                self.__nuts = nuts
        return self.__nuts if self.__nuts is None or (happyType.issequence(self.__nuts) and len(self.__nuts)>1)    \
            else self.__nuts[0]

    #/************************************************************************/
    @property
    def lau(self):
        """LAU property (:data:`getter`) of a :class:`Location` instance.
        This is the identifier of the LAU actually containing this instance.
        """ 
        pass
    
    #/************************************************************************/
    @property
    def geometry(self):
        """Geom(etry) property (:data:`getter`) of a :class:`Location` instance.
        It is generally defined as multipoint geometry (:class:`ogr.Geometry`) 
        featuring all the points listed in this instance.
        """ 
        if self.__geom in ([],None):
            try:
                geom = self.__get_geometry()
            except:     
                happyWarning('Geometry not available') 
                return
            else:
                self.__geom = geom
        return self.__geom if self.__geom is None or (happyType.issequence(self.__geom) and len(self.__geom)>1 ) \
            else self.__geom[0]         

    #/************************************************************************/
    def __repr__(self):
        try:
            return [','.join(p.replace(',',' ').split()) for p in self.place]
        except:
            return ''

    #/************************************************************************/
    def findnuts(self, **kwargs):  
        """Identify the NUTS area of the current location.
        
            >>> id = loc.findnuts(**kwargs)
            
        Keyword arguments
        -----------------
        kwargs :
            see method :meth:`services.GISCOService.coord2nuts`.
            
        Returns
        -------
        id : dict,str
            idenfier(s) representing the NUTS areas; when one level is requested,
            a single string identifier is returned, otherwise a dictionary indexed 
            by the NUTS level is returned.

        Raises
        ------
        happyError 
            when unable to identify NUTS region.
            
        Example
        -------
        
            >>> location = features.Location(place="Lisbon, Portugal")
            >>> location.findnuts()
                {0: 'PT', 1: 'PT1', 2: 'PT17', 3: 'PT170'}
            >>> location.findnuts(level=3)
                'PT170'
                
        See also
        --------
        :meth:`services.GISCOService.coord2nuts`.
        """
        id_ = self.__get_nuts(**kwargs)
        if happyType.isstring(id_):
            return id_
        elif happyType.issequence(id_) and all([happyType.isstring(i) for i in id_]):
            return {sum(c.isdigit() for c in i):i for i in id_}
        
    #/************************************************************************/
    def geocode(self, **kwargs):   
        """Convert the object place name to geographic coordinates using the 
        service used to initialise this instance.
        
            >>> coord = loc.geocode(**kwargs)
        
        Keyword arguments
        -----------------        
        kwargs : dict  
            see keyword arguments of the (various) :meth:`place2coord` methods.

        Returns
        -------
        coord : list
            a list/tuple of :literal:`(lat,Lon)` geographic coordinates associated
            to the :data:`place` attribute of the :class:`Location` object :data:`loc`.

        Raises
        ------
        happyError
            when unable to recognize address/location.

        Example
        -------

            >>> loc = features.Location(place='Paris, France', service='GoogleV3')
            >>> print loc.geocode()
                (48.856614, 2.3522219)
            >>> paris = features.serv.coord2place('48.85693, 2.3412')
            >>> print paris
                [u'76 Quai des Orf\xe8vres, 75001 Paris, France', u"Saint-Germain-l'Auxerrois, Paris, France", 
                 u'75001 Paris, France', u'1er Arrondissement, Paris, France', u'Paris, France', 
                 u'Paris, France', u'\xcele-de-France, France', u'France']
            >>> paris == features.serv.code(48.85693, 2.3412, reverse=True)
                True

        Note
        ----
        The output of the :meth:`geocode` method will not coincide with the :data:`coord`
        attribute of the considered instance in the case the latter was parsed for its 
        initialisation.
        
        See also
        --------
        :meth:`services.OSMService.place2coord`, :meth:`services.GISCOService.place2coord`, 
        :meth:`services.APIService.place2coord`, :meth:`~Location.reverse`.
        """
        try:
            assert self.__place not in ('',[''],None)
        except AssertionError:
            raise happyError('place not set') 
        else:
            try:
                return self.service.place2coord(place=self.__place, **kwargs)
            except:     
                raise happyError('unable to retrieve coordinates from place (address/location)') 

    #/************************************************************************/
    def reverse(self, **kwargs):
        """Convert the object geographic coordinates to a place (topo)name using the 
        service used to initialise this instance. 
       
            >>> place = loc.reverse(**kwargs)

        Keyword arguments
        -----------------
        kwargs : dict  
            see keyword arguments of the :meth:`coord2place` methods.

        Returns
        -------
        place : str
            a place (topo)name.        

        Raises
        ------
        happyError
            when unable to recognise coordinates.

        Example
        -------
        The user can use this method to retrieve the place(s) associated to any
        given geolocation(s): 
            
            >>> loc = features.Location('48.85693, 2.3412')
            >>> paris = loc.reverse()
            >>> paris
                [u'76 Quai des Orf\xe8vres, 75001 Paris, France', u"Saint-Germain-l'Auxerrois, Paris, France", 
                 u'75001 Paris, France', u'1er Arrondissement, Paris, France', u'Paris, France', 
                 u'Paris, France', u'\xcele-de-France, France', u'France']

        Notes
        -----
        * The output of the :meth:`reverse` method will not coincide with the :data:`place`
          attribute of the considered instance in the case the latter was parsed for its 
          initialisation.
        * The :meth:`reverse` may return no results in the case the :literal:`(lat,Lon)` 
          geographic coordinates defined in the :data:`coord` attribute represent a 
          *"remote"* location.
        
        See also
        --------
        :meth:`services.OSMService.coord2place`, :meth:`services.GISCOService.coord2place`, 
        :meth:`services.APIService.coord2place`, :meth:`~Location.geocode`.
        """
        # geocode may return no results if it is passed a  
        # non-existent address or a lat/lng in a remote location
        # raise LocationError('unrecognised location argument') 
        try:
            assert self.__coord not in ([],[None,None],None)
        except AssertionError:
            raise happyError('coordinates not set') 
        else:
            try:
                return self.service.coord2place(coord=self.__coord, **kwargs)
            except:     
                raise happyError('unable to retrieve place (address/location) from coordinates') 
    
    #/************************************************************************/
    def distance(self, loc, **kwargs):            
        """Compute pairwise distances between this instance location and other locations 
        parsed indifferently as places names or geographic coordinates.
        
            >>> D = loc.distance(loc, **kwargs)
    
        Arguments
        ---------
        loc : list,str,:class:`~features.Location`
            a location represented either as another instance of :class:`Location`,
            a tuple of (lat,Lon) coordinates or a place name expressed as a string.
            
        Keyword arguments
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
        happyError
            when wrong unit/code for geodesic distance or when unable to find/recognize
            locations.
            
        Examples
        --------      
        Let us compute some distances between geolocations expressed as either place 
        names or geographical coordinates:

            >>> loc = features.Location([26.062951, -80.238853], service='GISCO')
            >>> print(loc.distance([26.060484,-80.207268], dist='vincenty', unit='m'))
                3172.3596179302895
            >>> print(loc.distance([26.060484,-80.207268], dist='great_circle', unit='km'))
                3.167782321855102
            >>> print(loc.distance('Paris, France', dist='great_circle', unit='km'))
                7338.5353364838438
                
        Note
        ----
        Depending on the service parsed to initialise this instance, the method
        used for the effective distance calculation may be either the :meth:`distance`
        method of the |geopy| package or the :meth:`distance method of the |Google_Maps|
        API.
        
        See also
        --------
        :meth:`services._googleMapsAPI.distance`, :meth:`tools.GeoCoordinate.distance`.
        """
        if isinstance(loc, Location):
            coord = loc.coord
        else:
            func = lambda *a, **kw: [kw.pop(_Decorator.KW_PLACE, None), kw.pop(_Decorator.KW_COORD, None)]
            try:
                place, coord = _Decorator.parse_place_or_coordinate(func)(loc, **kwargs)
            except:
                pass
            else:
                if coord in ([],None):
                    coord = self.service.place2coord(place, unique=True)
        try:
            assert not coord in ([],None)
        except:
            raise happyError('unable to retrieve location coordinates') 
        try:
            return self.service.distance(self.coord, coord, **kwargs)
        except:
            return tools.GeoCoordinate.distance(self.coord, coord, **kwargs)
    
    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def routing(self, *args, **kwargs):
        """Compute the route starting at this instance location and going through
        the various steps/destinations represented by a list of (topo) name(s) or
        geographic coordinates. 
            
            >>> route, waypoints = loc.routing(*args, **kwargs)
    
        Arguments
        ---------
        args : list, list[str]
            list of locations represented either as list of :literal:`(lat,Lon)` 
            geographic coordinates or string of place (topo)name(s).
            
            
        Keyword arguments
        -----------------
        kwargs : dict
            see method :meth:`services.GISCOService.coord2route`.
            
        Returns
        -------
        route, waypoints : 
            shortest route and waypoints along the route; see :meth:`services.GISCOService.coord2route`
            method.
            
        Note
        ----
        This method is available only when the service parsed to initialise this
        instance is an instance of :class:`services.GISCOService` class.

        See also
        --------
        :meth:`services.GISCOService.coord2route`, :meth:`services.GISCOService.place2route`.
        """
        if not (GISCO_SERVICE and isinstance(self.service, services.GISCOService)):
            happyWarning('routing method available only with GISCO service')
            return
        try:
            place = kwargs.pop(_Decorator.KW_PLACE)
        except:
            coord = kwargs.pop(_Decorator.KW_COORD)
        else:
            coord = self.service.place2coord(place)
        coord = [self.coord,] + coord
        return self.service.coord2route(coord=coord, **kwargs)

    #/************************************************************************/
    @_Decorator.parse_projection
    def convert(self, **kwargs):
        """Convert the geolocations of the current instance to another spatial
        reference system (projection). 
       
            >>> new_loc = loc.convert(**kwargs)
        
        Keywords arguments
        ------------------
        proj : str,int
            spatial reference system in which the geographical coordinates will
            be projected.
            
        Returns
        -------
        new_loc : :class:`Location`
            geolocation whith coordinates equivalent to that of the current instance
            within the spatial reference system :data:`proj`.

        Raises
        ------
        happyError
            when unable to convert the instance geographical coordinates.
        
        See also
        --------
        :meth:`GISCOService.coordconvert`.
        """
        iproj = self.projection
        oproj = kwargs.pop(_Decorator.KW_PROJECTION,None)
        if oproj == iproj:
            happyWarning('identical projection system... nothing to do')
            _kwargs = {_Decorator.KW_COORD:         self.coord,
                       _Decorator.KW_PROJECTION:    iproj}
        else:
            try:
                new_coord = self.service.coordconvert(self.__coord, iproj = iproj, oproj = oproj)
            except:     
                raise happyError('unable to convert the current coordinates') 
            _kwargs = {_Decorator.KW_COORD:         new_coord,
                       _Decorator.KW_PROJECTION:    oproj}                
        return Location(**_kwargs)
     
    #/************************************************************************/
    def isnuts(self, nuts):
        """Check the identifier of the NUTS the current geolocation/instance
        belongs to.
            
            >>> ans = loc.isnuts(nuts)
            
        Arguments
        ---------
        nuts : str,:class:`features.NUTS`
            a string representing a NUTS identifier (*e.g.* something like 'ES30' 
            for the Comunidad de Madrid), or an instance of :class:`features.NUTS`.
            
        Returns
        -------
        ans : bool
            :data:`True` if the location belongs to the NUTS geometry represented
            by :data:`nuts` (whatever NUTS level), :data:`False` otherwise.
            
        Raises
        ------
        happyError
            when a wrong argument is parsed as the input NUTS identifier

        See also
        --------
        :meth:`~Location.findnuts`, :meth:`~Location.iscontained`.
        """
        if isinstance(nuts, NUTS): # features.NUTS
            fid = nuts.fid
        elif not happyType.isstring(nuts)   \
                or (happyType.issequence(nuts) and all([happyType.isstring(n) for n in nuts])):
            raise happyError('wrong type for input NUTS identifier')
        if not happyType.issequence(fid):
            fid = [fid,]
        nuts = self.nuts
        if not happyType.issequence(nuts):
            nuts = [nuts,]
        return any([id_ in fid for id_ in nuts])
     
    #/************************************************************************/
    def iscontained(self, layer):
        """Check whether the current geolocation/instance is contained in the geometry
        defined by a given layer.
            
            >>> ans = loc.iscontained(layer)
            
        Arguments
        ---------
        layer : :class:`osgeo.ogr.Layer`
            input vector layer to test.

        Returns
        -------
        ans : bool
            :data:`True` if the location belongs to the NUTS geometry represented
            by :data:`nuts` (whatever NUTS level), :data:`False` otherwise.

        Raises
        ------
        happyError
            when it is impossible to establish relationship

        See also
        --------
        :meth:`~Location.geometry`, :meth:`~Location.isnuts`, 
        :meth:`NUTS.contains`, :meth:`tools.GDALTransform.lay2fid`. 
        """
        #if not (GDAL_TOOL and isinstance(self.transform, tools.GDALTransform)):
        #    happyWarning('method available only with GDAL tool')
        #    return
        try:
            # geom = self.transform.coord2geom(self.coord, **kwargs)
            fid = self.transform.lay2fid(layer, self.geometry)
        except:
            raise happyError('impossible to establish relationship')
        if fid in ((),[],None)  \
                or (isinstance(fid,list) and all([id_ is None for id_ in fid])):
            return False
        else:
            return True

#%%
#==============================================================================
# CLASS NUTS
#==============================================================================
       
class NUTS(_Feature):
    """Class representing a |NUTS| geometry and defining simple description of its
    contents.
        
        >>> nuts = features.NUTS(*args)
    
    Arguments
    ---------
    nuts : dict, list[dict]
        a (list of) dictionary(ies) representing a single NUTS geometry.
        
    Notes
    -----
    Bulk datasets:
        
    * bulk download: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/
    * list of datasets: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/datasets.json
    * `units 2016 <http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/nuts-2016-units.html>`_
      listed in the `json file <http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/nuts-2016-units.json>`_.
    """
            
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        # dump whatever is in args into kwargs so as to simplify the process
        if args not in ((),(None,)):
            kwargs.update({_Decorator.KW_CONTENT: args[0] if len(args)==0 and happyType.issequence(args) else args}) 
            args = ()
        # we need to declare them beforehand, unless we use the mangled method...
        self.__dimensions = []
        self.__unit = ['']
        self.__file, self.__url = [''], ['']
        self.__layer, self.__feat, self.__geom = [], [], []
        self.__response, self.__content = [], []
        self.__level, self.__scale = [], []
        self.__year, self.__name = [], ['']        
        super(NUTS,self).__init__(**kwargs)        
        # initialise the attributes of the NUTS feature 
        items = []
        for key in settings.GISCO_DATA_INPUT:
            kw = getattr(_Decorator, 'KW_' + key)
            # kw = '_' + kw if key in ('RESPONSE','CONTENT') else kw   
            attr = kwargs.pop(kw, None)
            try:
                assert attr not in (None,[],{},'')
            except AssertionError: # note: force mangling
                #setattr(self, self.__mangled_attr(kw), None)                
                setattr(self, kw, None)   
            else:
                items.append(key)
                #setattr(self, self.__mangled_attr(kw), attr) 
                setattr(self, kw, attr)   
        # check that one at least is parsed
        try:
            assert len(items) == 1
        except AssertionError:
            try:
                assert items == [] 
            except AssertionError:
                raise happyError('incompatible keyword arguments parsed')
            else:   
                happyVerbose('no arguments parsed - NUTS initialised but not defined') 
                pass
        else:
            items = items[0]
        for key in settings.GISCO_DATA_DIMENSIONS:
            kw = getattr(_Decorator, 'KW_' + key)
            attr = kwargs.pop(kw, None)
            try:
                assert attr not in (None,[],{},'')
            except AssertionError:                 
                pass   
            else:
                # setattr(self, self.__mangled_attr(kw)), attr) 
                setattr(self, kw, attr)   
            
    #/************************************************************************/
    def __mangled_attr(self, attr):
        #ignore-doc
        return '_%s__%s' % (self.__class__.__name__, attr)
    
    ##/************************************************************************/
    #def __getattr__(self, attr_name): 
    #    # ignore-doc
    #    try:
    #        return super(NUTS,self).__getattribute__(attr_name) 
    #    except AttributeError:
    #        try:
    #            attr = [n[attr_name] for n in getattr(self, '__' + _Decorator.KW_GEOMETRY)]
    #            assert not attr in ([],[None])
    #        except:
    #            raise AttributeError('attribute %s not known' % attr_name)
    #        else:
    #            return attr if attr is None or len(attr)>1 else attr[0]

    #/************************************************************************/    
    @_Decorator.parse_url
    @_Decorator.parse_geometry
    @_Decorator._parse_class((str,dict), _Decorator.KW_CONTENT)
    #@_Decorator.parse_year
    #@_Decorator.parse_projection
    #@_Decorator.parse_scale
    #@_Decorator.parse_vector
    #@_Decorator.parse_level
    def __get_dimensions(self, **kwargs):
        #ignore-doc
        content = kwargs.pop(_Decorator.KW_CONTENT, None)
        geom = kwargs.pop(_Decorator.KW_GEOMETRY, None)
        url = kwargs.pop(_Decorator.KW_URL, None)
        unit = kwargs.pop(_Decorator.KW_UNIT, None)
        _argsNone = [1 for arg in (content, url, geom, unit) if arg in ('',None)]
        try:
            assert sum(_argsNone) >= 2
        except:
            raise happyError('incompatible arguments %s, %s and %s - parse one only' % \
                             (_Decorator.KW_CONTENT.upper(),_Decorator.KW_GEOMETRY.upper(),_Decorator.KW_URL.upper()))        
        if sum(_argsNone) == 4: # all None
            try:
                assert self.__geom # getattr(self, self.__mangled_attr(_Decorator.KW_GEOMETRY))
            except (AssertionError,AttributeError):
                try:
                    assert self.__content # getattr(self, self.__mangled_attr(_Decorator.KW_CONTENT))
                except (AssertionError,AttributeError):
                    try:
                        assert self.__url # getattr(self, self.__mangled_attr(_Decorator.KW_URL))
                    except (AssertionError,AttributeError):
                        try:
                            assert self.__unit # getattr(self, self.__mangled_attr(_Decorator.KW_UNIT))
                        except AssertionError:
                            pass
                        else:
                            unit = self.__unit
                    else:
                        url = self.__url
                else:
                    content = self.__content
            else:
                geom = self.__geom
        dimensions = []
        # let us define the default dimensions (those in settings.GISCO_DATA_DIMENSIONS)
        # e.g., [YEAR', 'PROJECTION', 'SCALE', 'VECTOR', 'LEVEL', 'FORMAT']
        defdim = _Decorator.parse_default(settings.GISCO_DATA_DIMENSIONS)(lambda **kw: kw)()
        [defdim.pop(getattr(_Decorator, 'KW_' + k),None) for k in ('SOURCE',)] # ('FORMAT','SOURCE')
        for key in defdim.keys():
            try:
                assert getattr(self, self.__mangled_attr(key)) # getattr(self, '__' + key)
            except:
                defval = None
            else:
                defval = getattr(self, key) 
            defdim.update({key: kwargs.get(key) or defval or defdim[key]})
        if unit in ([],'',None) and geom in ([],{},None) and content in ([],'',None) and url in ([],'',None):
            return [defdim,]
        if unit not in ([],'',None):
            dimensions = defdim.copy() 
            if (happyType.issequence(unit) and unit[0]!='NUTS')             \
                    or (happyType.isstring(unit) and unit!='NUTS'):
                #if not happyType.issequence(unit): 
                #    unit = [unit,]  
                try:
                    level = [sum(c.isdigit() for c in u) for u in unit]
                except:
                    raise happyError('impossible to define NUTS dimensions from input unit')
                else:
                    dimensions.update({_Decorator.KW_LEVEL: level if len(unit)>1 else level[0]})
            dimensions = [dimensions,]
        elif geom not in ([],None):
            if not happyType.issequence(geom): 
                geom = [geom,]  
            try:
                dimensions = [self.service.geom2dimension(g, **{_Decorator.KW_FORCE_LIST: True}) for g in geom]             
            except happyError as e:
                raise happyError(errtype=e)
            except:
                raise happyError('impossible to extract NUTS dimensions from input geometry')
        elif content not in ([],None):
            if not happyType.issequence(content): 
                content = [content,]  
            try:
                dimensions = [self.service.geom2dimension(c, **{_Decorator.KW_FORCE_LIST: True}) for c in content]             
            except happyError as e:
                raise happyError(errtype=e)
            except:
                raise happyError('impossible to extract NUTS dimensions from input content')
        elif url not in ([],'',None):
            if not happyType.issequence(url): 
                url = [url,]  
            try:
                dimensions = [self.service.url2dimension(u, **{_Decorator.KW_FORCE_LIST: True}) for u in url]             
            except happyError as e:
                raise happyError(errtype=e)
            except:
                raise happyError('impossible to extract NUTS dimensions from input URL')
        # [d.pop(k,None) for k in ('FORMAT',) for d in dimensions]
        if not (geom in ([],None) and content in ([],None)):
            [d.update({kw: d.get(kw) or defdim[kw]}) for kw in defdim.keys() for d in dimensions]
        # dimensions = _NestedDict([d.items() for d in dimensions])
        # test on projection
        try:
            assert len(set([d.get(_Decorator.KW_PROJECTION) for d in dimensions])) <=1
        except:
            raise happyError('currently, one projection per NUTS feature only is supported')
        return dimensions # if len(dimensions)>1 else dimensions[0]
   
    #/************************************************************************/    
    def __get_dimension(self, key, **kwargs): 
        #ignore-doc
        # Retrieve the dimension
        if key.upper() in ('UNIT','SOURCE'):
            happyWarning('keys %s and %s not used as dimensions' % ('UNIT','SOURCE'))
            return
        try:
            kw = getattr(_Decorator, 'KW_' + key.upper())
        except AttributeError:
            raise happyError('dimension %s not recognised' % key)
        dimensions = self._dimensions
        dimensions = [dimensions.copy(),] if happyType.ismapping(dimensions)    \
            else [d.copy() for d in dimensions]
        if kwargs != {}:
            [d.update(kwargs) for d in dimensions]     
        return [d.get(kw) for d in dimensions]

    #/************************************************************************/    
    def __get_unit(self, **kwargs): 
        #ignore-doc
        # Retrieve NUTS identifier
        return self.__get_dimension('SOURCE', **kwargs) # not 'UNIT'
    
    #/************************************************************************/    
    def __get_level(self, **kwargs): 
        #ignore-doc
        # Retrieve NUTS level
        return self.__get_dimension('LEVEL', **kwargs)
    
    #/************************************************************************/    
    def __get_scale(self, **kwargs): 
        #ignore-doc
        # Retrieve NUTS scale
        return self.__get_dimension('SCALE', **kwargs)
        
    #/************************************************************************/    
    def __get_year(self, **kwargs): 
        #ignore-doc
        # Retrieve NUTS year
        return self.__get_dimension('YEAR', **kwargs)
    
    ##/************************************************************************/    
    #def __get_projection(self, **kwargs): 
    #    """Retrieve NUTS projection.
    #    """     
    #    return self.__get_dimension('PROJECTION', **kwargs)

    #/************************************************************************/    
    @_Decorator._parse_class(str, _Decorator.KW_SOURCE)
    @_Decorator._parse_class(str, _Decorator.KW_UNIT)
    def __get_url(self, **kwargs):
        #ignore-doc
        source = kwargs.pop(_Decorator.KW_SOURCE, None)
        unit = kwargs.pop(_Decorator.KW_UNIT, None)
        #try:
        #    assert (source is None or happyType.isstring(source))           \
        #        and (unit is None or happyType.isstring(unit))
        #except:
        #    raise happyError('wrong format for SOURCE/UNIT arguments')
        try:
            assert source in ('',None) or unit in ('',None)
        except:
            raise happyError('incompatible arguments %s and %s - parse one only' % \
                             (_Decorator.KW_SOURCE.upper(),_Decorator.KW_UNIT.upper()))
        if source in ('',None) and unit in ('',None):
            try:
                assert self.__unit # getattr(self, self.__mangled_attr(_Decorator.KW_UNIT))
            except AssertionError:
                raise happyError('missing arguments %s and  %s - parse one at least' % \
                                 (_Decorator.KW_SOURCE.upper(),_Decorator.KW_UNIT.upper()))
            else:
                unit = self.unit
        source = source or unit
        if not happyType.issequence(source):
            source = [source,]       
        try:
            kwargs.update(self._dimensions)            
            url = [self.service.url_nuts(source=s, **kwargs) for s in source]         
        except:
            raise happyError('impossible to define URL from input data') 
        else:
            if not happyType.issequence(url):
                url = [url,]       
        return url

    #/************************************************************************/    
    @_Decorator._parse_class((_CachedResponse, aiohttp.ClientResponse,requests.Response), _Decorator.KW_RESPONSE)
    @_Decorator.parse_url
    def __get_file(self, **kwargs):
        #ignore-doc
        resp = kwargs.pop(_Decorator.KW_RESPONSE, None)
        url = kwargs.pop(_Decorator.KW_URL, None)
        try:
            assert resp in ([],None) or url in ('',[''],None)
        except:
            raise happyError('incompatible arguments %s and %s - parse one only' % \
                             (_Decorator.KW_RESPONSE.upper(),_Decorator.KW_URL.upper()))
        if resp in ('',None) and url in ('',None):
            try:
                assert self.__resp # getattr(self, self.__mangled_attr(_Decorator.KW_RESPONSE))
            except AssertionError:
                try:
                    assert self.__url # getattr(self, self.__mangled_attr(_Decorator.KW_URL))
                except AssertionError:
                    try:
                        url = self.__get_url(**kwargs) 
                        assert url not in  ('',[],None)
                    except:
                        raise happyError('missing arguments %s and  %s - parse one at least' % \
                                         (_Decorator.KW_RESPONSE.upper(),_Decorator.KW_URL.upper())) 
                else:
                    url = self.__url
            else:
                resp = self.__resp
        try:
            assert resp is not None
        except:
            try:
                resp = self.serv.get_response(url, **{_Decorator.KW_CACHING: True}) 
            except happyError as e:
                raise happyError(errtype=e)
            except:
                raise happyError('no reponse retrieved')
        if not happyType.issequence(resp):
            resp = [resp,]
        try:
            return [r._cache_path for r in resp]
        except:
            return []
        
    #/************************************************************************/    
    @_Decorator.parse_file
    @_Decorator.parse_url
    def __get_layer(self, **kwargs):
        #ignore-doc
        file, url =                         \
            kwargs.get(_Decorator.KW_FILE), kwargs.get(_Decorator.KW_URL)
        try:
            assert file in ('',None) or url in ('',None)
        except:
            raise happyError('incompatible arguments %s and %s - parse one only' % \
                             (_Decorator.KW_FILE.upper(),_Decorator.KW_URL.upper()))
        if file in ('',None) and url in ('',None):
            try:
                assert self.__file # getattr(self, self.__mangled_attr(_Decorator.KW_FILE))
            except AssertionError:
                try:
                    assert self.__url # getattr(self, self.__mangled_attr(_Decorator.KW_URL))
                except AssertionError:
                    try:
                        url = self.__get_url(**kwargs) 
                        assert url not in  ('',[],None)
                    except:
                        raise happyError('missing arguments %s and  %s - parse one at least' % \
                                         (_Decorator.KW_FILE.upper(),_Decorator.KW_URL.upper())) 
                else:
                    kwargs.update({_Decorator.KW_URL: self.url})
            else:
                kwargs.update({_Decorator.KW_FILE: self.file})
        try:
            layer = self.transform.get_layer(**kwargs)           
        except happyError as e:
            raise happyError(errtype=e)
        except:
            raise happyError('impossible to extract layer from input data')
        if not happyType.issequence(layer):
            layer = [layer,]            
        return layer
        
    #/************************************************************************/  
    @_Decorator.parse_file
    @_Decorator.parse_url
    @_Decorator._parse_class(ogr.Layer, _Decorator.KW_LAYER)
    def __get_feature(self, **kwargs):
        #ignore-doc
        file, layer, url =                  \
            kwargs.get(_Decorator.KW_FILE), kwargs.get(_Decorator.KW_LAYER), kwargs.get(_Decorator.KW_URL)
        _argsNone = [1 for arg in (file, url, layer) if arg in ('',None)]
        try:
            assert sum(_argsNone) >= 2
        except:
            raise happyError('incompatible arguments %s, %s and %s - parse one only' % \
                             (_Decorator.KW_FILE.upper(),_Decorator.KW_LAYER.upper(),_Decorator.KW_URL.upper()))
        if sum(_argsNone) == 3: # all None
            try:
                assert self.__layer # getattr(self, self.__mangled_attr(_Decorator.KW_LAYER)) 
            except AssertionError:
                try:
                    assert self.__file # getattr(self, self.__mangled_attr(_Decorator.KW_FILE))  
                except AssertionError:
                    try:
                        assert self.__url # getattr(self, self.__mangled_attr(_Decorator.KW_URL))
                    except AssertionError:
                        try:
                            url = self.__get_url(**kwargs) 
                            assert url not in  ('',[],None)
                        except:
                            raise happyError('missing arguments %s, %s and %s - parse one at least' % \
                                             (_Decorator.KW_FILE.upper(),_Decorator.KW_LAYER.upper(),_Decorator.KW_URL.upper())) 
                    else:
                        kwargs.update({_Decorator.KW_URL: self.url})
                else:
                    kwargs.update({_Decorator.KW_FILE: self.file})
            else:
                kwargs.update({_Decorator.KW_LAYER: self.layer})
        try:
            feature = self.transform.get_feature(**kwargs)           
        except happyError as e:
            raise happyError(errtype=e)
        except:
            raise happyError('impossible to extract vector features from input data')
        if not happyType.issequence(feature):
            feature = [feature,]            
        return feature

    #/************************************************************************/    
    #@_Decorator.parse_file
    @_Decorator.parse_url
    @_Decorator._parse_class(ogr.Feature, _Decorator.KW_FEATURE)
    def __get_geometry(self, **kwargs):
        #ignore-doc
        unit = kwargs.get(_Decorator.KW_UNIT) or kwargs.pop(_Decorator.KW_SOURCE, None)
        feature = kwargs.pop(_Decorator.KW_FEATURE, None)
        url = kwargs.pop(_Decorator.KW_URL, None)
        _argsNone = [1 for arg in (unit, feature, url) if arg in ('',None)]
        try:
            assert sum(_argsNone) >= 2
        except:
            raise happyError('incompatible arguments %s, %s and %s - parse one only' % \
                             (_Decorator.KW_UNIT.upper(), _Decorator.KW_FEATURE.upper(),_Decorator.KW_URL.upper()))
        if sum(_argsNone) == 3:
            try:
                assert self.__feat # getattr(self, self.__mangled_attr(_Decorator.KW_FEATURE))
            except (AssertionError,AttributeError):
                try:
                    assert self.__unit # getattr(self, self.__mangled_attr(_Decorator.KW_UNIT))
                except AssertionError:
                    try:
                        assert self.__url # getattr(self, self.__mangled_attr(_Decorator.KW_URL))
                    except (AssertionError,AttributeError):
                        try:
                            url = self.__get_url(**kwargs) 
                            assert url not in  ('',[],None)
                        except:
                            raise happyError('incompatible arguments %s and %s - parse one at least' % \
                                             (_Decorator.KW_FEATURE.upper(),_Decorator.KW_URL.upper()))
                    else:
                        url = self.__url
                else:
                    kwargs.update(self._dimensions)
                    kwargs.update({_Decorator.KW_UNIT: self.unit})
            else:
                kwargs.update({_Decorator.KW_FEATURE: self.feature})
        elif unit not in ('', None):
            kwargs.update(**{_Decorator.KW_UNIT: unit})
        kwargs.update({_Decorator.KW_OFORMAT: kwargs.pop(_Decorator.KW_OFORMAT, 'JSON')})         
        try:
            geom = [self.service.nuts_geometry(**self.service.url2dimension(u)) for u in url]
            # geom = [self.service.read_url(u, **kwargs) for u in url]
        except: 
            try:
                geom = self.transform.get_geometry(**kwargs)           
            except: 
                try:
                    geom = self.service.nuts_geometry(**kwargs)
                except happyError as e:
                    raise happyError(errtype=e)
                except:
                    raise happyError('impossible to extract vector geometries from input data')
        if not happyType.issequence(geom):
            geom = [geom,]            
        return geom
                
    #/************************************************************************/
    @property
    def _content(self):
        #ignore-doc
        return self.__content if self.__content in ([],None) or len(self.__content)>1     \
            else self.__content[0]
    @_content.setter
    def _content(self, content):
        if content is None:
            return
        elif not happyType.issequence(content):
            content = [content,]
        try:
            assert all([happyType.isstring(c) or happyType.ismapping(c) for c in content])
        except:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_CONTENT.upper())
        if all([happyType.ismapping(c) for c in content]):
            content = [happyType.jsonstringify(c) for c in content]
        func = lambda *a, **kw: kw.get(_Decorator.KW_CONTENT)
        self.__content = [_Decorator.parse_nuts(func)(nuts=json.loads(c)) for c in content]

    #/************************************************************************/
    @property
    def _response(self):
        #ignore-doc
        return self.__resp if self.__resp in ([],None) or len(self.__resp)>1     \
            else self.__resp[0]
    @_response.setter
    def _response(self, resp):
        if resp is None:
            return
        elif not happyType.issequence(resp):
            resp = [resp,]
        try:
            assert all([isinstance(r,(_CachedResponse, aiohttp.ClientResponse, requests.Response)) for r in resp])
        except:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_RESPONSE.upper())
        else:
            self.__resp = resp
        
    #/************************************************************************/
    @property
    def _dimensions(self):
        #ignore-doc
        if self.__dimensions in ([],{},None):
            try:
                dimensions = self.__get_dimensions()
            except:
                dimensions = None
            else:
                self.__dimensions = dimensions
        return self.__dimensions if self.__dimensions in ({},None)                      \
            or (happyType.issequence(self.__dimensions) and len(self.__dimensions)>1)   \
            else self.__dimensions[0]
    @_dimensions.setter
    def _dimensions(self, dimensions):
        try:
            assert dimensions is None or happyType.ismapping(dimensions) or             \
                (happyType.issequence(dimensions) and all([happyType.ismapping(d) for d in dimensions]))
        except:
            raise happyError('wrong format for DIMENSIONS argument')
        if dimensions is not None and not happyType.issequence(dimensions):
                dimensions = [dimensions,]
        self.__dimensions = dimensions
        
    #/************************************************************************/
    @property
    def unit(self):
        """Unit property (:data:`setter`/:data:`getter`) of a :class:`NUTS` 
        instance, if any. This is a string or a list of strings. 
        """ 
        if self.__unit in ('',[''],None):
            try:
                unit = self.__get_unit()
            except:
                unit = None
            else:
                self.__unit = unit
        return self.__unit if self.__unit in ('',None) or (happyType.issequence(self.__unit) and len(self.__unit)>1)    \
            else self.__unit[0]
    @unit.setter
    def unit(self, unit):
        try:
            assert unit is None or happyType.isstring(unit) or              \
                (happyType.issequence(unit) and all([happyType.isstring(u) for u in unit]))
        except:
            raise happyError('wrong format for %s argument' % _Decorator.KW_UNIT.upper())
        if unit is not None and not happyType.issequence(unit):
            unit = [unit,]
        self.__geometry, self.__dimensions = None, None
        self.mapping.clear()
        self.__unit = unit
                
    #/************************************************************************/
    @property
    def url(self):
        """URL property (:data:`setter`/:data:`getter`) of a :class:`NUTS` 
        instance, if any. This is a string or a list of strings.
        """ 
        if self.__url in ('',[''],None):
            try:
                url = self.__get_url()
            except:
                pass
            else:
                self.__url = url
        return self.__url if self.__url in ('',None) or len(self.__url)>1        \
            else self.__url[0]    
    @url.setter
    def url(self, url):
        try:
            assert url is None or happyType.isstring(url) or                \
                (happyType.issequence(url) and all([happyType.isstring(u) for u in url]))
        except:
            raise happyError('wrong format for %s argument' % _Decorator.KW_URL.upper())
        if url is not None:
            if not happyType.issequence(url):
                url = [url,]
            try:
                assert all([self.service.get_status(u) == requests.codes.ok for u in url])
            except NameError:
                pass
            except:
                raise happyError('wrong URL argument')
        self.__url = url
    
    #/************************************************************************/
    @property
    def file(self):
        """File property (:data:`setter`/:data:`getter`) of a :class:`NUTS` 
        instance, if any. This is a string or a list of strings.
        """ 
        if self.__file in ([],[''],None):
            try:
                file = self.__get_file()
            except:
                # raise happyError('unable to retrieve vector layer') 
                pass
            else:
                self.__file = file
        return self.__file if self.__file is None or len(self.__file)>1     \
            else self.__file[0]    
    @file.setter
    def file(self, file):
        try:
            assert file is None or happyType.isstring(file) or              \
                (happyType.issequence(file) and all([happyType.isstring(f) for f in file]))
        except:
            raise happyError('wrong format for %s argument' % _Decorator.KW_FILE.upper())
        if file is not None and not happyType.issequence(file):
            file = [file,]
        self.__file = file
                
    #/************************************************************************/
    @property
    def layer(self):
        """Layer property (:data:`setter`/:data:`getter`) of a :class:`NUTS` instance.
        This is an object of type :class:`ogr.Layer`, or a list of such objects.
        """ 
        if self.__layer in ([],None):
            try:
                layer = self.__get_layer()
            except:
                # raise happyError('unable to retrieve vector layer') 
                pass
            else:
                self.__layer = layer
        return self.__layer if self.__layer is None or len(self.__layer)>1     \
            else self.__layer[0]     
    @layer.setter
    def layer(self, layer):
        try:
            assert GDAL_TOOL is True
            decorator = _Decorator._parse_class(ogr.Layer, _Decorator.KW_LAYER)
            func = lambda **kw: kw.get(_Decorator.KW_LAYER)
            layer = decorator(func)(**{_Decorator.KW_LAYER: layer})
        except AssertionError:
            pass
        except:
            raise happyError('wrong format for %s argument' % _Decorator.KW_LAYER.upper())
        if layer is not None and not happyType.issequence(layer):
            layer = [layer,]
        self.__layer = layer 

    #/************************************************************************/
    @property
    def feature(self):
        """Feature property (:data:`setter`/:data:`getter`) of a :class:`NUTS` instance.
        This is an object of type :class:`ogr.Feature`, or a list of such objects.
        """ 
        if self.__feat in ([],None):
            try:
                feature = self.__get_feature()
            except:     
                #raise happyError('unable to retrieve feature vector') 
                pass
            else:
                self.__feat = feature
        return self.__feat if self.__feat is None or len(self.__feat)>1     \
            else self.__feat[0]   
    @feature.setter
    def feature(self, feature):
        try:
            assert GDAL_TOOL is True
            decorator = _Decorator._parse_class((ogr.Feature,list), _Decorator.KW_FEATURE)
            func = lambda **kw: kw.get(_Decorator.KW_FEATURE)
            feature = decorator(func)(**{_Decorator.KW_FEATURE: feature})
        except AssertionError:
            pass
        except:
            raise happyError('wrong format for %s argument' % _Decorator.KW_FEATURE.upper()) 
        if feature is not None and not happyType.issequence(feature):
            feature = [feature,]
        self.__feat = feature

    #/************************************************************************/
    @property
    def geometry(self):
        """Geometry property (:data:`setter`/:data:`getter`) of a :class:`NUTS` instance.
        This is a dictionary object, or an object of type :class:`base._NestedDict`, 
        or a list of such objects.
        """ 
        if self.__geom in ([],None):
            geom = self.__get_geometry() 
            try:
                geom = self.__get_geometry() 
            except:     
                #raise happyError('unable to retrieve feature') 
                pass
            else:
                self.__geom = geom
        if self.__geom not in ([],None): 
            #geom = [g.xvalues(**{_Decorator.KW_FORCE_LIST: True}) if isinstance(g, _NestedDict) else g \
            #        for g in self.__geom]
            geom = [g.xvalues() if isinstance(g, _NestedDict) else g \
                    for g in self.__geom]
            return geom if happyType.issequence(geom) and len(geom)>1 else geom[0]         
        else:
            return None
    @geometry.setter
    def geometry(self, geom):
        try:
            decorator = _Decorator._parse_class((str,dict,list), _Decorator.KW_GEOMETRY)
            # decorator = _Decorator._parse_class(None, _Decorator.KW_VECTOR)
            func = lambda **kw: kw.get(_Decorator.KW_GEOMETRY)
            geom = decorator(func)(**{_Decorator.KW_GEOMETRY: geom})
        except:
            raise happyError('wrong %s argument' % _Decorator.KW_GEOMETRY.upper()) 
        if geom is not None and not happyType.issequence(geom):
            geom = [geom,]
        try:
            geom_ = [happyType.jsonstringify(g) for g in geom]
        except:
            self.__geom = geom
        else:
            try:
                self.__geom = [_NestedDict(g) for g in geom_]
            except:
                self.__geom = geom_
         
    #/************************************************************************/    
    @property
    def coord(self):
        """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`) 
        of a :class:`NUTS` instance.
        This is an educated guess from the actual geometry NUTS name.
        """ 
        if self.__coord in ([],[None,None],None):
            try:
                coord = self.geocode(unique=True)
            except:     
                raise happyError('coordinates not found') 
            else:
                self.__coord = coord
        return self.__coord # if len(self.__coord)>1 else self.__coord[0]    

    #/************************************************************************/    
    @property
    def level(self):
        """Level property (:data:`getter`) of a :class:`NUTS` instance. 
        A `level` type is (a list of) :class:`int`.
        """
        if self.__level in ([],None):
            try:
                level = self.__get_level()
            except:     
                raise happyError('level not found') 
            else:
                self.__level = level
        return self.__level if self.__level is None or len(self.__level)>1  \
            else self.__level[0] 
    @level.setter
    def level(self, level):
        try:
            func = lambda **kw: kw.get(_Decorator.KW_LEVEL)
            level = _Decorator.parse_level(func)(**{_Decorator.KW_LEVEL: level})
        except:
            raise happyError('wrong %s argument' % _Decorator.KW_LEVEL.upper()) 
        if level is not None and not happyType.issequence(level):
                level = [level,]
        self.__level = level

    #/************************************************************************/    
    @property
    def year(self):
        """Year property (:data:`getter`) of a :class:`NUTS` instance. 
        A `year` type is (a list of) :class:`int`.
        """
        if self.__year in ([],None):
            try:
                year = self.__get_year()
            except:     
                raise happyError('year not found') 
            else:
                self.__year = year
        return self.__year if self.__year is None or len(self.__year)>1 else self.__year[0] 
    @year.setter
    def year(self, year):
        try:
            func = lambda **kw: kw.get(_Decorator.KW_YEAR)
            year = _Decorator.parse_year(func)(**{_Decorator.KW_YEAR: year})
        except:
            raise happyError('wrong %s argument' % _Decorator.KW_YEAR.upper()) 
        if year is not None and not happyType.issequence(year):
                year = [year,]
        self.__year = year

    #/************************************************************************/    
    @property
    def scale(self):
        """Scale property (:data:`getter`) of a :class:`NUTS` instance. 
        A `scale` type is (a list of) :class:`int`.
        """
        if self.__scale in ([],None):
            try:
                scale = self.__get_scale()
            except:     
                raise happyError('scale not found') 
            else:
                self.__scale = scale
        return self.__scale if self.__scale is None or len(self.__scale)>1 else self.__scale[0] 
    @scale.setter
    def scale(self, scale):
        try:
            func = lambda **kw: kw.get(_Decorator.KW_SCALE)
            scale = _Decorator.parse_scale(func)(**{_Decorator.KW_SCALE: scale})
        except:
            raise happyError('wrong %s argument' % _Decorator.KW_SCALE.upper()) 
        if scale is not None and not happyType.issequence(scale):
                scale = [scale,]
        self.__scale = scale
    
    #/************************************************************************/    
    @property
    def fid(self):
        """Feature identity property (:data:`getter`) of a :class:`NUTS` instance.
        """
        try:
            geom = self.geometry
        except:
            return None
        else:
            if not happyType.issequence(geom):
                geom = [geom,]
        try:
            fid = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_FID]     \
                   for f in geom]
        except:
            try:
                fid = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_FID] \
                             for g in geom                                         \
                             for f in g[_Decorator.parse_nuts.KW_FEATURES]]                          
            except:
                fid = None
        return fid if fid is None or len(fid)>1 else fid[0]
    
    #/************************************************************************/    
    @property
    def coordinates(self):
        try:
            geom = self.geometry
        except:
            return None
        else:
            if not happyType.issequence(geom):
                geom = [geom,]
        try:
            coord = [f[_Decorator.parse_nuts.KW_GEOMETRY][_Decorator.parse_nuts.KW_COORDINATES]     \
                   for f in geom]
        except:
            try:
                coord = [f[_Decorator.parse_nuts.KW_GEOMETRY][_Decorator.parse_nuts.KW_COORDINATES] \
                             for g in geom                                         \
                             for f in g[_Decorator.parse_nuts.KW_FEATURES]]                          
            except:
                coord = None
        return coord if coord is None or len(coord)>1 else coord[0]
    
    #/************************************************************************/    
    @property
    def name(self):
        """Name property (:data:`getter`) of a :class:`NUTS` instance. 
        A name type is :class:`str`.
        """
        try:
            geom = self.geometry
            assert geom not in ([],None)
        except:           
            try:
                cont = self._content
                assert cont is not None
            except:
                return None
            else:
                if not happyType.issequence(cont):
                    cont = [cont,]
                name = [c[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_NAME]          \
                        for c in cont]
        else:
            if not happyType.issequence(geom):
                geom = [geom,]
            try:
                name = [g[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_NUTS_NAME]      \
                            for g in geom]
            except:
                try:
                    name = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_NUTS_NAME]  \
                                 for g in geom                                                \
                                 for f in g[_Decorator.parse_nuts.KW_FEATURES]]                          
                except:
                    name = None
        finally:
            return name if name is None or len(name)>1 else name[0]
    
    #/************************************************************************/    
    @property
    def value(self):
        """Value property (:data:`getter`) of a :class:`NUTS` instance. 
        A value type is :class:`str`.
        """
        try:
            geom = self.geometry
            assert geom not in ([],None)
        except:           
            try:
                cont = self._content
                assert cont is not None
            except:
                return None
            else:
                if not happyType.issequence(cont):
                    cont = [cont,]
                value = [c[_Decorator.parse_nuts.KW_VALUE] for c in cont]
        else:
            if not happyType.issequence(geom):
                geom = [geom,]
            try:
                value = [g[_Decorator.parse_nuts.KW_VALUE] for g in geom]
            except:
                try:
                    value = [f[_Decorator.parse_nuts.KW_VALUE]                      \
                                 for g in geom                           \
                                 for f in g[_Decorator.parse_nuts.KW_FEATURES]]                          
                except:
                    value = None
        finally:
            return value if value is None or len(value)>1 else value[0]
    
    #/************************************************************************/    
    @property
    def place(self):
        """Place property of a :class:`NUTS` instance. This is actually a "shortcut"
        to :data:`name` property.
        """
        return self.name
    
    #/************************************************************************/
    def load(self, **kwargs):
        """Load the geometry stored in this NUTS instance.
        
            >>> data = nuts.load(**kwargs)
        
        Keyword arguments
        -----------------
        fmt : str
            flag providing the output format; any string in :data:`settings.NUTS_FORMATS`,
            *e.g.* :literal:`json, gpd, str`, is accepted so as to generally supported
            JSON (dictionary), :mod:`geopandas` and :type:`str` output formats.
        kwargs : dict
            any other keyword arguments used to filter the input geometry(ies),*e.g.*
            regarding source (unit), year, level, projection, scale and format of 
            the data.

        Raises
        ------
        happyError
            an error is raised when:
                * the load format is not recognised
                * some property is missing
                
        Example
        -------
                
        See also
        --------
        :meth:`~NUTS.loads`.
        """
        fmt = kwargs.pop(_Decorator.KW_OFORMAT, 'json')
        try:
            assert fmt in happyType.seqflatten(list(settings.NUTS_FORMATS.items()))
        except:
            raise happyError('loal format %s not recognised' % fmt)
        else:
            if fmt in settings.NUTS_FORMATS.keys():
                fmt = settings.NUTS_FORMATS[fmt]
            if fmt == 'gpd':
                try:
                    assert GEOPANDAS_TOOL
                except:
                    raise happyError('GEOPANDAS not installed - output GeoDataFrame not available')                    
        dimensions = self._dimensions
        dimensions = [dimensions.copy(),] if happyType.ismapping(dimensions)    \
            else [d.copy() for d in dimensions]
        # LEVEL is useless...
        [d.pop(_Decorator.KW_LEVEL,None) for d in dimensions]
        if kwargs != {}:
            if _Decorator.KW_UNIT in kwargs:
                kwargs.update({_Decorator.KW_SOURCE: kwargs.pop(_Decorator.KW_UNIT)}) 
            [d.update(kwargs) for d in dimensions] 
        # df = geopandas.read_file(self.url)
        # df = geopandas.GeoDataFrame(self.geom)
        try:
            assert self.__geom # getattr(self, self.__mangled_attr(_Decorator.KW_GEOMETRY))
        except AssertionError:
            try:
                if len(dimensions)>1:
                    dim = functools.reduce(lambda d1, d2:_NestedDict._deepmerge(d1, d2), dimensions)
                else:
                    dim = dimensions[0]
                geom = self.__get_geometry(**dim) 
                assert geom not in  ([],None)
            except:
                raise happyError('missing property %s' % _Decorator.KW_GEOMETRY.upper()) 
        else:
            geom = self.__geom
        try:
            for i, g in enumerate(geom):
                dimensions[i].update({_Decorator.KW_FORCE_LIST: True})
                geom[i] = g.xvalues(**dimensions[i]) if isinstance(g, _NestedDict) else g
        except:
            raise happyError('error when dumping arguments %s' % kwargs) 
        else:
            if len(geom) == 1 and happyType.issequence(geom[0]):
                geom = geom[0]
        #try:
        #    data = resp.content 
        #    data = json.loads(data.decode(chardet.detect(data)["encoding"]))
        #except:
        #    data = None
        #json.dumps(resp.json())
        if fmt in ('json','txt'):
            if fmt == 'txt':
                geom = [happyType.jsonstringify(g) for g in geom]
            return geom if (happyType.issequence(geom) and len(geom)>1) else geom[0]
        elif fmt == 'gpd':
            try:
                proj = self.__geom.dimensions[_Decorator.KW_PROJECTION]
                xlen = self.__geom.xlen()#analysis:ignore
            except:
                proj = self.projection
                xlen = len(geom)#analysis:ignore
            finally:
                if proj in settings.GISCO_PROJECTIONS.keys():
                    proj = settings.GISCO_PROJECTIONS[proj]
                crs = "+init=epsg:%s" % proj
            try:
                features = happyType.seqflatten([g['features'] for g in geom])
            except:
                features = geom[0]['features']
            finally:
                features = [f[0] if happyType.issequence(f) else f for f in features]
            return geopandas.GeoDataFrame.from_features(features, crs=crs)
            
    #/************************************************************************/
    def loads(self, **kwargs):
        """Load the geometry stored in this NUTS instance as a string. 

        Raises
        ------
        happyError
                
        See also
        --------
        :meth:`~NUTS.load`.
        """
        return self.load(**kwargs, **{_Decorator.KW_OFORMAT: 'txt'})
                    
    #/************************************************************************/
    def dump(self, **kwargs):
        pass
                    
    #/************************************************************************/
    def dumps(self, **kwargs):
        pass
        
    #/************************************************************************/
    def geocode(self, **kwargs):
        """Convert the NUTS name to geographic coordinates using the service defined 
        when initialising this instance.
            
            >>> coord = nuts.geocode(**kwargs)
            
        Keyword arguments
        -----------------
        kwargs : 
            see :meth:`place2coord` method.
            
        Returns
        -------
        coord : list, list[float]
            :literal:`(lat,Lon)` geographic coordinates associated to the name of
            this NUTS instance.

        Raises
        ------
        happyError
            
        Note
        ----
        The geographic coordinates output by the method :meth:`geocode` does not
        represent the centroid of the NUTS geometry. There is also no guarantee
        it is actually contained inside the NUTS geometry itself.
        
        See also
        --------
        :meth:`base._Service.place2coord`, :meth:`services.OSMService.place2coord`, 
        :meth:`services.GISCOService.place2coord`, :meth:`services.APIService.place2coord`.
        """
        try:
            return self.service.place2coord(place=self.name, **kwargs)
        except:     
            raise happyError('unable to retrieve coordinates from NUTS name') 
        
    #/************************************************************************/
    def identify(self, *args, **kwargs):
        """
        """
        func = lambda *a, **kw: [kw.pop(_Decorator.KW_PLACE), kw.pop(_Decorator.KW_COORD)]
        try:
            place, coord = _Decorator.parse_place_or_coordinate(func)(*args, **kwargs)          
        except:
            pass
        else:
            if coord in ([],None):
                coord = self.service.place2coord(place)        
        
    #/************************************************************************/
    def contains(self, *args, **kwargs):
        """Check whether the current NUTS geometry contains a given geolocation,
        expressed as either a place name or a set of geographical coordinates.
            
            >>> ans = nuts.contains(*args, **kwargs)
            
        Arguments
        ---------
        place : str
            toponame; possibly left empty, so as to consider the keyword argument 
            :data:`place` in :data:`kwargs` (see below), otherwise ignored.
        coord : list
            :literal:`(lat,Lon)` geographical coordinates; possibly left empty, 
            so as to consider the keyword argument :literal:`place` in :data:`kwargs`.

        Returns
        -------
        ans : bool 
            :data:`True` if the current NUTS geometry location contains the geolocation
            parsed as an argument, :data:`False` otherwise.

        Raises
        ------
        happyError
            
        References
        ----------
        * Wikipedia `'Point in polygon' problem <https://en.wikipedia.org/wiki/Point_in_polygon>`_.
        * V.Agafonkin: `A dive into spatial search algorithms <https://blog.mapbox.com/a-dive-into-spatial-search-algorithms-ebd0c5e39d2a>`_.

        See also
        --------
        :meth:`Location.iscontained`, :meth:`tools.GDALTransform.lay2fid`. 
        """
        if len(args)==1 and isinstance(args[0],Location):
            try:
                loc = args[0]
            except:
                pass
        else:
            func = lambda *a, **kw: kw
            try:
                kwargs = _Decorator.parse_place_or_coordinate(func)(*args, **kwargs) 
                [kwargs.pop(key) for key in kwargs.keys() if key not in [_Decorator.KW_PLACE, _Decorator.KW_COORD]]
                assert not kwargs is {}
            except:
                raise happyError('unable to retrieve coordinates')
            else:
                loc = Location(kwargs)
        return self.fid in loc.nuts()
        
    #/************************************************************************/
    def carto(self, **kwargs):
        """Create a map where the vector geometry(ies) provided by the given NUTS instance 
        are represented.
        
            >>> nuts.carto(**kwargs)

        See also
        --------
        :meth:`tools.LeafMap.add_area`, :meth:`~NUTS.load`, :meth:`~NUTS.choro`.
        """
        __no_widget = kwargs.pop(_Decorator.KW_NO_WIDGET, False)
        if WIDGET_TOOL is True and __no_widget is False:
            # see https://github.com/jupyter-widgets/ipyleaflet/blob/master/examples/CountriesGeoJSON.ipynb
            label = ipywidgets.Label(layout=ipywidgets.Layout(width='100%'))
            def hover_handler(event=None, id=None, properties=None):
                label.value = "NUTS area: %s - code: %s - level: %s" %      \
                    (properties[_Decorator.parse_nuts.KW_NUTS_NAME], properties[_Decorator.parse_nuts.KW_NUTS_ID], properties[_Decorator.parse_nuts.KW_LEVEL])    
        else:
            hover_handler = None    
        self.mapping.add_area(self.load(**kwargs), 
                              hover = hover_handler, 
                              name='NUTS area'
                              )
        if WIDGET_TOOL is True and __no_widget is False:
            return ipywidgets.VBox([self.mapping.Map, label])
        else:
            return self.mapping.Map
        
    #/************************************************************************/
    def choro(self, data, **kwargs):
        """Create a choropleth map over the geometry(ies) provided by the given NUTS
        instance.

        See also
        --------
        :meth:`tools.LeafMap.choropleth`, :meth:`~NUTS.load`, :meth:`~NUTS.carto`.
        """
        gdf = self.load(**{_Decorator.KW_OFMT: 'gpd'}, **kwargs)
        pass
        
#%%
#==============================================================================
# CLASS Area
#==============================================================================
       
class Area(_Feature):
    """
    """

    #/************************************************************************/
    @_Decorator.parse_nuts
    def __init__(self, **kwargs):
        self._area = kwargs.pop(_Decorator.KW_AREA, [])
        super(Area,self).__init__(**kwargs)
    
    #/************************************************************************/
    def __getattr__(self, attr_name): 
        # this covers the case: geometry, properties and type
        try:
            return super(Area,self).__getattribute__(attr_name) 
        except AttributeError:
            attr = [n[attr_name] for n in self._area]
            return attr if len(attr)>1 else attr[0]

    #/************************************************************************/
    @property
    def feature(self):
        """Feature property (:data:`getter`) of an :class:`Area` instance.
        """
        return self._area if len(self._area)>1 else self._area[0]
    
    @property
    def coord(self):
        """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`) 
        of an :class:`Area` instance.
        This is an educated guess from the actual geometry NUTS name.
        """ 
        if self._coord in ([],[None,None],None):
            try:
                func = lambda *a, **kw: kw.get(_Decorator.KW_COORD)
                coord = _Decorator.parse_area(func)(self.feature, filter='coord')
            except:     
                raise happyError('coordinates not found') 
            else:
                self._coord = coord
        return self._coord # if len(self._coord)>1 else self._coord[0]    
    
    @property
    def name(self):
        """Name property (:data:`getter`) of an :class:`Area` instance. 
        A name type is :class:`str`.
        """
        try:
            name = [a[_Decorator.parse_area.KW_PROPERTIES][_Decorator.parse_area.KW_NAME] \
                    for a in self.feature]
        except:
            return None
        else:
            return name if len(name)>1 else name[0]
    
    @property
    def extent(self):
        """Extent property (:data:`getter`) of an :class:`Area` instance. 
        A extent type is :class:`list`.
        """
        try:
            extent = [a[_Decorator.parse_area.KW_PROPERTIES][_Decorator.parse_area.KW_EXTENT] \
                    for a in self.feature]
        except:
            return None
        else:
            return extent if len(extent)>1 else extent[0]
    
    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def contains(self, *args, **kwargs):
        """
        """
        pass
       