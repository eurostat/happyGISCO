#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _mod_services

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _GISCOWIKI: https://webgate.ec.europa.eu/fpfis/wikis/display/GISCO/Geospatial+information+services+for+the+European+Commission+and+other+EU+users
.. |GISCOWIKI| replace:: `GISCO offline wiki <GISCOWIKI_>`_
.. _NUTS: http://ec.europa.eu/eurostat/web/nuts/background
.. |NUTS| replace:: `NUTS <NUTS_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `Open Street Map <OSM_>`_
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. |Nominatim| replace:: `Nominatim <Nominatim_>`_
.. _NominatimWIKI: https://wiki.openstreetmap.org/wiki/Nominatim
.. |NominatimWIKI| replace:: `NominatimWIKI <NominatimWIKI_>`_
.. _Google_Maps: https://developers.google.com/maps/
.. |Google_Maps| replace:: `Google Maps <Google_Maps_>`_
.. _Google_Places: https://developers.google.com/places/
.. |Google_Places| replace:: `Google Places <Google_Places_>`_
.. _ArcGIS: http://arcgis.com
.. |ArcGIS| replace:: `ArcGIS <ArcGIS_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_
.. _googlemaps: https://pypi.python.org/pypi/googlemaps
.. |googlemaps| replace:: `Google Maps <googlemaps_>`_
.. _googleplaces: https://github.com/slimkrazy/python-google-places
.. |googleplaces| replace:: `Google Places <googleplaces_>`_
.. _Nuts2json: https://github.com/eurostat/Nuts2json
.. |Nuts2json| replace:: `Nuts2json <Nuts2json_>`_

Module implementing simple requests to various web-based geographical services, 
including |Eurostat| |GISCO|, |OSM| |Nominatim| and |Google_Maps|.

**Description**

Perform operations using online web-services, *e.g.*:

* query and collection through |GISCO| web-services,
* query and collection through external GIS web-services,
* simple geographical data handling and geospatial processing.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`functools`, :mod:`json`

*optional*:     :mod:`geopy`, :mod:`googlemaps`, :mod:`googleplaces`

*call*:         :mod:`settings`, :mod:`base`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:46:51 2018

__all__         = ['OSMService', 'GISCOService', 'APIService', 
                   '_googleMapsAPI', '_googlePlacesAPI', '_geoCoderAPI']

# generic import
import os, io, sys#analysis:ignore

import functools#analysis:ignore
import zipfile

# local imports
from happygisco import settings
from happygisco.settings import happyVerbose, happyWarning, happyError, happyType
from happygisco.base import _Decorator, _Service

# requirements
try: # dummy me...
    GISCO_SERVICE = True
    OSM_SERVICE = True
except:
    pass

try:
    import googlemaps
except ImportError:
    API_SERVICE = False
    happyWarning('GOOGLEMAPS package (https://pypi.python.org/pypi/googlemaps/) not loaded')
else:
    API_SERVICE = True
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
    import pandas as pd
except ImportError:
    PANDAS_INSTALLED = False
    happyWarning('Pandas package (http://pandas.pydata.org) not loaded')   
except:
    PANDAS_INSTALLED = True
    print('pandas help: https://pandas.pydata.org/pandas-docs/stable/')

try:
    import Levenshtein
except ImportError:
    LEVENSHTEIN_INSTALLED = False
    happyWarning('python-Levenshtein package (https://github.com/ztane/python-Levenshtein) not loaded - Map resources not available')
else:
    LEVENSHTEIN_INSTALLED = True
    print('Levenshtein help: https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html')
    
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
# CLASS OSMService
#==============================================================================
    
