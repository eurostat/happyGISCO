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

*require*:      :mod:`io`, :mod:`io`, :mod:`collections`, :mod:`itertools`, :mod:`json`

*optional*:     :mod:`geopy`, :mod:`googlemaps`, :mod:`googleplaces`, :mod:`pandas`, :mod:`Levenshtein`

*call*:         :mod:`settings`, :mod:`base`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr  7 01:46:51 2018

__all__         = ['OSMService', 'GISCOService', 'APIService', 
                   '_googleMapsAPI', '_googlePlacesAPI', '_geoCoderAPI']

# generic import
import io
import collections, itertools

# local (absolute) imports
from happygisco import happyVerbose, happyWarning, happyError, happyType
from happygisco import settings
from happygisco.base import _Decorator, _Service, _NestedDict#analysis:ignore

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
    happyWarning('missing GOOGLEMAPS package (https://pypi.python.org/pypi/googlemaps/)')
else:
    API_SERVICE = True
    happyVerbose('GOOGLEMAPS help: https://github.com/googlemaps/google-maps-services-python')

try:
    import googleplaces
except ImportError:
    happyWarning('missing GOOGLEPLACES package (https://github.com/slimkrazy/python-google-places)')   
else:
    API_SERVICE = True
    happyVerbose('GOOGLEPLACES help: https://github.com/slimkrazy/python-google-places')

try:
    import geopy
except ImportError:
    happyWarning('missing GEOPY package (https://github.com/geopy/geopy)')   
else:
    API_SERVICE = True
    happyVerbose('GEOPY help: http://geopy.readthedocs.io/en/latest/')
   
try:
    assert geopy or googlemaps or googleplaces
except:
    API_SERVICE = False
    happyWarning('NO external API service available')
   
try:
    import pandas as pd
except ImportError:
    PANDAS_INSTALLED = False
    happyWarning('missing Pandas package (http://pandas.pydata.org)')   
except:
    PANDAS_INSTALLED = True
    happyVerbose('pandas help: https://pandas.pydata.org/pandas-docs/stable/')

try:
    import Levenshtein
except ImportError:
    LEVENSHTEIN_INSTALLED = False
    happyWarning('missing python-Levenshtein package (https://github.com/ztane/python-Levenshtein) - Map resources not available')
else:
    LEVENSHTEIN_INSTALLED = True
    happyVerbose('Levenshtein help: https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html')
    
try:                                
    import simplejson as json
except ImportError:
    # happyWarning("missing SIMPLEJSON package (https://pypi.python.org/pypi/simplejson/)", ImportWarning)
    try:                                
        import json
    except ImportError: 
        # happyWarning("JSON module missing in Python Standard Library", ImportWarning)
        class json:
            def loads(arg):  return '%s' % arg

#%%
#==============================================================================
# CLASS OSMService
#==============================================================================
    
