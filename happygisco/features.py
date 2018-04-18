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

*call*         :mod:`settings`, :mod:`services`, :mod:`tools`         

**Contents**

"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:34:07 2018

__all__         = ['Place', 'Location', 'NUTS']

# generic import
import os, sys#analysis:ignore

import functools#analysis:ignore

# local imports
from happygisco import settings
from happygisco.settings import happyWarning, happyVerbose#analysis:ignore
from happygisco.decorators import _geoParsing
from happygisco import services     
from happygisco.services import GISCO_SERVICE, API_SERVICE
from happygisco.tools import GDAL_SERVICE

# requirements

#==============================================================================
# CLASS __Feature
#==============================================================================
            
class __Feature(object):    
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self.__service, self.__geolib, self.__arcgis = None, None, None
        try:
            assert GDAL_SERVICE
        except:
            happyWarning('GDAL services not available')
            pass
        else:
            self.__geolib = services.GDALService()
        try:
            assert API_SERVICE or GISCO_SERVICE
        except:
            happyWarning('external API and GISCO services not available')
        else:
            service = kwargs.pop('serv', settings.CODER_GISCO)
            if service is None: # whatever works
                try:
                    assert GISCO_SERVICE is True
                    self.__service = services.GISCOService(coder=service)
                except:
                    try:
                        assert API_SERVICE is True
                        self.__service = services.APIService(coder=service)
                    except:
                        raise IOError('no service available')
            elif isinstance(service,str):
                if service in services.GISCOService.CODER:
                    self.__service = services.GISCOService(coder=service)
                elif service in services.APIService.CODER:
                    self.__service = services.APIService(coder=service)
                else:
                    raise IOError('service %s not available' % service)
            if not isinstance(self.__service,(services.GISCOService,services.APIService)):
                raise IOError('service %s not supported' % service)
       
    @property
    def service(self):
        """Service attribute (:data:`getter`) of a :class:`__Feature` instance. 
        A `service` type is a :class:`~happygisco.services.GISCOService` 
        or a :class:`~happygisco.services.APIService` object.
        """
        return self.__service
       
    @property
    def geolib(self):
        """
        """
        return self.__geolib

#==============================================================================
# CLASS Place
#==============================================================================
            
class Place(__Feature):
    """Class
    """

    #/************************************************************************/
    @_geoParsing.parse_place
    def __init__(self, place, **kwargs):
        """Initialise an instance of :class:`Place` class.
        
            >>> P = Place(place, **kwargs)
        
        Argument
        --------
        place : tuple, tuple[str]
            a string defining a location name, _e.g._ of the form :literal:`locatity, country`,
            for instance :literal:`Paris, France`; possibly left empty, so as to consider the 
            keyword argument :data:`place` in :data:`kwargs` (see below), otherwise 
            all keyword arguments are ignored.
            
        Keyword Argument
        ----------------
        place : str, tuple[str]
            a string defining a location name; ignored when the argument :data:`place` above is
            passed.
        """
        super(Place,self).__init__(**kwargs)
        self.__place = place
        self.__lat, self.__lon = None, None

    #/************************************************************************/
    @property
    def place(self):
        """Place attribute (:data:`getter`) of a :class:`Place` instance. 
        A `place` type is  (a list of) :class:`str`\ .
        """
        return self.__place  if len(self.__place)>1 else self.__place[0]
   
    #/************************************************************************/
    def __repr__(self):
        return [','.join(p.replace(',',' ').split()) for p in self.place]

    #/************************************************************************/
    def geocode(self, **kwargs):   
        """Convert place names to geographic coordinates (default) and reciprocally, 
        depending on the type of input arguments passed.
        
            >>> loc = place.geocode(**kwargs)
        
        Keyword Arguments
        -----------------        
        kwargs : dict  
            

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
        :meth:`~Location.reverse`
        """
        if self.__lat in ([],None) or self.__lon in ([],None):
            try:
                lat, lon = self.service.place2coord(place=self.place, **kwargs)
            except:     
                raise IOError('unrecognised address/location argument') 
            else:
                self.__lat, self.__lon = lat, lon
        return self.__lat, self.__lon
    
    #/************************************************************************/
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

    #/************************************************************************/
    @_geoParsing.parse_place
    def route(self, place, **kwargs):
        lat, lon = self.service.place2coord(place)
        lat = self.__lat + [lat if len(lat)>1 else [lat,]][0]
        lon = self.__lon + [lon if len(lon)>1 else [lon,]][0]
        return self.service.coord2route(lat, lon, **kwargs)
     
    #/************************************************************************/
    def iscontained(self, layer, **kwargs):
        pass
    
    #/************************************************************************/
    def findnuts(self, **kwargs):
        return self.service.place2nuts(self.place, **kwargs)

#==============================================================================
# CLASS Location
#==============================================================================
   
