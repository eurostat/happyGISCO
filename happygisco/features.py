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
from happygisco.tools import GDAL_TOOL, FOLIUM_TOOL
from happygisco import services     
from happygisco.services import GISCO_SERVICE, API_SERVICE
    
# requirements
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
# ENLARGE YOUR _Feature
#==============================================================================
        
#/****************************************************************************/
# let us complement the definition of _Feature
def __init(inst, *args, **kwargs):
    # kwargs.pop(_Decorator.KW_PLACE); kwargs.pop(_Decorator.KW_COORD)
    try:
        assert GDAL_TOOL
    except:
        happyWarning('GDAL transform utilities not available')
    else:
        inst._transform = tools.GDALTransform()
    try:
        assert FOLIUM_TOOL
    except:
        happyWarning('folium mapping services not available')
    else:
        inst._mapping = None # tools.FoliumMap()
    try:
        assert API_SERVICE or GISCO_SERVICE
    except:
        happyWarning('external API and GISCO services not available')
    else:
        service = kwargs.pop('serv', settings.CODER_GISCO)
        if service is None: # whatever works
            try:
                assert GISCO_SERVICE is True
                inst._service = services.GISCOService(coder=service)
            except:
                try:
                    assert API_SERVICE is True
                    inst._service = services.APIService(coder=service)
                except:
                    raise IOError('no service available')
        elif isinstance(service,str):
            if service in services.GISCOService.CODER:
                inst._service = services.GISCOService(coder=service)
            elif service in services.APIService.CODER:
                inst._service = services.APIService(coder=service)
            else:
                raise IOError('service %s not available' % service)
        if not isinstance(inst._service,(services.GISCOService,services.APIService)):
            raise IOError('service %s not supported' % service)
_Feature.__init__ = classmethod(__init)

#/****************************************************************************/
def __lat(inst):
    try:
        lat = inst.coord[0]
    except:
        try:
            lat = inst.coord.get(_Decorator.KW_LAT)
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

def __service(inst, service):
    if not (service is None or isinstance(service,(services.GISCOService,services.APIService,services.OSMService))):
        raise happyError('wrong type for SERVICE property')
    inst._service = service
_Feature.service = _Feature.service.setter(__service)

        
#%%
#==============================================================================
# CLASS Location
#==============================================================================
            