class OSMService(_Service):
    """Class providing conversion methods and geocoding tools that run the |Nominatim| 
    online web-service of the |OSM| API.
        
    ::
       
        >>> serv = services.OSMService(**kwargs)
            
    Keyword arguments
    -----------------
    domain : str
        domain of |OSM| web-services (hosted by... |OSM|); default is :data:`settings.OSM_URL`,
        *e.g.* an URL domain like :literal:`'nominatim.openstreetmap.org'`. 
 
    Attributes
    ----------     
    CODER :
        coder dictionary defining the connection to |OSM| based web-service
        set to {:data:`settings.CODER_OSM`: :data:`settings.KEY_OSM` }, *e.g*
        :literal:`{'OSM': None}`.
    """
    
    CODER = {settings.CODER_OSM: settings.KEY_OSM}
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        try:
            assert OSM_SERVICE is not False
        except:
            raise happyError('OSM service not available')
        super(OSMService, self).__init__(**kwargs)
        self.__domain = kwargs.pop('domain', settings.OSM_URL) 

    #/************************************************************************/
    @property
    def domain(self):
        """Domain property (:data:`getter`/:data:`setter`) defining the complete
        URL of |OpenStreetMap|, *e.g.* :data:`settings.OSM_URL`, of an instance 
        of this class. 
        """ # A domain type is :class:`str`.
        return self.__domain
    @domain.setter#analysis:ignore
    def domain(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for DOMAIN parameter')
        self.__domain = url or ''

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Generate the query URL for |Nominatim| geocoding web-service (from toponame to
        geocoordinate).
        
        ::
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`format, json_callback, accept-language, extratags, namedetails, q, street, city,`
            :data:`county, state, country, postalcode, countrycodes, viewbox, bounded,addressdetails,`
            :data:`email, limit, dedupe, debug, polygon_geojson, polygon_kml,polygon_svg`, 
            and :data:`polygon_text`;
            see |NominatimWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *geocode* results (*i.e.*, geocoordinates) 
            associated to a given place using |Nominatim| web-service; the generic form of 
            :data:`url` is :literal:`domain/search?{filters}` with :literal:`filters` the 
            filters passed through :data:`kwargs`.
        
        Example
        -------
        Let us create a simple URL for querying the geolocation of a toponame:
        
        ::
            
            >>> serv = services.OSMService()
            >>> serv.url_geocode(q='Paris+France', format='json')
                'https://nominatim.openstreetmap.org/search?q=Paris+France&format=json'
        
        See also
        --------
        :meth:`~OSMService.url_reverse`, :meth:`~OSMService.url_route`, 
        :meth:`~OSMService.url_transform`, :meth:`base._Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https')
        query = kwargs.pop('query', 'search')
        keys = kwargs.pop('keys',
                          ['format', 'json_callback', 'accept-language', 'extratags', 'namedetails', 
                           'q', 'street', 'city', 'county', 'state', 'country', 'postalcode', 'countrycodes', 
                           'viewbox', 'bounded', 'addressdetails', 'email', 'limit', 'dedupe', 'debug', 
                           'polygon_geojson', 'polygon_kml', 'polygon_svg', 'polygon_text']
                          )
        happyVerbose('\n            * '.join(['input filters used for geocoding service :',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=protocol,
                             domain=self.domain, 
                             query=query, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for |Nominatim| reverse geocoding web-service (from 
        geocoordinate to toponame).
        
        ::
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`lat, lon, format, json_callback, accept-language, extratags, email, osm_type,`
            :data:`osm_id, zoom, addressdetails, polygon_geojson, polygon_kml, polygon_svg`, and 
            :data:`polygon_text`;
            see |NominatimWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *reverse geocode* results (*i.e.*, 
            toponame) associated to given geocoordinates using |Nominatim| web-service; 
            the generic form of :data:`url` is :literal:`domain/reverse?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        We can generate the URL for querying the toponame associated to a given
        geolocation:
        
        ::

            >>> serv = services.OSMService()
            >>> serv.url_reverse(lon=10, lat=52)
                'https://nominatim.openstreetmap.org/reverse?lon=10&lat=52'
        
        See also
        --------
        :meth:`~OSMService.url_geocode`, :meth:`~OSMService.url_route`, 
        :meth:`~OSMService.url_transform`, :meth:`base._Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https')
        query = kwargs.pop('query', 'reverse')
        keys = kwargs.pop('keys',
                          ['format', 'json_callback', 'accept-language', 'extratags', 'email', 
                           'osm_type', 'osm_id', 'lat', 'lon', 'zoom', 'addressdetails', 
                           'polygon_geojson', 'polygon_kml', 'polygon_svg', 'polygon_text']
                          )
        happyVerbose('\n            * '.join(['input filters used for reverse geocoding service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=protocol,
                             domain=self.domain, 
                             query=query, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    def _place2area(self, place, **kwargs): 
        """Iterable version of :meth:`~OSMService.place2area`.
        """
        if not happyType.issequence(place):     place = [place,]
        place = ['+'.join(p.replace(',',' ').split()) for p in place]
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt is not None:
            kwargs.update({'format':fmt or 'json'})
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
                assert key is not None
            except AssertionError:
                try:
                    assert data != [] 
                except:
                    raise happyError('geolocation for place %s not recognised' % p)  
                else:
                    pass
            else:
                try:
                    assert key in data and data[key] != [] 
                except AssertionError:
                    happyVerbose('geolocation for place %s not recognised' % p, verb=True)  
                    data = None
                else:
                    data = data.get(key)
            yield data if data is None or happyType.ismapping(data) or len(data)>1 else data[0]

    #/************************************************************************/
    #@_Decorator.parse_place
    #def place2area(self, place, **kwargs): 
    #    place = ['+'.join(p.replace(',',' ').split()) for p in place]
    #    area = []
    #    fmt = kwargs.pop('format','')
    #    if fmt is not None:
    #        kwargs.update({'format':fmt or 'json'})
    #    for p in place:
    #        kwargs.update({'q': p})
    #        try:
    #            url = self.url_geocode(**kwargs)
    #            assert self.get_status(url) is not None
    #        except:
    #            raise happyError('error geolocation request')
    #        else:
    #            response = self.get_response(url)
    #        try:
    #            data = json.loads(response.text)
    #            assert data not in({},None)
    #        except:
    #            raise happyError('geolocation for place %s not loaded' % p)
    #        try:
    #            assert data != [] 
    #        except:
    #            raise happyError('geolocation for place %s not recognised' % p)      
    #        else:
    #            area.append(data if len(data)>1 else data[0])
    #    return area if len(area)>1 else area[0]
    @_Decorator.parse_place
    def place2area(self, place, **kwargs):
        """Retrieve the geographical information associated to a given place as a
        geometry object using |OSM| service.
        
        ::
        
            >>> area = serv.place2area(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, namedetails,`
            :data:`street, city, county, state, country, postalcode, countrycodes, viewbox,`
            :data:`bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson,`
            :data:`polygon_kml, polygon_svg, polygon_text`;
            are accepted; see :meth:`~OSMService.url_geocode`.
        
        Returns
        -------
        area : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input olace(s) in :data:`place`, one for each 
            place mentioned.
                  
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
                
        Examples
        --------
        We will retrieve the geolocation of Berlin, Germany:
        
        ::
        
            >>> berlin = 'Berlin, Germany'
        
        For that purpose, we can build the desired |OSM| URL:
        
        ::
        
            >>> serv = services.OSMService()
            >>> serv.url_geocode(place=berlin) 
                'https://nominatim.openstreetmap.org/search?format=json&q=Berlin+Germany'
        
        though the method :meth:`place2area` enables us to run the operation all
        in once: 
        
        ::

            >>> serv.place2area(berlin, format='json')
                [{'boundingbox': ['52.3570365', '52.6770365', '13.2288599', '13.5488599'],
                   'class': 'place',
                  'display_name': 'Berlin, 10117, Deutschland',
                  'icon': 'https://nominatim.openstreetmap.org/images/mapicons/poi_place_city.p.20.png',
                  'importance': 0.31553744940772,
                  'lat': '52.5170365',
                  'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                  'lon': '13.3888599',
                  'osm_id': '240109189', 'osm_type': 'node',
                  'place_id': '226584215',
                  'type': 'city'},
                 {'boundingbox': ['52.33826', '52.67551', '13.08835', '13.76116'],
                  'class': 'boundary',
                  'display_name': 'Berlin, Deutschland',
                  'icon': 'https://nominatim.openstreetmap.org/images/mapicons/poi_boundary_administrative.p.20.png',
                  'importance': 0.31553744940772,
                  'lat': '52.5198535',
                  'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                  'lon': '13.4385964',
                  'osm_id': '62422', 'osm_type': 'relation',
                  'place_id': '178741737',
                  'type': 'administrative'},
                 ...
                 {'boundingbox': ['52.4186824', '52.4187824', '13.1963552', '13.1964552'],
                  'class': 'tourism',
                  'display_name': 'Berlin, A 115, Nikolassee, Steglitz-Zehlendorf, Berlin, 14109, Deutschland',
                  'icon': 'https://nominatim.openstreetmap.org/images/mapicons/tourist_art_gallery2.p.20.png',
                  'importance': 0.11025,
                  'lat': '52.4187324',
                  'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                  'lon': '13.1964052',
                  'osm_id': '1069490670', 'osm_type': 'node',
                  'place_id': '11522486',
                  'type': 'artwork'}]  
                
        See also
        --------
        :meth:`~OSMService.coord2place`, :meth:`~OSMService.place2coord`, 
        :meth:`~OSMService.url_geocode`, :meth:`~GISCOService.place2area`, 
        :meth:`base._Service.get_status`, :meth:`base._Service.get_response`.
        """
        unique = kwargs.pop('unique',False)
        area = []
        [area.append(data if data is None or (len(data)>1 and unique is False) else data[0]) \
             for data in self._place2area(place, **kwargs)]
        return area if area==[] or len(area)>1 else area[0]
       
    #/************************************************************************/
    def _coord2area(self, coord, **kwargs): 
        """Iterable version of :meth:`~OSMService.coord2area`.
        """
        if not happyType.issequence(coord):     
            coord = list(coord)
        if not all([happyType.issequence(c) for c in coord]):     
            coord = [list(c) for c in coord]
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt is not None:
            kwargs.update({'format':fmt or 'json'})
        for i in range(len(coord)):
            kwargs.update({'lat': coord[i][0], 'lon': coord[i][1]})
            try:
                url = self.url_reverse(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error geolocation request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in ({},None)
            except:
                raise happyError('place for geolocation %s not loaded' % coord[i])
            try:
                assert key is not None
            except AssertionError:
                try:
                    assert data != [] 
                except:
                    raise happyError('place for geolocation %s not recognised' % coord[i])  
                else:
                    pass
            else:
                try:
                    assert key in data and data[key] != [] 
                except AssertionError:
                    # for instance: {'features': [], 'type': 'FeatureCollection'} empty
                    # raise happyError('place for geolocation %s not recognised' % coord[i])  
                    happyVerbose('place for geolocation %s not recognised' % coord[i], verb=True) 
                    data = None
                else:
                    data = data.get(key)
            yield data if data is None or not happyType.ismapping(data) or len(data)>1 else data[0]
       
    #/************************************************************************/
    #@_Decorator.parse_coordinate
    #def coord2area(self, lat, lon, **kwargs): # specific use
    #    area = []
    #    for i in range(len(lat)):
    #        kwargs.update({'lat': lat[i], 'lon': lon[i]})
    #        try:
    #            url = self.url_reverse(**kwargs)
    #            assert self.get_status(url) is not None
    #        except:
    #            raise happyError('error geolocation request')
    #        else:
    #            response = self.get_response(url)
    #        try:
    #            data = json.loads(response.text)
    #            assert data not in({},None)
    #        except:
    #            raise happyError('place for geolocation (%s,%s) not loaded' % (lat[i], lon[i]))
    #        try:
    #            assert _Decorator.parse_area.KW_FEATURES in data     \
    #                and data[_Decorator.parse_area.KW_FEATURES] != []
    #        except:
    #            raise happyError('place for geolocation (%s,%s) not recognised' % (lat[i], lon[i]))      
    #        else:
    #            p = data.get(_Decorator.parse_area.KW_FEATURES)
    #            area.append(p if len(p)>1 else p[0])
    #    return area[0] if len(area)==1 else area
    @_Decorator.parse_coordinate
    def coord2area(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographic coordinates using |OSM| service.
                
        ::

            >>>  area = serv.coord2area(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, email, osm_type,` 
            :data:`osm_id, zoom, addressdetails, polygon_geojson, polygon_kml, polygon_svg, polygon`
            are accepted; see :meth:`~OSMService.url_reverse`.
        
        Returns
        -------
        area : dict, list[dict]
            a (list of) geometry(ies), *i.e.* dictionary(ies) describing the geographical
            information related to the input geographic coordinate(s) in :data:`coord`, 
            one for each coordinate listed.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
        ::
        
            >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
        ::
        
            >>> serv = services.OSMService()
            >>> serv.url_reverse(coord=berlin) 
                'https://nominatim.openstreetmap.org/reverse?format=json&lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2area` does everything at once:
         
        ::
       
            >>> serv.coord2area(berlin, format='json')
                {'address': {'address29': 'Douglas',
                  'city': 'Berlin',
                  'city_district': 'Mitte',
                  'country': 'Deutschland', 'country_code': 'de',
                  'neighbourhood': 'Spandauer Vorstadt',
                  'postcode': '10117',
                  'road': 'Unter den Linden',
                  'state': 'Berlin',
                  'suburb': 'Mitte'},
                 'boundingbox': ['52.517222', '52.517422', '13.388877', '13.389077'],
                 'display_name': 'Douglas, Unter den Linden, Spandauer Vorstadt, Mitte, Berlin, 10117, Deutschland',
                 'lat': '52.517322',
                 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                 'lon': '13.388977',
                 'osm_id': '1818862993', 'osm_type': 'node',
                 'place_id': '18439434'}
        
        See also
        --------
        :meth:`~OSMService.place2coord`, :meth:`~OSMService.url_reverse`, 
        :meth:`base._Service.get_status`, :meth:`base._Service.get_response`.
        """
        area = []
        [area.append(data if data is None or len(data)>1 else data[0]) \
             for data in self._coord2area(coord, **kwargs)]
        return area[0] if area==[] or len(area)==1 else area

    @_Decorator.parse_place
    def place2coord(self, place, **kwargs):
        """Retrieve the  geographic coordinates of a given place provided by its 
        (topo)name using |OSM| service.
        
        ::
        
            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, namedetails,` 
            :data:`street, city, county, state, country, postalcode, countrycodes, viewbox,`
            :data:`bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson,`
            :data:`polygon_kml, polygon_svg`, and :data:`polygon_text`
            are accepted; see :meth:`~OSMService.url_geocode`.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`False`, hence all geometries are parsed.
        order : str
            a flag used to define the order of the output geographic coordinates; 
            it can be either :literal:`'lL'` for :literal:`(lat,Lon)` order or 
            :literal:`'Ll'` for a :literal:`(lon,lat)` order; default is :literal:`'lL'`.            
            
        Returns
        -------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.

        Examples
        --------
        We can easily retrieve the geolocations associated to well-known places:
        
        ::
        
            >>> serv = services.OSMService()
            >>> serv.place2coord('Berlin, Germany')
                [[52.5170365, 13.3888599],
                 [52.5198535, 13.4385964],
                 [54.0363605, 10.4461313],
                 [54.405119, 9.4319966],
                 [52.5034002, 13.3386373],
                 [52.5129535, 13.3299651],
                 [52.5208803, 13.4107774],
                 [47.984547, 10.1865807],
                 [52.4758015, 13.3248541],
                 [52.4187324, 13.1964052]]        
            >>> serv.place2coord('Roma, Italy', order='Ll', unique=True)
                [12.4829321, 41.8933203]
            
        Note
        ----
        This method simply "decorates" the method :meth:`~OSMService._place2area`
        with :meth:`_Decorator.parse_area`.
            
        See also
        --------
        :meth:`~OSMService.place2area`, :meth:`~OSMService.coord2place`,
        :meth:`GISCOService.place2coord`.
        """
        unique = kwargs.pop('unique',False)
        order = kwargs.pop('order','lL')
        coord = []
        func = lambda **kw: [kw.get('coord')]
        [coord.append(data if data is None or len(data)>1 else data[0])     \
             for g in self._place2area(place, **kwargs)                     \
             for data in _Decorator.parse_area(func)(g, filter='coord', order=order, unique=unique)]
        return coord if coord==[] or len(coord)>1 else coord[0]

    @_Decorator.parse_coordinate
    def coord2place(self, coord, **kwargs):
        """Retrieve the (topo)name of a given location provided by its geographic 
        coordinates using |OSM| service.
        
        ::
       
            >>> place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`format, json_callback, accept-language, extratags, namedetails,` 
            :data:`street, city, county, state, country, postalcode, countrycodes, viewbox,`
            :data:`bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson, polygon_kml,`
            :data:`polygon_svg`, and :data:`polygon_text`
            are accepted; see :meth:`~OSMService.url_geocode`.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`False`, hence all geometries are parsed.
            
        Returns
        -------
        place : str, list[str]
            place (topo) name(s).

        Examples
        --------
        Let us see whether we can identify some places through their geolocations:
        
        ::
            
            >>> serv = services.OSMService()
            >>> serv.coord2place([41.8933203, 12.4829321])
                'Statua equestre di Marco Aurelio, Piazza del Campidoglio, Municipio Roma I, Roma, RM, LAZ, 00186, Italia'        
            >>> serv.coord2place([55.6867243, 12.5700724])
                '3A, Øster Farimagsgade, Indre Østerbro, Frederiksstaden, København, Københavns Kommune, Region Hovedstaden, 1353, Danmark'
            
        Note
        ----
        This method simply "decorates" the method :meth:`~OSMService._coord2area`
        with :meth:`_Decorator.parse_area`.
            
        See also
        --------
        :meth:`~OSMService.coord2area`, :meth:`~OSMService.place2coord`,
        :meth:`GISCOService.coord2place`.
        """
        unique = kwargs.pop('unique',False)
        place = []
        func = lambda *a, **kw: [kw.get('place')]
        [place.append(data if data is None or len(data)>1 else data[0])     \
             for a in self._coord2area(coord, **kwargs)                     \
             for data in _Decorator.parse_area(func)(a, filter='place', unique=unique)]
        return place if place==[] or len(place)>1 else place[0]

#%%
#==============================================================================
# CLASS GISCOService
#==============================================================================
    
class GISCOService(OSMService):
    """Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
        
    ::
       
        >>> serv = services.GISCOService(**kwargs)
            
    Keyword arguments
    -----------------
    rest : str
        domain of web-services hosted by |GISCO|; default is :data:`settings.GISCO_URL`,
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
        try:
            assert 'domain' not in kwargs.keys()
            # assert not('domain' in kwargs.keys() and 'url_rest' in kwargs.keys())
        except:
            happyVerbose('parameter DOMAIN ignored (URL_REST can be used instead)', verb=True)
            # raise happyError('incompatible parameters DOMAIN and URL_REST')
        self.__domain = kwargs.get('url_rest', settings.GISCO_RESTURL) # or self.url_rest
        self.__url_cache = kwargs.get('url_cache', settings.GISCO_CACHEURL)
        self.__url_map = kwargs.get('url_map', settings.GISCO_TILEURL)
        self.__arcgis = kwargs.get('arcgis', settings.GISCO_ARCGIS)
                
    #/************************************************************************/
    @property
    def url_rest(self):
        """REST property (:data:`getter`/:data:`setter`) defining the complete
        URL of REST services, *e.g.* :data:`settings.GISCO_RESTURL`, of an instance 
        of this class. 
        """
        return self.__domain
    @url_rest.setter#analysis:ignore
    def url_rest(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for url_rest parameter')
        self.__domain = url or ''
        
    # let us just override the super property domain
    domain = url_rest

    #/************************************************************************/
    @property
    def url_cache(self):
        """Cache property (:data:`getter`/:data:`setter`) defining the complete
        URL of |GISCO| cache services, *e.g.* :data:`settings.GISCO_CACHEURL`, of 
        an instance of this class. 
        """ 
        return self.__url_cache
    @url_cache.setter#analysis:ignore
    def url_cache(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for url_cache parameter')
        self.__url_cache = url or ''

    #/************************************************************************/
    @property
    def url_map(self):
        """URL property (:data:`getter`/:data:`setter`) defining the complete
        URL of GISCO mapping services, *e.g.* :data:`settings.GISCO_MAPURL`, of 
        an instance of this class. 
        """ 
        return self.__url_map
    @url_map.setter#analysis:ignore
    def url_map(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for url_map parameter')
        self.__url_map = url or ''

    #/************************************************************************/
    @property
    def arcgis(self):
        """Domain property (:data:`getter`/:data:`setter`) defining the ArcGIS
        URL, *e.g.* :data:`settings.GISCO_ARCGIS`, of the an instance of this class. 
        """ # A domain type is :class:`str`.
        return self.__arcgis
    @arcgis.setter#analysis:ignore
    def arcgis(self, arcgis):
        if arcgis is not None and not happyType.isstring(arcgis):
            raise TypeError('wrong type for ARCGIS parameter')
        self.__arcgis = arcgis or ''
    
    #/************************************************************************/
    def url_nuts(self, **kwargs):
        """Generate the URL in the |GISCO| domain for the (bulk or not) download 
        of NUTS data (in vector format).
        
        ::
            
            >>> url = serv.url_nuts(**kwargs)
           
        Keyword Arguments
        -----------------
        unit : str
        bulk : bool
        year : int
        scale : str,int
        fmt : str
        proj : str,int
        feat : str,int
        source : str
             
        Returns
        -------
        url : str
        
        Notes
        -----
        Unit naming convention: id-spatialtype-scale-projection-year.format
        where
        
        id: unique unit code. Particular cases: NUTS code (2-5 chars), country code (2 chars).
        spatialtype: region/label/line.
        scale: 01m/03m/10m/20m/60m. The map scale the data is optimized for.
        projection: 4-digit EPSG code
        year: 4-digit year. Particular cases: NUTS release years: 2013/2010/2006/2003
        format: geojson/topojson
        
        Examples
        --------
        
        ::
            
            >>> serv = services.GISCOService()
            >>> serv.url_nuts() # default: full bulk dataset...
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.geojson.zip'
            >>> serv.url_nuts(unit='NUTS") 
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_RG_01M_2013_4326_LEVL_0.geojson'
            >>> serv.url_nuts(unit='AD')
                'http://europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AD-region-01m-4326-2013.geojson'
                
            >>> serv.url_nuts(year = 2016, scale = 10, feature = 'boundary')
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_BN_10M_2016_4326_LEVL_0.geojson'
            >>> serv.url_nuts(unit='bulk', year = 2016, scale = 60, fmt = 'shp')
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2016-60m.shp.zip'
            >>> serv.url_nuts(year = 2010, feature = 'label', level = 2)  
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_LB_2010_4326_LEVL_2.geojson'
            >>> serv.url_nuts(year = 2010, scale = 1, feature = 'line', level = 'ALL', proj = 'EPSG3857')  
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_BN_01M_2010_3857.geojson'
            >>> serv.url_nuts(unit='info', year = 2010)  
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/nuts-2010-units.json'
                
            >>> serv.url_nuts(unit='MK', year = 2006, scale = 20, feature = 'region', proj = 'LAEA')
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/MK-region-20m-3035-2006.geojson'
            >>> serv.url_nuts(unit='BE100', year = 2016, scale = 3, feature = 'label')
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE100-label-03m-4326-2016.geojson'        
        
        Note also:
        
        ::
                
            >>> serv.url_nuts(unit='BE100', year = 2016, scale = 3, feature = 'boundary', fmt ='shp')
                    ! only LABEL and REGION features are supported with single NUTS units distribution - FEATURE argument ignored !
                    ! only GEOJSON is supported with single NUTS units distribution - FMT argument ignored !
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE100-region-03m-4326-2016.geojson'       
        
        Further note that it is possible to build the URL linking to the NUTS datasets 
        from the preformated |Nuts2json| data collection:
        
        ::  
            
            >>> serv.url_nuts(source='nuts2json', size=800, level=2)
                'https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/2013/wm/800px/2.topojson'
            >>> serv.url_nuts(source='nuts2json', proj='LAEA', year=2010)
                'https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/2010/laea/400px/0.topojson'
        """
        # check whether a specific unit is looked for
        try:
            unit = kwargs.pop(_Decorator.KW_UNIT, None)
            assert unit is None or happyType.isstring(unit)
        except AssertionError:
            raise happyError('wrong format/value for UNIT argument')
        else:
            if unit is None : 
                unit = 'NUTS' # force to 'NUTS' instead of None    
            unit = unit.upper()
        # btw, do we want to download GISCO data?
        try:
            source = kwargs.pop('source', 'GISCO')
            assert happyType.isstring(source)
        except AssertionError:
            raise happyError('wrong format/value for SOURCE argument')
        else:
            source = source.upper()      
        # retrieve the year
        year = kwargs.pop(_Decorator.KW_YEAR, settings.DEF_GISCO_YEAR)
        # retrieve the scale
        scale = kwargs.pop(_Decorator.KW_SCALE, settings.DEF_GISCO_SCALE)
        if scale in settings.GISCO_SCALES.keys():
            scale = settings.GISCO_SCALES[scale]
        # retrieve the format
        fmt = kwargs.pop(_Decorator.KW_FORMAT, 
                         settings.DEF_NUTS2JSON_FORMAT if source == 'NUTS2JSON' else settings.DEF_GISCO_FORMAT)
        if source != 'NUTS2JSON' and fmt in settings.GISCO_FORMATS.keys():
            fmt = settings.GISCO_FORMATS[fmt]
        # retrieve the projection
        proj = kwargs.pop(_Decorator.KW_PROJECTION, 
                          settings.DEF_NUTS2JSON_PROJECTION if source == 'NUTS2JSON' else settings.DEF_GISCO_PROJECTION)
        if source == 'NUTS2JSON' and proj in settings.NUTS2JSON_PROJECTIONS.keys():
            proj = settings.NUTS2JSON_PROJECTIONS[proj]
        elif proj in settings.GISCO_PROJECTIONS.keys():
            proj = settings.GISCO_PROJECTIONS[proj]
        # retrieve the spatial type
        feat = kwargs.pop(_Decorator.KW_FEATURE, settings.DEF_GISCO_FEATURE) 
        if feat in settings.GISCO_FEATURES.keys():
            feat = settings.GISCO_FEATURES[feat]
        # retrieve the level
        level = kwargs.pop(_Decorator.KW_LEVEL,  
                           settings.NUTS2JSON_NUTSLEVELS[0] if source == 'NUTS2JSON' else settings.GISCO_NUTSLEVELS[0])
        size = kwargs.pop('size',  
                           settings.NUTS2JSON_MAPSIZE[0] if source == 'NUTS2JSON' else None)
        # set the compression format
        zip_  = '.zip' if unit == 'BULK' else ''
        # check...
        ##if unit in happyType.seqflatten(list(settings.GISCO_FEATURES.items())):
        ##    feat = settings.GISCO_FEATURES[unit] if unit in list(settings.GISCO_FEATURES.keys()) else unit
        ##    unit = 'NUTS'
        ##elif unit in ('BULK','INFO','NUTS'):
        ##    pass
        theme = settings.GISCO_NUTSTHEME 
        if source == 'NUTS2JSON':
            # the files can be retrieved on-the-fly from the base URL 
            #       https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/ 
            # according to the file pattern:
            #       /<YEAR>/<PROJECTION>/<SIZE>/<NUTS_LEVEL>.<FORMAT>
            protocol = 'https'
            domain = settings.NUTS2JSON_DOMAIN
            url = '%s://%s/%s/%s/%spx/%s.%s' % (protocol, domain,
                                                year, proj, size, level,
                                                fmt)  
        elif unit == 'BULK': # zipped files
            # example: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2016-10m.shp.zip
            domain = settings.GISCO_DISTRIBUTION['download']['domain']
            basename = settings.GISCO_DISTRIBUTION['download']['basename']
            if fmt == 'shx': 
                fmt='shp' # blearghhhhhh... no logics in GISCO file naming...
            url = '%s://%s/%s/%s/%s-%s-%s.%s%s' % (settings.PROTOCOL, 
                                        self.url_cache, theme, domain,
                                        basename, year, scale.lower(),
                                        fmt, zip_ )
        elif unit == 'INFO':
            domain = ''
            fmt = settings.GISCO_NUTSDATASET['fmt']
            basename = settings.GISCO_NUTSDATASET['data']
            url = '%s://%s/%s/%s.%s' % (settings.PROTOCOL, 
                                        self.url_cache, theme,
                                        basename.format(year=year), fmt )
        elif unit == 'NUTS': # units
            domain = {v:k for k,v in settings.GISCO_FORMATS.items()}[fmt]
            basename = settings.GISCO_DISTRIBUTION['distribution']['basename']
            if not feat in list(settings.GISCO_FEATURES.values()):
                feat = settings.GISCO_FEATURES[feat]
            if feat == 'LB': # no indication of scale!!!
                scale = ''
            else:
                scale = '_' + str(scale)
            if level == 'ALL':
                level = ''
            else:
                level = '_LEVL_' + str(level)
            # example: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/topojson/NUTS_BN_01M_2016_3035_LEVL_3.json
            url = '%s://%s/%s/%s/%s%s_%s%s_%s_%s%s.%s' % (settings.PROTOCOL, 
                                        self.url_cache, theme, domain,
                                        basename, unit, feat.upper(), scale.upper(), year, proj, level,
                                        fmt )
        else: # files
            # example: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT-region-01m-3035-2016.geojson
            domain = settings.GISCO_DISTRIBUTION['distribution']['domain']
            basename = settings.GISCO_DISTRIBUTION['distribution']['basename']
            if not feat in list(settings.GISCO_FEATURES.keys()):
                feat = {v:k for k,v in settings.GISCO_FEATURES.items()}[feat]
            if feat not in ('label','region'):
                happyWarning('only LABEL and REGION features are supported with single NUTS units distribution - %s argument ignored' % _Decorator.KW_FEATURE.upper())
                feat = 'region'
            if fmt != 'geojson':
                happyWarning('only GEOJSON is supported with single NUTS units distribution - %s argument ignored' % _Decorator.KW_FORMAT.upper())
                fmt = 'geojson'
            url = '%s://%s/%s/%s/%s%s-%s-%s-%s-%s.%s' % (settings.PROTOCOL, 
                                        self.url_cache, theme, domain,
                                        basename, unit, feat.lower(), scale.lower(), proj, year, 
                                        fmt )  
        return url   

    
    #/************************************************************************/
    def url_lau(self, **kwargs):
        """Generate the URL of the |GISCO| LAU data files.
        
        ::
            
            >>> url = serv.url_lau(**kwargs)
           
        Keyword Arguments
        -----------------
        """
        pass

    #/************************************************************************/
    def url_country(self, **kwargs):
        """Generate the URL (or name) of the |GISCO| countries vector datasets.
        
        ::
            
            >>> url = serv.url_country(**kwargs)
            
            
        Examples
        --------
        
        ::
            
            >>> serv = services.GISCOService()
            >>> serv.url_country()
                'http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/countries/countries-2013-units.json'
            >>> serv.url_country(unit='AT')
                'http://europa.eu/ec.eurostat/cache/GISCO/distribution/v2/countries/distribution/AT-region-01m-4326-2013.geojson'

        Note
        ----
        See for instance this `page <http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/countries/countries-2013-units.html>`_.
        """
        # check whether a specific unit is looked for
        try:
            unit = kwargs.pop(_Decorator.KW_UNIT, None)
            assert unit is None or happyType.isstring(unit)
        except AssertionError:
            raise happyError('wrong format/value for UNIT keyword argument')
        # retrieve the year
        year = kwargs.pop(_Decorator.KW_YEAR, settings.DEF_GISCO_YEAR)
        # retrieve the scale
        scale = kwargs.pop(_Decorator.KW_SCALE, settings.DEF_GISCO_SCALE)
        if scale in settings.GISCO_SCALES.keys():
            scale = settings.GISCO_SCALES[scale]
        # retrieve the format
        fmt = kwargs.pop(_Decorator.KW_FORMAT, settings.DEF_GISCO_FORMAT)
        #if fmt in settings.GISCO_FORMATS.keys():
        #    fmt = settings.GISCO_FORMATS[fmt]
        if fmt in list(settings.GISCO_FORMATS.values()):
            fmt = {v:k for k,v in settings.GISCO_FORMATS.items()}[fmt]
        # retrieve the projection
        proj = kwargs.pop(_Decorator.KW_PROJECTION, settings.DEF_GISCO_PROJECTION)
        if proj in settings.GISCO_PROJECTIONS.keys():
            proj = settings.GISCO_PROJECTIONS[proj]
        theme = 'countries'
        if unit is None:
            unit = 'INFO'
        if unit.upper() == 'INFO':
            domain = ''
            fmt = settings.GISCO_CTRYDATASET['fmt']
            basename = settings.GISCO_CTRYDATASET['data']
            url = '%s://%s/%s/%s.%s' % (settings.PROTOCOL, 
                                        self.url_cache, theme,
                                        basename.format(year=year), fmt )
        else:
            domain = 'distribution'
            space = 'region'
            url = '%s://%s/%s/%s/%s-%s-%s-%s-%s.%s' % (settings.PROTOCOL, 
                                        self.url_cache, theme, domain,
                                        unit, space, scale.lower(), proj, year, 
                                        fmt )             
        return url            
        
    #/************************************************************************/
    def url_tile(self, **kwargs):
        """Generate the URL (or name) of the |GISCO| tiling web-service that can
        be used as a background layer in map displays.
        
        ::
            
            >>> url, attr = serv.url_tile(**kwargs)
           
        Keyword Arguments
        -----------------
        tiles: str
            string representing the background tile layer used for the map display; 
            it must be one of the tiling supported by |GISCO|, *i.e.* any string in 
            :literal:`['bmarble','borders','roadswater','hypso','coast','copernicus',
                       'osmec','graybg','country','gray','natural','city','cloudless']`;
            see also the list of available tiling systems (together with the respective
            attributions) in :data:`settings.GISCO_TILES`.
        proj : str,int
            projection identifier; default identifier is  'EPSG3857', *i.e.* the one
            in :data:`settings.DEF_GISCO_TILEPROJ`.
        order : str
            order of the dimensions :literal:`x,y` and :literal:`z` of the tiling
            system; default: :literal:`z/y/x` (note that :literal:`{z}/{y}/{x}` 
            is also accepted).
            
        Returns
        -------
        url : str
        attr : str
        
        Examples
        --------
        
        ::
            
            >>> serv = services.GISCOService()
            >>> serv.url_tile(tiles='bmarble')
                ('http://europa.eu/webtools/maps/tiles/bmarble/3857/{z}/{y}/{x}',
                 '© NASA’s Earth Observatory')
            >>> serv.url_tile(tiles='osmec')
                ('http://europa.eu/webtools/maps/tiles/osm-ec/{z}/{y}/{x}', 
                 '© OpenStreetMap')
        """
        try:
            tiles = kwargs.get('tiles','')
            assert isinstance(tiles,str)
        except:
            raise happyError('wrong format/value for TILES keyword argument')
        else: 
            _d = {v['bckgrd']:k for k,v in settings.GISCO_TILES.items()}
            if tiles in list(_d.keys()):
                tiles = _d[tiles]
        try:
            attr = kwargs.get('attr','')
            assert attr is None or isinstance(attr,str)
        except:
            raise happyError('wrong format/value for ATTR keyword argument')
        if not tiles in settings.GISCO_TILES.keys():
            return tiles, attr   
        try:
            attr = settings.GISCO_TILES[tiles]['attr']
        except:
            pass
        try:
            bckgrd = settings.GISCO_TILES[tiles]['bckgrd']
        except:
            bckgrd = tiles # in case we forgot to specify a 'bckgrd' 
        try:
            proj = kwargs.pop('proj', settings.DEF_GISCO_TILEPROJ)
            assert proj in (None,'') or proj in happyType.seqflatten(settings.GISCO_PROJECTIONS.items())
        except:
            raise happyError('wrong format/value for PROJ keyword argument')
        else:
            if proj in (None,'') or settings.GISCO_TILES[tiles]['proj'] is False:
                proj = ''
            elif not proj in list(settings.GISCO_PROJECTIONS.values()):
                proj = settings.GISCO_PROJECTIONS[proj]
            proj = str(proj) + '/' if proj else ''               
        try:
            order = kwargs.pop('order',settings.GISCO_TILEORDER)
            assert isinstance(order,str) and all([o in set('xyz{}/') for o in order])
        except:
            raise happyError('wrong format for ORDER keyword argument')
        else:
            if all([o in set('xyz') for o in order]):
                order = '/'.join(['{%s}' % o for o in order])
        tiles = '%s://%s/%s/%s%s' % (settings.PROTOCOL, self.url_map, 
                                     bckgrd, proj, order)
        return tiles, attr            

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Generate the query URL for |GISCO| geocoding web-service (from toponame 
        to geocoordinate).
        
        ::
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword Arguments
        -----------------
        nominatim : bool
            flag set to :data:`True` when |Nominatim| geocoding service shall be 
            used; default is :data:`False`.
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`q, lat, lon, distance_sort, limit, osm_tag`, and :data:`lang`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *geocode* results (*i.e.*, geocoordinates) 
            associated to a given place using |GISCO| web-service; the generic form of 
            :data:`url` is :literal:`{domain}/api?{filters}` with :literal:`filters` 
            the filters passed through :data:`kwargs`.
        
        Example
        -------
        Let us create a simple URL for querying the geolocation of a toponame:
        
        ::
            
            >>> serv = services.GISCOService()
            >>> serv.url_geocode(q='Paris+France')
                'http://europa.eu/webtools/rest/gisco/api?q=Paris+France'
            
        Note
        ----
        This method overrides the *super* method :meth:`OSMService.url_geocode`.
        
        See also
        --------
        :meth:`~GISCOService.url_reverse`, :meth:`~GISCOService.url_route`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_findnuts`,
        :meth:`OSMService.url_geocode`.
        """
        nominatim = kwargs.pop('nominatim', False)
        kwargs.update({'keys': ['q', 'lat', 'lon', 'distance_sort', 'limit', 'osm_tag', 'lang'],
                       'path': 'nominatim' if nominatim else '',
                       'query': 'search.php' if nominatim else 'api',
                       'protocol': 'http'}
            )
        return super(GISCOService, self).url_geocode(**kwargs)
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for |GISCO| reverse geocoding web-service (from 
        geocoordinate to toponame).
        
        ::
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :data:`lat, lon, radius, distance_sort, limit`, and :data:`lang`;
            see |GISCOWIKI| on *background services* for more details.
        nominatim : bool
            flag set to :data:`True` when |Nominatim| reverse service shall be 
            used; default is :data:`False`.
                
        Returns
        -------
        url : str
            URL used to return the adequate *reverse geocode* results (*i.e.*, 
            toponame) associated to given geocoordinates using |GISCO| web-service; 
            the generic form of :data:`url` is :literal:`{domain}/reverse?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        We can generate the URL for querying the toponame associated to a given
        geolocation:
        
        ::

            >>> serv = services.GISCOService()
            >>> serv.url_reverse(lon=10, lat=52)
                'http://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52'
            
        Note
        ----
        This method overrides the *super* method :meth:`OSMService.url_reverse`.
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_route`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_findnuts`,
        :meth:`OSMService.url_reverse`.
        """
        nominatim = kwargs.pop('nominatim', False)
        kwargs.update({'keys': ['lat', 'lon', 'radius', 'distance_sort', 'limit', 'lang'],
                       'path': 'nominatim' if nominatim else '',
                       'query': 'reverse.php' if nominatim else 'reverse',
                       'protocol': 'http'}
            )
        return super(GISCOService, self).url_reverse(**kwargs)

    #/************************************************************************/
    def url_route(self, **kwargs):
        """Generate the query URL for |GISCO| routing web-service (from a list of
        geocoordinates to a route).
        
        ::
        
            >>> url = serv.url_route(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`coordinates, polyline, overview`, and :data:`???`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *routing* results associated to a list
            of given geocoordinates using |GISCO| web-service; 
            the generic form of :data:`url` is 
            :literal:`{domain}/route/v1/driving/{coordinates}?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        Let us generate the URL for querying the route going through a series of
        geolocations:
        
        ::

            >>> serv = services.GISCOService()
            >>> serv.url_route(coordinates='13.388860,52.517037;13.397634,52.529407;13.428555,52.523219')
                'https://europa.eu/webtools/rest/gisco/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_findnuts`,
        :meth:`base._Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https') # actually not necessary, http works as well  
        keys = ['overview', ] # ?
        happyVerbose('\n            * '.join(['input filters used for routing service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        coordinates = kwargs.pop('coordinates','')
        polyline = kwargs.pop(_Decorator.parse_coordinate.KW_POLYLINE,None)
        polyline = 'polyline(' + polyline + ')' if polyline else ''
        url = self.build_url(protocol=protocol,
                             domain=self.url_rest, 
                             query='route/v1/driving/%s' % coordinates or polyline, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        # test: 
        # url_route(lat=[13.388860, 13.397634, 13.428555],lon=[52.517037,52.529407,52.523219])

    #/************************************************************************/
    def url_transform(self, **kwargs):
        """Generate the query URL for |GISCO| projection tranform web-service (from 
        a geocoordinate in a given projection reference system to its transformation
        in another projection reference system)
         
        ::
       
            >>> url = serv.url_transform(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`inSR, outSR, geometries, transformation, transformForward` and :data:`f`;
            see |GISCOWIKI| on *background services* for more details.
                
        Returns
        -------
        url : str
            URL used to return the adequate *projection* results of a given
            geocoordinate using |GISCO| web-service; the generic form of :data:`url` 
            is :literal:`{arcgis}/Utilities/Geometry/GeometryServer/project?{filters}`
            with :literal:`filters` the filters passed through :data:`kwargs`.
       
        Example
        -------
        We can generate the URL for querying the tranform of a given geolocation
        from *WGS84* projection system to *LAEA*:
        
        ::

            >>> serv = services.GISCOService()
            >>> serv.url_transform(inSR=4326, outSR=3035, f='json',
                                   geometries='-9.1630,38.7775')
                'https://webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/Utilities/Geometry/GeometryServer/project?inSR=4326&outSR=3035&geometries=-9.1630,38.7775&f=json'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_route`, :meth:`~GISCOService.url_findnuts`,
        :meth:`base._Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'https')  
        keys = ['inSR', 'outSR', 'geometries', 'transformation', 'transformForward', 'f'] # ?
        happyVerbose('\n            * '.join(['input filters used for tranform service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=protocol,
                             domain=self.arcgis, 
                             query='Utilities/Geometry/GeometryServer/project', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    @_Decorator.parse_projection
    def url_findnuts(self, **kwargs):
        """Create a query URL to be submitted to the |GISCO| (simple) web-service 
        for NUTS codes identification.
        
        ::
        
            >>> url = serv.url_findnuts(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :data:`x, y, f, year, proj` and :data:`geometry`; see |GISCOWIKI| 
            on *background services* for more details.
            
        Returns
        -------
        url : str
            URL used to return the adequate *NUTS* results from a given
            geocoordinate using |GISCO| web-service; the generic form of :data:`url` 
            is :literal:`{domain}/nuts/find-nuts.py?{filters}` with :literal:`filters` 
            the filters passed through :data:`kwargs`.
            
        Example
        -----
        Let us build the URL that will allow us to identify the NUTS actually 
        associated with Berlin, Germany:
        
        ::

            >>> serv = services.GISCOService()
            >>> serv.url_findnuts(y=52.5170365, x=13.3888599, f='JSON', proj=4326)
                'http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py?y=52.5170365&x=13.3888599&f=JSON&proj=4326'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_route`, :meth:`~GISCOService.url_transform`,
        :meth:`base._Service.build_url`.
        """
        protocol = kwargs.pop('protocol', 'http')  
        keys = ['x', 'y', 'f', 'year', 'proj', 'geometry']
        happyVerbose('\n            * '.join(['input filters used for NUTS identification service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        # note that the service is case sensitive as f is concerned
        kwargs.update({'f': kwargs.get('f','JSON').upper()}) # let us avoid stupid mistakes
        url = self.build_url(protocol=protocol,
                             domain=self.url_rest, 
                             path='nuts', 
                             query='find-nuts.py', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        
    #/************************************************************************/
    def _data4country(self, country, **kwargs):
        """Iterable version of :meth:`~GISCOService.data4country`.
        """
        if not happyType.issequence(country):     
            country = [country,]
        for c in country:
            kwargs.update({'country': c})
            try:
                url = self.url_country(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error NUTS API request')
            else:
                response = self.get_response(url)
            try:
                file = response
                assert file not in({},None)
            except:
                raise happyError('geolocation for place %s not loaded' % c)
            yield c, file if file is None or happyType.ismapping(file) or len(file)>1 else file[0]
    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_format
    @_Decorator.parse_scale
    def data4country(self, country, **kwargs):
        """Download, and cache when requested, country vector files from |GISCO| Rest
        API.
        
        ::
            
            >>> fref = serv.data4country(country, **kwargs)            
            
        Returns
        -------
        fref : dict
        """
        fref = {}
        [fref.update({ctry: resp if resp is None or len(resp)>1 else resp[0]}) \
             for ctry, resp in self._data4country(country, **kwargs)]
        return fref
        
    #/************************************************************************/
    def _data4nuts(self, nuts, **kwargs):
        """Iterable version of :meth:`~GISCOService.data4nuts`.
        """
        if not happyType.issequence(nuts):     
            nuts = [nuts,]
        for n in nuts:
            kwargs.update({'unit': n})
            try:
                url = self.url_nuts(**kwargs)
                print(url)
                assert self.get_status(url) is not None
            except:
                raise happyError('error NUTS API request')
            else:
                response = self.get_response(url)
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            # print(response.json())
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(response.content)
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(response.text)
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            try:
                data = response.content
                assert data not in({},None)
            except:
                raise happyError('geolocation for place %s not loaded' % n)
            yield n, data
    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_format
    @_Decorator.parse_scale
    @_Decorator.parse_feature
    def data4nuts(self, nuts, **kwargs):
        """Download, and cache when requested, NUTS vector files from |GISCO| Rest
        API.
        
        ::
            
            >>> fref  = serv.data4nuts(nuts, **kwargs)
            
        Returns
        -------
        fref : dict
        """
        fref = {}
        [fref.update({n:resp if resp is None or not happyType.issequence(resp) or len(resp)>1 else resp[0]}) \
             for n, resp in self._data4nuts(nuts, **kwargs)]
        return fref

    #/************************************************************************/
    def data4idnuts(self, **kwargs):
        """
        
        ::
            
            >>> fref  = serv.data4idnuts(nuts, **kwargs)
            
        Returns
        -------
        
        Example
        -------
        
        ::
            
            >>> serv = services.GISCOService()
            >>> f = serv.data4idnuts()
            >>> t = pd.read_csv(f)
            >>> t.head()
                  CNTR_CODE NUTS_ID         NUTS_NAME
                0        AT     AT1     OSTÖSTERREICH
                1        AT    AT11   Burgenland (AT)
                2        AT   AT111  Mittelburgenland
                3        AT   AT112    Nordburgenland
                4        AT   AT113     Südburgenland
            >>> t[t['NUTS_ID']=='AT112']['NUTS_NAME']
                3    Nordburgenland
        """
        # retrieve the largest scale, i.e. the lowest resolution so as to download
        # the smallest file
        scale = sorted(list(settings.GISCO_SCALES.keys()))[-1]
        year = kwargs.pop(_Decorator.KW_YEAR, settings.DEF_GISCO_YEAR)
        fmt = 'shp' # instead of settings.DEF_GISCO_FORMAT since 'shp' is lighter
        kwargs.update({_Decorator.KW_UNIT: 'BULK', 
                       _Decorator.KW_SCALE: scale,
                       _Decorator.KW_FORMAT: fmt,
                       _Decorator.KW_YEAR: year})
        try:
            url = self.url_nuts(**kwargs)
            assert self.get_status(url) is not None
        except:
            raise happyError('error NUTS data request')
        else:
            response = self.get_response(url)
        data = settings.GISCO_NUTS2ID['data'].format(year=year)
        fmt = settings.GISCO_NUTS2ID['fmt']
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            if '%s.%s' % (data,fmt) not in zf.namelist():
                raise happyError('impossible to retrieve name to ID correspondance of NUTS')
            return io.BytesIO(zf.read('%s.%s' % (data,fmt)))
        # return pd.read_csv(io.BytesIO(zf.read(data)))
        
    #/************************************************************************/
    def _nuts2id(self, **kwargs):
        """Generic version of methods :meth:`~GISCOService.nuts2id` and
        :meth:`~GISCOService.id2nuts` used when linking NUTS identifiers with 
        unit names.
        """
        name = kwargs.pop(_Decorator.KW_NAME,None)
        _id = kwargs.pop(_Decorator.KW_ID,None)
        try:
            assert (name is None or _id is None)
        except:
            raise happyError('incompatible arguments %s and %s' % (_Decorator.KW_NAME.upper(),_Decorator.KW_ID.upper()))
        try:
            assert not(name is None and _id is None)
        except:
            raise happyError('missing arguments %s and %s' % (_Decorator.KW_NAME.upper(),_Decorator.KW_ID.upper()))
        unit = name or _id
        if not happyType.issequence(unit):
            unit = [unit,]
        try:
            assert all([happyType.isstring(u) for u in unit])
        except:
            raise happyError('wrong type for %s argument' % _Decorator.KW_NAME.upper() if name is not None else _Decorator.KW_ID.upper())        
        else:
            unit = [u.upper() for u in unit]
        group = kwargs.pop('group', False)
        lut = kwargs.pop(_Decorator.KW_FILE, None)
        if lut is None:
            lut = self.data4idnuts(**kwargs)
            try:
                assert PANDAS_INSTALLED is True
                lut = pd.read_csv(lut)
            except:
                raise happyError('impossible to load correspondance table')
        if name is not None:
            distance = kwargs.pop('dist', False)
            if distance is True:
                distance = 'jaro_winkler'
            if happyType.isstring(distance):
                try:
                    distance = getattr(Levenshtein,distance)
                except AttributeError:
                    raise happyError('Levenshtein distance %s not recognised' % distance)
            thres = kwargs.pop('thres', 0.9)
        else:
            distance, thres = None, None
        # the dim/cols of LUT are: 'CNTR_CODE', 'NUTS_ID', 'NUTS_NAME'
        if name is not None:
            dim1, dim2 = 'NUTS_NAME', 'NUTS_ID'
        else:            
            dim1, dim2 = 'NUTS_ID', 'NUTS_NAME'
        if group is True:
            yield lut[lut[dim1].str.upper().isin(unit)][dim2].tolist()
        else:
            for u in unit:       
                if LEVENSHTEIN_INSTALLED is True and distance not in (False,None):
                    yield lut[distance(lut[dim1].str.upper(),u)<thres][dim2].values
                else:
                    yield lut[lut[dim1].str.upper() == u][dim2].values
        
    #/************************************************************************/
    def nuts2id(self, name, **kwargs):
        """
        
        ::
            
            >>> id = serv.nuts2id(name, **kwargs)
            
        Returns
        -------
        """
        _id = []        
        kwargs.update({_Decorator.KW_NAME: name})
        [_id.append(data if len(data)>1 else data[0]) for data in self._nuts2id(**kwargs)]
        return _id
        
    #/************************************************************************/
    def id2nuts(self, _id, **kwargs):
        """
        
        ::
            
            >>> name = serv.id2nuts(id, **kwargs)
            
        Returns
        -------
        """
        name = []        
        kwargs.update({_Decorator.KW_ID: _id})
        [name.append(data if len(data)>1 else data[0]) for data in self._nuts2id(**kwargs)]
        return name
        
    #/************************************************************************/
    def _place2area(self, place, **kwargs): 
        """Iterable version of :meth:`~GISCOService.place2area`.
        """
        kwargs.update({'key': _Decorator.parse_area.KW_FEATURES})
        #return super(GISCOService,self)._place2area(place, **kwargs)
        for g in super(GISCOService,self)._place2area(place, **kwargs):
            yield g
    #/************************************************************************/
    @_Decorator.parse_place
    def place2area(self, place, **kwargs): 
        """Retrieve the geographical information associated to a given place as
        a geometry using |GISCO| service.
        
        ::
        
            >>> area = serv.place2area(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[lat, lon, distance_sort, limit, osm_tag, lang]`
            are accepted; see :meth:`~GISCOService.url_geocode`.
        
        Returns
        -------
        area : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input :data:`place`, one for each place 
            mentioned.
                  
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
                
        Example
        -------
        The method returns the complete list of geometries output by the web-servive:
         
        ::
           
            >>> serv = services.GISCOService()
            >>> serv.place2area('Madrid, Spain')
                [{'geometry': {'coordinates': [-3.7035825, 40.4167047], 'type': 'Point'},
                  'properties': {'country': 'Spain',
                   'extent': [-3.8889539, 40.6437293, -3.5179163, 40.3119774],
                   'name': 'Madrid',
                   'osm_id': 5326784, 'osm_key': 'place', 'osm_type': 'R', 'osm_value': 'city',
                   'postcode': '28001',
                   'state': 'Community of Madrid'},
                  'type': 'Feature'},
                 {'geometry': {'coordinates': [-3.7715627754518115, 40.5248319], 'type': 'Point'},
                  'properties': {'country': 'Spain',
                   'extent': [-4.5790058, 41.1657381, -3.0529852, 39.8845834],
                   'name': 'Community of Madrid',
                   'osm_id': 349055, 'osm_key': 'boundary', 'osm_type': 'R', 'osm_value': 'administrative'},
                  'type': 'Feature'},
                  {'geometry': {'coordinates': [-3.8275783867014415, 40.738663599999995], 'type': 'Point'},
                  'properties': {'country': 'Spain',
                   'extent': [-4.3409302, 41.1657381, -3.3946285, 40.3119774],
                   'name': 'Archidiócesis de Madrid',
                   'osm_id': 6932541, 'osm_key': 'boundary', 'osm_type': 'R', 'osm_value': 'religious_administration',
                   'state': 'Community of Madrid'},
                  'type': 'Feature'},
                  ...
                   {'geometry': {'coordinates': [-3.690692008891012, 40.41147845], 'type': 'Point'},
                  'properties': {'city': 'Madrid', 'country': 'Spain',
                   'extent': [-3.6925997, 40.4126075, -3.6889179, 40.4097313],
                   'housenumber': '2',
                   'name': 'Royal Botanical Garden of Madrid',
                   'osm_id': 15244804, 'osm_key': 'leisure', 'osm_type': 'W', 'osm_value': 'garden',
                   'postcode': '28014',
                   'state': 'Community of Madrid',
                   'street': 'Plaza Murillo'},
                  'type': 'Feature'}]
        
        Note
        ----
        This method overrides :meth:`OSMService.place2area` by further providing 
        the :literal:`features` key that will be extracted from the output geometry 
        dictionary(ies).
        
        See also
        --------
        :meth:`~GISCOService.place2coord`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2nuts`, :meth:`~GISCOService.place2nuts`, 
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.url_geocode`, 
        :meth:`OSMService.place2area`, :meth:`base._Service.get_response`.
        """
        kwargs.update({'key': _Decorator.parse_area.KW_FEATURES})
        return super(GISCOService,self).place2area(place=place, **kwargs)
        
    #/************************************************************************/
    #@_Decorator.parse_place
    #def _place2coord(self, place, **kwargs): 
    #    for g in super(GISCOService,self)._place2coord(place, **kwargs):
    #        yield g
    #/************************************************************************/
    @_Decorator.parse_place
    def place2coord(self, place, **kwargs): # specific use
        """Retrieve the geographic coordinates of a given place provided by its 
        (topo)name using |GISCO| service.
        
        ::
        
            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[lat, lon, distance_sort, limit, osm_tag, lang]`
            are accepted; see :meth:`~GISCOService.url_geocode`.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`False`, hence all geometries are parsed.
        order : str
            a flag used to define the order of the output geographic coordinates; 
            it can be either :literal:`'lL'` for :literal:`(lat,Lon)` order or 
            :literal:`'Ll'` for a :literal:`(lon,lat)` order; default is :literal:`'lL'`.            
            
        Returns
        -------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.

        Examples
        --------
        We can easily retrieve the geolocations associated to well-known places:
        
        ::
        
            >>> serv = services.GISCOService()
            >>> serv.place2coord('Berlin, Germany')
                [[52.5170365, 13.3888599], [52.5198535, 13.4385964]]        
            >>> serv.place2coord('Roma, Italy', order='Ll', unique=True)
                [10.4584101, 44.5996045]
            
        Note
        ----
        This method simply overrides the method :meth:`OSMService.place2coord`.
           
        See also
        --------
        :meth:`~OSMService.place2coord`, :meth:`~GISCOService.place2area`, 
        :meth:`~GISCOService.coord2place`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`.
        """
        return super(GISCOService,self).place2coord(place=place, **kwargs)

    #/************************************************************************/
    def _coord2area(self, coord, **kwargs): 
        """Iterable version of :meth:`~GISCOService.coord2area`.
        """
        kwargs.update({'key': _Decorator.parse_area.KW_FEATURES})
        #return super(GISCOService,self)._place2area(place, **kwargs)
        for a in super(GISCOService,self)._coord2area(coord, **kwargs):
            yield a
    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2area(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographic coordinates using |GISCO| service.
        
        ::
        
            >>>  area = serv.coord2area(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[radius, distance_sort, limit, lang]` are accepted; 
            see :meth:`~GISCOService.url_reverse`.
        
        Returns
        -------
        area : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input geographic coordinate(s) in :data:`coord`, 
            one for each coordinate listed.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
        ::
        
            >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
        ::
        
            >>> serv = services.OSMService()
            >>> serv.url_reverse(coord=berlin) 
                'https://nominatim.openstreetmap.org/reverse?format=json&lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2geom` does everything at once:
        
        ::
        
            >>> serv.coord2area(berlin, format='json')
                {'address': {'address29': 'Douglas',
                  'city': 'Berlin',
                  'city_district': 'Mitte',
                  'country': 'Deutschland', 'country_code': 'de',
                  'neighbourhood': 'Spandauer Vorstadt',
                  'postcode': '10117',
                  'road': 'Unter den Linden',
                  'state': 'Berlin',
                  'suburb': 'Mitte'},
                 'boundingbox': ['52.517222', '52.517422', '13.388877', '13.389077'],
                 'display_name': 'Douglas, Unter den Linden, Spandauer Vorstadt, Mitte, Berlin, 10117, Deutschland',
                 'lat': '52.517322',
                 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                 'lon': '13.388977',
                 'osm_id': '1818862993', 'osm_type': 'node',
                 'place_id': '18439434'}
        
        Note
        ----
        This method overrides :meth:`OSMService.coord2area` by further providing 
        the :literal:`features` key that will be extracted from the output geometry 
        dictionary(ies).
        
        See also
        --------
        :meth:`~OSMService.coord2area`, :meth:`~OSMService.url_reverse`, 
        :meth:`base._Service.get_status`, :meth:`base._Service.get_response`.
        """
        kwargs.update({'key': _Decorator.parse_area.KW_FEATURES})
        return super(GISCOService,self).coord2area(coord=coord, **kwargs)
      
    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2place(self, coord, **kwargs): # specific use
        """Retrieve the (topo)name of a given location provided by its geographic 
        coordinates using |GISCO| service.
        
        ::
        
            >>>  place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :data:`[radius, distance_sort, limit, lang]` are accepted; 
            see :meth:`~GISCOService.url_reverse`.
        
        Returns
        -------
        place : str, list[str]
            place (topo)name(s) identifying the input geolocation(s) in :data:`coord`.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
        ::
        
            >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
        ::
        
            >>> serv = services.GISCOService()
            >>> serv.url_reverse(lat=berlin[0], lon=berlin[1])
                'http://europa.eu/webtools/rest/gisco/reverse?lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2place` does everything at once:
        
        ::
        
            >>> serv.coord2place(berlin, format='json')
                'Caroline-von-Humboldt-Weg, Berlin, 10117, Germany'
        
        Note
        ----
        This method overrides :meth:`OSMService.coord2place` by further providing 
        the :literal:`features` key that will be extracted from the output geometry 
        dictionary(ies).
        
        See also
        --------
        :meth:`~OSMService.coord2place`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.place2area`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`, 
        :meth:`~GISCOService.url_reverse`.
        """
        kwargs.update({'key': _Decorator.parse_area.KW_FEATURES})
        return super(GISCOService,self).coord2place(coord=coord, **kwargs)

    #/************************************************************************/
    def _coord2nuts(self, coord, **kwargs):
        """Iterable version of :meth:`~GISCOService.coord2nuts`.
        """
        if not happyType.issequence(coord):     
            coord = list(coord)
        if not all([happyType.issequence(c) for c in coord]):     
            coord = [list(c) for c in coord]
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt is not None:
            kwargs.update({'f':fmt or 'JSON'})
        kwargs.update({#'year': kwargs.pop('year',2013), 
                       # 'proj': kwargs.pop('proj',4326),
                       'geometry': kwargs.pop('geometry','N')
                       })
        for i in range(len(coord)):
            kwargs.update({'x': coord[i][1], 'y': coord[i][0]})
            try:
                url = self.url_findnuts(**kwargs)
                assert self.get_status(url) is not None
            except:
                raise happyError('error NUTS request')
            else:
                response = self.get_response(url)
            try:
                data = json.loads(response.text)
                assert data not in ({},None)
            except:
                happyError('NUTS for location %s not loaded' % coord[i])
            try:
                assert key is not None
            except AssertionError:
                try:
                    assert data != [] 
                except:
                    raise happyError('NUTS for geolocation %s not recognised' % coord[i])  
                else:
                    pass
            else:
                try:
                    assert key in data and data[key] != [] 
                except AssertionError:
                    raise happyError('NUTS for geolocation %s and key %s not recognised' % (coord[i], key))  
                else:
                    data = data.get(key)
            yield data if not happyType.ismapping(data) or len(data)>1 else data[0]

    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_area
    @_Decorator.parse_coordinate
    def coord2nuts(self, coord, **kwargs):
        """Retrieve the various |NUTS| geometries (all levels) associated to given 
        geolocation(s) provided as geographic coordinates.
        
        ::
        
            >>> nuts = serv.coord2nuts(coord, **kwargs)

        Arguments
        ---------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        level : int
            integer in [0,3] defining the classification level of the NUTS geometry 
            to return, if not all (default when :data:`level` is :data:`None`).
        
        Returns
        -------
        nuts : dict, list[dict]
            a (list of) dictionary(ies) representing NUTS geometries.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the case the NUTS request is wrongly formulated.
            
        Examples
        --------
        We can easily retrieve all NUTS geometry associated to Rome, Italia from its
        geocoordinates:
        
        ::
            
            >>> serv.coord2nuts([41.8933203,12.4829321])
                [{'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '0',
                   'NAME_LATN': 'ITALIA', 'NUTS_ID': 'IT', 'NUTS_NAME': 'ITALIA',
                   'OBJECTID': '17',
                   'SHRT_ENGL': 'Italy'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'IT'},
                 {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '1',
                   'NAME_LATN': 'CENTRO (IT)', 'NUTS_ID': 'ITI', 'NUTS_NAME': 'CENTRO (IT)',
                   'OBJECTID': '94',
                   'SHRT_ENGL': 'Italy'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'ITI'},
                 {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2',
                   'NAME_LATN': 'Lazio', 'NUTS_ID': 'ITI4', 'NUTS_NAME': 'Lazio',
                   'OBJECTID': '330',
                   'SHRT_ENGL': 'Italy'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'ITI4'},
                 {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '3',
                   'NAME_LATN': 'Roma', 'NUTS_ID': 'ITI43', 'NUTS_NAME': 'Roma',
                   'OBJECTID': '1053',
                   'SHRT_ENGL': 'Italy'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'ITI43'}]  
            
        If we are interested in one level only instead:
                
        ::

            >>> serv.coord2nuts([41.8933203,12.4829321], level=2)
                {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2',
                  'NAME_LATN': 'Lazio', 'NUTS_ID': 'ITI4', 'NUTS_NAME': 'Lazio',
                  'OBJECTID': '330',
                  'SHRT_ENGL': 'Italy'},
                 'displayFieldName': 'NUTS_ID',
                 'layerId': 2, 'layerName': 'NUTS_2013',
                 'value': 'ITI4'}        
        
        See also
        --------
        :meth:`~GISCOService.place2area`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`,
        :meth:`~GISCOService.coord2place`, :meth:`~GISCOService.url_findnuts`, 
        :meth:`base._Service.get_response`.
        """
        level = kwargs.pop('level',None)
        kwargs.update({'key': _Decorator.parse_nuts.KW_RESULTS})
        nuts = []        
        #[nuts.append(data if len(data)>1 else data[0]) for data in self._coord2nuts(coord, **kwargs)]
        func = lambda **kw: [kw.get('nuts')]
        [nuts.append(data if len(data)>1 else data[0])                     \
             for g in self._coord2nuts(coord, **kwargs)                     \
             for data in _Decorator.parse_nuts(func)(g, level=level)]
        return nuts[0] if len(nuts)==1 else nuts

    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_place
    def place2nuts(self, place, **kwargs): # specific use
        """Retrieve the various |NUTS| geometries (all levels) associated to given 
        geolocation(s) provided as a (topo)name.
        
        ::
        
            >>> nuts = serv.place2nuts(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        level : int
            see :meth:`~GISCOService.coord2nuts` method.
        unique : bool
            when set to :data:`True`, a single geometry is filtered out, the first 
            available one; default to :data:`True`.
        
        Returns
        -------
        nuts : dict, list[dict]
            see :meth:`~GISCOService.coord2nuts` method.
                
        Example
        -------
        Let us run a simple example:
        
        ::
            
            >>> serv = services.GISCOService()
            >>> serv.place2nuts('Vilnius, Lituania')
                [{'attributes': {'CNTR_CODE': 'LT', 'LEVL_CODE': '0',
                   'NAME_LATN': 'LIETUVA', 'NUTS_ID': 'LT', 'NUTS_NAME': 'LIETUVA',
                   'OBJECTID': '19',
                   'SHRT_ENGL': 'Lithuania'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'LT'},
                 {'attributes': {'CNTR_CODE': 'LT', 'LEVL_CODE': '1',
                   'NAME_LATN': 'LIETUVA', 'NUTS_ID': 'LT0', 'NUTS_NAME': 'LIETUVA',
                   'OBJECTID': '96',
                   'SHRT_ENGL': 'Lithuania'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'LT0'},
                 {'attributes': {'CNTR_CODE': 'LT', 'LEVL_CODE': '2',
                   'NAME_LATN': 'Lietuva', 'NUTS_ID': 'LT00', 'NUTS_NAME': 'Lietuva',
                   'OBJECTID': '332',
                   'SHRT_ENGL': 'Lithuania'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'LT00'},
                 {'attributes': {'CNTR_CODE': 'LT', 'LEVL_CODE': '3',
                   'NAME_LATN': 'Vilniaus apskritis', 'NUTS_ID': 'LT00A', 'NUTS_NAME': 'Vilniaus apskritis',
                   'OBJECTID': '1066',
                   'SHRT_ENGL': 'Lithuania'},
                  'displayFieldName': 'NUTS_ID',
                  'layerId': 2, 'layerName': 'NUTS_2013',
                  'value': 'LT00A'}]
            
        Or one can also run:
        
        ::
            
            >>> serv.place2nuts('Valencia, Spain', level=2)
                {'attributes': {'CNTR_CODE': 'ES', 'LEVL_CODE': '2',
                  'NAME_LATN': 'Comunidad Valenciana', 'NUTS_ID': 'ES52', 'NUTS_NAME': 'Comunidad Valenciana',
                  'OBJECTID': '260',
                  'SHRT_ENGL': 'Spain'},
                 'displayFieldName': 'NUTS_ID',
                 'layerId': 2, 'layerName': 'NUTS_2013',
                 'value': 'ES52'}        
            
        Note
        ----
        This method simply runs :meth:`~GISCOService.place2coord` then 
        :meth:`~GISCOService.coord2nuts`.
        
        See also
        --------
        :meth:`~GISCOService.place2coord`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2area`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.url_geocode`, 
        :meth:`base._Service.get_response`.
        """
        kwargs.update({'unique': kwargs.pop('unique',True)})
        coord = self.place2coord(place, **kwargs)
        nuts = self.coord2nuts(coord, **kwargs)
        return nuts[0] if len(nuts)==1 else nuts
        #res = _Decorator.parse_nuts(lambda **kw: kw.get('nuts'))(nuts, **kwargs)
        #return res[0] if len(res)==1 else res

    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2route(self, coord, **kwargs):
        """Retrieve the route going through the various steps/destinations represented 
        by a list of geographic coordinates. 
        
        ::
        
            >>>  route, waypoints = serv.coord2route(coord, **kwargs)

        Arguments
        ---------
        coord : list[list]
            list of geolocations defining the different steps/destinations along 
            the route; the steps are expressed as tuple/list of :literal:`(lat,Lon)` 
            geographic coordinates; needs to be of length 2 at least.
        
        Returns
        -------
        route : dict
            encoded shortest route going through the steps/destinations defined in 
            :data:`coord`.
        waypoints : 
            additional waypoints along the route.
        
        Raises
        ------
        ~settings.happyError
            error is raised in the cases:
            
                * the route request is wrongly formulated,
                * the route is not available,                
                * the route is not recognised.

        Example
        -------
        Let us retrieve the route between Sofia and Prague, using the other methods
        defined by the service:
        
        ::
        
            >>> serv = services.GISCOService()
            >>> sofia = serv.place2coord(place='Sofia, Bulgaria', unique=True)
            >>> print(sofia)
                [42.6978634, 23.3221789]
            >>> prague = serv.place2coord(place='Prague, Czech Republic', unique=True)
            >>> rte, pts = serv.coord2route([sofia, prague])
            >>> print(rte)
                {'distance': 3457666.8,
                 'duration': 200144.5,
                 'geometry': '{|rpHgqrcGp}q@lq~@qjNl_tAr~bBvtw@|{dAfzzBzmMt|kBvglEbqm@`wcBzn{@rby@rsrOx|bArrgDpZpndCwtUnho@blm@pfvNi{iAlajD~eJnisAl{t@da|@a}F`fw@|cw@~h}BxxAvfw@gdo@plpBxkVfhsBrh}Dj_dAjbZxjrAhsdChprBlo}@fiHiGz_~El`k@vul@fgfC`nf@l`IvzwFxo]zn}@lzaBbeoAtgPhj{BzcwBlfW~d}Dg~vA`vnBdkpDb|pBmvM`rfAfy_@znb@exu@||hAmx\\frWhnOfoC`vgAnkX}~oBzjeAkih@dz\\iltBhgx@pnl@bbyEmwbAjx{GoohFh{rAzheA',
                 'legs': [{'distance': 3457666.8,
                   'duration': 200144.5,
                   'steps': [],
                   'summary': ''}]}
            >>> print(pts)
                [{'hint': 'OF_ThAvR_YQAAAAAIgAAAHgBAABZLQAAAAAAAIMhswJScQAAZoeLAqsO_AKHhIsCKUb8Ai4AAQEZfn5e', 'name': '', 'location': [42.698598, 50.073259]}, 
                 {'hint': 'bqpLg3shJoQAAAAACwAAAAAAAAA0AgAANgAAADa0BQJScQAA2Wp6AcfzFAJC3mMBBQ3cAAcAAQEZfn5e', 'name': '', 'location': [24.799961, 34.927559]}]
           
        See also
        --------
        :meth:`~GISCOService.place2route`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.url_route`, :meth:`base._Service.get_response`.
        """
        routes, waypoints = None, None
        if len(coord)<2 or not all([happyType.issequence(c) for c in coord]):
            raise happyError('wrong format for list of destinations along the route')
        if not coord in([],None):
            coordinates = ';'.join([','.join([str(l), str(L)]) for (l,L) in coord])
        elif kwargs.get():
            coordinates = kwargs.pop(_Decorator.parse_coordinate.KW_POLYLINE)
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
            assert _Decorator.parse_route.KW_CODE in data       \
                and data[_Decorator.parse_route.KW_CODE].upper() == "OK"
        except:
            raise happyError('route  not recognised')      
        else:
            routes = data.get(_Decorator.parse_route.KW_ROUTES)
            waypoints = data.get(_Decorator.parse_route.KW_WAYPOITNS)
        return routes[0], waypoints

    #/************************************************************************/
    @_Decorator.parse_place
    def place2route(self, place, **kwargs):
        """Retrieve the route going through the various steps/destinations represented 
        by a list of (topo) name(s). 
         
        ::
       
            >>>  route, waypoints = serv.place2route(place, **kwargs)

        Arguments
        ---------
        place : list[str]
            list of geolocations defining the different steps/destinations along 
            the route; the steps are expressed as place (topo) name(s); needs to 
            be of length 2 at least.
        
        Returns
        -------
        route, waypoints : 
            shortest route and waypoints along the route; see :meth:`~GISCOService.coord2route`
            method.
        
        Raises
        ------
        ~settings.happyError
            see :meth:`~GISCOService.coord2route` method.

        Example
        -------    
        We reproduce here the example already used in :meth:`~GISCOService.coord2route`
        but parsing directly the toponames to the method: 
        
        ::
        
            >>> serv = services.GISCOService()
            >>> serv.place2route(place=['Sofia, Bulgaria','Prague, Czech Republic'])
                ({'distance': 3457666.8,
                  'duration': 200144.5,
                  'geometry': '{|rpHgqrcGp}q@lq~@qjNl_tAr~bBvtw@|{dAfzzBzmMt|kBvglEbqm@`wcBzn{@rby@rsrOx|bArrgDpZpndCwtUnho@blm@pfvNi{iAlajD~eJnisAl{t@da|@a}F`fw@|cw@~h}BxxAvfw@gdo@plpBxkVfhsBrh}Dj_dAjbZxjrAhsdChprBlo}@fiHiGz_~El`k@vul@fgfC`nf@l`IvzwFxo]zn}@lzaBbeoAtgPhj{BzcwBlfW~d}Dg~vA`vnBdkpDb|pBmvM`rfAfy_@znb@exu@||hAmx\\frWhnOfoC`vgAnkX}~oBzjeAkih@dz\\iltBhgx@pnl@bbyEmwbAjx{GoohFh{rAzheA',
                  'legs': [{'distance': 3457666.8,
                    'duration': 200144.5,
                    'steps': [],
                    'summary': ''}]},
                 [{'hint': 'OF_ThAvR_YQAAAAAIgAAAHgBAABZLQAAAAAAAIMhswJScQAAZoeLAqsO_AKHhIsCKUb8Ai4AAQEZfn5e',
                   'location': [42.698598, 50.073259],
                   'name': ''},
                  {'hint': 'bqpLg3shJoQAAAAACwAAAAAAAAA0AgAANgAAADa0BQJScQAA2Wp6AcfzFAJC3mMBBQ3cAAcAAQEZfn5e',
                   'location': [24.799961, 34.927559],
                   'name': ''}])
           
        See also
        --------
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.url_route`.
        """
        if not happyType.issequence(place) or len(place)<2 or not all([happyType.isstring(p) for p in place]):
            raise happyError('wrong format for list of destinations along the route')
        kwargs.update({'unique': True})
        coord = [self.place2coord(p, **kwargs) for p in place]
        return self.coord2route(coord, **kwargs)

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
                 #'OpenMapQuest':     None,       # No API Key is needed by the Nominatim based platform
                 'MapQuest':         'key',  # API key provided by MapQuest
                 'LiveAddress':      'token',# Valid authentication token; LiveAddress geocoder provided by SmartyStreets
                 'Nominatim':        None,       # Nominatim geocoder for OpenStreetMap servers
                 } 
     
        #/********************************************************************/
        def __init__(self, **kwargs):
            # call geocoder module geopy: https://github.com/geopy/geopy'
            self._gc = None
            coder = kwargs.pop('coder', 'GeoNames')
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
        
        Most of the :class:`geopy.geocoders` methods are inherited by the class
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
        """Class emulating :class:`googlemaps.Client` API (whenever the package 
        |googlemaps| is available).

        Inherit many methods from original API.

        Most of the :class:`googlemaps.Client` methods are inherited by the
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
                raise IOError('Google client key not recognised')
            self.client_key = key
            super(_googlePlacesAPI,self).__init__(self.client_key)

        #/********************************************************************/
        geocode = classmethod(googleplaces.geocode_location)
        # nearby_search, text_search, get_place are regular attributes

_googlePlacesAPI.__doc__ =                                                  \
        """Class emulating :class:`googleplaces.GooglePlaces` API (whenever the 
        package |googleplaces| is available).

        Inherit most methods from original API.

        Most of the :class:`googleplaces.GooglePlaces` methods are inherited by the
        :class:`~services.APIService` class through composition and embedding 
        in container attributes. 
        """

#%%
#==============================================================================
# CLASS APIService
#==============================================================================
     
class APIService(_Service):
    """Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
        
    ::
       
        >>> serv = services.APIService(**kwargs)
            
    Keyword arguments
    -----------------
    domain : str
        domain of |OSM| web-services hosted by |GISCO|; default is :data:`settings.GISCO_URL`,
        *e.g.* an URL domain like :literal:`'europa.eu/webtools/rest/gisco/'`\ . 
    coder : str
        identifier of the geocoder, *e.g.* |Google_Maps|, |Google_Places|, 
        *etc*... used for geolocation queries.
    key/token/username : str
        key (depending on the :data:`coder` actually chosen) used to connect 
        to the geolocation API.
 
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
                 | _geoCoderAPI.CODER.items()) # we know there is no duplicate, so ok to use | ...

    AVAILABLE = list(CODER.keys())
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        # initial settings
        self.__coder, self.__coder_key = None, ''
        try:
            assert API_SERVICE is not False
        except:
            raise happyError('external API service not available')
        # read the arguments              
        self.__coder = kwargs.pop('coder', settings.CODER_GOOGLE_MAPS)
        if self.__coder not in self.CODER.keys():
            raise happyError('geocoder %s not recognised/available' % self.__coder)
        self.__coder_key  = kwargs.get(self.CODER[self.__coder]) # it is a get!!! maybe None
        if self.__coder in _googleMapsAPI.CODER.keys():
            try:
                # geomapper defined as an instance of _googleMapsAPI class derived
                # from googlemaps.GoogleMaps
                self.__coder = _googleMapsAPI(**kwargs) 
            except:
                raise happyError('Google Maps geocoder not available')
        elif self.__coder in _googlePlacesAPI.CODER.keys():
            try:
                # geolocator defined as an instance of _googlePlacesAPI class
                # derived from googleplaces.GooglePlaces
                self.__coder = _googlePlacesAPI(**kwargs) 
            except:
                raise happyError('Google Places geocoder not available')
        elif self.__coder in _geoCoderAPI.CODER.keys():
            try:
                # geocoder defined as an instance of _geoCoderAPI class derived from 
                # geopy.geocoders
                self.__coder = _geoCoderAPI(coder=self.__coder, **kwargs) 
            except:
                raise happyError('geopy geocoder not available')
            
    #/************************************************************************/
    @property
    def coder(self):
        """Coder property (:data:`getter`) of a :class:`APIService` instance. 
        A `coder` type is a either :class:`~happygisco.services._googlePlacesAPI`,  
        or a :class:`~happygisco.services._googleMapsAPI`, or  
        :class:`~happygisco.services._geoCoderAPI` object.
        """
        return self.__coder
            
    @property
    def coder_key(self):
        """Key property (:data:`getter`/:data:`setter`) of a :class:`APIService` 
        instance. 
        A `coder_key` type is a :class:`str` object.
        """
        return self.__coder_key
    @coder_key.setter
    def coder_key(self, key):
        if not isinstance(key, str):
            raise IOError('wrong type for CODER_KEY parameter')
        self.__coder_key = key

    #/************************************************************************/
    @_Decorator.parse_place
    def place2coord(self, place, **kwargs):
        """Retrieve the geographic coordinates of a given place provided by 
        its (topo)name.
                
        ::

            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            depends on the geocoder.
            
        Returns
        -------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of geographic :literal:`(lat,Lon)` 
            coordinates.
        
        See also
        --------
        :meth:`GISCOService.place2coord`.
        """
        coord = [] 
        for p in place:   
            try:
                res = self.coder.geocode(p)
                try:
                    lat, lon = res.latitude, res.longitude
                except:
                    try:
                        lat, lon = res.lat, res.Lon                    
                    except:
                        lat, lon = res
                assert lat not in ([],None) and lon not in ([],None)
                coord.append([lat,lon])
            except:
                coord.append(None)
                happyVerbose('\ncould not retrieve geolocation of %s' % p)
                # continue
            else:
                # happyVerbose('%s => %s' % (p, coord))
                pass
        return coord if len(coord)>1 else coord[0]

    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2place(self, coord, **kwargs):
        """Retrieve the (topo)name of a given location provided by its geographic
        coordinates using the API geocoding service.
        
        ::
        
            >>> place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            depends on the geocoder.
            
        Returns
        -------
        place : str, list[str]
            place (topo) name(s).

        See also
        --------
        :meth:`GISCOService.coord2place`.
        """
        place = [] 
        for i in range(len(coord)):   
            try:
                p = self.coder.reverse(coord[i][0],coord[i][1])
                assert p not in ('',None)
                place.append(p)
            except:
                place.append(None)
                happyVerbose('\ncould not retrieve place name for geolocation %s' % coord[i])
                # continue
            else:
                # happyVerbose('%s => %s' % (p, coord))
                pass
        return place if len(place)>1 else place[0]
