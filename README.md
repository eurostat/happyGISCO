happygisco
=========

Simple microservice (API) on top of _Eurostat_ GISCO web-services.
---

**About**

This project implements a `Python` interface of the API to GISCO services. Further, it encapsulates the interface within a container so as to be distributed... 

<table align="center">
    <tr> <td align="left"><i>documentation</i></td> <td align="left"><strike>available at: https://eurostat.github.io/place2nuts/</strike></td> </tr> 
    <tr> <td align="left"><i>status</i></td> <td align="left">since 2017 &ndash; <b>in construction</b></td></tr> 
    <tr> <td align="left"><i>contributors</i></td> 
    <td align="left" valign="middle">
<a href="https://github.com/gjacopo"><img src="https://github.com/gjacopo.png" width="40"></a>
</td> </tr> 
    <tr> <td align="left"><i>license</i></td> <td align="left"><a href="https://joinup.ec.europa.eu/sites/default/files/eupl1.1.-licence-en_0.pdfEUPL">EUPL</a> </td> </tr> 
</table>

This material is intended as a PoC for the article... 

**Description**

Two variants of the geolocation service are made available through the implementation of different classes:
* `GISCOService`: this is an interface to _Eurostat_ GISCO web-services; it also enables the users to retrieve the NUTS region at level 2 associated to a toponame (place);
* `APIService`: this uses external geo services (including  _Google maps_) to geolocate geographical features; it can be used together with [`gdal`](http://gdal.org) tools together and NUTS appropriate data sources. Note that it is a brute-force solution, since the program will explore sequentially all NUTS features so as to identify the correct region. This could be improved using a multithread process for instance, _e.g._ using [`multiprocessing`](https://docs.python.org/3.4/library/multiprocessing.html?highlight=process) module. Besides, the program does not check the validity of the result returned by _Google maps_ services, since this result can be ambiguous and/or inaccurate. On the simple examples tested (easily identified cities), the program provides with the outputs as expected.

In addition, the GISCO service enables the users to retrieve the NUTS region at level 2 associated to a toponame (place), _e.g._ for the simple example considered herein:

    ~~~
    Bremen, Germany => NUTS ID: DE50 - NUTS name: Bremen
    Florence, Italy => NUTS ID: ITI1 - NUTS name: Toscana
    Brussels, Belgium => NUTS ID: BE10 - NUTS name: RŽgion de Bruxelles-Capitale / Brussels Hoofdstedelijk Gewest	
    ~~~

**<a name="References"></a>References**

* _Eurostat_ NUTS [bulk data source](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip) and [how to](http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf) interpret it.
* _Eurostat_  GISCO webservices: [_find-nuts_](http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py) and [_geocode_](http://europa.eu/webtools/rest/gisco/api?).
* `gdal` [package](https://pypi.python.org/pypi/GDAL) and [cookbook](https://pcjericks.github.io/py-gdalogr-cookbook/index.html).
* Geo packages: [`googlemaps`](https://pypi.python.org/pypi/googlemaps/) and [`geopy`](https://github.com/geopy/geopy).