class Location(_Feature):
    """Generic class used so to define a geolocation, *e.g.* a (topo)name or a 
    set of geographic coordinates.
        
    ::
        
        >>> loc = features.Location(*args, **kwargs)
    
    Arguments
    ---------
    place : str, tuple[str]
        a string defining a location name, _e.g._ of the form :literal:`locality, country`,
        for instance :literal:`Paris, France`; possibly left empty, so as to consider the 
        keyword argument :data:`place` in :data:`kwargs`, otherwise ignored.
    coord : float, tuple[float]
        a pair of (tuple of) floats, defining the :literal:`(lat,Lon)` coordinates,
        for instance 48.8566 and 2.3515 to locate Paris; possibly left empty, so as 
        to consider the keyword argument :literal:`place` in :data:`kwargs`.
        
    Keyword Arguments
    -----------------
    radius : float
        accuracy radius around the geolocation :data:`coord` (or :data:`place`); 
        default: :data:`radius` is set to 0.001km, _i.e._ 1m.
    """

    #/************************************************************************/
    @_Decorator.parse_place_or_coordinate
    def __init__(self, *args, **kwargs):
        # kwargs.pop('order',None)
        self.__place = kwargs.pop(_Decorator.KW_PLACE, None)
        self.__coord = kwargs.pop(_Decorator.KW_COORD, None)
        super(Location,self).__init__(*args, **kwargs)
        self.__geom = None

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
        return self.__place if self.__place is None or len(self.__place)>1 else self.__place[0]    
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
    @property
    def nuts(self):
        """NUTS property (:data:`getter`) of a :class:`Location` instance.
        This is the identifier of the NUTS actually containing this instance.
        """ 
        if self.__nuts in ([],None):
            try:
                nuts = self.findnuts()
            except:     
                happyWarning('NUTS not found') 
                return
            else:
                if not isinstance(nuts,list): nuts = [nuts,]
                # note that "NUTS_ID" is present as a field of both outputs returned
                # by GDALTransform.coord2feat and GISCOService.coord2nuts
                self.__nuts = [n[_Decorator.parse_nuts.KW_NUTS_ID] for n in nuts]
        return self.__nuts    

    #/************************************************************************/
    @property
    def geom(self):
        """Geom(etry) property (:data:`getter`) of a :class:`Location` instance.
        This is a vector data built from the geolocations in this instance.
        """ 
        if self.__geom in ([],None):
            try:
                geom = self.geometry()
            except:     
                happyWarning('Geometry not available') 
                return
            else:
                self.__geom = geom
        return self.__geom

    #/************************************************************************/
    def __repr__(self):
        try:
            return [','.join(p.replace(',',' ').split()) for p in self.place]
        except:
            return ''
        
    #/************************************************************************/
    def geometry(self, **kwargs):
        """Build a vector geometry upon the geographical coordinates represented
        by this instance. 
         
        ::
       
            >>> geom = loc.geometry(**kwargs)
        
        Keyword Arguments
        -----------------        
        kwargs : dict  
            see keyword arguments of the :meth:`tools.GDALTransform.coord2geom` method.

        Returns
        -------
        geom : :class:`ogr.Geometry`
            multipoint geometry featuring all the points listed in this instance.

        Raises
        ------
        happyError
            when unable to build geometry.

        Example
        -------
        
        See also
        --------
        :meth:`tools.GDALTransform.coord2geom`.
        """
        try:
            return self.transform.coord2geom(self.coord, **kwargs)
        except:     
            raise happyError('unable to build a vector geometry upon given coordinates') 

    #/************************************************************************/
    def geocode(self, **kwargs):   
        """Convert the object place name to geographic coordinates using the 
        service used to initialise this instance.
        
        ::
        
            >>> coord = loc.geocode(**kwargs)
        
        Keyword Arguments
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

        Note
        ----
        The output of the :meth:`geocode` method will not coincide with the :data:`coord`
        attribute of the considered instance in the case the latter was parsed for its 
        initialisation.
        
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
        """Convert the object geographic coordinates to a place (topo)name using the 
        service used to initialise this instance. 
         
        ::
       
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
            when unable to recognize coordinates.

        Example
        -------
        
        ::

            >>> loc = features.Location('48.85693, 2.3412')
            >>> paris = loc.reverse()
            >>> print paris
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
    def distance(self, loc, **kwargs):            
        """Compute pairwise distances between this instance location and other locations 
        parsed indifferently as places names or geographic coordinates.
        
        ::
        
            >>> D = loc.distance(loc, **kwargs)
    
        Arguments
        ---------
        loc : list,str,:class:`~features.Location`
            a location represented either as another instance of :class:`Location`,
            a tuple of (lat,Lon) coordinates or a place name expressed as a string.
            
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
        IOError
            when wrong unit/code for geodesic distance or when unable to find/recognize
            locations.
            
        Examples
        --------      
        Let us compute some distances between geolocations expressed as either place 
        names or geographical coordinates:
            
        ::

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
        
        ::
            
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
            
        Example
        -------
            
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
    def transform(self,**kwargs):
        pass
    
    #/************************************************************************/
    def findnuts(self, **kwargs):
        """Compute the route starting at this instance location and going through
        the various steps/destinations represented by a list of (topo) name(s) or
        geographic coordinates. 
        
        ::
            
            >>> id = loc.findnuts(**kwargs)
    
        Keyword arguments
        -----------------
        kwargs : dict
            see method :meth:`services.GISCOService.coord2nuts`.
            
        Returns
        -------
        nuts : dict, list[dict]
            a (list of) dictionary(ies) representing NUTS geometries; see
            :meth:`services.GISCOService.coord2nuts` method.

        Raises
        ------
        happyError
            when unable to identify NUTS region.

        Example
        -------
            
        Note
        ----
        This method is available only when the service parsed to initialise this
        instance is an instance of :class:`services.GISCOService` class.

        See also
        --------
        :meth:`~Location.isnuts`,
        :meth:`services.GISCOService.coord2nuts`, :meth:`services.GISCOService.place2nuts`,
        :meth:`tools.GDALTransform.coord2feat`.
        """
        #if not (GISCO_SERVICE and GDAL_TOOL):
        #    happyWarning('findnuts method available only with GISCO service or GDAL tool')
        #    return
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
        try:
            if isinstance(feat,list):
                return [f['attributes'] for f in feat]
            else:
                return feat['attributes'] 
        except:
            return feat.items()  # return feat.ExportToJson()
     
    #/************************************************************************/
    def isnuts(self, nuts):
        """Check the identifier of the NUTS the current geolocation/instance
        belongs to.
        
        ::
            
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
            
        See also
        --------
        :meth:`~Location.findnuts`, :meth:`~Location.iscontained`.
        """
        if isinstance(nuts, NUTS):
            nuts = nuts.id
        elif not isinstance(nuts, str):
            raise happyError('wrong type for input NUTS identifier')
        return any([n == nuts for n in self.nuts])
     
    #/************************************************************************/
    def iscontained(self, layer):
        """Check whether the current geolocation/instance is contained in the geometry
        defined by a given layer.
        
        ::
            
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
            fid = self.transform.lay2fid(layer, self.geom)
        except:
            raise happyError('impossible to establish relationship')
        if fid in ((),[],None)  \
                or (isinstance(fid,list) and all([f is None for f in fid])):
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
        
    ::
        
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
    NUTS units:
    * `units 2016 http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/nuts-2016-units.html
    listed in the `json file <http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/nuts-2016-units.json>`_
    """
    
    #/************************************************************************/
    @classmethod
    def from_layer(cls, layer, **kwargs):
        layer = kwargs.pop(_Decorator.KW_LAYER, None)
        self = cls(**kwargs)
        if not layer in ([],None):
            self.__layer = layer
            self.__feature = self.transform.layer2feat(layer)
        return self
        
    #/************************************************************************/
    @_Decorator.parse_file
    @classmethod
    def from_file(cls, url, **kwargs):
        file = kwargs.pop(_Decorator.KW_FILE, None)
        self = cls(**kwargs)
        if not file in ([],None):
            self.__layer = self.transform.file2layer(file)
            # self.__vector = self.transform.layer2vector(self.__layer) # crash!!!
            self.__vector = self.transform.file2vector(file)
        return self
      
    #/************************************************************************/
    @classmethod
    @_Decorator.parse_url
    def from_url(cls, url, **kwargs):
        url = kwargs.pop(_Decorator.KW_URL, None)
        self = cls(**kwargs)
        if url is not None:
            feat = self.serv.get_response(url)
            self.__vector = feat.content
        return self
    
    #/************************************************************************/
    @_Decorator.parse_nuts
    def __init__(self, **kwargs):
        self.__feature = kwargs.pop(_Decorator.KW_FEATURE, [])
        super(NUTS,self).__init__(**kwargs)
    
    #/************************************************************************/
    def __getattr__(self, attr_name): 
        try:
            return super(NUTS,self).__getattribute__(attr_name) 
        except AttributeError:
            try:
                attr = [n[attr_name] for n in self.__nuts]
                assert not attr in ([],[None])
            except:
                raise happyError('attribute %s not known' % attr_name)
            else:
                return attr if len(attr)>1 else attr[0]

    #/************************************************************************/    
    @property
    def feature(self):
        """Feature property (:data:`getter`) of a :class:`NUTS` instance.
        """
        return self.__feature if self.__feature is None or len(self.__feature)>1 else self.__feature[0]

    #/************************************************************************/    
    @property
    def layer(self):
        """Layer property (:data:`getter`) of a :class:`NUTS` instance.
        """
        return self.__layer if self.__layer is None or len(self.__layer)>1 else self.__layer[0]

    #/************************************************************************/    
    @property
    def coord(self):
        """:literal:`(lat,Lon)` geographic coordinates property (:data:`getter`) 
        of a :class:`NUTS` instance.
        This is an educated guess from the actual geometry NUTS name.
        """ 
        if self._coord in ([],[None,None],None):
            try:
                coord = self.geocode(unique=True)
            except:     
                raise happyError('coordinates not found') 
            else:
                self._coord = coord
        return self._coord # if len(self._coord)>1 else self._coord[0]    


    #/************************************************************************/    
    def __get_vector(self):
        if not self.layer in ([],None):
            return self.transform.layer2vector(self.layer)

    #/************************************************************************/    
    def __get_feature(self):
        if not self.vector in ([],None):
            try:
                feature = {k:json.loads(v.ExportToJson()) for k,v in self.vector.items()}
            except:
                feature = {}
            return self.transform.layer2vector(self.layer)
            

    #/************************************************************************/    
    def __get_level(self):
#        if self.feature is None:
#            if self.vector is None:
        try:
            level = [int(f[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_LEVEL]) \
                    for f in self.feature]
        except:
            try:
                level = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_LEVEL] \
                         for f in self.feature]
            except:
                level = None
        else:
            return level if len(level)>1 else level[0]

    #/************************************************************************/    
    @property
    def level(self):
        """Level property (:data:`getter`) of a :class:`NUTS` instance. 
        A `level` type is (a list of) :class:`int`.
        """
        if self.__level is None:
            try:
                level = self.__get_level()
            except:     
                raise happyError('level not found') 
            else:
                self.__level = level
        return self.__level if self.__level is None or len(self.__level)>1 else self.__level[0] 
    
    @property
    def fid(self):
        """Feature identity property.
        """
        try:
            fid = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_FID] \
                   for f in self.feature]
        except:
            fid = None
        else:
            return fid if len(fid)>1 else fid[0]
    
    @property
    def nid(self):
        """NUTS identity property.
        """
        try:
            nid = [f[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_ID] \
                   for f in self.feature]
        except:
            try:
                nid = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_NUTS_ID] \
                       for f in self.feature]
            except:
                nid = None
        else:
            return nid if len(nid)>1 else nid[0]
    
    @property
    def name(self):
        """Name property (:data:`getter`) of a :class:`NUTS` instance. 
        A name type is :class:`str`.
        """
        try:
            name = [n[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_NAME] \
                    for n in self.feature]
        except:
            try:
                name = [f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_NUTS_NAME] \
                        for f in self.feature]
            except:
                name = None
        else:
            return name if len(name)>1 else name[0]
    
    @property
    def value(self):
        """Value property (:data:`getter`) of a :class:`NUTS` instance. 
        A value type is :class:`str`.
        """
        try:
            value = [n[_Decorator.parse_nuts.KW_VALUE] for n in self.feature]
        except:
            return None
        else:
            return value if len(value)>1 else value[0]
    
    @property
    def place(self):
        """Place property of a :class:`NUTS` instance. This is actually a "shortcut"
        to :data:`name` property.
        """
        return self.name
    
    #/************************************************************************/
    def geocode(self, **kwargs):
        """Convert the NUTS name to geographic coordinates using the service used 
        to initialise this instance.
        
        ::
            
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
        
        ::
            
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
        return self.id in loc.nuts()
        

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
       