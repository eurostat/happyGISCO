#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. __init__

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `OpenStreetMap <OSM_>`_
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. |Nominatim| replace:: `Nominatim <Nominatim_>`_
.. _Google: http://www.google.com
.. |Google| replace:: `Google <Google_>`_
.. _Google_Maps: https://developers.google.com/maps/
.. |Google_Maps| replace:: `Google Maps <Google_Maps_>`_
.. _Google_Places: https://developers.google.com/places/
.. |Google_Places| replace:: `Google Places <Google_Places_>`_

Simple microservice (API) built on top of |Eurostat| |GISCO| web-services, and 
not only.

**Description**

The :mod:`happyGISCO` package will enable you to perform very basic geospatial 
operations, *e.g.*:
    
    * geospatial units conversion,  
    * geographical system transformation, 
    * geolocation retrieval,
    
using common online web-based geoservices (with or without authentication requested):
    
    * |Nominatim| web-services based on |OSM|,
    * |GISCO| web-services hosted at |Eurostat| and replicating |OSM| web-services, 
    * |Google| web-services, *e.g.* |Google_Maps| and |Google_Places|.

**Usage**

    >>> import happygisco
    >>> print(happygisco.__all__)
        ['settings', 'tools', 'services', 'features']
    
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Thu Apr  5 16:40:31 2018

__all__ = ['settings', 'tools', 'services', 'features']#analysis:ignore

#==============================================================================
# PROGRAM METADATA
#==============================================================================

__project__     = 'happyGISCO'
__url__         = 'https://github.com/eurostat/happyGISCO'
__organization__ = 'European Commission (EC - DG ESTAT)'
# note that neither __project__ nor __url__ ar __organization__ are special/protected 
# variables in python language, unlike the other fields below
__description__ = 'Simple API to Eurostat GISCO web-services'
__package__     = __project__.lower() # already set in fact...
__date__        = '2018'
__author__      = 'Jacopo Grazzini'
__contact__     = 'jacopo.grazzini@ec.europa.eu'
__license__     = 'European Union Public Licence (EUPL)'
__version__     = '1'
__copyright__   = 'European Union'
                                   
#==============================================================================
# CORE DEFINITION
#==============================================================================

#/****************************************************************************/
# dummy __metadata class to retrieve easily the metadata of the software.
#/****************************************************************************/
class __metadata(dict):

    __metadata_keys = ['project', 'description', 'url', 'package', 'subpackage', \
                       'author', 'contact', 'license', 'copyright', 'organization', \
                       'credits', 'date', 'version']
    __lenght_longest_key = max([len(k) for k in __metadata_keys])
                        
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self
 
    #/************************************************************************/
    def copy(self, *args, **kwargs):
        return self.__class__(**self.__dict__)

    #/************************************************************************/
    def __repr__(self):
        return "<{} instance at {}>".format(self.__class__.__name__, id(self))
    def __str__(self):    
        l = self.__lenght_longest_key
        return "\n".join(["{} : {}".format(k.ljust(l),getattr(self,k))
            for k in self.__metadata_keys if self.get(k) not in ('',None)])    

    #/************************************************************************/
    def __getattr__(self, attr):
        if attr.startswith('__'):
            try:        nattr = attr[2:-2]
            except:     nattr = None
        else:
            nattr = attr
        if nattr in self.keys():  
            r = self.get(nattr)
        else:
            try:        object.__getattribute__(self, attr) 
            except:     pass
            r = None
        return r
        
#/****************************************************************************/
metadata = __metadata({'project'     : __project__,
                       'description' : __description__,
                       'package'     : __package__,
                       'version'     : __version__,
                       'author'      : __author__,
                       'contact'     : __contact__,
                       'license'     : __license__,
                       'copyright'   : __copyright__,
                       'organization':__organization__,
                       'url'         : __url__,
                       'date'        : __date__,
                       'credits'     : '',
                       'subpackage'  : ''
                       })                                                        