class Location(__Feature):
    """
    """
        
    #/************************************************************************/
    @_geoParsing.parse_coordinate
    def __init__(self, lat, lon, **kwargs):
        """Initialise an instance of :class:`Place` class.
        
            >>> L = Location(lat, lon, **kwargs)
            
        Arguments
        ---------
        lat,Lon : float, tuple[float]
            a pair of (tuple of) floats, defining the coordinates :literal:`(lat,Lon)`,
            for instance 48.8566 and 2.3515 to locate Paris; possibly left empty, so as 
            to consider the keyword argument :literal:`place` in :data:`kwargs`.
            
        Keyword Arguments
        -----------------
        lat, lon : tuple, float
            a tuple representing (lat,Lon) coordinates coordinates; ignored when the 
            arguments :data:`[lat,Lon]` above are passed.
        radius : float
            accuracy radius around the geolocation :data:`[lat,Lon]`; default:
            :data:`radius` is set to 0.001km, _i.e._ 1m.
        """
        self.__lat, self.__lon = lat, lon        
        self.__place = ''
        super(Location,self).__init__(**kwargs)

    #/************************************************************************/
    @property
    def lat(self):
        """Latitude attribute (:data:`getter`) of a :class:`Place`  instance. 
        A `lat` type is (a list of) :class:`float`\ .
        """
        return self.__lat if len(self.__lat)>1 else self.__lat[0]

    @property
    def lon(self):
        """Longitude attribute (:data:`getter`) of a :class:`Place` instance. 
        A `lon` type is (a list of) :class:`float`\ .
        """
        return self.__lon if len(self.__lon)>1 else self.__lon[0]
    
    @property
    def coordinates(self):              
        """Coordinates (latitude,longitude) attribute (:data:`getter`) of a 
        :class:`Location` instance.
        """ 
        return [self.latitude, self.longitude]

    #/************************************************************************/
    def reverse(self, **kwargs):
        """Convert geographic location (passed as a tuple of coordinates or a string 
        with those coordinates). 
        
            >>> place = loc.reverse(**kwargs)

        Keyword arguments
        -----------------
        kwargs: tuple, str
            .

        Returns
        -------
        place : str
            a place name.        

        Examples
        --------
        >>> loc = Location('48.85693, 2.3412')
        >>> paris = loc.reverse()
        >>> print paris
            [u'76 Quai des Orf\xe8vres, 75001 Paris, France', u"Saint-Germain-l'Auxerrois, Paris, France", 
             u'75001 Paris, France', u'1er Arrondissement, Paris, France', u'Paris, France', 
             u'Paris, France', u'\xcele-de-France, France', u'France']
        
        See also
        --------
        :meth:`~Place.geocode`
        """
        # geocode may return no results if it is passed a  
        # non-existent address or a lat/lng in a remote location
        # raise LocationError('unrecognised location argument')  
        if self.__place in (None,''):
            try:
                place = self.service.coord2place(lat=self.lat, lon=self.lon, **kwargs)
            except:     
                raise IOError('unrecognised address/location argument') 
            else:
                self.__place = place
        return self.__place

    #/************************************************************************/
    def transform(self,**kwargs):
        pass
    
    #/************************************************************************/
    @_geoParsing.parse_coordinate
    def route(self, lat, lon, **kwargs):
        lat = self.__lat + [lat if len(lat)>1 else [lat,]][0]
        lon = self.__lon + [lon if len(lon)>1 else [lon,]][0]
        return self.service.coord2route(lat, lon, **kwargs)

    #/************************************************************************/
    def iscontained(self, layer, **kwargs):
        pass
    
    #/************************************************************************/
    def findnuts(self, **kwargs):
        return self.service.coord2nuts(self.lat, self.lon, **kwargs)

#==============================================================================
# CLASS NUTS
#==============================================================================
       
class NUTS(__Feature):
    """
    """

    #/************************************************************************/
    @_geoParsing.parse_nuts
    def __init__(self, nuts, **kwargs):
        self.__nuts = nuts
        super(NUTS,self).__init__(**kwargs)
    
    #/************************************************************************/
    def __getattr__(self, attr_name): 
        try:
            return super().__getattribute__(attr_name) 
        except AttributeError:
            attr = [n[attr_name] for n in self.__nuts]
            return attr if len(attr)>1 else attr[0]

    #/************************************************************************/
    @property
    def nuts(self):
        """
        """
        return self.__nuts if len(self.__nuts)>1 else self.__nuts[0]
    
    @property
    def level(self):
        """Level attribute (:data:`getter`/:data:`setter`) of a :class:`NUTS` 
        instance. A `level` type is (a list of) :class:`int`\ .
        """
        try:
            level = [int(n[_geoParsing.parse_nuts.KW_ATTRIBUTES][_geoParsing.parse_nuts.KW_LEVEL]) \
                    for n in self.__nuts]
        except:
            return None
        else:
            return level if len(level)>1 else level[0]
    
    @property
    def id(self):
        """
        """
        try:
            _id = [n[_geoParsing.parse_nuts.KW_ATTRIBUTES][_geoParsing.parse_nuts.KW_NUTS_ID] \
                    for n in self.__nuts]
        except:
            return None
        else:
            return _id if len(_id)>1 else _id[0]
    
    @property
    def name(self):
        """Name attribute (:data:`getter`/:data:`setter`) of a :class:`NUTS` 
        instance. A name type is :class:`str`.
        """
        try:
            name = [n[_geoParsing.parse_nuts.KW_ATTRIBUTES][_geoParsing.parse_nuts.KW_NUTS_NAME] \
                    for n in self.__nuts]
        except:
            return None
        else:
            return name if len(name)>1 else name[0]
    
    @property
    def value(self):
        """
        """
        try:
            value = [n[_geoParsing.parse_nuts.KW_VALUE] for n in self.__nuts]
        except:
            return None
        else:
            return value if len(value)>1 else value[0]
        
    #/************************************************************************/
    def identify(self, place, **kwargs):
        """
        """
        pass
    
    #/************************************************************************/
    def contains(self, place, **kwargs):
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
