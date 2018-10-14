[![DOI](https://zenodo.org/badge/125985870.svg)](https://zenodo.org/badge/latestdoi/125985870) 
happygisco
=========

Simple geoservice interface (API) on top of _Eurostat_ _GISCO_ web-services.
---

 The project `happyGISCO` (pronounce as if you were French) provides with the implementation of a `Python` interface to [_GISCO_](http://ec.europa.eu/eurostat/web/gisco) web-services. The module `happygisco` will enable you to:
 
 * run some of the basic geographical operations supported by _GISCO_, *e.g.* geocoding, routing and NUTS identification,
 * retrieve most of the datasets (*e.g.*, vector layers of countries, NUTS, ...) made available through _GISCO_ Rest API.

<table align="center">
    <tr> <td align="left"><i>documentation</i></td> <td align="left">available at: http://happygisco.readthedocs.io</td> </tr> 
    <tr> <td align="left"><i>status</i></td> <td align="left">since 2018 &ndash; <b>in construction</b></td></tr> 
    <tr> <td align="left"><i>contributors</i></td> 
    <td align="left" valign="middle">
<a href="https://github.com/gjacopo"><img src="https://github.com/gjacopo.png" width="40"></a>
</td> </tr> 
    <tr> <td align="left"><i>license</i></td> <td align="left"><a href="https://joinup.ec.europa.eu/sites/default/files/eupl1.1.-licence-en_0.pdfEUPL">EUPL</a> </td> </tr> 
</table>

This material accompanies the articles referenced below and illustrates the idea of **_Eurostat_ data as a service**. The rationale is further described in the paper _"Empowering and interacting with statistical produsers: A practical example with Eurostat data as a service"_.

**Quick install and start**

TBC

Once installed, the module can be imported simply:

```python
>>> import happygisco
```

<!-- .. ` ok, I just added that here for a clean editing of code blocks in Xcode... sorry this is useless! -->

**Notebook examples**

Simple examples are available in the form of _Jupyter_ notebooks under the [_notebooks/_](https://github.com/eurostat/happyGISCO/tree/master/notebooks) folder, *e.g.*:

* some [basic calls](http://nbviewer.jupyter.org/github/eurostat/happyGISCO/blob/master/notebooks/example_GISCO_services.ipynb) to the geocoding services,
* a [simple application](http://nbviewer.jupyter.org/github/eurostat/happyGISCO/blob/master/notebooks/example_GISCO_features.ipynb) with NUTS vector features,
* an extended workflow for location identification and retrieval. 

**Usage**

###### Services

Some variants of the geolocation service are made available through the implementation of different classes:

* `OSMService`:  this is an interface to [_OpenStreetMap_](https://www.openstreetmap.org)  native **geocoding and routing web-services**;
* `GISCOService`: this is an interface to _Eurostat_ _GISCO_ web-services; the geocoding and routing tools are also based on _OpenStreetMap_ (the class `GISCOService` derives from `OSMService`); it also enables the users to **retrieve the NUTS region at any level from any geolocation given by its toponame (place) or its geographical coordinates**;
* `APIService`: this calls other "external" geo- web-services (including  [_Google maps_](https://cloud.google.com/maps-platform/)), *e.g.* to **geolocate geographical features**.

Note that **no caching** is performed when running the services, unless they are run from one of the features instance below (*e.g.* `Location`).

It is pretty straigthforward to create an instance of a service, for example `GISCOService` to call _GISCO_ web-services:

```python
>>> from happygisco import services
>>> service = services.GISCOService()
```

<!-- .. ` -->
and run the supported methods:
 
```python
>>> place = "Lampedusa, Italia"
>>> coord = service.place2coord(place, unique=True)
>>> print(coord)
    [35.511134150000004, 12.59629135962961]
>>> alt_place = service.coord2place(coord)
>>> print(alt_place)
    'Strada di Ponente, Lampedusa e Linosa, (Sicily), Italy'
>>> nuts = service.coord2nuts(coord, level=2)
>>> print(nuts)
    {'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2', 'NAME_LATN': 'Sicilia',
     'NUTS_ID': 'ITG1',  'NUTS_NAME': 'Sicilia',  'OBJECTID': '320',
     'SHRT_ENGL': 'Italy'},
     'displayFieldName': 'NUTS_ID',
     'layerId': 2, 'layerName': 'NUTS_2013', 'value': 'ITG1'}
```

 <!-- .. ` -->
Note that, in order to make things easier, it is possible to parse lists of places instead of single places: 
 
```python
>>> axis = ['Rome, Italy', 'Berlin, Germany', 'Tokyo, Japan']
>>> for p in axis:  # either iterating over the places
...     print(service.place2coord(p, unique=True))
    [41.8933203, 12.4829321]
    [52.5170365, 13.3888599]
    [34.6968642, 139.4049033]
>>> coord = service.place2coord(axis, unique=True) # or running the method for the whole list
>>> print(coord)
    [[41.8933203, 12.4829321], [52.5170365, 13.3888599], [34.6968642, 139.4049033]]
>>> service.coord2nuts(coord, level=2)
    [{'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2', 'NAME_LATN': 'Lazio',
      'NUTS_ID': 'ITI4', 'NUTS_NAME': 'Lazio', 'OBJECTID': '330',
      'SHRT_ENGL': 'Italy'},
      'displayFieldName': 'NUTS_ID',
      'layerId': 2, 'layerName': 'NUTS_2013', 'value': 'ITI4'},
     {'attributes': {'CNTR_CODE': 'DE', 'LEVL_CODE': '2', 'NAME_LATN': 'Berlin',
      'NUTS_ID': 'DE30', 'NUTS_NAME': 'Berlin', 'OBJECTID': '202',
      'SHRT_ENGL': 'Germany'},
      'displayFieldName': 'NUTS_ID',
      'layerId': 2, 'layerName': 'NUTS_2013', 'value': 'DE30'},
     None]
```
 
<!-- .. ` -->
You are also offered to use other geo web-services using `APIService`, *e.g.* any of those listed below:

 ```python 
>>> print(APIService.AVAILABLE)
    ['GMaps', 'OpenMapQuest', 'YahooPlaceFinder', 'LiveAddress', 'Bing', 'GeoNames', 'GoogleV3', 'Nominatim', 'MapQuest'] 
```

<!-- .. ` -->
Depending on the service selected, you may be requested to provide with your own credentials:
 
```python 
>>> service = services.APIService(coder='Nominatim') # no key required
>>> service.place2coord('Paris, France')
    [48.8566101, 2.3514992]
>>> service = services.APIService(coder='GMaps', key='???') # use your own key here
>>> service.place2coord('Paris, France')
    [48.856614, 2.3522219]
>>> service = services.APIService(coder='GeoNames', username='???') # use your own username here
>>> service.place2coord('Paris, France')
    [48.85341, 2.3488]
```

<!-- .. ` -->
###### Features

It is possible to create **simple geographical features whose methods implement and apply the different services defined above**, *e.g.*:

* a `Location`: a feature representing a geolocation, *i.e.* defined as a topo/placename or as a list of geographical coordinates,
* an `Area`: a simple vector geometry () in the sense of _GISCO_ services expressed as a dictionary, *i.e.*, structured like the JSON file returned by the  `GISCO` geocoding or reverse geocoding services,
* a `NUTS`: the vector geometry representing a NUTS area expressed as a dictionary, *i.e.*, structured like the JSON file returned by the  `GISCO` `findnuts` services.

One can for instance declare a specific location, and run any of the methods supported by the `Location` class:

```python
>>> from happygisco import features
>>> location = features.Location(place="Lisbon, Portugal")
>>> location.coord
    [38.7077507, -9.1365919]
>>> location.routing('Paris, France')
    ({'distance': 3058767.9, 'duration': 377538.2,
      'geometry': 'uv}qEaeqhEo_XlbOutDa`~@uuVocZqa|@ttDqaZneRwcjEetxBwfYags@}_nAugsAmaYcmcApxCiiuDcvi@webB`dFeix@q}VqdvAfaj@greAtqEuwi@c~QmvqCuhZ}o`AzzVkv{@egOo|Vjf@avyCrlZocsFwo_@ef`DgdKkqQ{gPbkA{pUgwq@h{[s}`B`hJsgnBaq^oMetAkab@q~j@at~@hbd@yheAhmh@gad@vyz@dit@uxz@kjt@knh@lbd@ibd@xheAp~j@`t~@dtAjab@`q^nMahJrgnBe|[x}`BvqU`wq@nkPsgAt_KlnQdo_@r}_DwkZlksFkg@joyCdhOjzVk{V|f|@vhZph`Ab~Q`vqCsnEjpi@wdj@tyeAx|Vd`vA_cF~mx@~ui@tebB_yCtguD~aYjocAn`nAhgsAtfYrgs@pdjEbrxBhaZieR~a|@{tD`vV|cZ~}F`_}@nuUaaN',
      'legs': [{'distance': 1530444.4, 'duration': 188741.1, 'steps': [], 'summary': ''},
               {'distance': 1528323.5, 'duration': 188797.1, 'steps': [], 'summary': ''}]},
     [{'hint': 'DcOGgEuuRIQAAAAAAAAAAE0AAAAAAAAASgQAAOofZwBScQAAzuv3AcpmDwImok4CMZZ0_wAAAQEZfn5e',
       'location': [33.024974, 34.563786], 'name': ''},
      {'hint': 'mRIbgp0SG4IAAAAAAAAAAFoAAAAAAAAAogIAADJYZwFScQAAeuyjAgCdNAIifukCi-EjAAAAAQEZfn5e',
       'location': [44.297338, 37.002496], 'name': ''},
      {'hint': 'DcOGgEuuRIQAAAAAAAAAAE0AAAAAAAAASgQAAOofZwBScQAAzuv3AcpmDwLU3csCvrFGAAAAAQEZfn5e',
       'location': [33.024974, 34.563786], 'name': ''}])
>>> location.findnuts(level=[2,3])
     {2: 'PT17', 3: 'PT170'}
>>> location.distance('Paris, France')
    1455.7107037157618
```

<!-- .. ` -->
What about creating a NUTS object:

```python 
>>> nuts = features.NUTS()
```

<!-- .. ` -->
###### Tools

**Geospatial tools are derived from [`gdal`](http://gdal.org) methods** and provided in the `GDALTransform` class. 

These tools can be used, for instance, with NUTS appropriate vector data sources to operate the NUTS identification. Note that it is a brute-force solution, since the program will explore sequentially all NUTS features so as to identify the correct region. This could be improved using a multithread process for instance, _e.g._ using [`multiprocessing`](https://docs.python.org/3.4/library/multiprocessing.html?highlight=process) module. Besides, the program does not check the validity of the result returned by _Google maps_ services, since this result can be ambiguous and/or inaccurate.
 
In the associated classes `GeoAngle` and `GeoCoordinate`, you will find also some basic implementations of simple geoprocessing tools, *e.g.* units conversion, (geodesic) distance calculation, ... For a quick review on the latter, have for instance a look at [this](https://www.timeanddate.com/worldclock/distanceresult.html?p1=195&p2=133).

**<a name="Data"></a>Data resources**
 
* The Geographic Information System of the Commission at _Eurostat_: [_GISCO_ ](http://ec.europa.eu/eurostat/web/gisco/overview).
* _GISCO_ webservices: [_find-nuts_](http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py) and [_geocode_](http://europa.eu/webtools/rest/gisco/api?).
* _GISCO_ data distribution [REST API](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2) and its [visualisation tool](http://ec.europa.eu/eurostat/cache/RCI).
* _GISCO_ [themes](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/themes.json) with links to [countries](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/countries/) (corresponding [list of datasets](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/countries/datasets.json)) and [NUTS](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/) (corresponding [list of datasets](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/datasets.json)).
* NUTS [bulk download page](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/). You can for instance download [2013 (1:60 Million) NUTS data](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-60m.shp.zip) and find out [how to](http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf) interpret it.
* NUTS [online](http://ec.europa.eu/eurostat/web/regions-and-cities/overview) and NUTS on [RAMON](http://ec.europa.eu/eurostat/ramon/index.cfm?TargetUrl=DSP_PUB_WELC).
* _GISCO_ [`administrative and statistical units`](http://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units) and [`correspondence table`](http://ec.europa.eu/eurostat/ramon/miscellaneous/index.cfm?TargetUrl=DSP_DEGURBA) between degree of urbanisation (DEGURBA) or local administrative units. 
* _TERCET_ [tool](http://ec.europa.eu/eurostat/tercet) and [territorial typologies](http://ec.europa.eu/eurostat/web/nuts/tercet-territorial-typologies).
* Service [Nuts2json](https://github.com/eurostat/Nuts2json) of NUTS `topojson`/`geojson` datasets reformatted for web-mapping (datasets and scripts).
 
**<a name="Software"></a>Software resources/dependencies**

* `gdal` [package](https://pypi.python.org/pypi/GDAL) and [cookbook](https://pcjericks.github.io/py-gdalogr-cookbook/index.html).
* Geocoding/processing packages: [`googlemaps`](https://pypi.python.org/pypi/googlemaps/), [`googleplaces`](https://github.com/slimkrazy/python-google-places) or [`geopy`](https://github.com/geopy/geopy) (_suggested_).
* Packages for (geospatial) data handling: [`pandas`](http://pandas.pydata.org) and [`geopandas`](http://geopandas.org).
* Packages for map visualisations: [`ipyleaflet`](https://github.com/jupyter-widgets/ipyleaflet) or [`folium`](https://github.com/python-visualization/folium).
* [asyncio](https://docs.python.org/3/library/asyncio.html) library and [aiohttp](https://pypi.org/project/aiohttp/) for asynchronous I/O.
* Packages for caching: [`requests_cache`](https://pypi.python.org/pypi/requests-cache) or [`cachecontrol`](https://pypi.python.org/pypi/requests-cache). 

**<a name="References"></a>References**

* Grazzini J., Museux J.-M. and Hahn M. (2018): [**Empowering and interacting with statistical produsers: A practical example with Eurostat data as a service**](https://www.researchgate.net/publication/325973362_Empowering_and_interacting_with_statistical_produsers_a_practical_example_with_Eurostat_data_as_a_service), in Proc. _Conference of European Statistics Stakeholders_.
* Grazzini J., Lamarche P., Gaffuri J. and Museux J.-M. (2018): [**"Show me your code, and then I will trust your figures": Towards software-agnostic open algorithms in statistical production**](https://www.researchgate.net/publication/325320551_Show_me_your_code_and_then_I_will_trust_your_figures_Towards_software-agnostic_open_algorithms_in_statistical_production), in Proc.  _Quality Conference_.
* Downey. A (2012): [Think `Python`](http://www.greenteapress.com/thinkpython/thinkpython.pdf), Green Tea Press.
