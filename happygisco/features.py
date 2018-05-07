#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_features

Module for place/location features definition and description.

**Description**

Define the main classes for the representation of place/location features, as well 
as NUTS regions, to which geotransformations are associated.
    
**Dependencies**

*require*      :mod:`os`, :mod:`sys`

*call*         :mod:`settings`, :mod:`base`, :mod:`services`, :mod:`tools`         

**Contents**

"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:34:07 2018

__all__         = ['Location', 'Area', 'NUTS']

# generic import
import os, sys#analysis:ignore

import functools#analysis:ignore

# from typing import Dict, Tuple, List

# local imports
from happygisco import settings
from happygisco.settings import happyWarning, happyVerbose, happyError, happyType#analysis:ignore
#from happygisco import base
from happygisco.base import _Feature, _Decorator#analysis:ignore
from happygisco import tools     
from happygisco.tools import GDAL_TOOL
from happygisco import services     
from happygisco.services import GISCO_SERVICE, API_SERVICE

# requirements

#%%
#==============================================================================
# ENLARGE YOUR _Feature
#==============================================================================
        
#/****************************************************************************/
# let us complement the definition of _Feature
def __init(inst, *args, **kwargs):
    # kwargs.pop(_Decorator.KW_PLACE); kwargs.pop(_Decorator.KW_COORD)
    try:
        assert GDAL_TOOL
    except:
        happyWarning('GDAL services not available')
    else:
        inst.__tool = tools.GDALTool()
    try:
        assert API_SERVICE or GISCO_SERVICE
    except:
        happyWarning('external API and GISCO services not available')
    else:
        service = kwargs.pop('serv', settings.CODER_GISCO)
        if service is None: # whatever works
            try:
                assert GISCO_SERVICE is True
                inst.__service = services.GISCOService(coder=service)
            except:
                try:
                    assert API_SERVICE is True
                    inst.__service = services.APIService(coder=service)
                except:
                    raise IOError('no service available')
        elif isinstance(service,str):
            if service in services.GISCOService.CODER:
                inst.__service = services.GISCOService(coder=service)
            elif service in services.APIService.CODER:
                inst.__service = services.APIService(coder=service)
            else:
                raise IOError('service %s not available' % service)
        if not isinstance(inst.__service,(services.GISCOService,services.APIService)):
            raise IOError('service %s not supported' % service)
_Feature.__init__ = __init

#/****************************************************************************/
def __lat(inst):
    try:
        lat = inst.__coord[0]
    except:
        try:
            lat = inst.__coord.get(_Decorator.KW_LAT)
        except:  # AttributeError
            raise happyError('coordinates parameter not set')
    return lat if lat is None or len(lat)>1 else lat[0]
_Feature.lat = property(__lat) 
_Feature.lat.__doc__ =                                                      \
    """Latitude property (:data:`getter`) of a :class:`_Feature` instance. 
    A `lat` type is (a list of) :class:`float`\ .
    """
def __Lon(inst):
    try:
        Lon = inst.coord[1]
    except:
        try:
            Lon = inst.coord.get(_Decorator.KW_LON)
        except:  # AttributeError
            raise happyError('coordinates parameter not set')
    return Lon if Lon is None or len(Lon)>1 else Lon[0]
_Feature.Lon = property(__Lon) 
_Feature.Lon.__doc__ =                                                      \
    """Longitude property (:data:`getter`) of a :class:`_Feature` instance. 
    A `Lon` type is (a list of) :class:`float`\ .
    """
    
def __coordinates(inst):  
    try:            
        return [_ for _ in zip(inst.lat, inst.Lon)]
    except:
        return [inst.lat, inst.Lon]
_Feature.coordinates = property(__coordinates) 
_Feature.coordinates.__doc__ =                                              \
    """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`) of 
    a :class:`_Feature` instance.
    """ 

#%%
#==============================================================================
# CLASS Location
#==============================================================================
            
