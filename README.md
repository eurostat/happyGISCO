place2nuts
========

Identifying NUTS regions associated to a given place or geolocation.
---

**About**

**Description**

*[PoC.py](PoC.py): this is a quick and dirty (`Python`) implementation of the service as a Proof of Concept (PoC); it shows how one can retrieve the NUTS
region at level 2 associated to a toponame (place), _e.g._ for the simple example considered herein:
~~~
Bremen, Germany => NUTS ID: DE50 - NUTS name: Bremen
Florence, Italy => NUTS ID: ITI1 - NUTS name: Toscana
Brussels, Belgium => NUTS ID: BE10 - NUTS name: RŽgion de Bruxelles-Capitale / Brussels Hoofdstedelijk Gewest	
~~~
For that purpose, it uses _Google maps_ geo services (through the `googlemaps` package) and
`gdal` tools together with NUTS appropriate data sources. Note that it is a brute force application, since the program will explore sequentially all NUTS 
features so as to identify the correct region. This could be improved using a multithread process for instance, _e.g._ using [`multiprocessing`](https://docs.python.org/3.4/library/multiprocessing.html?highlight=process) module. Besides, the PoC does not check the
validity of the result returned by _Google maps_ services, since this result can be ambiguous and/or inaccurate. On the simple examples tested (easily
identified cities), the PoC provides with the outputs as expected.

**<a name="References"></a>References**

* _Eurostat_ NUTS [bulk data source](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip) and 
[how to](http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf) interpret it.
* `gdal` [package](https://pypi.python.org/pypi/GDAL) and [cookbook](https://pcjericks.github.io/py-gdalogr-cookbook/index.html).
* Geo servoces: [`googlemaps`](https://pypi.python.org/pypi/googlemaps/) and [`geopy`](https://github.com/geopy/geopy).

