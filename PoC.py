#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 08:38:26 2018

@author: gjacopo
"""

import os

try:
    from osgeo import ogr
except ImportError:
    print('visit: https://pypi.python.org/pypi/GDAL')
    raise IOError
else:
    print('GDAL help: https://pcjericks.github.io/py-gdalogr-cookbook/index.html')
    
try:
    import googlemaps
except ImportError:
    print('visit: https://pypi.python.org/pypi/googlemaps/')
    raise IOError
else:
    print('googlemaps help: https://github.com/googlemaps/google-maps-services-python')

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