class Location(_Feature):
    """Generic class used so to define a geolocation, *e.g.* a (topo)name or a 
    set of geographic coordinates.
        
    ::
        
        >>> loc = features.GeoLocation(*args, **kwargs)
    
    Arguments
    ---------
    place : tuple, tuple[str]
        a string defining a location name, _e.g._ of the form :literal:`locality, country`,
        for instance :literal:`Paris, France`; possibly left empty, so as to consider the 
        keyword argument :data:`place` in :data:`kwargs` (see below), otherwise 
        all keyword arguments are ignored.
    coord : float, tuple[float]
        a pair of (tuple of) floats, defining the :literal:`(lat,Lon)` coordinates,
        for instance 48.8566 and 2.3515 to locate Paris; possibly left empty, so as 
        to consider the keyword argument :literal:`place` in :data:`kwargs`.
        
    Keyword Arguments
    -----------------
    place,coord : 
        same as above; ignored when the arguments :data:`coord` or :data:`place` 
        are parsed.
    radius : float
        accuracy radius around the geolocation :data:`coord` (or :data:`place`); 
        default: :data:`radius` is set to 0.001km, _i.e._ 1m.
    """

    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def __init__(self,**kwargs):
        # kwargs.pop('order',None)
        self.__place = kwargs.pop(_Decorator.KW_PLACE, None)
        self.__coord = kwargs.pop(_Decorator.KW_COORD, None)
        super(Location,self).__init__(**kwargs)

    #/************************************************************************/
    @property
    def place(self):
        """Place attribute (:data:`getter/setter`/:data:`setter`) of a :class:`Location` 
        instance. A `place` type is  (a list of) :class:`str`\ .
        """
        if self.__place in ('',[''],None):
            try:
                place = self.reverse()
            except:     
                raise happyError('place not found') 
            else:
                self.__place = place
        return self.__place if len(self.__place)>1 else self.__place[0]    
    @place.setter
    def place(self,place):
        try:
            place = _Decorator.parse_place(lambda p: p)(place)
        except:
            raise happyError('unrecognised address/location argument') 
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
        return self.__coord # if len(self.__coord)>1 else self.__coord[0]    
    @coord.setter
    def coord(self,coord):
        try:
            coord = _Decorator.parse_coordinates(lambda c: c)(coord)
        except:
            raise happyError('unrecognised coordinates argument') 
        self.__coord = coord

    #/************************************************************************/
    def __repr__(self):
        return [','.join(p.replace(',',' ').split()) for p in self.place]

    #/************************************************************************/
    def geocode(self, **kwargs):   
        """Convert the object place name to geographic coordinates.
        
        ::
        
            >>> coord = loc.geocode(**kwargs)
        
        Keyword Arguments
        -----------------        
        kwargs : dict  
            see keyword arguments of the :meth:`place2coord` methods.

        Returns
        -------
        coord : list
            a list/tuple of :literal:`(lat,Lon)` geographic coordinates associated
            to the :data:`place` attribute of the :class:`Location` object :data:`loc`.

        Raises
        ------
        happyError
            when unable to recognize address/location.

        Examples
        --------
        
        ::

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
        
        See also
        --------
        :meth:`base._Service.place2coord`, :meth:`services.OSMService.place2coord`, 
        :meth:`services.GISCOService.place2coord`, :meth:`services.APIService.place2coord`, 
        :meth:`~Location.reverse`.
        """
        try:
            return self.service.place2coord(place=self.place, **kwargs)
        except:     
            raise happyError('unable to retrieve coordinates from place (address/location)') 

    #/************************************************************************/
    def reverse(self, **kwargs):
        """Convert the object geographic coordinates to a place (topo)name. 
         
        ::
       
            >>> place = loc.reverse(**kwargs)

        Keyword arguments
        -----------------
        kwargs : dict  
            see keyword arguments of the :meth:`coord2place` methods.

        Returns
        -------
        place : str
            a place name.        

        Raises
        ------
        happyError
            when unable to recognize coordinates.

        Examples
        --------
        
        ::

            >>> loc = features.Location('48.85693, 2.3412')
            >>> paris = loc.reverse()
            >>> print paris
                [u'76 Quai des Orf\xe8vres, 75001 Paris, France', u"Saint-Germain-l'Auxerrois, Paris, France", 
                 u'75001 Paris, France', u'1er Arrondissement, Paris, France', u'Paris, France', 
                 u'Paris, France', u'\xcele-de-France, France', u'France']

        Note
        ----
        It may return no results in case the :literal:`(lat,Lon)` geographic
        coordinates of a remote location were parsed.
        
        See also
        --------
        :meth:`base._Service.coord2place`, :meth:`services.OSMService.coord2place`, 
        :meth:`services.GISCOService.coord2place`, :meth:`services.APIService.coord2place`, 
        :meth:`~Location.geocode`.
        """
        # geocode may return no results if it is passed a  
        # non-existent address or a lat/lng in a remote location
        # raise LocationError('unrecognised location argument') 
        try:
            return self.service.coord2place(coord=self.coord, **kwargs)
        except:     
            raise happyError('unable to retrieve place (address/location) from coordinates') 
    
    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def distance(self, *args, **kwargs):            
        """Method used for computing pairwise distances between this object location 
        and other geolocatoins passed indifferently as places names or geographic 
        coordinates.
        
        ::
        
            >>> D = loc.distance(*args, **kwargs)
    
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
        
        ::

            >>> loc = features.Location([26.062951, -80.238853])
            >>> print loc.distance([26.060484,-80.207268], 
                                   dist='vincenty', unit='m')
                3172.3596179302895
            >>> print loc.distance([26.060484,-80.207268],
                                   dist='great_circle', unit='km')
                3.167782321855102
            >>> print loc.distance('Paris, France', 
                                   dist='great_circle', unit='km')
                7338.5353364838438
        """
        func = lambda *a, **kw: [kw.pop(_Decorator.KW_PLACE), kw.pop(_Decorator.KW_COORD)]
        try:
            place, coord = _Decorator.parse_place_or_coordinate(func)(*args, **kwargs)          
        except:
            pass
        else:
            if coord in ([],None):
                coord = self.service.place2coord(place)
        return tools.GeoCoordinate.distance(self.coord, coord, **kwargs)
    
    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def route(self, *args, **kwargs):
        try:
            place = kwargs.pop(_Decorator.KW_PLACE)
        except:
            coord = kwargs.pop(_Decorator.KW_COORD)
        else:
            coord = self.service.place2coord(place)
        coord = [self.coord,] + coord
        return self.service.coord2route(coord=coord, **kwargs)

    #/************************************************************************/
    def transform(self,**kwargs):
        pass
     
    #/************************************************************************/
    def iscontained(self, layer, **kwargs):
        pass
    
    #/************************************************************************/
    def findnuts(self, **kwargs):
        return self.service.place2nuts(self.place, **kwargs)

