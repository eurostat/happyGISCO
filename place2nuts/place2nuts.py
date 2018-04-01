#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 08:38:26 2018

@author: gjacopo
"""

import os, sys
import warnings
import settings

   
try:                                
    import requests # urllib2
except ImportError:                 
    warnings.warn('REQUESTS package (https://pypi.python.org/pypi/requests/) not loaded - GISCO ONLINE service not available')
    ONLINE = False

try:
    from osgeo import ogr
except ImportError:
    OFFLINE = False
    warnings.warn('GDAL package (https://pypi.python.org/pypi/GDAL) not loaded - OFFLINE service not available')
else:
    print('GDAL help: https://pcjericks.github.io/py-gdalogr-cookbook/index.html')
    
try:
    import googlemaps
except ImportError:
    OFFLINE = False
    warnings.warn('GOOGLEMAPS package (https://pypi.python.org/pypi/googlemaps/) not loaded - OFFLINE service not available')
else:
    print('GOOGLEMAPS help: https://github.com/googlemaps/google-maps-services-python')
   
try:                                
    import simplejson as json
except ImportError:
    warnings.warn("missing SIMPLEJSON package (https://pypi.python.org/pypi/simplejson/)", ImportWarning)
    try:                                
        import json
    except ImportError: 
        warnings.warn("JSON module missing in Python Standard Library", ImportWarning)
        class json:
            def loads(arg):  return '%s' % arg

class Place2NUTS(object):
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        """Initialisation of a :class:`Place2NUTS` instance.

            >>> x = Place2NUTS(**kwargs)
        """
        self.__locations, self.__nuts    = {}, {}
        self.__session      = None
        self.__client       = None
        self.__domain       = settings.GISCO_URL
        self.__offline      = kwargs.pop('offline', False)
        self.__googlekey    = kwargs.pop('googlekey', settings.GOOGLE_KEY)
        self.__nutsfile     = kwargs.pop('nutsfile', '')
        if self.offline is False:
            try:
                assert ONLINE is not False
                self.__session = requests.Session()
            except:
                raise IOError('ONLINE service not available')
        else:
            try:
                assert OFFLINE is not False
                self.__client = googlemaps.Client(key=self.offline) 
            except:
                raise IOError('OFFLINE service not available')

    #/************************************************************************/
    @property
    def domain(self):
        return self.__domain
    @domain.setter#analysis:ignore
    def domain(self, domain):
        if not isinstance(domain, str):
            raise IOError('wrong type for DOMAIN parameter')
        self.__domain = domain
        
    #/************************************************************************/
    @property
    def session(self):
        return self.__session
    #@session.setter#analysis:ignore
    #def session(self, session):
    #    if not isinstance(session, requests.sessions.Session):
    #        raise IOError('wrong type for SESSION parameter')
    #    self.__session = session
        
    #/************************************************************************/
    @property
    def client(self):
        return self.__client
    #@client.setter#analysis:ignore
    #def client(self, client):
    #    if not isinstance(client, googlemaps.Client):
    #        raise IOError('wrong type for SESSION parameter')
    #    self.__client = client
            
    #/************************************************************************/
    @property
    def offline(self):
        return self.__offline
    @offline.setter#analysis:ignore
    def offline(self, offline):
        if not isinstance(offline, bool):
            raise IOError('wrong type for OFFLINE parameter')
        self.__offline = offline
            
    #/************************************************************************/
    @property
    def googlekey(self):
        return self.__googlekey
    @googlekey.setter#analysis:ignore
    def googlekey(self, googlekey):
        if not isinstance(googlekey, str):
            raise IOError('wrong type for GOOGLEKEY parameter')
        self.__googlekey = googlekey
            
    #/************************************************************************/
    @property
    def nutsfile(self):
        return self.__nutsfile
    @nutsfile.setter#analysis:ignore
    def nutsfile(self, nutsfile):
        if not isinstance(nutsfile, str):
            raise IOError('wrong type for NUTSFILE parameter')
        self.__nutsfile = nutsfile
    
    #/************************************************************************/
    def get_status(self, url):
        """Download just the header of a URL and return the server's status code.
        """        
        try:
             response = self.__session.head(url)
             response.raise_for_status()
        except:
             raise IOError('wrong request formulated')  
        else:
             status = response.status_code
             response.close()
        return status
    
    #/************************************************************************/
    def get_response(self, url, **kwargs):
        """
        """
        try:
            response = self.__session.get(url)                
        except:
            raise IOError('wrong request formulated')  
        else:
            response.raise_for_status()
        return response   
    
    #/************************************************************************/
    @classmethod
    def __build_url(cls, *args, **kwargs):
        """Create a query URL to *NUTS* web service.
        
            >>> url = Place2NUTS.build_url(*args, **kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            define the parameters for web service.
                
        Returns
        -------
        url : str
            link to NUTS web service to submit the specified query.

        Note
        ----
        The generic url formatting is:
            {domain}/{path}/{query}?{filters}
        """
        # retrieve parameters/build url
        if args not in (None,()):       domain = args[0]
        else:                           domain = kwargs.pop('domain','')
        url = domain.strip("/")
        protocol = kwargs.pop('protocol', settings.DEF_PROTOCOL)
        if protocol not in settings.PROTOCOLS:
            raise IOError('web protocol not recognised')
        if not url.startswith(protocol):  
            url = "%s://%s" % (protocol, url)
        if 'path' in kwargs:      
            url = "%s/%s" % (url, kwargs.pop('path'))
        if 'query' in kwargs:      
            url = "%s/%s?" % (url, kwargs.pop('query'))
        if kwargs != {}:
            #_izip_replicate = lambda d : [(k,i) if isinstance(d[k], (tuple,list))        \
            #        else (k, d[k]) for k in d for i in d[k]]
            _izip_replicate = lambda d : [[(k,i) for i in d[k]] if isinstance(d[k], (tuple,list))        \
                else (k, d[k])  for k in d]          
            filters = '&'.join(['{k}={v}'.format(k=k, v=v) for (k, v) in _izip_replicate(kwargs)])
            # filters = '&'.join(map("=".join,kwargs.items()))
            try:        
                last = url.rsplit('/',1)[1]
                if any([last.endswith(c) for c in ('?', '/')]):     sep = ''
            except:     
                sep = '?'
            url = "%s%s%s" % (url, sep, filters)
        return url


    #/************************************************************************/
    def url_location(self, **kwargs):
        return self.__build_url(domain=self.domain, query='api')
    
    #/************************************************************************/
    def url_nuts(self, **kwargs):
        return self.__build_url(domain=self.domain, path='nuts', query='find-nuts.py')
        
    #/************************************************************************/
    def place2loc(self, *args, **kwargs):
        if args not in (None,()):       place = args[0]
        else:                           place = kwargs.pop('place', None)
        if place in (None,'') or not isinstance(place,str):
            raise IOError('wrong input place')
        else:
            place = '+'.join(place.replace(',',' ').split())
        kwargs.update({'q': place})
        try:
            url = self.url_location(self, **kwargs)
            self.get_status(url)
        except:
            raise IOError('error geolocation request')
        else:
            response = self.get_response(url)
        try:
            location = json.loads(response.text)
            assert location not in({},None)
        except:
            raise IOError('Place geolocation not recognised')
        # pprint(location)

    #/************************************************************************/
    def loc2nuts(self, *args, **kwargs):
        if args not in (None,()):       lat, lon = args[:1]
        else:                           lat, lon = kwargs.pop('lon'), kwargs.pop('lat')
        if lat is None or lon is None:
            raise IOError('wrong input geographical location')
        # Usage: x=<longitude>&y=<latitude>&f=<JSON/XML>&year=<2013/2010/2006>&proj=3035&geometry=<N/Y>
        kwargs.update({'x': lon, 'y': lat,
                       'year': kwargs.pop('year',2013),
                       'geometry': 'Y', 'f': 'JSON'})
        try:
            url = self.url_nuts(self, **kwargs)
            self.get_status(url)
        except:
            raise IOError('error NUTS request')
        else:
            response = self.get_response(url)
        try:
            nuts = json.loads(response.text)
            assert nuts is not None
        except:
            raise IOError('Place NUTS not recognised')
        
    #/************************************************************************/
    def place2nuts():
        return
    
    #/************************************************************************/
    def __call__(self, *args, **kwargs):
        return self.place2nuts(*args, **kwargs)
    
PLACES      = ['Bremen, Germany', 'Florence, Italy', 'Brussels, Belgium']
GOOGLE_KEY  = '' # you need to provide your own API key here
NUTSDIR     = 'ref-nuts-2013-01m'
NUTSFILE    = 'NUTS_RG_01M_2013_4326_LEVL_2.shp' # region

gmaps = googlemaps.Client(key=GOOGLE_KEY) 
Locations = ogr.Geometry(ogr.wkbMultiPoint)

print('')
for place in PLACES:   
    try:
        geocode = gmaps.geocode(place)
        coord = geocode[0]['geometry']['location']
        assert coord is not None
    except:
        print('\nCould not retrieve geolocation of %s' % place)
        continue
    else:
        print('%s => %s' % (place, coord))
    try:
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.AddPoint(coord['lng'], coord['lat']) 
    except:
        print('\nCould not add geolocation')
    else:
        Locations.AddGeometry(pt)

try:
    assert Locations is not None
except:
    print('\nCould not retrieve any geolocation')
    raise IOError
else:
    print(Locations.ExportToWkt())

try:
    driver = ogr.GetDriverByName('ESRI Shapefile')
    Nuts = driver.Open(os.path.join(NUTSDIR,NUTSFILE), 0) # 0 means read-only
    assert Nuts is not None
except:
    print('\nCould not open %s' % NUTSFILE)
    print('visit: http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip')
    raise IOError
else:
    print('\nOpened %s' % NUTSFILE)
    print('NUTS help: http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf')
    
try:
    layer = Nuts.GetLayer()
    assert layer is not None
except:
    print('\nCould not get vector layer')
    raise IOError
else:
    featureCount = layer.GetFeatureCount()
    print('\nNumber of features in %s: %d' % (os.path.basename(NUTSFILE),featureCount))
    
Regions = []

# iterate through points
for i in range(0, Locations.GetGeometryCount()): # because it is a MULTIPOINT
    pt = Locations.GetGeometryRef(i)
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
            Regions.append(feature)
    if len(Regions)<i+1:    
        Regions.append(None)

try:
    assert not all([region is None for region in Regions])
except:
    print('\nNUTS regions (level 2) not found')
else:
    print('\nNUTS regions (level 2) identified')
    for i, place in enumerate(PLACES):
        items = Regions[i].items()
        print('%s => NUTS ID: %s - NUTS name: %s' % (place, items['NUTS_ID'],items['NUTS_NAME']))
# will display:
# Bremen, Germany => NUTS ID: DE50 - NUTS name: Bremen
# Florence, Italy => NUTS ID: ITI1 - NUTS name: Toscana
# Brussels, Belgium => NUTS ID: BE10 - NUTS name: Région de Bruxelles-Capitale / Brussels Hoofdstedelijk Gewest	
