[![DOI](https://zenodo.org/badge/125985870.svg)](https://zenodo.org/badge/latestdoi/125985870) 
happygisco
=========

Simple geoservice interface (API) on top of _Eurostat_ GISCO web-services.
---

**About**

This project implements a `Python` interface to [GISCO](http://ec.europa.eu/eurostat/web/gisco) web-services, *e.g.* geocoding, routing and NUTS identification. 
This material accompanies the articles referenced below and illustrates the idea of **_Eurostat_ data as a service**. 

<table align="center">
    <tr> <td align="left"><i>documentation</i></td> <td align="left">available at: http://happygisco.readthedocs.io</td> </tr> 
    <tr> <td align="left"><i>status</i></td> <td align="left">since 2018 &ndash; <b>in construction</b></td></tr> 
    <tr> <td align="left"><i>contributors</i></td> 
    <td align="left" valign="middle">
<a href="https://github.com/gjacopo"><img src="https://github.com/gjacopo.png" width="40"></a>
</td> </tr> 
    <tr> <td align="left"><i>license</i></td> <td align="left"><a href="https://joinup.ec.europa.eu/sites/default/files/eupl1.1.-licence-en_0.pdfEUPL">EUPL</a> </td> </tr> 
</table>

**Description**

****Services****

Some variants of the geolocation service are made available through the implementation of different classes:

* `OSMService`:  this is an interface to [_OpenStreetMap_](https://www.openstreetmap.org)  native **geocoding and routing web-services**;
* `GISCOService`: this is an interface to _Eurostat_ GISCO web-services; the geocoding and routing tools are also based on _OpenStreetMap_ (the class `GISCOService` derives from `OSMService`); it also enables the users to **retrieve the NUTS region at any level from any geolocation given by its toponame (place) or its geographical coordinates**;
* `APIService`: this calls other "external" geo- web-services (including  [_Google maps_](https://cloud.google.com/maps-platform/)), *e.g.* to **geolocate geographical features**.

****Features****

It is possible to create **simple geographical features whose methods implement and apply the different services defined above**, *e.g.*:

* a `Location`: a feature representing a geolocation, *i.e.* defined as a topo/placename or as a list of geographical coordinates,
* an `Area`: a simple vector geometry () in the sense of _GISCO_ services expressed as a dictionary, *i.e.*, structured like the JSON file returned by the  `GISCO` geocoding or reverse geocoding services,
* a `NUTS`: the vector geometry representing a NUTS area expressed as a dictionary, *i.e.*, structured like the JSON file returned by the  `GISCO` `findnuts` services.


****Tools****

**Geospatial tools are derived from [`gdal`](http://gdal.org) methods** and provided in the `GDALTool` class. 

These tools can be used, for instance, with NUTS appropriate vector data sources to operate the NUTS identification. Note that it is a brute-force solution, since the program will explore sequentially all NUTS features so as to identify the correct region. This could be improved using a multithread process for instance, _e.g._ using [`multiprocessing`](https://docs.python.org/3.4/library/multiprocessing.html?highlight=process) module. Besides, the program does not check the validity of the result returned by _Google maps_ services, since this result can be ambiguous and/or inaccurate.

**Quick install and start**

TBC

Once installed, the module can be imported simply:

```python
import happygisco
```


Then one can simply create a dedicated services:

```python
from happygisco import services
service = services.GISCOService()
```


**Examples**

Simple examples are available in the form of _Jupyter_ notebooks under the [_notebooks/_](https://github.com/eurostat/happyGISCO/tree/master/notebooks) folder, *e.g.*:

* a [basic use]( https://cdn.rawgit.com/eurostat/happyGISCO/c7153073/notebooks/Example%20of%20Eurostat%20'Data%20as%20a%20Service'%20using%20happyGISCO%20module.html) of the geocoding services,
* an example of features definition and geocoding,
* an extended workflow for location identification and retrieval. 

**<a name="Resources"></a>Resources**

* _Eurostat_ NUTS [bulk data source](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip) and [how to](http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf) interpret it.
* _Eurostat_  GISCO webservices: [_find-nuts_](http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py) and [_geocode_](http://europa.eu/webtools/rest/gisco/api?).
* `gdal` [package](https://pypi.python.org/pypi/GDAL) and [cookbook](https://pcjericks.github.io/py-gdalogr-cookbook/index.html).
* Geo packages: [`googlemaps`](https://pypi.python.org/pypi/googlemaps/) and [`geopy`](https://github.com/geopy/geopy).

**<a name="References"></a>References**

* Grazzini J., Museux J.-M. and Hahn M. (2018): [**Empowering and interacting with statistical produsers: A practical example with Eurostat data as a service**](), submitted to _Conference of European Statistics Stakeholders_.
* Grazzini J., Lamarche P., Gaffuri J. and Museux J.-M. (2018): [**"Show me your code, and then I will trust your figures": Towards software-agnostic open algorithms in statistical production**](https://www.researchgate.net/publication/325320551_Show_me_your_code_and_then_I_will_trust_your_figures_Towards_software-agnostic_open_algorithms_in_statistical_production), in Proc.  _Quality Conference_.