#%%
#==============================================================================
# CLASS NUTS
#==============================================================================
       
class NUTS(_Feature):
    """
    """

    #/************************************************************************/
    @_Decorator.parse_nuts
    def __init__(self, **kwargs):
        self.__nuts = kwargs.pop(_Decorator.KW_NUTS, [])
        super(NUTS,self).__init__(**kwargs)
    
    #/************************************************************************/
    def __getattr__(self, attr_name): 
        try:
            return super(NUTS,self).__getattribute__(attr_name) 
        except AttributeError:
            attr = [n[attr_name] for n in self.__nuts]
            return attr if len(attr)>1 else attr[0]

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

    @property
    def level(self):
        """Level property (:data:`getter`) of a :class:`NUTS` instance. 
        A `level` type is (a list of) :class:`int`\ .
        """
        try:
            level = [int(n[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_LEVEL]) \
                    for n in self.__nuts]
        except:
            return None
        else:
            return level if len(level)>1 else level[0]
    
    @property
    def id(self):
        """Identity property.
        """
        try:
            _id = [n[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_ID] \
                    for n in self.__nuts]
        except:
            return None
        else:
            return _id if len(_id)>1 else _id[0]
    
    @property
    def name(self):
        """Name property (:data:`getter`) of a :class:`NUTS` instance. 
        A name type is :class:`str`.
        """
        try:
            name = [n[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_NAME] \
                    for n in self.__nuts]
        except:
            return None
        else:
            return name if len(name)>1 else name[0]
    
    @property
    def value(self):
        """Value property (:data:`getter`) of a :class:`NUTS` instance. 
        A value type is :class:`str`.
        """
        try:
            value = [n[_Decorator.parse_nuts.KW_VALUE] for n in self.__nuts]
        except:
            return None
        else:
            return value if len(value)>1 else value[0]
        
    #/************************************************************************/
    def geocode(self, **kwargs):
        """
        """
        try:
            return self.service.place2coord(place=self.name, **kwargs)
        except:     
            raise happyError('unable to retrieve coordinates from NUTS name') 
        
    #/************************************************************************/
    def identify(self, place, **kwargs):
        """
        """
        pass
    
    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def contains(self, *args, **kwargs):
        """
        """
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
        self.__area = kwargs.pop(_Decorator.KW_AREA, [])
        super(Area,self).__init__(**kwargs)
    
    #/************************************************************************/
    def __getattr__(self, attr_name): 
        # this covers the case: geometry, properties and type
        try:
            return super(Area,self).__getattribute__(attr_name) 
        except AttributeError:
            attr = [n[attr_name] for n in self.__area]
            return attr if len(attr)>1 else attr[0]
 
    #/************************************************************************/
    @property
    def feature(self):
        """
        """
        return self.__area if len(self.__area)>1 else self.__area[0]
    
    @property
    def coord(self):
        """Geographic coordinates :literal:`(lat,Lon)` attribute (:data:`getter`) 
        of a :class:`NUTS` instance.
        This is an educated guess from the actual geometry NUTS name.
        """ 
        if self.__coord in ([],[None,None],None):
            try:
                func = lambda *a, **kw: kw.get(_Decorator.KW_COORD)
                coord = _Decorator.parse_area(func)(self.geometry, filter='coord')
            except:     
                raise happyError('coordinates not found') 
            else:
                self.__coord = coord
        return self.__coord # if len(self.__coord)>1 else self.__coord[0]    
    
    @property
    def name(self):
        """Name attribute (:data:`getter`) of a :class:`Area` instance. 
        A name type is :class:`str`.
        """
        try:
            name = [a[_Decorator.parse_area.KW_PROPERTIES][_Decorator.parse_area.KW_NAME] \
                    for a in self.__area]
        except:
            return None
        else:
            return name if len(name)>1 else name[0]
    
    @property
    def extent(self):
        """Extent attribute (:data:`getter`) of a :class:`Area` instance. 
        A extent type is :class:`list`.
        """
        try:
            extent = [a[_Decorator.parse_area.KW_PROPERTIES][_Decorator.parse_area.KW_EXTENT] \
                    for a in self.__area]
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
