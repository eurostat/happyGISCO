#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_entities

Module for place/location entities definition

**About**

*credits*:      `grazzja <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      0.1
--
*since*:        Sat Apr  7 01:34:07 2018

**Description**

Define place and NUTS entities to which geotransformations are associated.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`json`

*optional*:     :mod:`requests`, :mod:`osgeo`, :mod:`googlemaps`, :mod:`googleplaces`

*call*:         :mod:`settings`, :mod:`services`         

**Contents**

"""

# generic import
import os, sys#analysis:ignore
import warnings

import functools#analysis:ignore

# requirements

try:
    from osgeo import ogr
except ImportError:
    # GDAL_RESOURCE = False
    warnings.warn('GDAL package (https://pypi.python.org/pypi/GDAL) not loaded - Inline resources not available')
else:
    print('GDAL help: https://pcjericks.github.io/py-gdalogr-cookbook/index.html')

# local imports
import settings
from settings import nutsVerbose, _geoDecorators
import services     
from services import GISCO_SERVICE, API_SERVICE

    
#==============================================================================
# CLASS __Entity
#==============================================================================
            
class __Entity(object):    
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self.__service = None
        try:
            assert API_SERVICE or GISCO_SERVICE
        except:
            raise IOError('external API and GISCO services not available')
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

#==============================================================================
# CLASS Place
#==============================================================================
            
class Place(__Entity):
    """
    """
    @_geoDecorators.parse_place_or_coordinates
    def __init__(self, *args, **kwargs):
        """
        """
        super(Place,self).__init__(*args, **kwargs)
        self.__place = kwargs.get('place')
        self.__lat, self.__lon = kwargs.get('lat'), kwargs.get('lon')

    @property
    def place(self):
        """
        """
        return self.__place
       
    @property
    def service(self):
        """
        """
        return self.__service
       
    @property
    def coord(self):
        """
        """
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
        try:
            return self.service.place2coord(place=self.place, *kwargs)
        except:     
            raise IOError('unrecognised address/location argument') 
    
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
    
class NUTS(object):
    """
    """
    @_geoDecorators.parse_nuts
    def __init__self(self, *args, **kwargs):
        pass
    
    def identify(self, place, **kwargs):
        pass
    
    def contains(self, place, **kwargs):
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