class OSMService(_Service):
    """Class providing conversion methods and geocoding tools that run the |Nominatim| 
    online web-service of the |OSM| API.
       
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
        URL of |OSM|, *e.g.* :data:`settings.OSM_URL`, of an instance of this class. 
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
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :literal:`[format, json_callback, accept-language, extratags, namedetails, q, street, city,`
            :literal:`county, state, country, postalcode, countrycodes, viewbox, bounded, addressdetails,`
            :literal:`email, limit, dedupe, debug, polygon_geojson, polygon_kml,polygon_svg, polygon_text]`;
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
            
            >>> serv = services.OSMService()
            >>> serv.url_geocode(q='Paris+France', format='json')
                'https://nominatim.openstreetmap.org/search?q=Paris+France&format=json'
        
        See also
        --------
        :meth:`~OSMService.url_reverse`, :meth:`~OSMService.url_routing`, 
        :meth:`~OSMService.url_transform`, :meth:`base._Service.build_url`.
        """
        query = kwargs.pop('query', 'search')
        keys = kwargs.pop('keys', None) or                                  \
            ['format', 'json_callback', 'accept-language', 'extratags', 'namedetails', 
             'q', 'street', 'city', 'county', 'state', 'country', 'postalcode', 'countrycodes', 
             'viewbox', 'bounded', 'addressdetails', 'email', 'limit', 'dedupe', 'debug', 
             'polygon_geojson', 'polygon_kml', 'polygon_svg', 'polygon_text']
        happyVerbose('\n            * '.join(['input filters used for geocoding service :',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=settings.PROTOCOL,
                             domain=self.domain, 
                             query=query, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for |Nominatim| reverse geocoding web-service (from 
        geocoordinate to toponame).
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :literal:`lat, lon, format, json_callback, accept-language, extratags, email, osm_type,`
            :literal:`osm_id, zoom, addressdetails, polygon_geojson, polygon_kml, polygon_svg, polygon_text]`;
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

            >>> serv = services.OSMService()
            >>> serv.url_reverse(lon=10, lat=52)
                'https://nominatim.openstreetmap.org/reverse?lon=10&lat=52'
        
        See also
        --------
        :meth:`~OSMService.url_geocode`, :meth:`~OSMService.url_routing`, 
        :meth:`~OSMService.url_transform`, :meth:`base._Service.build_url`.
        """
        query = kwargs.pop('query', 'reverse')
        path = kwargs.pop('path','')
        keys = kwargs.pop('keys', None) or                                  \
            ['format', 'json_callback', 'accept-language', 'extratags', 'email', 
             'osm_type', 'osm_id', 'lat', 'lon', 'zoom', 'addressdetails', 
             'polygon_geojson', 'polygon_kml', 'polygon_svg', 'polygon_text']
        happyVerbose('\n            * '.join(['input filters used for reverse geocoding service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=settings.PROTOCOL,
                             domain=self.domain, 
                             query=query, 
                             path=path,
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    def _place2geom(self, place, **kwargs): 
        """Iterable version of :meth:`~OSMService.place2geom`.
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
            except:
                raise happyError('error geolocation URL formatting')
            try:
                data = self.read_url(url, fmt='JSON')
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
    #def place2geom(self, place, **kwargs): 
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
    def place2geom(self, place, **kwargs):
        """Retrieve the geographical information associated to a given place as a
        geometry object using |OSM| service.
        
            >>> area = serv.place2geom(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[format, json_callback, accept-language, extratags, namedetails,`
            :literal:`street, city, county, state, country, postalcode, countrycodes, viewbox,`
            :literal:`bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson,`
            :literal:`polygon_kml, polygon_svg, polygon_text]` are accepted; see :meth:`~OSMService.url_geocode`.
        
        Returns
        -------
        area : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input olace(s) in :data:`place`, one for each 
            place mentioned.
                  
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
                
        Examples
        --------
        We will retrieve the geolocation of Berlin, Germany:
        
            >>> berlin = 'Berlin, Germany'
        
        For that purpose, we can build the desired |OSM| URL:
        
            >>> serv = services.OSMService()
            >>> serv.url_geocode(place=berlin) 
                'https://nominatim.openstreetmap.org/search?format=json&q=Berlin+Germany'
        
        though the method :meth:`place2geom` enables us to run the operation all
        in once: 

            >>> serv.place2geom(berlin, format='json')
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
        :meth:`~OSMService.url_geocode`, :meth:`~GISCOService.place2geom`, 
        :meth:`base._Service.get_status`, :meth:`base._Service.get_response`.
        """
        unique = kwargs.pop('unique',False)
        area = []
        [area.append(data if data is None or (len(data)>1 and unique is False) else data[0]) \
             for data in self._place2geom(place, **kwargs)]
        return area if area==[] or len(area)>1 else area[0]
       
    #/************************************************************************/
    def _coord2geom(self, coord, **kwargs): 
        """Iterable version of :meth:`~OSMService.coord2geom`.
        """
        if not happyType.issequence(coord):     
            coord = list(coord)
        if not all([happyType.issequence(c) for c in coord]):     
            coord = [list(c) for c in coord]
        fmt = kwargs.pop('format','')
        key = kwargs.pop('key',None)
        if fmt not in ('', None):
            kwargs.update({'format':'json'})
        for i in range(len(coord)):
            kwargs.update({'lat': coord[i][0], 'lon': coord[i][1]})
            try:
                url = self.url_reverse(**kwargs)
            except:
                raise happyError('error geolocation reverse URL formatting')
            try:
                data = self.read_url(url, fmt='JSON')
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
    #def coord2geom(self, lat, lon, **kwargs): # specific use
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
    #            assert _Decorator.parse_geometry.KW_FEATURES in data     \
    #                and data[_Decorator.parse_geometry.KW_FEATURES] != []
    #        except:
    #            raise happyError('place for geolocation (%s,%s) not recognised' % (lat[i], lon[i]))      
    #        else:
    #            p = data.get(_Decorator.parse_geometry.KW_FEATURES)
    #            area.append(p if len(p)>1 else p[0])
    #    return area[0] if len(area)==1 else area
    @_Decorator.parse_coordinate
    def coord2geom(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographic coordinates using |OSM| service.

            >>>  area = serv.coord2geom(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[format, json_callback, accept-language, extratags, email, osm_type,` 
            :literal:`osm_id, zoom, addressdetails, polygon_geojson, polygon_kml, polygon_svg, polygon]`
            are accepted; see :meth:`~OSMService.url_reverse`.
        
        Returns
        -------
        area : dict, list[dict]
            a (list of) geometry(ies), *i.e.* dictionary(ies) describing the geographical
            information related to the input geographic coordinate(s) in :data:`coord`, 
            one for each coordinate listed.
        
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
            >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
            >>> serv = services.OSMService()
            >>> serv.url_reverse(coord=berlin) 
                'https://nominatim.openstreetmap.org/reverse?format=json&lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2geom` does everything at once:
       
            >>> serv.coord2geom(berlin, format='json')
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
        geom = []
        [geom.append(data if data is None or len(data)>1 else data[0]) \
             for data in self._coord2geom(coord, **kwargs)]
        return geom[0] if geom==[] or len(geom)==1 else geom

    @_Decorator.parse_place
    def place2coord(self, place, **kwargs):
        """Retrieve the  geographic coordinates of a given place provided by its 
        (topo)name using |OSM| service.
        
            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[format, json_callback, accept-language, extratags, namedetails,` 
            :literal:`street, city, county, state, country, postalcode, countrycodes, viewbox,`
            :literal:`bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson,`
            :literal:`polygon_kml, polygon_svg,polygon_text]` are accepted; 
            see :meth:`~OSMService.url_geocode`.
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
            
        Notes
        -----
        * Note that the geocoding may apparently result in some erroneous answer
          owing to the naming ambiguity, *e.g.*:
            
            >>> serv.place2coord('Rome, Italy') # most surely the right location
                [41.8933203, 12.4829321]
            >>> serv.place2coord('Roma, Italy') # nothing like the one above
                [[44.5996045, 10.4584101],
                 [44.705595, 9.717744893877548],
                 [44.4369452, 11.2235352]]
            >>> serv.place2coord('Roma, Italia')
                [[41.8933203, 12.4829321],
                 [41.706989, 12.6911183],
                 [42.141078, 12.3836686],
                 [41.988224, 13.067989],
                 [41.5393232, 13.2796473]]
            
        * This method simply "decorates" the method :meth:`~OSMService._place2geom`
          with :meth:`_Decorator.parse_geometry`.

        See also
        --------
        :meth:`~OSMService.place2geom`, :meth:`~OSMService.coord2place`,
        :meth:`GISCOService.place2coord`.
        """
        unique, order = kwargs.pop('unique',False), kwargs.pop('order','lL')
        coord = []
        # note the presence below of *a so as to ensure that None responses are 
        # also parsed
        func = lambda *a, **kw: [kw.get(_Decorator.KW_COORD)]
        [coord.append(data if data is None or len(data)>1 else data[0])     \
             for g in self._place2geom(place, **kwargs)                     \
             for data in _Decorator.parse_geometry(func)(g, filter='coord', order=order, unique=unique)]
        return coord if coord==[] or len(coord)>1 else coord[0]

    @_Decorator.parse_coordinate
    def coord2place(self, coord, **kwargs):
        """Retrieve the (topo)name of a given location provided by its geographic 
        coordinates using |OSM| service.
       
            >>> place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`format, json_callback, accept-language, extratags, namedetails,` 
            :literal:`street, city, county, state, country, postalcode, countrycodes, viewbox,`
            :literal:`bounded, addressdetails, email, limit, dedupe, debug, polygon_geojson, polygon_kml,`
            :literal:`polygon_svg, polygon_text]` are accepted; see :meth:`~OSMService.url_geocode`.
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
            
            >>> serv = services.OSMService()
            >>> serv.coord2place([41.8933203, 12.4829321])
                'Statua equestre di Marco Aurelio, Piazza del Campidoglio, Municipio Roma I, Roma, RM, LAZ, 00186, Italia'        
            >>> serv.coord2place([55.6867243, 12.5700724])
                '3A, Øster Farimagsgade, Indre Østerbro, Frederiksstaden, København, Københavns Kommune, Region Hovedstaden, 1353, Danmark'
            
        Note
        ----
        This method simply "decorates" the method :meth:`~OSMService._coord2geom`
        with :meth:`_Decorator.parse_geometry`.
            
        See also
        --------
        :meth:`~OSMService.coord2geom`, :meth:`~OSMService.place2coord`,
        :meth:`GISCOService.coord2place`.
        """
        unique = kwargs.pop('unique',False)
        place = []
        func = lambda *a, **kw: [kw.get(_Decorator.KW_PLACE)]
        [place.append(data if data is None or len(data)>1 else data[0])     \
             for a in self._coord2geom(coord, **kwargs)                     \
             for data in _Decorator.parse_geometry(func)(a, filter='place', unique=unique)]
        return place if place==[] or len(place)>1 else place[0]

#%%
#==============================================================================
# CLASS GISCOService
#==============================================================================
    
class GISCOService(OSMService):
    """Class providing conversion methods and geocoding tools that run the |GISCO| 
    online web-service, itself based on |OSM| |Nominatim| API.
       
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
            # assert not('domain' in kwargs.keys() and 'rest_url' in kwargs.keys())
        except:
            happyVerbose('parameter DOMAIN ignored (URL_REST can be used instead)', verb=True)
            # raise happyError('incompatible parameters DOMAIN and URL_REST')
        self.__domain = kwargs.get(_Decorator.KW_REST_URL,      settings.GISCO_RESTURL) # or self.rest_url
        self.__cache_url = kwargs.get(_Decorator.KW_CACHE_URL,  settings.GISCO_CACHEURL)
        self.__map_url = kwargs.get(_Decorator.KW_MAP_URL,      settings.GISCO_TILEURL)
        self.__arcgis = kwargs.get(_Decorator.KW_ARCGIS,        settings.GISCO_ARCGIS)
                 
    #/************************************************************************/
    def __getattr__(self, attr): 
        #if attr in inspect.getmembers(base._NestedDict, predicate=inspect.ismethod):
        #   return object.__getattribute__(self, attr)
        try:
            assert attr in [settings.GISCO_PATTERNS[entity]['info'].format(year=year) 
                for year in settings.GISCO_YEARS for entity in ('country','nuts','nutsid')]
            # 'countries-{year}-units',  'nuts-{year}-units',  'NUTS_AT_{year}',
            return getattr(self, '__' + attr)
        except (AttributeError,AssertionError):
            # raise happyError('attribute %s not recognised' % attr)
            raise AttributeError('attribute %s not recognised' % attr)
        # ok, we are being naughty here, hiding this from the user...

    #/************************************************************************/
    @property
    def rest_url(self):
        """REST property (:data:`getter`/:data:`setter`) defining the complete
        URL of REST services, *e.g.* :data:`settings.GISCO_RESTURL`, of an instance 
        of this class. 
        """
        return self.__domain
    @rest_url.setter#analysis:ignore
    def rest_url(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for %s parameter' % _Decorator.KW_REST_URL.upper())
        self.__domain = url or ''
        
    # let us just override the super property domain
    domain = rest_url

    #/************************************************************************/
    @property
    def cache_url(self):
        """Cache property (:data:`getter`/:data:`setter`) defining the complete
        URL of |GISCO| cache services, *e.g.* :data:`settings.GISCO_CACHEURL`, of 
        an instance of this class. 
        """ 
        return self.__cache_url
    @cache_url.setter#analysis:ignore
    def cache_url(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for %s parameter' % _Decorator.KW_CACHE_URL.upper())
        self.__cache_url = url or ''

    #/************************************************************************/
    @property
    def map_url(self):
        """URL property (:data:`getter`/:data:`setter`) defining the complete
        URL of GISCO mapping services, *e.g.* :data:`settings.GISCO_MAPURL`, of 
        an instance of this class. 
        """ 
        return self.__map_url
    @map_url.setter#analysis:ignore
    def map_url(self, url):
        if url is not None and not happyType.isstring(url):
            raise TypeError('wrong type for %s parameter' % _Decorator.KW_MAP_URL.upper())
        self.__map_url = url or ''

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
            raise TypeError('wrong type for %s parameter' % _Decorator.KW_ARCGIS.upper())
        self.__arcgis = arcgis or ''
    
    #/************************************************************************/
    def url_nuts(self, source=None, **kwargs):
        """Generate the URL in the |GISCO| domain for the (bulk or not) download 
        of NUTS data (in vector format).
            
            >>> url = serv.url_nuts(source, **kwargs)
           
        Keyword arguments
        -----------------
        file : str
        year : int
        scale : str,int
        fmt : str
        proj : str,int
        feat : str,int
             
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
        It is actually possible to generate the URLs of all |NUTS| related datasets 
        available from |GISCO| Rest API and/or bulk download website:
            
            >>> serv = services.GISCOService()
            >>> serv.url_nuts()  # default: a given NUTS dataset...
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_RG_01M_2013_4326_LEVL_0.geojson'
            >>> serv.url_nuts('BULK')
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.geojson.zip'
            >>> serv.url_nuts('AD')
                'https://europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AD-region-01m-4326-2013.geojson'
                
            >>> serv.url_nuts('NUTS', year = 2016, scale = 10, vector = 'boundary')
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_BN_10M_2016_4326_LEVL_0.geojson'
            >>> serv.url_nuts('BULK', year = 2016, scale = 60, fmt = 'shp')
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2016-60m.shp.zip'
            >>> serv.url_nuts(year = 2010, vector = 'label', level = 2)  
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_LB_2010_4326_LEVL_2.geojson'
            >>> serv.url_nuts(year = 2010, scale = 1, vector = 'boundary', level = 'ALL', proj = 'Mercator')  
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_BN_01M_2010_3857.geojson'
            >>> serv.url_nuts('INFO', year = 2010)  
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/nuts-2010-units.json'
                
            >>> serv.url_nuts('MK', year = 2006, scale = 20, vector = 'region', proj = 'LAEA')
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/MK-region-20m-3035-2006.geojson'
            >>> serv.url_nuts('BE100', year = 2016, vector = 'LB')
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE100-label-4326-2016.geojson'        
        
        Note also:
                
            >>> serv.url_nuts('BE100', year = 2016, scale = 3, vector = 'boundary', fmt ='shp')
                    ! only LABEL and REGION features are supported with single NUTS units distribution - FEATURE argument ignored !
                    ! only GEOJSON is supported with single NUTS units distribution - FMT argument ignored !
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE100-region-03m-4326-2016.geojson'       
        
        Further note that it is possible to build the URL linking to the NUTS datasets 
        from the preformated |Nuts2json| data collection:
            
            >>> serv.url_nuts('nuts2json', scale = '20m', level = 2)
                'https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/2013/4326/20M/nutsrg_2.json'
            >>> serv.url_nuts('nuts2json', proj = 'EPSG3035', year = 2010, fmt = 'topojson')
                'https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/2010/3035/60M/0.json'
                
        See also
        --------
        :meth:`~GISCOService.nuts_response`, :meth:`~GISCOService.url_country`,
        :meth:`~GISCOService.url2nutsinfo`.        
        """
        # check whether a specific unit is looked for
        # btw, do we want to download GISCO data?
        try:
            assert source is None or happyType.isstring(source)
        except:
            raise happyError('wrong format/value for SOURCE argument')
        else:
            if source in (None, ''): 
                source = 'NUTS' # force to 'NUTS' in case it is None
            source = source.upper()
        # retrieve the keyword parameters... note that all this parsing/checking/cleaning
        # may have been done thanks to the parse_* methods
        year = kwargs.pop(_Decorator.KW_YEAR, settings.DEF_GISCO_YEAR)
        scale = kwargs.pop(_Decorator.KW_SCALE, 
                           settings.DEF_NUTS2JSON_SCALE if source == 'NUTS2JSON' else   \
                           settings.DEF_GISCO_SCALE if source in ('BULK','NUTS','INFO') else None)
        if source != 'NUTS2JSON' and scale in settings.GISCO_SCALES.keys():
            scale = settings.GISCO_SCALES[scale]
        fmt = kwargs.pop(_Decorator.KW_FORMAT, 
                         settings.DEF_NUTS2JSON_FORMAT if source == 'NUTS2JSON' else   \
                         settings.DEF_GISCO_FORMAT if source in ('BULK','NUTS') else None)
        if source != 'NUTS2JSON' and fmt in settings.GISCO_FORMATS.keys():
            fmt = settings.GISCO_FORMATS[fmt]
        #elif fmt in settings.DEF_NUTS2JSON_FORMAT.keys():
        #    fmt = settings.DEF_NUTS2JSON_FORMAT[fmt]
        proj = kwargs.pop(_Decorator.KW_PROJECTION, 
                          settings.DEF_NUTS2JSON_PROJECTION if source == 'NUTS2JSON' else   \
                          settings.DEF_GISCO_PROJECTION if source in ('BULK','NUTS','INFO') else None)
        if source != 'NUTS2JSON' and proj in settings.GISCO_PROJECTIONS.keys():
            proj = settings.GISCO_PROJECTIONS[proj]
        elif proj in settings.NUTS2JSON_PROJECTIONS.keys():
            proj = settings.NUTS2JSON_PROJECTIONS[proj]
        vec = kwargs.pop(_Decorator.KW_VECTOR, settings.DEF_GISCO_VECTOR) 
        if vec in settings.GISCO_VECTORS.keys():
            vec = settings.GISCO_VECTORS[vec]
        level = kwargs.pop(_Decorator.KW_LEVEL, settings.GISCO_NUTSLEVELS[0])        
        ## retrieve the default parameters values    
        #defkw = _Decorator.parse_default(settings.GISCO_DATA_DIMENSIONS, _force_list_=True)(lambda **kw: kw)
        #defkw = defkw()
        # set the compression format
        theme = settings.GISCO_NUTSTHEME 
        # start...
        url = {}
        protocol = settings.PROTOCOL # 'https'
        if source == 'NUTS2JSON':
            # the files can be retrieved on-the-fly from the base URL 
            #       https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/ 
            # according to the file pattern:
            #   * for topojson: /<YEAR>/<PROJECTION>/<SIZE>/<NUTS_LEVEL>.json
            #   * for geojson:  /<YEAR>/<PROJECTION>/<SIZE>/<TYPE>_<NUTS_LEVEL>.json
            # where <TYPE> depends on geom variable
            domain = settings.NUTS2JSON_DOMAIN
            url = '{a}://{b}/{c}/{d}/{e}/{f}{g}.{h}'.format                 \
                (a=protocol, b=domain, c=year, d=proj, e=scale.upper(), 
                 f='' if fmt!= 'geojson' else ('nutsrg_' if vec == 'RG' else 'nutsbn_'), 
                 g=level, h='json')
        elif source == 'BULK': # zipped files
            # example: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2016-10m.shp.zip
            domain = settings.GISCO_PATTERNS['bulk']['domain']
            basename = settings.GISCO_PATTERNS['bulk']['base']
            fmt = 'shp' if fmt=='shx' else fmt 
            fmt += '.' + settings.GISCO_PATTERNS['bulk']['compress']
            url = '{a}://{b}/{c}/{d}/{e}{f}-{g}.{h}'.format                           \
                (a=protocol, b=self.cache_url, c=theme, d=domain,
                 e=basename, f=year, g=scale.lower(), h=fmt)
        elif source == 'INFO':
            domain = ''
            if fmt != settings.GISCO_PATTERNS['nuts']['fmt']:
                if fmt is not None:
                    happyWarning('only JSON format is supported with INFO file - %s argument ignored' % _Decorator.KW_FORMAT.upper())
                fmt = settings.GISCO_PATTERNS['nuts']['fmt']
            basename = settings.GISCO_PATTERNS['nuts']['info']
            url = '{a}://{b}/{c}/{d}.{e}'.format                                     \
                (a=protocol, b=self.cache_url, c=theme, 
                 d=basename.format(year=year), e=fmt)
        elif source == 'NUTS': # unit == 'ALL'
            domain = {v:k for k,v in settings.GISCO_FORMATS.items()}[fmt]
            basename = settings.GISCO_PATTERNS['nuts']['base']
            if not vec in list(settings.GISCO_VECTORS.values()):
                vec = settings.GISCO_VECTORS[vec]
            # no indication of scale!!!
            scale = '' if vec == 'LB' else '_' + str(scale)
            level = '' if level == 'ALL' else '_LEVL_' + str(level)
            url = '{a}://{b}/{c}/{d}/{e}{f}{g}_{h}_{i}{j}.{k}'.format       \
                (a=protocol, b=self.cache_url, c=theme, d=domain,
                 e=basename, f=vec.upper(), g=scale.upper(), h=year, i=proj, j=level,
                 k=fmt)
            # example: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/topojson/NUTS_BN_01M_2016_3035_LEVL_3.json
        else: # files
            domain = settings.GISCO_PATTERNS['nuts']['domain']
            if not vec in list(settings.GISCO_VECTORS.keys()):
                vec = {v:k for k,v in settings.GISCO_VECTORS.items()}[vec]
            if vec not in ('label','region'):
                happyWarning('only LABEL and REGION features are supported with single NUTS units distribution - %s argument ignored' % _Decorator.KW_GEOMETRY.upper())
                vec = 'region' # settings.DEF_GISCO_VECTOR
            elif vec == 'label':
                if scale != '':
                    if scale is not None:
                        happyWarning('scale are not supported with LABEL datasets - %s argument ignored' % _Decorator.KW_SCALE.upper())
                    scale = ''
                if proj not in (3035,4258):
                    if proj is not None:
                        happyWarning('only 3035 and 4258 projections are supported with single LABEL unit distribution - %s argument ignored' % _Decorator.KW_PROJECTION.upper())
                    proj = 3035
            if vec == 'region': # not elif
                scale = scale.lower() + '-'
            if fmt != 'geojson':
                if fmt is not None:
                    happyWarning('only GEOJSON is supported with single NUTS units distribution - %s argument ignored' % _Decorator.KW_FORMAT.upper())
                fmt = 'geojson'
            url = '{a}://{b}/{c}/{d}/{e}-{f}-{g}{h}-{i}.{j}'.format        \
                (a=protocol, b=self.cache_url, c=theme, d=domain,
                 e=source, f=vec.lower(), g=scale, h=proj, i=year, 
                 j=fmt)
            # example: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT-region-01m-3035-2016.geojson
        return url if url is None or len(url)>1 else url[0]          
    
    #/************************************************************************/
    def url_lau(self, source=None, **kwargs):
        """Generate the URL of the |GISCO| LAU data files.
            
            >>> url = serv.url_lau(source=None, **kwargs)
           
        Keyword arguments
        -----------------
        """
        pass

    #/************************************************************************/
    def url_country(self, source=None, **kwargs):
        """Generate the URL (or name) of the |GISCO| countries vector datasets.
            
            >>> url = serv.url_country(source=None, **kwargs)
            
            
        Examples
        --------
            
            >>> serv = services.GISCOService()
            >>> serv.url_country()
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/countries/countries-2013-units.json'
            >>> serv.url_country(unit='AT')
                'https://europa.eu/ec.eurostat/cache/GISCO/distribution/v2/countries/distribution/AT-region-01m-4326-2013.geojson'

        Note
        ----
        See for instance this `page <http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/countries/countries-2013-units.html>`_.
                
        See also
        --------
        :meth:`~GISCOService.country_response`, :meth:`~GISCOService.country_codes`, 
        :meth:`~GISCOService.url_nuts`.        
        """
        # check whether a specific unit is looked for
        try:
            assert source is None or happyType.isstring(source)
        except:
            raise happyError('wrong format/value for SOURCE argument')
        else:
            if source in (None, ''): 
                source = 'INFO' # force to 'INFO' in case it is None
            source = source.upper()
        # retrieve the year
        year = kwargs.pop(_Decorator.KW_YEAR, settings.DEF_GISCO_YEAR)
        # retrieve the scale
        scale = kwargs.pop(_Decorator.KW_SCALE, 
                           settings.DEF_GISCO_SCALE if source != 'NUTS2JSON' else settings.DEF_NUTS2JSON_SCALE)
        if source != 'NUTS2JSON' and scale in settings.GISCO_SCALES.keys():
            scale = settings.GISCO_SCALES[scale]
        fmt = kwargs.pop(_Decorator.KW_FORMAT, 
                         settings.DEF_GISCO_FORMAT if source != 'NUTS2JSON' else settings.DEF_NUTS2JSON_FORMAT)
        if source != 'NUTS2JSON' and fmt in settings.GISCO_FORMATS.keys():
            fmt = settings.GISCO_FORMATS[fmt]
        #elif fmt in settings.GISCO_FORMATS.values():
        #    fmt = {v:k for k,v in settings.GISCO_FORMATS.items()}[fmt]
        #elif fmt in settings.DEF_NUTS2JSON_FORMAT.keys():
        #    fmt = settings.DEF_NUTS2JSON_FORMAT[fmt]
        proj = kwargs.pop(_Decorator.KW_PROJECTION, 
                          settings.DEF_GISCO_PROJECTION if source != 'NUTS2JSON' else settings.DEF_NUTS2JSON_PROJECTION)
        if source != 'NUTS2JSON' and proj in settings.GISCO_PROJECTIONS.keys():
            proj = settings.GISCO_PROJECTIONS[proj]
        elif proj in settings.NUTS2JSON_PROJECTIONS.keys():
            proj = settings.NUTS2JSON_PROJECTIONS[proj]
        vec = kwargs.pop(_Decorator.KW_VECTOR, settings.DEF_GISCO_VECTOR) 
        if vec in settings.GISCO_VECTORS.keys():
            vec = settings.GISCO_VECTORS[vec]
        theme = 'countries'
        protocol = settings.PROTOCOL # 'https'
        if source == 'NUTS2JSON':
            # the files can be retrieved on-the-fly from the base URL 
            #       https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/ 
            # according to the file pattern:
            #   * for topojson: /<YEAR>/<PROJECTION>/<SIZE>/<NUTS_LEVEL>.json
            #   * for geojson:  /<YEAR>/<PROJECTION>/<SIZE>/<TYPE>_<NUTS_LEVEL>.json
            # where <TYPE> depends on geom variable
            domain = settings.NUTS2JSON_DOMAIN
            url = '{a}://{b}/{c}/{d}/{e}/{f}.{g}'.format                 \
                (a=protocol, b=domain, c=year, d=proj, e=scale.upper(), 
                 f='' if fmt!= 'geojson' else ('cntrg' if vec == 'RG' else 'cntbn'), 
                 g='json')
        elif source == 'INFO':
            domain = ''
            fmt = settings.GISCO_PATTERNS['country']['fmt']
            basename = settings.GISCO_PATTERNS['country']['info']
            url = '{a}://{b}/{c}/{d}.{e}'.format                            \
                (a=protocol, b=self.cache_url, c=theme,
                 d=basename.format(year=year), e=fmt)
        else:
            domain = settings.GISCO_PATTERNS['country']['domain']
            space = 'region'
            url = '{a}://{b}/{c}/{d}/{e}-{f}-{g}-{h}-{i}.{j}'.format        \
                (a=protocol, b=self.cache_url, c=theme, d=domain,
                 e=source, f=space, g=scale.lower(), h=proj, i=year, j=fmt)             
        return url            
        
    #/************************************************************************/
    def url_tile(self, tiles=None, **kwargs):
        """Generate the URL (or name) of the |GISCO| tiling web-service that can
        be used as a background layer in map displays.
            
            >>> url, attr = serv.url_tile(tiles=None, **kwargs)
           
        Arguments
        ---------
        tiles: str
            string representing the background tile layer used for the map display; 
            it must be one of the tiling supported by |GISCO|, *i.e.* any string in 
            :literal:`['bmarble','borders','roadswater','hypso','coast','copernicus',`
            :literal:`'osmec','graybg','country','gray','natural','city','cloudless']`;
            see also the list of available tiling systems (together with the respective
            attributions) in :data:`settings.GISCO_TILES`.
           
        Keyword arguments
        -----------------
        proj : str,int
            projection identifier; default identifier is :literal:`'EPSG3857'`, *i.e.* the one
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
            
            >>> serv = services.GISCOService()
            >>> serv.url_tile('bmarble')
                ('https://europa.eu/webtools/maps/tiles/bmarble/3857/{z}/{y}/{x}',
                 '© NASA’s Earth Observatory')
            >>> serv.url_tile('osmec')
                ('https://europa.eu/webtools/maps/tiles/osm-ec/{z}/{y}/{x}', 
                 '© OpenStreetMap')
        """
        try:
            assert tiles is None or happyType.isstring(tiles)
        except:
            raise happyError('wrong format/value for TILES argument')
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
            assert proj in (None,'') or proj in happyType.seqflatten(list(settings.GISCO_PROJECTIONS.items()))
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
        tiles = '%s://%s/%s/%s%s' % (settings.PROTOCOL, self.map_url, 
                                     bckgrd, proj, order)
        return tiles, attr            

    #/************************************************************************/
    def url_geocode(self, **kwargs):
        """Generate the query URL for |GISCO| geocoding web-service (from toponame 
        to geocoordinate).
        
            >>> url = serv.url_geocode(**kwargs)
           
        Keyword arguments
        -----------------
        nominatim : bool
            flag set to :data:`True` when |Nominatim| geocoding service shall be 
            used; default is :data:`False`.
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :literal:`q, lat, lon, distance_sort, limit, osm_tag`, and :literal:`lang`;
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
            
            >>> serv = services.GISCOService()
            >>> serv.url_geocode(q='Paris+France')
                'https://europa.eu/webtools/rest/gisco/api?q=Paris+France'
            
        Note
        ----
        This method overrides the *super* method :meth:`OSMService.url_geocode`.
        
        See also
        --------
        :meth:`~GISCOService.url_reverse`, :meth:`~GISCOService.url_routing`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_findnuts`,
        :meth:`OSMService.url_geocode`.
        """
        nominatim = kwargs.pop('nominatim', False)
        kwargs.update({'keys': ['q', 'lat', 'lon', 'distance_sort', 'limit', 'osm_tag', 'lang'],
                       'path': 'nominatim' if nominatim else '',
                       'query': 'search.php' if nominatim else 'api',
                       'protocol': settings.PROTOCOL}
            )
        if nominatim:   kwargs.pop('key', None)
        return super(GISCOService, self).url_geocode(**kwargs)
    
    #/************************************************************************/
    def url_reverse(self, **kwargs):
        """Generate the query URL for |GISCO| reverse geocoding web-service (from 
        geocoordinate to toponame).
        
            >>> url = serv.url_reverse(**kwargs)
           
        Keyword arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed keyword arguments are: 
            :literal:`lat, lon, radius, distance_sort, limit`, and :literal:`lang`;
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

            >>> serv = services.GISCOService()
            >>> serv.url_reverse(lon=10, lat=52)
                'https://europa.eu/webtools/rest/gisco/reverse?lon=10&lat=52'
            
        Note
        ----
        This method overrides the *super* method :meth:`OSMService.url_reverse`.
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_routing`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_findnuts`,
        :meth:`OSMService.url_reverse`.
        """
        nominatim = kwargs.pop('nominatim', False)
        kwargs.update({'keys': None if nominatim else ['lat', 'lon', 'radius', 'distance_sort', 'limit', 'lang'],
                       'path': 'nominatim' if nominatim else '',
                       'query': 'reverse.php' if nominatim else 'reverse',
                       'protocol': settings.PROTOCOL}
            )
        if nominatim:   kwargs.pop('key', None)
        return super(GISCOService, self).url_reverse(**kwargs)

    #/************************************************************************/
    def url_routing(self, **kwargs):
        """Generate the query URL for |GISCO| routing web-service (from a list of
        geocoordinates to a route).
        
            >>> url = serv.url_routing(**kwargs)
           
        Keyword arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :literal:`coordinates, polyline, overview`, and :literal:`???`;
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

            >>> serv = services.GISCOService()
            >>> serv.url_routing(coordinates='13.388860,52.517037;13.397634,52.529407;13.428555,52.523219')
                'https://europa.eu/webtools/rest/gisco/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_transform`, :meth:`~GISCOService.url_findnuts`,
        :meth:`base._Service.build_url`.
        """
        keys = ['overview', ] # ?
        happyVerbose('\n            * '.join(['input filters used for routing service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        coordinates = kwargs.pop('coordinates','')
        polyline = kwargs.pop(_Decorator.parse_coordinate.KW_POLYLINE,None)
        polyline = 'polyline(' + polyline + ')' if polyline else ''
        url = self.build_url(protocol=settings.PROTOCOL,
                             domain=self.rest_url, 
                             query='route/v1/driving/%s' % coordinates or polyline, 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        # test: 
        # url_routing(lat=[13.388860, 13.397634, 13.428555],lon=[52.517037,52.529407,52.523219])

    #/************************************************************************/
    def url_transform(self, **kwargs):
        """Generate the query URL for |GISCO| projection tranform web-service (from 
        a geocoordinate in a given projection reference system to its transformation
        in another projection reference system)
       
            >>> url = serv.url_transform(**kwargs)
           
        Keyword arguments
        -----------------
        kwargs : dict
            parameters used to build the query URL; allowed parameters are: 
            :literal:`inSR, outSR, geometries, transformation, transformForward` and :literal:`f`;
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

            >>> serv = services.GISCOService()
            >>> serv.url_transform(inSR=4326, outSR=3035, f='json',
                                   geometries='-9.1630,38.7775')
                'https://webgate.ec.europa.eu/estat/inspireec/gis/arcgis/rest/services/Utilities/Geometry/GeometryServer/project?inSR=4326&outSR=3035&geometries=-9.1630,38.7775&f=json'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_routing`, :meth:`~GISCOService.url_findnuts`,
        :meth:`base._Service.build_url`.
        """
        keys = ['inSR', 'outSR', 'geometries', 'transformation', 'transformForward', 'f'] # ?
        happyVerbose('\n            * '.join(['input filters used for tranform service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        url = self.build_url(protocol=settings.PROTOCOL,
                             domain=self.arcgis, 
                             query='Utilities/Geometry/GeometryServer/project', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url

    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    def url_findnuts(self, **kwargs):
        """Create a query URL to be submitted to the |GISCO| (simple) web-service 
        for NUTS codes identification.
        
            >>> url = serv.url_findnuts(**kwargs)
           
        Keyword arguments
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

            >>> serv = services.GISCOService()
            >>> serv.url_findnuts(y=52.5170365, x=13.3888599, f='JSON', proj=4326)
                'https://europa.eu/webtools/rest/gisco/nuts/find-nuts.py?y=52.5170365&x=13.3888599&f=JSON&proj=4326'
        
        See also
        --------
        :meth:`~GISCOService.url_geocode`, :meth:`~GISCOService.url_reverse`, 
        :meth:`~GISCOService.url_routing`, :meth:`~GISCOService.url_transform`,
        :meth:`base._Service.build_url`.
        """
        keys = ['x', 'y', 'f', 'year', 'proj', 'geometry']
        happyVerbose('\n            * '.join(['input filters used for NUTS identification service:',]+[attr + '='+ str(kwargs[attr]) \
                                            for attr in kwargs.keys() if attr in keys]))
        # note that the service is case sensitive as f is concerned
        kwargs.update({'f': kwargs.get('f','JSON').upper()}) # let us avoid stupid mistakes
        url = self.build_url(protocol=settings.PROTOCOL,
                             domain=self.rest_url, 
                             path='nuts', 
                             query='find-nuts.py', 
                             **{k:v for k,v in kwargs.items() if k in keys})
        happyVerbose('output url:\n            %s' % url)
        return url
        
    #/************************************************************************/
    def _data_response(self, data, dimensions, **kwargs):
        """Generic version of methods :meth:`~GISCOService.country_response` and
        :meth:`~GISCOService.nuts_response`.
        """
        __del_source = True
        source = dimensions.get('SOURCE')
        if len(source) == 1: source = source[0]
        dic = _NestedDict([(getattr(_Decorator,'KW_' + k), v) for k,v in dimensions.items() \
                               if __del_source is False or source not in ('NUTS2JSON','BULK','INFO') or k!='SOURCE'],
                           **{_Decorator.KW_ORDER: True}) # [getattr(_Decorator,'KW_' + k) for k in dimensions.keys()]
        dim = {}
        for prod in itertools.product(*list(dimensions.values())):
            dim.update(dict(zip([getattr(_Decorator,'KW_' + attr) for attr in dimensions.keys()], prod)))
            try:
                build_url = getattr(self, 'url_' + data.lower())
            except AttributeError:
                raise happyError('argument DATA not recognised - must be ''nuts'' or ''country''')
            else:
                url = build_url(**dim)
            try:
                response = self.read_url(url, **kwargs) # fmt = 'resp'
            except:
                raise happyError('file for %s data not loaded' % data)
            else:
                if __del_source is True and source in ('NUTS2JSON','BULK','INFO'):
                    dim.pop(_Decorator.KW_SOURCE)
                dic.xupdate(response, **dim)
                response = None
        return dic 
    
    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_format
    @_Decorator.parse_scale
    @_Decorator.parse_vector 
    def country_response(self, **kwargs):
        """Download, and cache when requested, country vector files from |GISCO| Rest
        API.
            
            >>> dresp = serv.country_response(code=None, **kwargs)            
            
        Returns
        -------
        dresp : :class:`base._NestedDict`
        
        See also
        --------
        :meth:`~GISCOService.country_response`, :meth:`~GISCOService._data_response`.
        """
        try:
            source = kwargs.pop(_Decorator.KW_SOURCE, None)
            assert source is None or happyType.isstring(source)
        except AssertionError:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_SOURCE.upper())
        try:
            code = kwargs.pop(_Decorator.KW_CODE, None)
            assert code is None or happyType.isstring(code) or                          \
                (happyType.issequence(code) and all([happyType.isstring(c) for c in code]))
        except AssertionError:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_CODE.upper())        
        try:
            assert source is None or code is None
        except:
            raise happyError('incompatible parameters %s and %s' % (_Decorator.KW_CODE.upper(),_Decorator.KW_SOURCE.upper()))
        else:
            if code is None and source is None:
                source = 'INFO'  # force to 'NUTS' in case both are None
            elif code is not None:
                if code in ('INFO','NUTS2JSON'): # let's avoid dumb mistake
                    source = code
                    code = None
                elif not happyType.issequence(code):
                    code = [code,]
            else: 
                source = source.upper()
        dimensions = settings.GISCO_DATA_DIMENSIONS.copy()
        if source == 'INFO':
            # ['SOURCE', 'YEAR', 'FORMAT']
            [dimensions.remove(attr) for attr in ('PROJECTION', 'SCALE', 'VECTOR', 'LEVEL')] 
        elif source == 'NUTS2JSON':
            # ['SOURCE', 'YEAR', 'PROJECTION', 'SCALE', 'FORMAT']
            [dimensions.remove(attr) for attr in ('VECTOR', 'LEVEL')] 
        else:
            # ['SOURCE', 'YEAR', 'PROJECTION', 'SCALE', 'FORMAT']
            [dimensions.remove(attr) for attr in ('LEVEL',)] 
        dimensions = collections.OrderedDict(zip(dimensions,[None]*len(dimensions)))        
        for attr in dimensions.keys():
            val = kwargs.pop(getattr(_Decorator,'KW_' + attr), None)
            if val is None: 
                continue
            if not happyType.issequence(val):      val = [val,]
            dimensions.update({attr: val})
        dimensions.update({'SOURCE': [source,] if source is not None else code})
        return self._data_response('country', dimensions, **kwargs)

    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_format
    @_Decorator.parse_level
    @_Decorator.parse_scale
    @_Decorator.parse_vector
    def nuts_response(self, **kwargs):
        """Download, and cache when requested, responses associated to NUTS vector 
        files available through |GISCO| Rest API.
            
            >>> dresp = serv.nuts_response(**kwargs)
            
        Returns
        -------
        dresp : :class:`base._NestedDict`
        
        Examples
        --------
        The method can be used to retrieve well-parameterised responses from |GISCO| 
        Rest API:
            
            >>> serv = services.GISCOService()
            >>> r = serv.nuts_response(source='NUTS', year=2010)
            >>> print(r)
                <Response [200]>
            >>> print(r.url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_RG_60M_2010_4326_LEVL_0.geojson'
            >>> print(r.dimensions)
                OrderedDict([(source, 'NUTS'),
                             ('year', 2010),
                             ('proj', 4326),
                             ('scale', '60m'),
                             ('vector', 'RG'),
                             ('level', 0),
                             ('fmt', 'geojson')])
            >>> r = serv.nuts_response(unit='AT1', year=[2013,2016], scale=['20m','60m'], vector='region')
            >>> print(r)
                 {2013: {4326: {'20m': {'RG': {'geojson': <Response [200]>}},
                    '60m': {'RG': {'geojson': <Response [200]>}}}},
                  2016: {4326: {'20m': {'RG': {'geojson': <Response [200]>}},
                    '60m': {'RG': {'geojson': <Response [200]>}}}}})            
            >>> print(r.url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT1-region-60m-4326-2013.geojson' 
            >>> r = serv.nuts_response(source='BULK', year=2016, scale='60m')
            >>> print(r.dimensions)
                OrderedDict([('year', 2016),
                             ('scale', '60m'),
                             ('fmt', 'geojson')])
            >>> print(r.url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2016-60m.geojson.zip'
                
        Note also that multiple units can be called at once:
            
            >>> r = serv.nuts_response(unit=['BE1','AT1'], year=[2013,2016], scale=['20m','60m'], vector='region')
            >>> print(r)
                 {'AT1': {2013: {4326: {'20m': {'RG': {'geojson': <Response [200]>}},
                     '60m': {'RG': {'geojson': <Response [200]>}}}},
                   2016: {4326: {'20m': {'RG': {'geojson': <Response [200]>}},
                     '60m': {'RG': {'geojson': <Response [200]>}}}}},
                  'BE1': {2013: {4326: {'20m': {'RG': {'geojson': <Response [200]>}},
                     '60m': {'RG': {'geojson': <Response [200]>}}}},
                   2016: {4326: {'20m': {'RG': {'geojson': <Response [200]>}},
                     '60m': {'RG': {'geojson': <Response [200]>}}}}}})
            >>> print(r.dimensions)
                OrderedDict([('source', ['BE1', 'AT1']),
                             ('year', [2013, 2016]),
                             ('proj', 4326),
                             ('scale', ['20m', '60m']),
                             ('vector', 'RG'),
                             ('fmt', 'geojson')])
            >>> print(r.url)
                ['https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE1-region-20m-4326-2013.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE1-region-60m-4326-2013.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE1-region-20m-4326-2016.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE1-region-60m-4326-2016.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT1-region-20m-4326-2013.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT1-region-60m-4326-2013.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT1-region-20m-4326-2016.geojson',
                 'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT1-region-60m-4326-2016.geojson']
            >>> r['BE1'][2016][4326]['20m']['RG']['geojson'].content
                b'{"crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}}, "type": "FeatureCollection", 
                   "features": [{"geometry": {"type": "Polygon", 
                   "coordinates": [[[4.28308, 50.81361], [4.28883, 50.8918], [4.435, 50.89895], [4.48508, 50.7931], [4.38437, 50.75974], [4.28308, 50.81361]]]}, 
                   "type": "Feature", "properties": {"CNTR_CODE": "BE", "NUTS_NAME": "R\\u00c9GION DE BRUXELLES-CAPITALE/BRUSSELS HOOFDSTEDELIJK GEWEST", 
                   "LEVL_CODE": 1, "FID": "BE1", "NUTS_ID": "BE1"}, "id": "BE1"}]}'
            >>> r.get(source='BE1', year=2016, scale='20m').url
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE1-region-20m-4326-2016.geojson'

        See also
        --------
        :meth:`~GISCOService.country_response`, :meth:`~GISCOService._data_response`.
        """
        try:
            source = kwargs.pop(_Decorator.KW_SOURCE, None)
            assert source is None or happyType.isstring(source)
        except AssertionError:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_SOURCE.upper())
        try:
            unit = kwargs.pop(_Decorator.KW_UNIT, None)
            assert unit is None or happyType.isstring(unit) or                          \
                (happyType.issequence(unit) and all([happyType.isstring(u) for u in unit]))
        except AssertionError:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_UNIT.upper())        
        try:
            assert source is None or unit is None
        except:
            raise happyError('incompatible parameters %s and %s' % (_Decorator.KW_UNIT.upper(),_Decorator.KW_SOURCE.upper()))
        else:
            if unit is None and source is None:
                source = 'NUTS'  # force to 'NUTS' in case both are None
            elif unit is not None:
                if unit=='ALL':
                    source = 'NUTS'
                elif unit in ('NUTS','BULK','INFO','NUTS2JSON'): # let's avoid dumb mistake
                    source = unit
                    unit = None
                elif not happyType.issequence(unit):
                    unit = [unit,]
            else: 
                source = source.upper()                
        dimensions = settings.GISCO_DATA_DIMENSIONS.copy()
        if source == 'BULK':
            # ['SOURCE', 'YEAR', 'SCALE', 'FORMAT']
            [dimensions.remove(attr) for attr in ('PROJECTION', 'VECTOR', 'LEVEL')] 
        elif source == 'INFO':
            # ['SOURCE', 'YEAR', 'FORMAT']
            [dimensions.remove(attr) for attr in ('PROJECTION', 'SCALE', 'VECTOR', 'LEVEL')] 
        elif source == 'NUTS2JSON':
            # ['SOURCE', 'YEAR', 'PROJECTION', 'SCALE', 'LEVEL', 'FORMAT']
            [dimensions.remove(attr) for attr in ('VECTOR',)] 
        elif source == 'NUTS' or kwargs.get(_Decorator.KW_UNIT) == 'ALL':
            # ['SOURCE', 'YEAR', 'PROJECTION', 'SCALE', 'VECTOR', 'LEVEL', 'FORMAT']
            pass
        else:
            # ['SOURCE', 'UNIT', 'YEAR', 'PROJECTION', 'SCALE', 'VECTOR', 'FORMAT']
            [dimensions.remove(attr) for attr in ('LEVEL',)] 
        dimensions = collections.OrderedDict(zip(dimensions,[None]*len(dimensions)))        
        for attr in dimensions.keys():
            val = kwargs.pop(getattr(_Decorator,'KW_' + attr), None)
            if val is None: 
                continue
            if not happyType.issequence(val):      val = [val,]
            dimensions.update({attr: val})
        # we have to cheat here to support NUTS2JSON package 
        if source == 'NUTS2JSON':
            if 'FORMAT' in dimensions:
                dimensions.update({'FORMAT': ['topojson' if f=='json' else f        \
                                                          for f in dimensions.get('FORMAT')]})
            if 'SCALE' in dimensions:
                dimensions.update({'SCALE': [settings.DEF_NUTS2JSON_SCALE if s not in settings.NUTS2JSON_SCALES else s       \
                                                          for s in dimensions.get('SCALE')]})
            if 'PROJECTION' in dimensions:
                dimensions.update({'PROJECTION': [settings.DEF_NUTS2JSON_PROJECTION if p not in settings.NUTS2JSON_PROJECTIONS else p        \
                                                          for p in dimensions.get('PROJECTION')]})
        elif source not in ('NUTS','BULK','INFO'):
            if 'VECTOR' in dimensions:
                dimensions.update({'VECTOR': ['RG' if v not in ('LB','label','RG','region') else v      \
                                                          for v in dimensions.get('VECTOR')]})
                _anylabel = any([v in ('LB','label') for v in dimensions.get('VECTOR')])
                _alllabels = all([v in ('LB','label') for v in dimensions.get('VECTOR')])
            else:
                _anylabel, _alllabels = False, False
            if 'FORMAT' in dimensions:
                dimensions.update({'FORMAT': ['geojson' for g in dimensions.get('FORMAT')]})
            if 'PROJECTION' in dimensions:
                dimensions.update({'PROJECTION': [3035 if _anylabel and p not in (3035,'LAEA','EPSG3035',4258,'ETRS89','EPSG4258') else p      \
                                                          for p in dimensions.get('PROJECTION')]})
            if 'SCALE' in dimensions and _alllabels:
                dimensions.pop('SCALE')
        dimensions.update({'SOURCE': [source,] if source is not None else unit})
        return self._data_response('NUTS', dimensions, **kwargs)

    #/************************************************************************/
    def nuts_content(self, response, **kwargs):
        if isinstance(response,(_CachedResponse, requests.Response)):
            return self.read_response(response, **kwargs)
        else:
            content = copy.deecopy(response)
            content.xupdate()
            self.read_response(v, **kwargs) for k, v in response.xvalues()

        
    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_scale
    #@_Decorator.parse_level # we actually set None as default value
    def nuts_info(self, **kwargs):
        """Returns some information regarding the |NUTS| datasets disseminated through
        |GISCO| Rest API.
            
            >>> data = serv.nuts_info(**kwargs)
            
        Keyword arguments
        -----------------
        info : str
            defines the nature of the information that will be retrieved; it can be
            either:
            
                * :literal:'UNITS' to return the identifiers of all NUTS regions 
                  (or a subset of it) available at any level,
                * :literal:'BULK' to return the list of NUTS datasets included 
                  in the bulk (zipped) download files,
                * :literal:'NAMES' to return the correspondance table between the 
                  names and the identifiers of all NUTS regions (or a subset of it);
                  
            default: :data:`info=UNITS`, and information regarding the NUTS 
            identifiers is returned.
        unit : str, list
            (list of) ISO-code(s) of country/regions from about which information  
            is returned; in the case :data:`info` is set to :literal:'UNITS' or
            :literal:'NAMES', it is actually used as a prefix to further filter/select
            the regions/units of interest; it is ignored otherwise (*i.e.* in the
            case :data:`info=BULK`); default: this is not used.
        level : int, str, list 
            level of the NUTS region to consider; in the case :data:`info` is set 
            to :literal:'UNITS' or :literal:'NAMES', this (these) NUTS level(s) 
            is(are) also used to further filter the regions/units of interest; it 
            can take any value in :data:`settings.GISCO_NUTSLEVELS`; default: 
            :data:`level='ALL'`, *i.e.* all NUTS levels are considered.
        _caching_ : bool
            flag set to actually download the files when retrieving the information; 
            default: :data:`_caching_=False` when :data:`info=BULK`, *i.e.* the file(s) 
            is (are) not written on the disk and :data:`_caching_=True` in all other
            cases (:data:`info in ('UNITS','NAMES')`); see also 
            :meth:`base._Service.get_service`.
            
        Returns
        -------
        data : list,pandas.DataFrame
            output dataset/list depending on the information to retrieve, it can be:
                
                * the list of NUTS regions/units available in |GISCO| database, 
                  given the arguments :data:`unit` and :data:`level` above;
                * the content of the bulk (zipped) download files of NUTS datasets,
                * the correspondance table between the names and the identifiers
                  of NUTS regions/units available in |GISCO| database, given the 
                  arguments :data:`unit` and :data:`level` above. 
        
        Examples
        --------
        Here is the best way to retrieve the list of NUTS units disseminated on |GISCO|
        database:
            
            >>> units = serv.nuts_info(info='UNITS', unit='AT', level=2)
            >>> print(units)
                ['AT11', 'AT12', 'AT13', 'AT21', 'AT22', 'AT31', 'AT32', 'AT33', 'AT34']
            >>> units = serv.nuts_info(info='UNITS', level=0)
            >>> print(units)
                ['AT', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DEA', 'DEB', 'DEC', 'DED', 'DEE', 'DEF', 'DEG', 'DK', 'EE', 
                'EL', 'ES', 'FI', 'FR', 'FRA', 'HR', 'HU', 'IE', 'IS', 'IT', 'ITC', 'ITF', 'ITG', 'ITH', 'ITI', 'LI', 
                'LT', 'LU', 'LV', 'ME', 'MK', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'TR', 'TRA', 'TRB',
                'TRC', 'UK', 'UKC', 'UKD', 'UKE', 'UKF', 'UKG', 'UKH', 'UKI', 'UKJ', 'UKK', 'UKL', 'UKM', 'UKN']            
            >>> units = serv.nuts_units(unit='AT', level=[2,3])
            >>> print(units)
                ['AT11', 'AT111', 'AT112', 'AT113', 'AT12', 'AT121', 'AT122', 'AT123', 'AT124', 'AT125', 'AT126', 
                 'AT127', 'AT13', 'AT130', 'AT21', 'AT211', 'AT212', 'AT213', 'AT22', 'AT221', 'AT222', 'AT223', 
                 'AT224', 'AT225', 'AT226', 'AT31', 'AT311', 'AT312', 'AT313', 'AT314', 'AT315', 'AT32', 'AT321', 
                 'AT322', 'AT323', 'AT33', 'AT331', 'AT332', 'AT333', 'AT334', 'AT335', 'AT34', 'AT341', 'AT342']
 
        One can also retrieve some information regarding the list of files available
        in one of the bulk NUTS download files:
            
            >>> serv.nuts_info(info='BULK', year=2013, scale='60m')
                ['NUTS_RG_60M_2013_3035.geojson',
                 'NUTS_RG_60M_2013_3035_LEVL_0.geojson',
                 'NUTS_RG_60M_2013_3035_LEVL_1.geojson',
                 'NUTS_RG_60M_2013_3035_LEVL_2.geojson',
                 'NUTS_RG_60M_2013_3035_LEVL_3.geojson',
                 'NUTS_RG_60M_2013_3857.geojson',
                  ...
                 'NUTS_BN_60M_2013_4326.geojson',
                 'NUTS_BN_60M_2013_4326_LEVL_0.geojson',
                 'NUTS_BN_60M_2013_4326_LEVL_1.geojson',
                 'NUTS_BN_60M_2013_4326_LEVL_2.geojson',
                 'NUTS_BN_60M_2013_4326_LEVL_3.geojson',
                 'NUTS_AT_2013.csv',
                 'NUTS_RG_BN_60M_2013.csv',
                 'metadata.pdf',
                 'metadata.xml',
                 'release-notes.txt']      
                
        Finally, one can get information regarding the names of the NUTS regions:
            
            >>> data = serv.nuts_info(info='NAMES')
            >>> data.head()
                     CNTR_CODE NUTS_ID                                         NUTS_NAME
                0           AT     AT1                                     OSTÖSTERREICH
                1           AT    AT11                                   Burgenland (AT)
                2           AT   AT111                                  Mittelburgenland
                3           AT   AT112                                    Nordburgenland
                4           AT   AT113                                     Südburgenland
                5           AT    AT12                                  Niederösterreich                
                ...
                1943        UK    UKN0                                  Northern Ireland
                1944        UK   UKN05                West and South of Northern Ireland
                1945        CY      CY                                            ΚΥΠΡΟΣ
                1946        ES      ES                                            ESPAÑA
                1947        HU      HU                                      MAGYARORSZÁG
                1948        ME      ME                                         ЦРНА ГОРА
                1949        NL      NL                                         NEDERLAND
                1950        SI      SI                                         SLOVENIJA        
            >>> serv.nuts_info(info='NAMES', units=['BE','BG'])
                     CNTR_CODE NUTS_ID                                          NUTS_NAME
                41          BE     BE1  RÉGION DE BRUXELLES-CAPITALE / BRUSSELS HOOFDS...
                42          BE   BE100  Arr. de Bruxelles-Capitale / Arr. van Brussel-...
                43          BE     BE2                                      VLAAMS GEWEST
                44          BE    BE21                                    Prov. Antwerpen
                45          BE   BE211                                     Arr. Antwerpen
                46          BE   BE212                                      Arr. Mechelen    
                ...
                1720        BG   BG334                                          Търговище
                1721        BG   BG341                                             Бургас
                1722        BG   BG344                                       Стара Загора
                1723        BG     BG4               ЮГОЗАПАДНА И ЮЖНА ЦЕНТРАЛНА БЪЛГАРИЯ
                1724        BG   BG422                                            Хасково
                1725        BG   BG424                                             Смолян   
            >>> serv.nuts_info(info='NAMES', unit=['BE','BG'], level=[0,2])
                     CNTR_CODE NUTS_ID                                          NUTS_NAME
                1675        BE      BE                                    BELGIQUE-BELGIË
                1676        BG      BG                                           БЪЛГАРИЯ
                44          BE    BE21                                    Prov. Antwerpen
                48          BE    BE22                                 Prov. Limburg (BE)
                52          BE    BE23                              Prov. Oost-Vlaanderen
                58          BE    BE24                               Prov. Vlaams-Brabant
                69          BE    BE31                               Prov. Brabant Wallon
                77          BE    BE33                                        Prov. Liège
                82          BE    BE34                              Prov. Luxembourg (BE)
                88          BE    BE35                                        Prov. Namur
                1709        BE    BE10  Région de Bruxelles-Capitale / Brussels Hoofds...
                1711        BE    BE25                              Prov. West-Vlaanderen
                1713        BE    BE32                                      Prov. Hainaut
                92          BG    BG31                                      Северозападен
                102         BG    BG33                                      Североизточен
                105         BG    BG34                                         Югоизточен
                108         BG    BG41                                         Югозападен
                114         BG    BG42                                     Южен централен
                1717        BG    BG32                                  Северен централен
                            
        Notes
        -----
        * In the case :data:`info=NAMES`, a :class:`pandas.DataFrame` data structure
          is returned. 
        * When providing information about a bulk (zipped) download file, the file
          is, by default, NOT downloaded (*i.e.*, not physically written on the drive).
          If you want to avoid multiple requests and actually already download the
          file when retrieving the information, set the :data:`_caching_` variable to 
          :data:`True`.
        * It is recommended, for efficiency reasons, to set the option :data:`_caching_=True`
          considering that some of the info requests may be formulated several times.
        
        See also
        --------
        :meth:`~GISCOService.country_info`, :meth:`~GISCOService.nuts_response`, 
        :meth:`~GISCOService.url_nuts`, :meth:`base._Service.read_response`.
        """
        data = None
        info = kwargs.pop(_Decorator.KW_INFO, None)
        try:
            assert info is None or happyType.isstring(info)
        except AssertionError:
            raise happyError('wrong format for %s argument' % _Decorator.KW_INFO.upper())        
        else:
            if info is None:
                info = 'UNITS'
            info = info.upper()            
        try:
            assert info in ('NAMES', 'BULK', 'UNITS')
        except AssertionError:
            raise happyError('wrong value for %s argument' % _Decorator.KW_INFO.upper())        
        unit = kwargs.pop(_Decorator.KW_UNIT, None)
        try:
            assert unit is None or happyType.isstring(unit)            \
                or (happyType.issequence(unit) and all([happyType.isstring(u) for u in unit]))
        except AssertionError:
            raise happyError('wrong format/value for %s argument' % _Decorator.KW_UNIT.upper())        
        else:
            if unit is not None:
                if not happyType.issequence(unit):
                    unit = [unit,]
                unit = [u.upper() for u in unit]
        caching = kwargs.pop(_Decorator.KW_CACHING, True if info in ('NAMES', 'UNITS') else False)
        force_download = kwargs.pop(_Decorator.KW_FORCE, False)
        try:
            assert isinstance(caching, bool) and isinstance(force_download, bool)
        except AssertionError:
            raise happyError('wrong format/value for %s/%s arguments' % (_Decorator.KW_CACHING.upper(),_Decorator.KW_FORCE.upper()))        
        if info in ('NAMES', 'BULK'):
            source = 'BULK'
        else:
            source = 'INFO'
        kwargs.update({_Decorator.KW_SOURCE: source,
                       _Decorator.KW_CACHING: caching})                 
        if info in ('NAMES','UNITS'):            
            level = kwargs.pop(_Decorator.KW_LEVEL, None) # settings.GISCO_NUTSLEVELS
            if level is not None:
                if level == 'ALL' or set(level) == set(settings.GISCO_NUTSLEVELS):
                    level = None # settings.GISCO_NUTSLEVELS
                elif not happyType.issequence(level):
                    level = [level,]
        if info == 'NAMES':
            scale = sorted(list(settings.GISCO_SCALES.keys()))[-1]
            year = kwargs.pop(_Decorator.KW_YEAR, settings.DEF_GISCO_YEAR)
            kwargs.update({_Decorator.KW_SCALE: scale,
                           _Decorator.KW_FORMAT: 'shp', # instead of settings.DEF_GISCO_FORMAT since 'shp' is lighter
                           _Decorator.KW_YEAR: year})
            base = settings.GISCO_PATTERNS['nutsid']['info'].format(year=year)
            # ok, now let's cheat a bit: we are actually going to store this 
            # table with the service, so as to avoid loading it everytime...
            if caching is True and force_download is False:
                try:
                    # note that because we use the prefix '__', this is actually
                    # unaccesible to the user
                    data = getattr(self, '__' + base)   
                except:
                    pass
            fmt = settings.GISCO_PATTERNS['nutsid']['fmt']
        try:
            assert data is None
            resp = self.nuts_response(**kwargs)
        except AssertionError:
            pass
        except:
            raise happyError('error loading NUTS response')
        if info == 'BULK':
            try:
                data = self.read_response(resp, fmt='zip', namelist=True)
            except:
                raise happyError('error zip NUTS file reading')
        elif info == 'NAMES':
            try:
                assert data is None
                data = self.read_response(resp, fmt='zip', read = '%s.%s' % (base,fmt))
            except AssertionError:
                pass
            except:
                raise happyError('error zip NUTS file reading')
            else:
                data = pd.read_csv(io.BytesIO(data))
            if caching is True:
                try:
                    setattr(self, '__' + base, data)   
                except:
                    pass
            if unit is not None:
                data = pd.concat(data[data['NUTS_ID'].str.startswith(u)] for u in unit) 
            if level is not None:
                data = pd.concat(data[data['NUTS_ID'].apply(lambda x: sum(c.isdigit() for c in x)==l)] for l in level)
        else:
            try:
                data = self.read_response(resp, fmt='jsontext')
            except:
                raise happyError('error info NUTS file reading')
            else:
                data = list(data.keys())
            if unit is not None:
                data = [d for d in data if any([d.startswith(u) for u in unit])]
            if level is not None:
                data = [d for d in data if any([sum(c.isdigit() for c in d)==l for l in level])]
        return data

    #/************************************************************************/
    def country_info(self, **kwargs):
        """Returns the list of ISO-codes of countries available in |GISCO| database.
            
            >>> countries = serv.country_info(**kwargs)
            
        Keyword arguments
        -----------------
        info : str
            defines the nature of the information about countries that will be 
            retrieved; currently, it supports only :literal:`CODES`, *i.e.* country
            ISO-codes are returned.
            
        Returns
        -------
        countries : 
            list of all countries ISO-codes that are available (as labels at least)
            in |GISCO| database.
        
        Example
        -------
        One single command used to return all availble countries:
            
            >>> serv.country_info(info = 'CODES')
                ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW',
                 ...
                 'XF', 'XG', 'XH', 'XI', 'XL', 'XM', 'XN', 'XO', 'XU', 'XV', 'YE', 'ZA', 'ZM', 'ZW']        
        
        Note
        ----
        Actually, the command :data:`serv.country_info()` alone (*i.e.* without 
        arguments) also returns the expected result.
        
        See also
        --------
        :meth:`~GISCOService.nuts_units`, :meth:`~GISCOService.country_response`, 
        :meth:`~GISCOService.url_country`, :meth:`base._Service.read_response`.
        """
        info = kwargs.pop(_Decorator.KW_INFO, None)
        try:
            assert info is None or happyType.isstring(info)
        except AssertionError:
            raise happyError('wrong format for %s argument' % _Decorator.KW_INFO.upper())        
        else:
            if info is None:
                info = 'CODES'
            info = info.upper()            
        try:
            assert info in ('CODES',)
        except AssertionError:
            raise happyError('wrong value for %s argument' % _Decorator.KW_INFO.upper())  
        else:
            source = 'INFO'
        kwargs.update({_Decorator.KW_SOURCE: source,
                       _Decorator.KW_CACHING: kwargs.pop(_Decorator.KW_CACHING, False)})                 
        try:
            resp = self.country_response(**kwargs)
        except:
            raise happyError('error loading country response')
        try:
            data = self.read_response(resp, fmt='jsontext')
        except:
            raise happyError('error info country file reading')
        else:
            data = list(data.keys())
        return data
        
    #/************************************************************************/
    def nutsid2name(self, **kwargs):
        """
            
            >>> id = serv.nutsid2name(name=name, **kwargs)
            >>> name = serv.nutsid2name(id=id, **kwargs)
            
        Arguments
        ---------
        id : str
        name : str
            
        Keyword arguments
        -----------------
        info : :class:`pandas.DataFrame`
        group : bool
        dist : bool,str
        kwargs :
            see :meth:`nuts_info` method.
            
        Returns
        -------
        
        Examples
        --------
        
            >>> print(serv.nutsid2name(id='AT'))
                None
            >>> serv.nutsid2name(id='AT', dist='contains')
                ['OSTÖSTERREICH',
                 'Burgenland (AT)', 'Mittelburgenland', 'Nordburgenland', 'Südburgenland', 'Niederösterreich', 'Mostviertel-Eisenwurzen',
                 'Niederösterreich-Süd', 'Sankt Pölten', 'Waldviertel', 'Weinviertel', 'Wiener Umland/Nordteil', 'Wiener Umland/Südteil', 'Wien', 'Wien',
                 'SÜDÖSTERREICH',
                 'Kärnten', 'Klagenfurt-Villach', 'Oberkärnten', 'Unterkärnten', 'Graz', 'Liezen', 'Östliche Obersteiermark', 'West- und Südsteiermark',
                 'Westliche Obersteiermark', 'Oberösterreich', 'Innviertel', 'Linz-Wels', 'Mühlviertel', 'Steyr-Kirchdorf', 'Salzburg', 'Lungau', 'Pinzgau-Pongau', 
                 'Salzburg und Umgebung', 'Tirol', 'Innsbruck', 'Osttirol', 'Tiroler Oberland', 'Tiroler Unterland', 'Vorarlberg', 'Rheintal-Bodenseegebiet',
                 'ÖSTERREICH',
                 'Steiermark', 'Oststeiermark',
                 'WESTÖSTERREICH',
                 'Traunviertel', 'Außerfern', 'Bludenz-Bregenzer Wald']        
            >>> serv.nutsid2name(name='Gwent Valley')
                'UKL16'
            >>> serv.nutsid2name(name='ЦРНА ГОРА')
                ['ME0', 'ME00', 'ME000', 'ME']
            >>> serv.nutsid2name(name='Caithness')
                'UKM61'
            >>> serv.nutsid2name(name='France', dist='contains')
                ['FR1', 'FR10', 'FR']
            >>> serv.nutsid2name(id=['FR1', 'FR10', 'FR'])
                ['ÎLE DE FRANCE', 'Île de France', 'FRANCE']
        
        See also
        --------
        :meth:`~GISCOService.nuts_info`.
        """
        name, _id = kwargs.pop(_Decorator.KW_NAME,None), kwargs.pop(_Decorator.KW_ID,None)
        try:
            assert (name is None or _id is None)
        except:
            raise happyError('incompatible arguments %s and %s' % (_Decorator.KW_NAME.upper(),_Decorator.KW_ID.upper()))
        try:
            assert not(name is None and _id is None)
        except:
            raise happyError('missing arguments %s and %s' % (_Decorator.KW_NAME.upper(),_Decorator.KW_ID.upper()))
        source = name or _id
        if not happyType.issequence(source):
            source = [source,]
        try:
            assert all([happyType.isstring(s) for s in source])
        except:
            raise happyError('wrong type for %s argument' % _Decorator.KW_NAME.upper() if name else _Decorator.KW_ID.upper())        
        else:
            source = [s.upper() for s in source]
        info = kwargs.pop(_Decorator.KW_INFO, None)
        group = kwargs.pop('group', False)
        dist = kwargs.pop('dist', False)
        try:
            assert info is None or isinstance(info, pd.DataFrame)
        except:
            raise happyError('wrong type for %s argument' % _Decorator.KW_INFO.upper())  
        else: # load the data!
            if info is None:
                info = self.nuts_info(info='NAMES', **kwargs)
        if name is not None and LEVENSHTEIN_INSTALLED is True:
                dist = dist and 'jaro_winkler'
                try:
                    distance = getattr(Levenshtein,dist)
                except AttributeError:
                    raise happyError('Levenshtein distance %s not recognised' % distance)
                else: 
                    distance = lambda c1, c2: dist(c1.str.upper().str, c2) < 0.9
        else:
            dist = dist or 'exact'
            if dist == 'exact':         
                distance = lambda c1, c2: c1.str.upper() == c2
            elif dist in ('match', 'contains', 'startswith', 'endswith'): 
                distance = lambda c1, c2: getattr(c1.str.upper().str, dist)(c2) # does not work :(
            elif dist == 'find':         
                distance = lambda c1, c2: c1.str.upper().str.find(c2) > 0
        # the dim/cols of LUT are: 'CNTR_CODE', 'NUTS_ID', 'NUTS_NAME'
        if name is not None:
            dim1, dim2 = 'NUTS_NAME', 'NUTS_ID'
        else:            
            dim1, dim2 = 'NUTS_ID', 'NUTS_NAME'
        try:
            if group is True:
                dest = info[info[dim1].str.isin(source)][dim2].tolist()
            else:
                dest = [info[distance(info[dim1],s)][dim2].values.tolist() for s in source]
        except:
            dest = None
        else:
            if dest not in ([],[[]],[None]):
                dest = [d if d is None or len(d)>1 else d[0] for d in dest]
        return dest if dest is None or len(dest)>1 else dest[0]
        
    #/************************************************************************/
    def url2nutsid(self, url):
        """Check whether a given URL represents a |NUTS| dataset disseminated though
        |GISCO| Rest API and return information about it.
            
            >>> dimensions = serv.url2nutsid(url)
                        
        Arguments
        ---------
        url : str
        
        Returns
        -------
        dimensions : dict        
        
        Examples
        --------
        Here are few examples of a simple identification of |NUTS| parameters from
        automatically generated URLs (reversing the generation process):
            
            >>> url = serv.url_nuts(source='BULK', fmt='geojson')
            >>> print(url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-60m.geojson.zip'
            >>> serv.url2nutsid(url)
                OrderedDict([('year', 2013), 
                             ('scale', '60m'), 
                             ('fmt', 'geojson')])
            >>> url = serv.url_nuts('BE100', year = 2016, vector = 'label')
            >>> print(url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE100-label-3035-2016.geojson'
            >>> serv.url2nutsid(url)
                OrderedDict([('source', 'BE100'),
                             ('year', 2016),
                             ('proj', 3035),
                             ('vector', 'LB'),
                             ('fmt', 'geojson')])
            >>> url = serv.url_nuts('AT', year = 2010, scale = 1, proj = 'Mercator')
            >>> print(url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT-region-01m-3857-2010.geojson'
            >>> serv.url2nutsid(url)
                OrderedDict([('source', 'AT'),
                             ('year', 2010),
                             ('proj', 3857),
                             ('scale', '01m'),
                             ('vector', 'RG'),
                             ('fmt', 'geojson')])
            >>> url = serv.url_nuts(source='NUTS', level=3, fmt='shp')
            >>> print(url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_RG_60M_2013_4326_LEVL_3.shx'
            >>> serv.url2nutsid(url)
                OrderedDict([('year', 2013),
                             ('proj', 4326),
                             ('scale', '60M'),
                             ('vector', 'RG'),
                             ('level', 3),
                             ('fmt', 'shp')])
            >>> url = serv.url_nuts(source='NUTS', level='ALL', vector='label', fmt='geojson')
            >>> print(url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/geojson/NUTS_LB_2013_4326.geojson'
            >>> serv.url2nutsid(url)
                OrderedDict([('year', 2013),
                             ('proj', 4326),
                             ('vector', 'LB'),
                             ('level', 'ALL'),
                             ('fmt', 'geojson')])
            >>> url = serv.url_nuts(source='NUTS2JSON',  fmt='geojson')
            >>> print(url)
                'https://raw.githubusercontent.com/eurostat/Nuts2json/gh-pages/2013/3857/60M/nutsrg_0.json'
            >>> serv.url2nutsid(url)
                OrderedDict([('year', 2013),
                             ('proj', 3857),
                             ('scale', '60M'),
                             ('vector', 'RG'),
                             ('level', 0),
                             ('fmt', 'geojson')])
                
        See also
        --------
        :meth:`~GISCOService.url_nuts`, :meth:`~GISCOService.geom2nutsid`.
        """
        unit, year, scale, fmt, proj, vec, level =                         \
            None, None, None, None, None, None, None
        isgisco, isnuts2json = url.find(self.cache_url), url.find(settings.NUTS2JSON_DOMAIN)
        if isgisco < 0 and isnuts2json < 0:
            happyVerbose('URL not recognised as GISCO/NUTS2JSON URL')
            return None # {}
        # let us look at the last part of the URL only
        if isgisco > 0:
            turl = url.split(self.cache_url)[-1]
            url = url.split('/')[-1]
            sub = url.split('.')
            if url.count('.') > 1: # or len(sub)>2
                fmt = sub[-2] 
            elif turl.find(settings.GISCO_PATTERNS['bulk']['compress']) >= 0:
                # if we reach this point, it means that only the compress extension 
                # appears in the name, not the format of the dataset
                fmt = None
            else:
                fmt = sub[-1]
            fmt = {v:k for k,v in settings.GISCO_FORMATS.items()}[fmt]
            if turl.find(settings.GISCO_PATTERNS['bulk']['domain']) >= 0    \
                    and turl.find(settings.GISCO_PATTERNS['bulk']['base']) > 0:
                sub = sub[0].replace(settings.GISCO_PATTERNS['bulk']['base'],'').split('-')
                year, scale = sub
            elif turl.find(settings.GISCO_PATTERNS['nuts']['fmt']) >= 0     \
                    and turl.find(settings.GISCO_PATTERNS['nuts']['info']) > 0:
                year = sub[0].split('-')[1]
            elif turl.find(settings.GISCO_PATTERNS['nuts']['base']) >= 0:
                sub = sub[0].replace(settings.GISCO_PATTERNS['nuts']['base'],'').split('_')
                vec = sub[0]
                if vec == 'LB':         year, proj = sub[1:3]
                else:                   scale, year, proj = sub[1:4]
                if 'LEVL' in sub:       level = sub[-1]
                else:                   level = 'ALL'
            elif turl.find(settings.GISCO_PATTERNS['nuts']['domain']) >= 0:
                sub = sub[0].split('-')
                unit, vec = sub[0:2]
                if vec == 'label':      proj, year = sub[2:]
                else:                   scale, proj, year = sub[2:]
                vec = settings.GISCO_VECTORS[vec]
        elif isnuts2json > 0:
            sub = url.split(settings.NUTS2JSON_DOMAIN)[-1].split('.')[0]
            if sub.startswith('/'):     sub = sub[1:]
            year, proj, scale, data = sub.split('/')
            sub = data.split('_')
            if len(sub)>1:              vec, level, fmt = *sub, 'geojson'
            else:                       level, fmt = sub[0], 'topojson'
            vec = 'RG' if vec=='nutsrg' else ('LB' if vec=='nutsbn' else vec)
        # ['UNIT', 'YEAR', 'PROJECTION', 'SCALE', 'VECTOR', 'LEVEL', 'FORMAT']
        kwargs = {}
        if unit is not None:
            kwargs.update({'SOURCE': unit})
        if year is not None:
            kwargs.update({'YEAR': int(year)})
        if proj is not None:
            kwargs.update({'PROJECTION': int(proj)})
        if scale is not None:
            kwargs.update({'SCALE': scale})
        if vec is not None:
            kwargs.update({'VECTOR': vec})
        if level is not None:
            kwargs.update({'LEVEL': int(level) if level!='ALL' else level})
        if fmt is not None:
            kwargs.update({'FORMAT': fmt})  
        dimensions = collections.OrderedDict(zip(settings.GISCO_DATA_DIMENSIONS,
                                                 [None]*len(settings.GISCO_DATA_DIMENSIONS)))
        keys = list(dimensions.keys())
        [dimensions.update({getattr(_Decorator, 'KW_' + k): kwargs.get(k)})  \
             or dimensions.pop(k) if k in kwargs else dimensions.pop(k) for k in keys]
        return dimensions

    #/************************************************************************/
    def geom2nutsid(self, geom):
        """Check whether a given URL represents a |NUTS| dataset disseminated though
        |GISCO| Rest API and return information about it.
            
            >>> dimensions = serv.geom2nutsid(geom)
                        
        Arguments
        ---------
        geom : str
        
        Returns
        -------
        dimensions : dict        
        
        Examples
        --------
        
            >>> resp = serv.nuts_response(unit='BE100', year = 2016, vector = 'label')
            >>> print(resp.url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/BE100-label-3035-2016.geojson'
            >>> geom = resp.xvalues().text
            >>> print(geom)
                '{"crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3035"}}, 
                  "type": "FeatureCollection", 
                  "features": [{"geometry": {"type": "Point", "coordinates": [3923952, 3096269]}, 
                                "type": "Feature", 
                                "properties": {"CNTR_CODE": "BE", "NUTS_NAME": "Arr. de Bruxelles-Capitale/Arr. van Brussel-Hoofdstad", 
                                               "LEVL_CODE": 3, "FID": "BE100", "NUTS_ID": "BE100"}, 
                                "id": "BE100"}]
                 }'
            >>> serv.geom2nutsid(geom)
                OrderedDict([('source', 'BE100'),
                             ('proj', '3035'),
                             ('vector', 'LB'),
                             ('level', 3)])
            >>> resp = serv.nuts_response(unit='AT', year = 2010, scale = 1, proj = 'Mercator')
            >>> print(resp.url)
                'https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/distribution/AT-region-01m-3857-2010.geojson'
            >>> geom = resp.xvalues().text
            >>> print(geom)
                {"crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3857"}}, 
                 "type": "FeatureCollection", 
                 "features": [{"geometry": {"type": "MultiPolygon", "coordinates": [[[[1163776, 6033263], [1163403, 6033073], 
                ...
                                                                                      [1162055, 6027947], [1163776, 6033263]]]]}, 
                                "type": "Feature", 
                                "properties": {"CNTR_CODE": "AT", "NUTS_NAME": "\u00d6sterreich", 
                                               "LEVL_CODE": 0, "FID": "AT", "NUTS_ID": "AT"}, 
                                "id": "AT"}]
                 }                                                                                      
            >>> serv.geom2nutsid(geom)
                OrderedDict([('source', 'AT'),
                             ('proj', '3857'),
                             ('vector', 'RG'),
                             ('level', 0)])      
            >>> geom = serv.coord2nuts([41.8933203,12.4829321], level=2)  
            >>> print(geom)                                                                             
                {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2',
                 'NAME_LATN': 'Lazio', 'NUTS_ID': 'ITI4', 'NUTS_NAME': 'Lazio',
                 'OBJECTID': '330',
                 'SHRT_ENGL': 'Italy'},
                 'displayFieldName': 'NUTS_ID',
                 'layerId': 2, 'layerName': 'NUTS_2013',
                 'value': 'ITI4'}
             >>> serv.geom2nutsid(geom)
                 OrderedDict([('source', 'ITI4'), 
                              ('year', '2013'), 
                              ('level', '2')])
                  
        See also
        --------
        :meth:`~GISCOService.url2nutsid`.
        """
        try:
            assert happyType.isstring(geom) or happyType.ismapping(geom)
        except:
            raise happyError('wrong format/value for input geometry')
        if happyType.isstring(geom):
            try:
                geom = json.loads(geom) 
            except:
                raise happyError('impossible to retrieve dictionary structure from input string')
        dimensions = collections.OrderedDict(zip([getattr(_Decorator, 'KW_' + k) for k in settings.GISCO_DATA_DIMENSIONS],
                                                 [None]*len(settings.GISCO_DATA_DIMENSIONS)))
        dimensions.pop(_Decorator.KW_FORMAT)        
        if _Decorator.parse_nuts.KW_ATTRIBUTES in geom.keys():
            [dimensions.pop(k) for k in (_Decorator.KW_SCALE,_Decorator.KW_PROJECTION,_Decorator.KW_VECTOR)]
            dimensions.update({_Decorator.KW_SOURCE:                \
                                   geom[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_NUTS_ID],
                               _Decorator.KW_LEVEL:                  \
                                   geom[_Decorator.parse_nuts.KW_ATTRIBUTES][_Decorator.parse_nuts.KW_LEVEL],
                               _Decorator.KW_YEAR:                 \
                                   geom[_Decorator.parse_nuts.KW_LAYERNAME].split('NUTS_')[-1]
                               })
        else: #if _Decorator.parse_nuts.KW_PROPERTIES in geom.keys():
            [dimensions.pop(k) for k in (_Decorator.KW_SCALE,_Decorator.KW_YEAR)]
            dimensions.update({_Decorator.KW_PROJECTION:
                                geom[_Decorator.parse_nuts.KW_CRS][_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_NAME].split(':EPSG::')[-1]})
            features = geom[_Decorator.parse_nuts.KW_FEATURES]
            dimensions = [dimensions.copy() for f in features]
            [dimensions[i].update({_Decorator.KW_SOURCE:                \
                                       f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_NUTS_ID],
                                   _Decorator.KW_LEVEL:                  \
                                       f[_Decorator.parse_nuts.KW_PROPERTIES][_Decorator.parse_nuts.KW_LEVEL],
                                   _Decorator.KW_VECTOR:                 \
                                       {"Polygon": 'RG', "MultiPolygon": 'RG', "LineString": 'BN', "Point": 'LB'}   \
                                       [f[_Decorator.parse_nuts.KW_GEOMETRY][_Decorator.parse_nuts.KW_TYPE]]
                                    })
                    for i, f in enumerate(features)]
        return dimensions if dimensions in ([],[None]) or len(dimensions)>1 else dimensions[0]
      
    #/************************************************************************/
    def _place2geom(self, place, **kwargs): 
        """Iterable version of :meth:`~GISCOService.place2geom`.
        """
        kwargs.update({'key': _Decorator.parse_geometry.KW_FEATURES})
        #return super(GISCOService,self)._place2geom(place, **kwargs)
        for g in super(GISCOService,self)._place2geom(place, **kwargs):
            yield g
    #/************************************************************************/
    @_Decorator.parse_place
    def place2geom(self, place, **kwargs): 
        """Retrieve the geographical information associated to a given place as
        a geometry using |GISCO| service.
        
            >>> geom = serv.place2geom(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[lat, lon, distance_sort, limit, osm_tag, lang]`
            are accepted; see :meth:`~GISCOService.url_geocode`.
        
        Returns
        -------
        geom : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input :data:`place`, one for each place 
            mentioned.
                  
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the geolocation cannot be loaded,                
                * the geolocation is not recognised.
                
        Example
        -------
        The method returns the complete list of geometries output by the web-servive:
           
            >>> serv = services.GISCOService()
            >>> serv.place2geom('Madrid, Spain')
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
        This method overrides :meth:`OSMService.place2geom` by further providing 
        the :literal:`features` key that will be extracted from the output geometry 
        dictionary(ies).
        
        See also
        --------
        :meth:`~GISCOService.place2coord`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2nuts`, :meth:`~GISCOService.place2nuts`, 
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.url_geocode`, 
        :meth:`OSMService.place2geom`, :meth:`base._Service.get_response`.
        """
        if not kwargs.get('nominatim'):
            kwargs.update({'key': _Decorator.parse_geometry.KW_FEATURES})
        return super(GISCOService,self).place2geom(place=place, **kwargs)
        
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
        
            >>> coord = serv.place2coord(place, **kwargs)

        Arguments
        ---------
        place : str, list[str]
            place (topo) name(s).
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[lat, lon, distance_sort, limit, osm_tag, lang]`
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
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2nuts`, :meth:`~GISCOService.place2nuts`, 
        :meth:`~GISCOService.coord2route`, :meth:`OSMService.place2coord`.
        """
        return super(GISCOService,self).place2coord(place=place, **kwargs)

    #/************************************************************************/
    #def _coord2geom(self, coord, **kwargs): 
    #    """Iterable version of :meth:`~GISCOService.coord2geom`.
    #    """
    #    if not kwargs.get('nominatim'):
    #       kwargs.update({'key': _Decorator.parse_geometry.KW_FEATURES})
    #    #return super(GISCOService,self)._place2geom(place, **kwargs)
    #    for a in super(GISCOService,self)._coord2geom(coord, **kwargs):
    #        yield a
    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2geom(self, coord, **kwargs): # specific use
        """Retrieve the place (topo)name of a given location provided by its 
        geographic coordinates using |GISCO| service.
        
            >>>  geom = serv.coord2geom(coord, **kwargs)

        Arguments
        ---------
        coord : float, list[float]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[radius, distance_sort, limit, lang]` are accepted; 
            see :meth:`~GISCOService.url_reverse`.
        
        Returns
        -------
        geom : dict, list[dict]
            a (list of) geometry(ies), *i.e.* a dictionary describing the geographical
            information related to the input geographic coordinate(s) in :data:`coord`, 
            one for each coordinate listed.
        
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
            >>> berlin = [52.5170365, 13.3888599]
        
        We can build an |OSM| URL to get the result:
        
            >>> serv = services.OSMService()
            >>> serv.url_reverse(lat=berlin[0], lon=berlin[1]) 
                'https://europa.eu/webtools/rest/gisco/nominatim/reverse.php?lat=52.5170365&lon=13.3888599&format=json'
        
        Otherwise, the method :meth:`coord2geom` can do everything at once, with
        or without calling the |Nominatim| service:
        
            >>> serv.coord2geom(berlin, format='json', nominatim=True)
                {"place_id": "17695918",
                "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http:\/\/www.openstreetmap.org\/copyright",
                "osm_type": "node",
                "osm_id": "1818862993",
                "lat": "52.517322", "lon": "13.388977",
                "display_name": "Douglas, Unter den Linden, Spandauer Vorstadt, Mitte, Berlin, 10117, Germany",
                "address": {"address29": "Douglas",
                            "road": "Unter den Linden",
                            "neighbourhood": "Spandauer Vorstadt",
                            "suburb": "Mitte",
                            "city_district": "Mitte",
                            "city": "Berlin",
                            "state": "Berlin",
                            "postcode": "10117",
                            "country": "Germany",
                            "country_code": "de"}
                }
            >>> serv.coord2geom(berlin, format='json')
                {'geometry': {'coordinates': [13.3983821, 52.5135992], 
                    'type': 'Point'},
                 'properties': {'city': 'Berlin',
                    'country': 'Germany', 'housenumber': '30',
                    'osm_id': 1602537143, 'osm_key': 'place', 'osm_type': 'N',
                    'osm_value': 'house',
                    'postcode': '10117', 'state': 'Berlin',
                    'street': 'Caroline-von-Humboldt-Weg'},
                 'type': 'Feature'
                 }
                         
        Note
        ----
        This method overrides :meth:`OSMService.coord2geom` by further providing 
        the :literal:`features` key that will be extracted from the output geometry 
        dictionary(ies).
        
        See also
        --------
        :meth:`~OSMService.coord2geom`, :meth:`~OSMService.url_reverse`, 
        :meth:`base._Service.get_status`, :meth:`base._Service.get_response`.
        """
        if not kwargs.get('nominatim'):
            kwargs.update({'key': _Decorator.parse_geometry.KW_FEATURES})
        return super(GISCOService,self).coord2geom(coord=coord, **kwargs)
      
    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2place(self, coord, **kwargs): # specific use
        """Retrieve the (topo)name of a given location provided by its geographic 
        coordinates using |GISCO| service.
        
            >>>  place = serv.coord2place(coord, **kwargs)

        Arguments
        ---------
        coord : list[float], list[list]
            geolocation(s) expressed as tuple/list of :literal:`(lat,Lon)` geographic
            coordinates.
        
        Keyword arguments
        -----------------
        kwargs : dict
            keywords in :literal:`[radius, distance_sort, limit, lang]` are accepted; 
            see :meth:`~GISCOService.url_reverse`.
        
        Returns
        -------
        place : str, list[str]
            place (topo)name(s) identifying the input geolocation(s) in :data:`coord`.
        
        Raises
        ------
        happyError
            error is raised in the cases:
            
                * the geolocation request is wrongly formulated,
                * the place cannot be loaded,                
                * the place is not recognised.
                
        Example
        -------
        Let us what we actually retrieve when we enter the geolocation of the
        (approximate) centre of Berlin, Germany:
        
            >>> berlin = [52.5170365, 13.3888599]
        
        We can build the desired |OSM| URL to get the result:
        
            >>> serv = services.GISCOService()
            >>> serv.url_reverse(lat=berlin[0], lon=berlin[1])
                'https://europa.eu/webtools/rest/gisco/reverse?lat=52.5170365&lon=13.3888599'
        
        however, the method :meth:`coord2place` does everything at once:
        
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
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.coord2nuts`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`, 
        :meth:`~GISCOService.url_reverse`.
        """
        kwargs.update({'key': _Decorator.parse_geometry.KW_FEATURES})
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
            except:
                raise happyError('error findnuts URL formatting')
            try:
                data = self.read_url(url, fmt='JSON')
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
                    # raise happyError
                    happyVerbose('NUTS for geolocation %s and key %s not recognised' % (coord[i], key))
                    data = None
                else:
                    data = data.get(key)
            yield data if data is None or not happyType.issequence(data) or len(data)>1 else data[0]

    #/************************************************************************/
    @_Decorator.parse_year
    @_Decorator.parse_projection
    @_Decorator.parse_geometry
    @_Decorator.parse_coordinate
    def coord2nuts(self, coord, **kwargs):
        """Retrieve the various |NUTS| geometries (all levels) associated to given 
        geolocation(s) provided as geographic coordinates.
        
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
            a (list of) dictionary(ies) representing NUTS geometries; :data:`None`
            is returned when the coordinates refer to a location outside the EU.
        
        Raises
        ------
        happyError
            error is raised in the case the NUTS request is wrongly formulated.
            
        Examples
        --------
        We can easily retrieve all NUTS geometry associated to Rome, Italia from its
        geocoordinates:
            
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
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.place2coord`, 
        :meth:`~GISCOService.place2nuts`, :meth:`~GISCOService.coord2route`,
        :meth:`~GISCOService.coord2place`, :meth:`~GISCOService.url_findnuts`, 
        :meth:`base._Service.get_response`.
        """
        level = kwargs.pop('level',None)
        #if 'key' not in kwargs:
        kwargs.update({'key': _Decorator.parse_nuts.KW_RESULTS})
        nuts = []        
        #[nuts.append(data if len(data)>1 else data[0]) for data in self._coord2nuts(coord, **kwargs)]
        func = lambda *a, **kw: [kw.get(_Decorator.KW_NUTS)]
        [nuts.append(data if data is None or len(data)>1 else data[0])      \
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
        :meth:`~GISCOService.place2geom`, :meth:`~GISCOService.coord2place`, 
        :meth:`~GISCOService.coord2route`, :meth:`~GISCOService.url_geocode`, 
        :meth:`base._Service.get_response`.
        """
        kwargs.update({'unique': kwargs.pop('unique',True)})
        coord = self.place2coord(place, **kwargs)
        nuts = self.coord2nuts(coord, **kwargs)
        return nuts[0] if len(nuts)==1 else nuts

    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2route(self, coord, **kwargs):
        """Retrieve the route going through the various steps/destinations represented 
        by a list of geographic coordinates. 
        
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
        happyError
            error is raised in the cases:
            
                * the route request is wrongly formulated,
                * the route is not available,                
                * the route is not recognised.

        Example
        -------
        Let us retrieve the route between Sofia and Prague, using the other methods
        defined by the service:
        
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
        :meth:`~GISCOService.url_routing`, :meth:`base._Service.get_response`.
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
            url = self.url_routing(**kwargs)
        except:
            raise happyError('error route URL formatting')
        try:
            data = self.read_url(url, fmt='JSON')
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
        happyError
            see :meth:`~GISCOService.coord2route` method.

        Example
        -------    
        We reproduce here the example already used in :meth:`~GISCOService.coord2route`
        but parsing directly the toponames to the method: 
        
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
        :meth:`~GISCOService.url_routing`.
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
