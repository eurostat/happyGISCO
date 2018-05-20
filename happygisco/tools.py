#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_tools

.. Links

.. _GDAL: https://pypi.python.org/pypi/GDAL
.. |GDAL| replace:: `Geospatial Data Abstraction Library (GDAL) <GDAL_>`_
.. _PyGeoTools: https://github.com/jfein/PyGeoTools
.. |PyGeoTools| replace:: `PyGeoTools <PyGeoTools_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_

Library of simple tools for simple geographical data (geolocations and geocoordinates)
handling and processin.

**Description**
    
The term *"(geo)location"* in geography is used to identify a point or an area on the 
Earth's surface or elsewhere. 

The classes/methods defined in this module help at performing various basic operations 
on locations, *e.g.* geographical system transformations and geospatial units 'conversions'.
It will also enable you to retrieve geolocation based on geographical coordinates/toponames
so as to represent equivalently and (almost...) uniquely locations.

**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`math`

*optional*:     :mod:`osgeo`, :mod:`numpy`, :mod:`multiprocessing`

*call*:         :mod:`settings`, :mod:`base`        

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Apr 14 20:23:34 2018

__all__         = ['GeoLocation', 'GeoDistance', 'GeoAngle', 'GeoCoordinate', 'GDALTool']

# generic import
import os, sys#analysis:ignore
import math

import functools#analysis:ignore

try:
    import numpy as np
except ImportError:
    pass

# local imports
from happygisco import settings
from happygisco.settings import happyVerbose, happyWarning, happyError
from happygisco.base import _Decorator, _Tool
 
try:                            
    import multiprocessing 
except ImportError:             
    MULTIPROCESSING=False 
    happyWarning('multiprocessing package (https://docs.python.org/3/library/multiprocessing.html) not loaded - Parallel processing not available')
    NCPUS = 1
else:              
    MULTIPROCESSING=True  
    NCPUS = multiprocessing.cpu_count()              

try:
    GDAL_TOOL = True
    from osgeo import ogr
except ImportError:
    GDAL_TOOL = False
    happyWarning('GDAL package (https://pypi.python.org/pypi/GDAL) not loaded - Inline resources not available')
else:
    print('GDAL help: https://pcjericks.github.io/py-gdalogr-cookbook/index.html')

#%%
#==============================================================================
# CLASS GeoLocation
#==============================================================================
 
## class GeoLocation:
# we get rid of the 'old-style' class to enable inheritance with 'super()' method
# so that issubclass(GeoLocation, object) is True
class GeoLocation(object):
    """Class used to represent coordinates on a sphere, most likely Earth, as suggested  
    in http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates.

    |       # This class is based from the code smaple in this paper:
    |       #     http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates        
    |       # The owner of that website, Jan Philip Matuschek, is the full owner of 
    |       # his intellectual property. This class is simply a Python port of his very
    |       # useful Java code. All code written by Jan Philip Matuschek and ported herein 
    |       # (which is all of this class) is owned by Jan Philip Matuschek.
    
    The class :class:`GeoLocation` extends the original :class:`GeoLocation` class 
    implemented in the |PyGeoTools| tools (see source code 
    `here <https://github.com/jfein/PyGeoTools/blob/master/geolocation.py>`_). This 
    class is simply a `Python` port of the original `Java` code by Jan Philip Matuschek.
    """
 
    MIN_LAT = math.radians(-90)
    MAX_LAT = math.radians(90)
    MIN_LON = math.radians(-180)
    MAX_LON = math.radians(180)
    
    ## EARTH_RADIUS = 6378.1  # kilometers
    # Equatorial radius 6378137 m 
    EARTH_RADIUS    = 6378.1370 # in km, for consistency with EARTH_RADIUS 
      
    #/************************************************************************/
    @classmethod
    def from_degrees(cls, deg_lat, deg_Lon):
        rad_lat = math.radians(deg_lat)
        rad_Lon = math.radians(deg_Lon)
        ## return GeoLocation(rad_lat, rad_Lon, deg_lat, deg_Lon)
        # to ensure inheritance
        return cls(rad_lat, rad_Lon, deg_lat, deg_Lon)
        
    #/************************************************************************/
    @classmethod
    def from_radians(cls, rad_lat, rad_Lon):
        deg_lat = math.degrees(rad_lat)
        deg_Lon = math.degrees(rad_Lon)
        ## return GeoLocation(rad_lat, rad_Lon, deg_lat, deg_Lon)
        return cls(rad_lat, rad_Lon, deg_lat, deg_Lon)
        
    #/************************************************************************/
    def __init__(self, rad_lat, rad_Lon, deg_lat, deg_Lon):
        # initialise an instance of GeoLocation
        self.rad_lat = float(rad_lat)
        self.rad_Lon = float(rad_Lon)
        self.deg_lat = float(deg_lat)
        self.deg_Lon = float(deg_Lon)
        self.__check_bounds()
        
    #/************************************************************************/
    def __check_bounds(self):
        if (self.rad_lat < GeoLocation.MIN_LAT 
                or self.rad_lat > GeoLocation.MAX_LAT 
                or self.rad_Lon < GeoLocation.MIN_LON 
                or self.rad_Lon > GeoLocation.MAX_LON):
            raise happyError("Illegal arguments")
        
    #/************************************************************************/
    def __str__(self):
        ## degree_sign= u'\N{DEGREE SIGN}'
        return ("(lat,Lon) : ({0:.5f}, {1:.5f}) deg = ({2:.6f}, {3:.6f}) rad").format(
            self.deg_lat, self.deg_Lon, self.rad_lat, self.rad_Lon)
            
    #/************************************************************************/
    def distance_to(self, other, radius=EARTH_RADIUS):
        # compute the great circle distance between this GeoLocation instance and 
        # the "other".
        # returns the distance from the geolocation represented by the current 
        # instance to other geolocation
        if not isinstance(other,GeoLocation):
            raise happyError('distance must be computed to another instance of the GeoLocation class')
        return radius * math.acos(
                math.sin(self.rad_lat) * math.sin(other.rad_lat) +
                math.cos(self.rad_lat) * 
                math.cos(other.rad_lat) * 
                math.cos(self.rad_Lon - other.rad_Lon)
            )
            
    #/************************************************************************/
    def bounding_locations(self, distance, radius=EARTH_RADIUS):
        # compute the bounding coordinates of all points on the surface of a 
        # sphere that has a great circle distance to the point represented by this 
        # GeoLocation` instance that is less or equal to the distance argument
        # returns a list of two geolocations - the SW corner and the NE corner - that
        # represents the bounding box defined by the distance :literal:`dist`
        if radius < 0 or distance < 0:
            raise happyError('illegal arguments')
        # angular distance in radians on a great circle
        rad_dist = distance / radius
        min_lat = self.rad_lat - rad_dist
        max_lat = self.rad_lat + rad_dist
        if min_lat > GeoLocation.MIN_LAT and max_lat < GeoLocation.MAX_LAT:
            delta_Lon = math.asin(math.sin(rad_dist) / math.cos(self.rad_lat))
            
            min_Lon = self.rad_Lon - delta_Lon
            if min_Lon < GeoLocation.MIN_LON:
                min_Lon += 2 * math.pi
                
            max_Lon = self.rad_Lon + delta_Lon
            if max_Lon > GeoLocation.MAX_LON:
                max_Lon -= 2 * math.pi
        # a pole is within the distance
        else:
            min_lat = max(min_lat, GeoLocation.MIN_LAT)
            max_lat = min(max_lat, GeoLocation.MAX_LAT)
            min_Lon = GeoLocation.MIN_LON
            max_Lon = GeoLocation.MAX_LON
        
        return [ getattr(self.__class__,'from_radians')(min_lat, min_Lon), 
                getattr(self.__class__,'from_radians')(max_lat, max_Lon) ]

#%%
#==============================================================================
# CLASS GeoDistance
#==============================================================================

class GeoDistance(object):
    """Class used for (geodesic) distance representation and calculation.
 
    Attributes
    ----------     
    EARTH_RADIUS_EQUATOR : 
        Equatorial radius: **6378.1370 km**.
    EARTH_RADIUS_POLAR : 
        Polar radius: **6356.7523 km**.
    WGS84_SEMIAXIS_a :         
        major semi-axis of WGS-84 geoidal  reference equal to :data:`EARTH_RADIUS_EQUATOR`.
    WGS84_SEMIAXIS_b :
        ibid, minor semi-axis equal to :data:`EARTH_RADIUS_POLAR`.
    EARTH_RADIUS_MEAN :          
        mean radius defined by the `IUGG <http://www.iugg.org>`_, set to 
        :data:`(2*WGS84_SEMIAXIS_a + WGS84_SEMIAXIS_b)/3`, equal to **6371.0087 km**.
    EARTH_RADIUS_AVERAGE :          
        average radius: **6372.7950 km**.
    DECIMAL_PRECISION : 
        integer defining the precision in location coordinates: **5**.        
    M_TO :
        dictionary of equivalent distances expressed in :literal:`['m', 'km', 'mi', 'ft']` 
        units that are equivalent to **1 m**.
    KM_TO,MI_TO,FT_TO :
        ibid for **1 km**, **1 mi** (mile) and **1 ft** (foot) respectively.
    """
        
    #/************************************************************************/
    # Earth radius: http://en.wikipedia.org/wiki/Earth_radius
    # EARTH_RADIUS defined in ExtGeoLocation
    # distances from points on the surface to the center range from 6,353 km 
    # to 6,384 km 
    # Equatorial radius 6378137 m 
    EARTH_RADIUS_EQUATOR    = GeoLocation.EARTH_RADIUS # 6378.1370 km 
    # Polar radius 6356752.3 m
    EARTH_RADIUS_POLAR      = 6356.7523 
    # Semi-axes of WGS-84 geoidal reference
    WGS84_SEMIAXIS_a        = EARTH_RADIUS_EQUATOR  # Major semiaxis 
    WGS84_SEMIAXIS_b        = EARTH_RADIUS_POLAR  # Minor semiaxis
    # Mean radius defined by IUGG
    EARTH_RADIUS_MEAN       = (2*WGS84_SEMIAXIS_a + WGS84_SEMIAXIS_b)/3. # 6371008.766 m
    # Average radius: 6372795 m 
    EARTH_RADIUS_AVERAGE    = 6372.7950 # geodist.EARTH_RADIUS

    #/************************************************************************/
    # units and measures
    M_DIST_UNIT, KM_DIST_UNIT, MI_DIST_UNIT, FT_DIST_UNIT = 'm', 'km', 'mi', 'ft'
    DIST_UNITS          = {KM_DIST_UNIT:'kilometers',
                           MI_DIST_UNIT: 'miles',
                           M_DIST_UNIT: 'meters',
                           FT_DIST_UNIT: 'feet'} 
    KM_TO    = {M_DIST_UNIT: 1000,    KM_DIST_UNIT: 1.,        MI_DIST_UNIT: 0.621371,    FT_DIST_UNIT:3280.84}
    M_TO     = {M_DIST_UNIT: 1.,      KM_DIST_UNIT: 0.001,     MI_DIST_UNIT: 0.000621371, FT_DIST_UNIT:3.28084}
    MI_TO    = {M_DIST_UNIT: 1609.34, KM_DIST_UNIT: 1.60934,   MI_DIST_UNIT: 1.,          FT_DIST_UNIT:5280.}
    FT_TO    = {M_DIST_UNIT: 0.3048,  KM_DIST_UNIT: 0.0003048, MI_DIST_UNIT:0.000189394,  FT_DIST_UNIT:1.}

    RESOLUTION          = {'unit': KM_DIST_UNIT, 'value': 0.001}
    # RESOLUTION      = 0.001 # we mean 1 meter

    #/************************************************************************/
    @classmethod
    def units_to(cls, from_, to_, dist=1.):            
        """Perform simple distance units conversion.
        
        ::
        
            >>> d = GeoDistance.units_to(from_, to_, dist)

        Arguments
        ---------
        from_,to_ : str
            'origin' and 'destination' units: any strings from the list 
            :literal:`['m','km','mi','ft']`.
        dist : float
            distance value to convert; default to 1.

        Example
        -------
        
        ::
            
            >>> GeoDistance.units_to('mi', 'ft',  10.)
                52800.0
        """
        # if from_==to:     return dist
        # simple variable used in distance conversions
        UNITS_TO =  {cls.M_DIST_UNIT: cls.M_TO,     
                     cls.KM_DIST_UNIT: cls.KM_TO, 
                     cls.MI_DIST_UNIT: cls.MI_TO,   
                     cls.FT_DIST_UNIT: cls.FT_TO}
        return UNITS_TO[from_][to_] * dist            

    #/************************************************************************/
    @classmethod
    def convert_distance_units(cls, to_=None, **kwargs):
        """Convert composed distance units to a single one.
        
        ::
        
            >>> d = GeoDistance.convert_distance_units(to_='km', **kwargs)

        Arguments
        ---------
        to_ : str
            desired 'destination' unit: any string in the list :literal:`['m','km','mi','ft']`; 
            default to :literal:`'km'`\ .
        
        Keyword Arguments
        -----------------
        kwargs : dict
            dictionary of composed distances indexed by their unit, which can be
            any string in the list :literal:`['m','km','mi','ft']`.
            
        Raises
        ------
        ~settings.happyError
            when unable to recognize any of the distance units in :data:`kwargs`.

        Examples
        --------
        Use indifferently dictionaries or positional arguments to pass the quantities 
        to convert:  
        
        ::
        
            >>> GeoDistance.convert_distance_units('m', **{'km':1, 'm':10}) 
                1010
            >>> GeoDistance.convert_distance_units(to_='m', mi=2,  ft=10, km=0.5)
                3721.7279999999996
            >>> 2*GeoDistance.MI_TO['m'] + 10.*GeoDistance.FT_TO['m'] + 0.5*GeoDistance.KM_TO['m']
                3721.7279999999996
        """
        if to_ is None:
            to_ = cls.KM_DIST_UNIT
        elif not to_ in cls.DIST_UNITS.keys():
            raise happyError('unit {} not implemented'.format(to_))
        dist = 0.
        for u in cls.DIST_UNITS.keys():
            if u in kwargs: dist += cls.units_to(u, to_, kwargs.get(u))
        return dist

    #/************************************************************************/
    @classmethod
    def estimate_radius_WGS84(cls, lat, **kwargs):
        """Calculate the Earth radius at a given latitude, according to the WGS-84 
        ellipsoid [m].
        
        ::
        
            >>> R = GeoDistance.estimate_radius_WGS84(lat, **kwargs)
            
        Raises
        ------
        ~settings.happyError 
            when unable to recognize the distance unit.
            
        Example
        -------
        The Earth radius at Paris, France latitude is approximately:
        
        ::
            
            >>> GeoDistance.estimate_radius_WGS84(48.864716)
                6357.369614537118
        """
        a = cls.WGS84_SEMIAXIS_a  # major semiaxis
        b = cls.WGS84_SEMIAXIS_b  # minor semiaxis 
        An, Bn = a*a * math.cos(lat), b*b * math.sin(lat)
        Ad, Bd = a * math.cos(lat), b * math.sin(lat)
        res = math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )            
        unit = kwargs.pop('unit', cls.KM_DIST_UNIT)
        try:    return res * cls.KM_TO[unit]
        except: raise happyError('unit {} not implemented'.format(unit))

#%%
#==============================================================================
# CLASS GeoAngle
#==============================================================================

class GeoAngle(object):
    """
    """

    #/************************************************************************/
    # units and measures
    DEG_ANG_UNIT, RAD_ANG_UNIT, DPS_ANG_UNIT = 'deg', 'rad', 'dps'
    ANG_UNITS           = {DEG_ANG_UNIT: 'degrees',
                           RAD_ANG_UNIT: 'radians',
                           DPS_ANG_UNIT: 'degrees/primes/seconds'} 
    DECIMAL_PRECISION   = 5
        
    #/************************************************************************/
    @classmethod
    def dps2deg(cls, dps):
        """Convert (degrees, primes, seconds) format to degrees.
        
        ::
        
            >>> degrees = GeoAngle.dps2deg(dps)
            
        Example
        -------
        Paris, France latitude in DPS format is: 48° 51' 52.9776'' N. Let us convert 
        it to degrees:
        
        ::
        
            >>> GeoAngle.dps2deg([48, 51, 52.9776])
                48.864716
            
        See also
        --------
        :meth:`~GeoAngle.deg2dps`, :meth:`~GeoAngle.dps2rad`.
        """
        degrees, primes, seconds = dps
        return degrees + primes/60.0 + seconds/3600.0    

    #/************************************************************************/
    @classmethod
    def deg2dps(cls, degrees): 
        """Convert degrees format to (degrees, primes, seconds).
        
        ::
        
            >>> dps = GeoAngle.deg2dps(degrees)
            
        Example
        -------
        Let us convert Paris, France latitude (48.864716 degrees) into DPS format:
        
        
        ::
            
            >>> GeoAngle.deg2dps(48.864716) 
                (48, 51, 52.9776)
            
        See also
        --------
        :meth:`~GeoAngle.dps2deg`, :meth:`~GeoAngle.deg2rad`.
        """
        intdeg = math.floor(degrees)
        primes = (degrees - intdeg)*60.0
        intpri = math.floor(primes)
        seconds = (primes - intpri)*60.0
        seconds = round(seconds, cls.DECIMAL_PRECISION)
        return (int(intdeg), int(intpri), seconds)
 
    #/************************************************************************/
    @classmethod
    def deg2rad(cls, degrees): 
        """Convert degrees format to radians.
        
        ::
        
            >>> radians = GeoAngle.deg2rad(degrees)
            
        Example
        -------
        
        ::
            
            >>> import math
            >>> GeoAngle.deg2rad(90) == math.pi/2
                True
            
        See also
        --------
        :meth:`~GeoAngle.rad2deg`, :meth:`~GeoAngle.deg2dps`.
        """
        return math.radians(degrees) # math.pi*degrees/180.0   

    #/************************************************************************/
    @classmethod
    def rad2deg(cls, radians): 
        """Convert radians format to degrees.
        
        ::
        
            >>> degrees = GeoAngle.rad2deg(radians)
            
        Example
        -------
        
        ::

            >>> import math
            >>> GeoAngle.rad2deg(math.pi) == 180
                True
            
        See also
        --------
        :meth:`~GeoAngle.deg2rad`, :meth:`~GeoAngle.rad2dps`.
        """
        return math.degrees(radians) # 180.0*radians/math.pi    

    #/************************************************************************/
    @classmethod
    def dps2rad(cls, dps):  
        """Convert (degrees, primes, seconds) format to radians.
        
        ::
        
            >>> radians = GeoAngle.dps2rad(dps)
            
        Examples
        --------
        
        ::
        
            >>> import math
            >>> GeoAngle.dps2rad([45,0,0]) == math.pi/4
                True
            >>> GeoAngle.dps2rad([48, 51, 52.9776])
                0.8528501822519535
                
        Note
        ----
        Compose the methods :meth:`~GeoAngle.dps2deg` and :meth:`~GeoAngle.deg2rad`.
            
        See also
        --------
        :meth:`~GeoAngle.rad2dps`, :meth:`~GeoAngle.dps2deg`.
        """
        return cls.deg2rad(cls.dps2deg(dps))

    #/************************************************************************/
    @classmethod
    def rad2dps(cls, rad):  
        """Convert radians format to (degrees, primes, seconds).
        
        ::
        
            >>> dps = GeoAngle.rad2dps(radians)
            
        Example
        -------
        
        ::
            
            >>> import math
            >>> GeoAngle.rad2dps(math.pi)
                (180, 0, 0.0)
            >>> GeoAngle.rad2dps(GeoAngle.dps2rad([48, 51, 52.9776])) == (48, 51, 52.9776)
                True
                
        Note
        ----
        Compose the methods :meth:`~GeoAngle.rad2deg` and :meth:`~GeoAngle.deg2dps`.
        
        See also
        --------
        :meth:`~GeoAngle.dps2rad`, :meth:`~GeoAngle.rad2deg`.
        """
        return cls.deg2dps(cls.rad2deg(rad))

    #/********************************************************************/
    @classmethod
    def ang_units_to(cls, from_, to_, ang=0.):            
        """Perform simple angular units conversion.
        
        ::
        
            >>> u = GeoAngle.ang_units_to(from_, to_, ang=0.)

        Arguments
        ---------
        from_,to_ : str
            'origin' and 'destination' units: any strings in :literal:`['deg','rad','dps']`.
        ang : float
            angle value to convert; default to 0.
            
        Example
        -------
        Here is another way to convert Paris, France latitude (48.864716 degrees) 
        into DPS format:
        
        ::
        
            >>> GeoAngle.ang_units_to('deg','dps',48.864716)
                (48, 51, 52.9776)
            
        Note
        ----
        This is just a single method wrapping all angle conversion methods.
            
        See also
        --------
        :meth:`~GeoAngle.dps2deg`, :meth:`~GeoAngle.dps2rad`, :meth:`~GeoAngle.deg2rad`, 
        :meth:`~GeoAngle.deg2dps`, :meth:`~GeoAngle.rad2deg`, :meth:`~GeoAngle.rad2dps`.
        """
        # if from_==to:     return ang
        deg_to = {cls.RAD_ANG_UNIT: cls.deg2rad, 
                  cls.DEG_ANG_UNIT: lambda x:x,   
                  cls.DPS_ANG_UNIT: cls.deg2dps}
        rad_to = {cls.RAD_ANG_UNIT: lambda x:x,  
                  cls.DEG_ANG_UNIT: cls.rad2deg,  
                  cls.DPS_ANG_UNIT: cls.rad2dps}
        dps_to = {cls.RAD_ANG_UNIT: cls.dps2rad,  
                  cls.DEG_ANG_UNIT: cls.dps2deg, 
                  cls.DPS_ANG_UNIT: lambda x:x}
        return {cls.RAD_ANG_UNIT: rad_to, cls.DEG_ANG_UNIT: deg_to, cls.DPS_ANG_UNIT: dps_to}[from_][to_](ang)       

    #/************************************************************************/
    @classmethod
    def convert_angle_units(cls, to_=None, **kwargs):
        """Convert composed angular units to a single one.
        
        ::
        
            >>> u = GeoAngle.convert_angle_units(to_='deg', **kwargs)

        Arguments
        ---------
        to_ : str
            desired 'final' unit: any string in :literal:`['deg','rad','dps']`; default
            to :literal:`'deg'`.
        
        Keyword Arguments
        -----------------
        kwargs : dict
            dictionary of composed angles indexed by their unit, which can be, again,
            any string in :literal:`['deg','rad','dps']`.
            
        Raises
        ------
        ~settings.happyError 
            when unable to recognize the distance unit :data:`to_`.
            
        Note
        ----
        This is very unlikely that one will use a composition of angular units.
        """
        if to_ is None:
            to_ = cls.DEG_ANG_UNIT
        elif not to_ in cls.ANG_UNITS.keys():
            raise happyError('unit {} not implemented'.format(to_))
        if to_==cls.DPS_ANG_UNIT: # we will convert first the different values in degrees
            dps = True
            to_ = cls.DEG_ANG_UNIT
        else:
            dps = False
        ang = 0.
        for u in cls.ANG_UNITS.keys():
            if u in kwargs: ang += cls.ang_units_to(u, to_, kwargs.get(u)) # from_=u, to_=to_
        if dps is True: # we convert back the sum in dps
            ang = cls.ang_units_to(cls.DEG_ANG_UNIT, cls.DPS_ANG_UNIT, ang)
        return ang
        
    #/************************************************************************/
    @classmethod
    def latdeg2m(cls, dlat, alat):
        """Convert latitude difference in degrees into meters at given average
        latitude.
        
        ::
        
            >>> dy = GeoCoordinate.latdeg2m(dlat, alat)

        Arguments
        ---------
        dlat : float
            latitude difference in degrees.
        alat : float
            average latitude at which the distance is calculated (between the two 
            fixes).
            
        Returns
        -------
        dy : float
            latitude difference in meters.
            
        Example
        -------
        
        What do 0.1 degree latitude difference at the latitude of Bee (VB), Italia,
        correspond to in meters? Approximately 11.11km!
        
        ::
            
            >>> GeoCoordinate.latdeg2m(0.1, 45.9611)
                11114.987939044277
                
        References
        ----------
        * Wikipedia `latitude page <https://en.wikipedia.org/wiki/Latitude>`_.
        * `Calculation of distance represented by degrees of Latitude and Longitude <https://www.colorado.edu/geography/gcraft/warmup/aquifer/html/distance.html>`_.
        * `Finding distances based on Latitude and Longitude <https://andrew.hedges.name/experiments/haversine/>`_.
        * `Calculate distance between two latitude-longitude points? (Haversine formula) <https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula>`_.
        * `Jcoord <http://www.jstott.me.uk/jcoord/>_` conversion tool between latitude/longitude.

        See also
        --------
        :meth:`~GeoCoordinate.latm2deg`, :meth:`~GeoCoordinate.londeg2m`,
        :meth:`~GeoCoordinate.distance_to_from`.
        """
        rlat = GeoAngle.deg2rad(alat) 
        p = 111132.09 - 566.05 * math.cos(2 * rlat) + 1.2 * math.cos(4 * rlat)
        return dlat * p        

    #/************************************************************************/
    @classmethod
    def londeg2m(cls, dlon, alat):
        """Convert longitude difference in degrees into meters at given average
        latitude.
        
        ::
        
            >>> dx = GeoCoordinate.londeg2m(dLon, alat)

        Arguments
        ---------
        dLon : float
            longitude difference in degrees.
        alat : float
            average latitude at which the distance is calculated (between the two 
            fixes).
            
        Returns
        -------
        dx : float
            longitude difference in meters.
            
        Example
        -------
        
        What do 0.1 degree longitude difference at the latitude of Bee (VB), Italia,
        correspond to in meters? Approximately 7.75km!
        
        ::
            
            >>> GeoCoordinate.londeg2m(0.1, 45.9611)
                7751.998346588658
                
        References
        ----------
        * Wikipedia `longitude page <https://en.wikipedia.org/wiki/Longitude>_`.
        * `Calculation of distance represented by degrees of Latitude and Longitude <https://www.colorado.edu/geography/gcraft/warmup/aquifer/html/distance.html>`_.
        * `Finding distances based on Latitude and Longitude <https://andrew.hedges.name/experiments/haversine/>`_.
        * `Calculate distance between two latitude-longitude points? (Haversine formula) <https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula>`_.
        * `Jcoord <http://www.jstott.me.uk/jcoord/>_` conversion tool between latitude/longitude.
            
        See also
        --------
        :meth:`~GeoCoordinate.lonm2deg`, :meth:`~GeoCoordinate.latdeg2m`,
        :meth:`~GeoCoordinate.distance_to_from`.
        """
        rlat = GeoAngle.deg2rad(alat) 
        p = 111415.13 * math.cos(rlat) - 94.55 * math.cos(3 * rlat)
        return dlon * p

    #/************************************************************************/
    @classmethod
    def latm2deg(cls, dy, alat):
        """Convert latitude difference in meters into degrees at given average
        latitude.
        
        ::
        
            >>> dlat = GeoCoordinate.latm2deg(dy, alat)

        Arguments
        ---------
        dy : float
            latitude difference in meters.
        alat : float
            average latitude at which the distance is calculated (between the two 
            fixes).
            
        Returns
        -------
        dlat : float
            latitude difference in degrees.
            
        Example
        -------
        
        What do 100km latitude difference at the latitude of Bee (VB), Italia,
        correspond to in degrees? Approximately 0.9 degrees!
        
        ::
            
            >>> GeoCoordinate.latm2deg(100000, 45.9611)
                0.8996860864664017
                
        References
        ----------
        See references in :meth:`~GeoCoordinate.latdeg2m`.
        
        See also
        --------
        :meth:`~GeoCoordinate.latdeg2m`, :meth:`~GeoCoordinate.lonm2deg`,
        :meth:`~GeoCoordinate.distance_to_from`.
        """
        rlat = GeoAngle.deg2rad(alat) 
        p = 111132.09 - 566.05 * math.cos(2 * rlat) + 1.2 * math.cos(4 * rlat)
        return dy / p        

    #/************************************************************************/
    @classmethod
    def lonm2deg(cls, dx, alat):
        """Convert longitude difference in degrees into meters at given average
        latitude.
        
        ::
        
            >>> dLon = GeoCoordinate.lonm2deg(dx, alat)

        Arguments
        ---------
        dx : float
            longitude difference in meters.
        alat : float
            average latitude at which the distance is calculated (between the two 
            fixes).
            
        Returns
        -------
        dLon : float
            longitude difference in degrees.
            
        Example
        -------
        
        What do 100km longitude difference at the latitude of Bee (VB), Italia,
        correspond to in degrees? Approximately 1.29 degrees!
        
        ::
            
            >>> GeoCoordinate.lonm2deg(100000, 45.9611)
                1.2899899552223972
                
        References
        ----------
        See references in :meth:`~GeoCoordinate.londeg2m`.
            
        See also
        --------
        :meth:`~GeoCoordinate.londeg2m`, :meth:`~GeoCoordinate.latm2deg`,
        :meth:`~GeoCoordinate.distance_to_from`.
        """
        rlat = GeoAngle.deg2rad(alat) 
        p = 111415.13 * math.cos(rlat) - 94.55 * math.cos(3 * rlat)
        return dx / p

#%%
#==============================================================================
# CLASS GeoCoordinate
#==============================================================================

class GeoCoordinate(GeoLocation):
    """Class of geographic/location attributes and methods used to define, describe 
    and represent the geospatial status of an object.
    
    This class emulates :class:`~tools.GeoLocation`.
    It inherits, for instance, the methods :meth:`_check_bounds` from the original 
    class that aim at checking for :literal:`(lat, Lon)` coordinates consistency; 
    instead, methods :meth:`distance_to` (computation of great circle distance 
    between geolocations) and :meth:`bounding_locations` (computation of the 
    bounding coordinates of all points) are overriden.
        
    ::
 
        >>> coord = GeoCoordinate(*args, **kwargs)
            
    Arguments
    ---------
    args : tuple[float]
        arguments in :data:`args` define uniquely an instance of this class; it
        can be either:     
            * a pair of :literal:`(lat,Lon)` expressed in radians,
            * a pair of :literal:`(lat,Lon)` expressed in degrees,
            * a pair of :literal:`(lat,Lon)` expressed in DPS format 
              (degrees, primes, seconds),
            * a 4-tuple of :literal:`(lat,Lon)` expressed both in radians and degrees 
              (in this order).

    Keyword arguments
    -----------------
    unit_angle : str
        name of the unit used for the definition of the angles parsed through 
        :data:`args`; default is :data:`GeoAngle.DEG_ANG_UNIT`, *i.e.* 'deg'.

    Attributes
    ----------     
    MIN_LATITUDE : 
        dummy min latitude value in degree: -90.
    MAX_LATITUDE : 
        ibid for max latitude: 90.
    MIN_LONGITUDE : 
        dummy min longitude value in degree: -180. 
    MAX_LONGITUDE : 
        ibid for max longitude: 180. 
    """

    #/************************************************************************/
    # dummy...
    MIN_LATITUDE, MAX_LATITUDE = -90., 90.
    MIN_LONGITUDE, MAX_LONGITUDE = -180., 180. 
    # or shall we consider over Europe only?

    DIST_FUNCS = {'great_circle':'GreatCircleDistance',
                 'vincenty': 'VincentyDistance'} # names used in geopy

    DECIMAL_PRECISION   = 5 #10
    
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        deg = [None, None] 
        dps = [None, None]
        if args in((),(None,)):
            return
        elif len(args)==2:
            unit = kwargs.pop('unit_angle', GeoAngle.DEG_ANG_UNIT)
            for i in range(2): # convert to degrees whatever the input is
                try:    
                    dps[i] = GeoAngle.convert_angle_units(GeoAngle.DPS_ANG_UNIT, **{unit: args[i]})
                    deg[i] = GeoAngle.convert_angle_units(GeoAngle.DEG_ANG_UNIT, **{unit: args[i]})
                except: raise happyError('unit {} not implemented'.format(unit))
            if unit==GeoAngle.RAD_ANG_UNIT:
                rad = list(args)
            else:
                rad = [GeoAngle.deg2rad(l) for l in deg]
            args = rad + deg
        elif len(args)!=4:
            raise happyError('wrong number of input arguments')
        super(GeoCoordinate,self).__init__(*args)
        self.dps_lat, self.dps_Lon = dps

    #/************************************************************************/
    @classmethod 
    def from_radians(cls, rad_lat, rad_Lon):
        """Return a geolocation instance from :literal:`(lat,Lon)` coordinates 
        expressed in degrees.
        
        ::
        
            >>> coord = GeoCoordinate.from_radians(rad_lat, rad_Lon)
         
        Arguments
        ---------        
        rad_lat,rad_Lon : tuple
            latitude and longitude (respectively) expressed in radians.

        Returns
        -------
        coord : :class:`~tools.GeoCoordinate`
            a :class:`GeoCoordinate` instance from the input :literal:`(lat,Lon)` 
            coordinates :data:`(rad_lat,rad_Lon)`.
            
        Example
        -------
        
        ::
            >>> import math 
            >>> loc = GeoCoordinate.from_radians(math.pi/4,math.pi/2)
            >>> isinstance(loc, GeoCoordinate)
                True
            >>> loc.rad_Lon == math.pi/2
                True
            >>> loc.deg_lat == 45
                True
            >>> loc.dps_Lon == (90, 0, 0.0)
                True

        See also
        --------
        :meth:`from_dps`, :meth:`from_degrees`\ .        
        """
        return cls(rad_lat, rad_Lon, unit_angle=GeoAngle.RAD_ANG_UNIT)
    
    #/************************************************************************/
    @classmethod 
    def from_degrees(cls, deg_lat, deg_Lon):
        """Return a geolocation instance from :literal:`(lat,Lon)` coordinates 
        expressed in degrees.
        
        ::
        
            >>> coord = GeoCoordinate.from_degrees(deg_lat, deg_Lon)
         
        Arguments
        ---------        
        deg_lat,deg_Lon : tuple
            latitude and longitude (respectively) expressed in degrees.

        Returns
        -------
        coord : :class:`~happygisco.tools.GeoCoordinate`
            a :class:`GeoCoordinate` instance from the input :literal:`(lat,Lon)` 
            coordinates :data:`(deg_lat,deg_Lon)`.
            
        Example
        -------
        
        ::
            >>> import math 
            >>> loc = GeoCoordinate.from_degrees(45,90)
            >>> isinstance(loc, GeoCoordinate)
                True
            >>> loc.rad_Lon == math.pi/2
                True
            >>> loc.dps_lat == (45, 0, 0.0)
                True
            >>> loc.dps_Lon == (90, 0, 0.0)
                True

        Let us create the geolocation associated of Bee (VB), Italia from its
        actual coordinates:
            
            >>> bee = GeoCoordinate.from_degrees(45.9611, 8.5809)
            >>> print(bee)
                (lat,Lon) : (45.96110, 8.58090) deg 
                    = (0.802173, 0.149765) rad 
                    = ((45, 57, 39.96), (8, 34, 51.24)) dps
 
        See also
        --------
        :meth:`from_dps`, :meth:`from_radians`\ .         
        """
        return cls(deg_lat, deg_Lon, unit_angle=GeoAngle.DEG_ANG_UNIT)
   
    #/************************************************************************/
    @classmethod 
    def from_dps(cls, dps_lat, dps_Lon): # new generator
        """Return a geolocation instance from :literal:`(lat,Lon)` coordinates 
        expressed in DPS format.
        
        ::
        
            >>> coord = GeoCoordinate.from_dps(dps_lat, dps_Lon)
         
        Arguments
        ---------        
        dps_lat,dps_Lon : tuple
            latitude and longitude (respectively) expressed in DPS format: 
            (degrees, primes, seconds).

        Returns
        -------
        coord : :class:`~happygisco.tools.GeoCoordinate`
            a :class:`GeoCoordinate` instance from the input :literal:`(lat,Lon)` 
            coordinates :data:`(dps_lat,dps_Lon)`.
            
        Example
        -------
        
        ::
            >>> import math 
            >>> loc = GeoCoordinate.from_dps((45, 0, 0.0),(90, 0, 0.0))
            >>> isinstance(loc, GeoCoordinate)
                True
            >>> loc.rad_Lon == math.pi/2
                True
            >>> loc.deg_lat == 45
                True
            >>> loc.deg_Lon == 90
                True

        See also
        --------
        :meth:`from_degrees`, :meth:`from_radians`\ .         
        """
        ## deg_lat = cls.dps2deg(dps_lat)
        ## deg_Lon = cls.dps2deg(dps_Lon)
        ## return cls(deg_lat, deg_Lon, unit_angle=GeoAngle.DEG_ANG_UNIT)
        return cls(dps_lat, dps_Lon, unit_angle=GeoAngle.DPS_ANG_UNIT)
 
    #/************************************************************************/
    @property
    def coordinates(self):
        """:literal:`(lat,Lon)` geographic coordinates (in degrees) property 
        (:data:`getter`) of a :class:`GeoCoordinate` instance.
        """ 
        return [self.deg_lat, self.deg_Lon]
        
    #/************************************************************************/
    def __str__(self):
        # string printing method.
        try:
            return super(GeoCoordinate,self).__str__()  \
                + " = ({0}, {1}) dps".format(self.dps_lat, self.dps_Lon)
        except:
            return ''
    
    #/************************************************************************/
    # inherits:
    #   - _check_bounds: check lat,long coordinates
    #   - distance_to: compute the great circle distance between geolocations
    #   - bounding_locations: compute the bounding coordinates of all points
    #/************************************************************************/

    #/************************************************************************/
    def bounding_locations(self, distance, **kwargs):
        """Method overriding super method from :class:`~tools.GeoLocation`  
        for computing bounding coordinates of all points on the surface of a sphere 
        that have a great circle distance to the point represented by this 
        :class:GeoCoordinate` instance that is less or equal to the distance argument.
        
        ::
        
            >>> bbox = coord.bounding_locations(dist, **kwargs)

        Arguments
        ---------
        dist : float
            distance to the location; it must be set in the unit defined by :data:`'unit'`
            (see below).
            
        Keyword Arguments
        -----------------
        unit : str
            distance measurement unit, *i.e.* distance unit of the input :data:`distance` 
            parameter; it can be any string from the list :literal:`['m','km','mi','ft']`; 
            default is :literal:`'km'`.
        radius : float
            the radius of the sphere; must be measured in the same unit as the 
            :data:`dist` parameter; defaults to Earth radius :data:`GeoDistance.EARTH_RADIUS_EQUATOR`.
            
        Returns
        -------
        bbox : list
            a pair of :literal:`(lat,Lon)` geographic coordinates (in degrees) 
            that represent the SW corner and the NE corner (in this order) of a 
            bounding box; this INcircle of this bounding box contains all the 
            points that have a great circle distance to the point represented by 
            the input geolocation which is less or equal to the :data:`dist` 
            parameter.
            
        Example
        -------
        
        Let us define a boundinx box of 10km (in each direction) around Paris 
        city centre:
            
        ::
            
            >>> paris = GeoCoordinate(48.85693, 2.3412)
            >>> bbox = paris.bounding_locations(10)
            >>> SW, NE = bbox
            >>> print(SW)
                [48.76709847158804, 2.2046657132894265]
            >>> print(NE)
                [48.946761528411955, 2.477734286710574]
            
        Note
        ----
        Only the points in the INcircle inscribed in the bounding box are actually
        at a distance lower than :data:`radius` from the geolocation :data:`coord`.
        In particular, the SW and NE corners are approximately at a distance 
        sqrt(2 * :data:`radius` **2) from the geolocation.
        
        See also
        --------
        :meth:`GeoLocation.bounding_locations`, :meth:`~GeoCoordinate.bounding_locations_from`.
        """
        # distance must be in the unit defined by 'unit'
        radius = kwargs.pop('radius', GeoDistance.EARTH_RADIUS_EQUATOR) # self.EARTH_RADIUS
        unit = kwargs.pop('unit', GeoDistance.KM_DIST_UNIT)
        try:    radius = radius * GeoDistance.KM_TO[unit] 
        except: raise happyError('unit {} not implemented'.format(unit))
        # the result will depend on the unit defined by distance (in unit)
        bbox = super(GeoCoordinate,self).bounding_locations(distance, radius=radius)
        return [bbox[0].coordinates, bbox[1].coordinates] 
        
    #/************************************************************************/
    @classmethod
    def bounding_locations_from(cls, loc, distance, **kwargs):
        """Compute bounding coordinates of all points on the surface of a sphere 
        that have a great circle distance to a given point that is less or equal 
        to the distance argument. 
        
        ::
        
            >>> bbox = GeoCoordinate.bounding_locations_from(loc, distance, **kwargs)
    
        Arguments
        ---------
        loc : list/tuple
            a tuple of lenght 2 defining the :literal:`(lat,Lon)` coordinates of 
            a location; it must be set in the unit defined by :data:`unit_angle`
            (see below).
        distance : float
            in between-locations distance, see :meth:`bounding_locations`.
            
        Keyword Arguments
        -----------------
        unit_angle : str
            angle measurement unit, *i.e.* unit of the input :data:`loc` parameter; 
            it can be any string in :literal:`['deg','rad','dps']`; default is 
            :literal:`'deg'`.                
        unit, radius : 
            see :meth:`~GeoLocation.bounding_locations`.
            
        Note
        ----
        Generalise the :meth:`GeoCoordinate.bounding_locations` method.
            
        Example
        -------
        
        Note that can pass indifferently a :class:`GeoCoordinate` instances or a 
        list of :literal:`(lat,Lon)` geographical coordinates:
        
        ::
            
            >>> paris = GeoCoordinate(48.85693, 2.3412)
            >>> bbox = GeoCoordinate.bounding_locations_from(paris,1)
            >>> print(bbox)
                [[48.8479468471588, 2.327546578583882],
                 [48.865913152841195, 2.3548534214161183]]
            >>> bbox_ = GeoCoordinate.bounding_locations_from(paris.coordinates,1)
            >>> print(bbox_)
                [[48.8479468471588, 2.327546578583882],
                 [48.865913152841195, 2.3548534214161183]]
            
        See also
        --------
        :meth:`~GeoCoordinate.bounding_locations`, :meth:`GeoLocation.bounding_locations`.
        """
        # ang_unit is both the unit of input and output locations
        ang_unit = kwargs.pop('unit_angle',GeoAngle.DEG_ANG_UNIT) 
        if not ang_unit in [GeoAngle.DEG_ANG_UNIT, GeoAngle.RAD_ANG_UNIT, GeoAngle.DPS_ANG_UNIT]:
            raise happyError('unit angle {} not implemented'.format(ang_unit))
        if isinstance(loc,GeoCoordinate):
            geoloc = loc
        else:
            # dist_unit = kwargs.pop('unit', cls.KM_DIST_UNIT)
            if ang_unit==GeoAngle.DEG_ANG_UNIT:          geoloc = cls.from_degrees(*loc)
            elif ang_unit==GeoAngle.RAD_ANG_UNIT:        geoloc = cls.from_radians(*loc)
            elif ang_unit==GeoAngle.DPS_ANG_UNIT:        geoloc = cls.from_dps(*loc)
            #radius = kwargs.pop('earth_radius', None)
        radius = kwargs.pop('radius', GeoDistance.EARTH_RADIUS_EQUATOR) # GeoDistance.EARTH_RADIUS
        #if radius is None:
        #    radius = GeoDistance.estimate_radius_WGS84(geoloc.deg_lat)
        kwargs.update({'radius': radius})
        bb_sw, bb_ne = geoloc.bounding_locations(distance, **kwargs)
        # extract bounding box in radians an reconvert in desired unit
        bbox = [list(map(lambda x: GeoAngle.ang_units_to(GeoAngle.DEG_ANG_UNIT,ang_unit,x),_)) \
                for _ in geoloc.bounding_locations(distance, **kwargs)]
        return bbox
 
    #/************************************************************************/
    @classmethod
    def centroid(cls, *args, **kwargs):
        """Retrieve the approximate centroid of a polygon (bounding box). Accuracy 
        is not a major aspect here. 
        
        ::
        
            >>> lat, Lon = GeoCoordinate.centroid(*args)            

        Arguments
        ---------
        args : list[tuple], list[:class:`~happygisco.tools.GeoCoordinate`]
            a list of :literal:`(lat,Lon)` geographical coordinates, or instances
            of the :class:`GeoCoordinate` class, representing the vertices of a 
            polygon.
            
        Keyword Arguments
        -----------------
        unit_angle : str
            angle measurement unit, *i.e.* unit of the input :data:`args` parameter; 
            useful when a mix of :class:`GeoCoordinate` instances and coordinate
            tuples are passed, can be ignored otherwise: the output coordinates will 
            be expressed in the same unit as the input parameters :data:`args` (see
            below).
            
        Returns
        ------- 
        lat, Lon : tuple
            :literal:`(lat,Lon)` geographical coordinates of the centroid point,
            in the same unit as the input parameters :data:`args`.
            
        Example
        -------

        Let us first retrieve the corner coordinates of a bounding box built around
        Paris city centre:
            
        ::
            
            >>> paris = GeoCoordinate(48.85693, 2.3412)
            >>> bbox = paris.bounding_locations(1)
            
        then we can already retrieve the centroid of the polygon associated to
        the corners only, and see it coincides with Paris location:
            
        ::
            
            >>> centroid =  GeoCoordinate.centroid(*bbox)      
            >>> print(centroid)
                (48.85693, 2.3412)
 
        Note
        ----
        Convert the polygon to a rectangle by selecting the points with: 

            * lowest/highest latitude,
            * lowest/highest longitude,
            
        among all :literal:`(lat,Lon)` vertex coordinates passed as arguments, 
        then get the center of this rectangle as the centroid point.
        """
        lat_list, Lon_list = [], []
        ang_unit = kwargs.pop('unit_angle',GeoAngle.DEG_ANG_UNIT)
        for arg in args:
            if isinstance(arg,GeoCoordinate):
                lat_list.append(GeoAngle.ang_units_to('deg',ang_unit,arg.coordinates[0]))
                Lon_list.append(GeoAngle.ang_units_to('deg',ang_unit,arg.coordinates[1]))
            else:    
                lat_list.append(arg[0])
                Lon_list.append(arg[1])
        Lon_list.sort()
        lat_list.sort()
        lat = float(lat_list[0]) + ((float(lat_list[len(lat_list)-1]) - float(lat_list[0])) / 2.)
        Lon = float(Lon_list[0]) + ((float(Lon_list[len(Lon_list)-1]) - float(Lon_list[0])) / 2.)
        return (lat, Lon)
        
     #/************************************************************************/
    def distance_to(self, other, **kwargs): # override method distance_to
        """Method overriding super method from :class:`tools.GeoLocation`
        for computing the great circle distance between this :class:`GeoCoordinate` 
        instance and another (where measurement unit is passed as an argument).
        
        ::
        
            >>> R = coord.distance_to(other, **kwargs)

        Arguments
        ---------
        other : :class:`~happygisco.tools.GeoCoordinate`
            a :class:`GeoCoordinate` instance to which compute a distance.
            
        Keyword Arguments
        -----------------
        unit,radius : 
            see :meth:`bounding_locations`.
            
        Returns
        -------
        R : float
            distance computed in the unit defined through the :data:`unit` keyword
            argument (default is :literal:`km`).
            
        Example
        -------
        
        We can easily retrieve the geodesic distance between two geolocations, for
        instance between Paris, France and Bee, Italia (in km):
            
        ::
            
            >>> paris = GeoCoordinate(48.85693, 2.3412)
            >>> bee = GeoCoordinate.from_degrees(45.9611, 8.5809)    
            >>> print(bee.distance_to(paris))
                569.7000178930588
            
        See also
        --------
        :meth:`~GeoCoordinate.distance`, :meth:`~GeoCoordinate.distance_to_from`.
        """
        if not isinstance(other,GeoCoordinate):
            try:
                other = GeoCoordinate(*other)
            except:
                pass # crash next...
        radius = kwargs.pop('radius', GeoDistance.EARTH_RADIUS_EQUATOR) # GeoDistance.EARTH_RADIUS
        res = super(GeoCoordinate,self).distance_to(other, radius=radius)
        # res = GeoLocation.distance_to(self, other, radius=radius)
        # note: "super() cannot be used with old-style class":
        unit = kwargs.pop('unit', GeoDistance.KM_DIST_UNIT)
        try:    return res * GeoDistance.KM_TO[unit]
        except: raise happyError('unit {} not implemented'.format(unit))
        
    #/************************************************************************/
    @classmethod
    def distance_to_from(cls, loc1, loc2, **kwargs):
        """Compute the (approximate) great circle distance between two points on 
        the Earth (specified in decimal degrees). Accuracy is not a major aspect 
        here. 
        
        ::
        
            >>> R = GeoCoordinate.distance_to_from(loc1, loc2, **kwargs)            

        Arguments
        ---------
        loc1,loc2 : list,:class:`~happygisco.tools.GeoCoordinate`
            :literal:`(lat,Lon)` coordinates of the two location points, in the 
            same unit as the parameters in :data:`args`.
            
        Keyword Arguments
        -----------------
        unit_angle,unit : 
            see :meth:`bounding_locations_from`.
            
        Returns
        -------
        lat, Lon : tuple
            
        Example
        -------
        Following the schema of the :meth:`` method, one can equivalently retrieve
        distances between geolocations:
            
        ::
            
            >>> paris = GeoCoordinate(48.85693, 2.3412)
            >>> bee = GeoCoordinate.from_degrees(45.9611, 8.5809)    
            >>> print(GeoCoordinate.distance_to_from(paris, bee))
                569.7000178930588
    
        Note
        ----
        Generalise the :meth:`distance_to` method.
        Inspired by the code in: http://stackoverflow.com/a/4913653/983244.
            
        See also
        --------
        :meth:`~GeoCoordinate.distance`, :meth:`~GeoCoordinate.distance_to`.
        """
        ang_unit = kwargs.pop('unit_angle',GeoAngle.DEG_ANG_UNIT)
        try:    
            lat1, lng1 = [GeoAngle.ang_units_to('deg',ang_unit,_) for _ in loc1.coordinates]
        except: 
            lat1, lng1 = loc1
        try:    
            lat2, lng2 = [GeoAngle.ang_units_to('deg',ang_unit,_) for _ in loc2.coordinates]
        except: 
            lat2, lng2 = loc2
        # convert to radians 
        #lat1, lng1, lng2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])
        lat1, lng1 = map(lambda x: GeoAngle.ang_units_to(ang_unit,GeoAngle.RAD_ANG_UNIT,x), [lat1, lng1])
        lat2, lng2 = map(lambda x: GeoAngle.ang_units_to(ang_unit,GeoAngle.RAD_ANG_UNIT,x), [lat2, lng2])
        dlng, dlat = lng2 - lng1, lat2 - lat1 #analysis:ignore
        # for 'visual' consistency, we use the same formula as that of geolocation.distance_to,
        # but the results are obviously the same as the formula below
        a = math.sin(lat2) * math.sin(lat1) + math.cos(lat2) * math.cos(lat1) * math.cos(dlng)
        if a>1.0:       a = 1.0
        elif a<-1.0:    a = -1.0
        c = math.acos(a)
        ## haversine formula 
        #a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        #c = 2 * math.asin(math.sqrt(a2)) 
        radius = kwargs.pop('earth_radius', GeoDistance.EARTH_RADIUS_EQUATOR) # GeoDistance.EARTH_RADIUS
        unit = kwargs.pop('unit', GeoDistance.KM_DIST_UNIT)
        try:    return c * radius * GeoDistance.KM_TO[unit] 
        except: raise happyError('unit {} not implemented'.format(unit))
        
    #/************************************************************************/
    @classmethod
    def distance(cls, *args, **kwargs):            
        """Class method used for computing pairwise distances between given locations, 
        passed as geographic coordinates.
        
        ::
        
            >>> D = GeoCoordinate.distance(*args, **kwargs)
    
        Arguments
        ---------
        args : tuple
            a pair of locations represented as a tuple of :literal:`(lat,Lon)` 
            geographical coordinates.

        Keyword Arguments
        -----------------        
        dist : str  
            name of the geo-principle used to estimate the distance: it is any string
            in :literal:`['great_circle','vincenty']` since they represente the Great
            Circle distance and the Vincenty distance; see :meth:`geopy.distance` method
            of the |geopy| package; default to :literal:`'great_circle'`.
        unit : str  
            name of the unit used to return the result: any string from the list
            :literal:`['m','km','mi','ft']`; default to 'km'.
            
        Returns
        -------
        D : :class:`np.array`
            matrix of pairwise distances computed in :data:`unit` unit.
        
        Raises
        ------
        ~settings.happyError
            an error is raised in cases of:
                
                * unexpected variable for lat/long,
                * wrong unit/code for geodesic distance.
            
        Examples
        --------  
        
        ::

            >>> GeoCoordinate.distance((26.062951, -80.238853), (26.060484,-80.207268), 
                                       dist='vincenty', unit='m')
                3172.3596179302895
            >>> GeoCoordinate.distance((26.062951, -80.238853), (26.060484,-80.207268), 
                                       dist='great_circle', unit='km')
                3.167782321855102
            
        See also
        --------
        :meth:`~GeoCoordinate.distance_to`, :meth:`~GeoCoordinate.distance_to_from`.
        """
        if args in (None,()):           return
        else:                           locs = list(args)    
        nlocs = len(locs)
        if not all([isinstance(locs[i],(list,tuple)) and len(locs[i])==2 for i in range(nlocs)]):
            raise happyError('unexpected variable for lat/long')
        unit = kwargs.pop('unit', GeoDistance.KM_DIST_UNIT)
        if unit not in GeoDistance.DIST_UNITS.keys():
            raise happyError('wrong unit for geodesic distance')
        code = kwargs.get('dist')
        if code is not None and code not in cls.DIST_FUNCS.keys():
            raise happyError('wrong code for geodesic distance')
        try:    
            assert geopy#analysis:ignore
            # in order to accept the 'getattr' below, the geopy.distance needs
            # to be loaded in the first place
            import geopy.distance
        except: 
            if code is not None and code!='great_circle':
                code = 'great_circle'
                happyWarning('great_circle distance is considered')
            distance = lambda x,y:  cls.distance_to_from(x,y) 
            cunit = lambda d: d * GeoDistance.KM_TO[unit]
        else:   
            code = code or 'great_circle'
            distance = getattr(geopy.distance, GeoDistance.DIST_FUNCS[code]) 
            cunit = lambda d: getattr(d, GeoDistance.DIST_UNITS[unit])
        dist = np.zeros([nlocs,nlocs])
        np.fill_diagonal(dist, 0.)
        for i in range(nlocs):
            for j in range(i+1,nlocs):
                dist[i][j] = dist[j][i] = cunit(distance(locs[i],locs[j]))
        if nlocs==2:        dist = dist[1][0]
        return dist
            
    #/************************************************************************/
    @classmethod      
    def round(cls, coordinates):
        """Round coordinates up to an (internal, fixed) precision of 5 digits.
        
        ::
        
            >>> coordinates = GeoCoordinate.round(coordinates)
            
        Arguments
        ---------
        coordinates : float, list
            a list with of float values, *e.g.* representing :literal:`(lat,Lon)` 
            coordinates.
            
        Returns
        -------
        coordinates : float, list
            a list of coordinates rounded to :data:`~GeoCoordinate.DECIMAL_PRECISION` 
            precision.
            
        Examples
        -------- 
        
        ::

            >>> GeoCoordinate.round(2.216707433489782)
                2.21671
            >>> GeoCoordinate.round([2.216707433489782, 48.72843804413901, 2.477292566510218, 48.98924195586099])
                [2.21671, 48.72844, 2.47729, 48.98924]
        """
        if True:    
            around = lambda x: round(x,cls.DECIMAL_PRECISION)
        else: # np.around issue with floating precision       
            around = lambda x:np.around(x,decimals=cls.DECIMAL_PRECISION)
        try:        return [around(c) for c in coordinates]
        except:
            try:    return around(coordinates)
            except: return coordinates
            
    #/************************************************************************/
    @classmethod      
    def bbox2latlon(cls, bbox): 
        """Convert an AOI bounding box into the corresponding :literal:`(lat, Lon, rad)` format.
        
        ::
        
            >>> lat, Lon, rad = GeoCoordinate.bbox2latlon(bbox)
        
        Arguments
        ---------
        bbox : list
            a bounding box represented as a 4-lenght list with the :literal:`(lat,Lon)` 
            coordinates of the South-West and North-East corners of the input polygon. 

        Returns
        -------
        lat,Lon,rad : float
            parameters defining the CIRCUMcircle of the input bounding box :data:`bbox`.

        Examples
        -------- 
        
        ::
            
            >>> bbox = [2.216707433489782, 48.72843804413901, 2.477292566510218, 48.98924195586099]
            >>> lLr = GeoCoordinate.bbox2latlon(bbox)
            >>> print(lLr)
                (2.347, 48.85884, 14.50401801879798)
        
        As mentioned, no idempotence, but the centre of the bounding box is still preserved: 
        
        ::
        
            >>> GeoCoordinate.latlon2bbox(*lLr) == bbox
                False
            >>> lLr_ = GeoCoordinate.bbox2latlon(GeoCoordinate.latlon2bbox(*lLr))
            >>> print(lLr_)
                (2.347, 48.85884, 29.007998346748554)
            >>> lLr_[:2] == lLr[:2] # are the coordinates of the centre preserved?
                True
            
        Note
        ----
        This method and :meth:`~GeoCoordinate.latlon2bbox` method are not idempotent 
        (say it otherwise :data:`~GeoCoordinate.latlon2bbox(~GeoCoordinate.bbox2latlon(bbox)` 
        does not return :data:`bbox`): see comments on CIRCUMcircle and INcircle; however,
        the centre of the bounding box :data:`bbox` (hence the tuple :data:`(lat,Lon)`) 
        is preserved.
        
        See also
        --------
        :meth:`~GeoCoordinate.centroid`, :meth:`~GeoCoordinate.distance_to_from`,
        :meth:`~GeoCoordinate.latlon2bbox`.
        """
        lat, Lon = cls.centroid(bbox[0:2], bbox[2:4])      
        rad = cls.distance_to_from(bbox[0:2], bbox[2:4])/2.
        return lat, Lon, rad
             
    #/************************************************************************/
    @classmethod      
    def latlon2bbox(cls, lat, Lon, rad, **kwargs): 
        """Convert an AOI in :literal:`(lat, Lon, rad)` format into the corresponding 
        bounding box.
        
        ::
        
            >>> bbox = GeoCoordinate.latlon2bbox(lat, Lon, rad, **kwargs)
        
        Arguments
        ---------
        lat,Lon,rad : float
            see :meth:`bbox2latlon`\ .
            
        Returns
        -------
        bbox : list
            bounding box (see :meth:`~GeoCoordinate.bbox2latlon`) whose INcircle 
            is the circle defined by the centre :data:`(lat,Lon)` and a radius 
            :data:`rad`.

        Example
        ------- 
        
        ::
        
            >>> lLr = (2.347, 48.85884, 14.50401801879798)
            >>> GeoCoordinate.latlon2bbox(*lLr)
                [2.216707433489782, 48.72843804413901, 2.477292566510218, 48.98924195586099]
        
        See also
        --------
        :meth:`~GeoCoordinate.bbox2latlon`, :meth:`~GeoCoordinate.bounding_locations_from`.
        """
        return cls.bounding_locations_from([lat,Lon], rad, **kwargs)
            
    #/************************************************************************/
    @classmethod    
    def bbox2polygon(cls, bbox, order='lL'): 
        """Convert an AOI bounding box into the corresponding polygon of :literal:`(lat, Lon)`
        or :literal:`(Lon, lat)` coordinates (the latter case is used in GeoJSON format).
        
        ::
        
            >>> polygon = GeoCoordinate.bbox2polygon(bbox, order='lL')
        
        Arguments
        ---------
        bbox : list
            a bounding box represented as a 4-lenght list with the :literal:`(lat,Lon)` 
            coordinates (or :literal:`(Lon,lat)`; see :data:`order` below) of the 
            South-West and North-East corners of the input polygon. 
        order : str
            a string specifying the order of the coordinates inside the bounding box:
            it either 'lL' when latitudes come first (hence :literal:`(lat,Lon)`, 
            default), or 'Ll' when longitudes come first (hence :literal:`(Lon,lat):`).

        Returns
        -------
        polygon : list
            a 4-lenght list of :literal:`(lat,Lon)` (or :literal:`(Lon,lat)` when 
            :data:`order=='Ll'`) coordinates representing the input bounding box 
            :data:`bbox`.
        
        Raises
        ------
        ~settings.happyError 
            an error is raised when unrecognized order argument.
            
        Example
        ------- 
        
        ::

            >>> GeoCoordinate.bbox2polygon([2.2241, 48.81554, 2.4699, 48.90214])
                [[2.2241, 48.81554], [2.4699, 48.81554], [2.4699, 48.90214], [2.2241, 48.90214]] 
            >>> GeoCoordinate.bbox2polygon([2.2241, 48.81554, 2.4699, 48.90214],order='Ll')
                [[48.81554, 2.2241], [48.81554, 2.4699], [48.90214, 2.4699], [48.90214, 2.2241]]
        
        See also
        --------
        :meth:`~GeoCoordinate.polygon2bbox`.
        """
        polygon = [[bbox[0],bbox[1]], [bbox[2],bbox[1]],
                   [bbox[2],bbox[3]], [bbox[0],bbox[3]] ]
        if order=='lL': # default: order (lat,Lon)      
            return polygon
        elif order=='Ll':                   
            return [lL[::-1] for lL in polygon]
        else:
            raise happyError('unrecognized order argument')
            
    #/************************************************************************/
    @classmethod    
    def polygon2bbox(cls, polygon, order='lL'): 
        """Convert a polygon of :literal:`(lat, Lon)` (or :literal:`(Lon, lat)`)
        coordinates into an AOI bounding box.
        
        ::
        
            >>> bbox = GeoCoordinate.polygon2bbox(polygon, order='lL')
        
        Arguments
        ---------
        polygon,order : 
            see :meth:`~GeoCoordinate.bbox2polygon`.
        
        Returns
        -------
        bbox : list
            a 4-lenght list of :literal:`(lat,Lon)` (or :literal:`(Lon,lat)`) 
            coordinates; see :meth:`~GeoCoordinate.bbox2polygon`.
        
        Raises
        ------
        ~settings.happyError 
            an error is raised in case of unrecognized :data:`order` argument.

        Example
        ------- 
        
        ::

            >>> GeoCoordinate.polygon2bbox([[2.2241, 48.81554], [2.4699, 48.81554],
                                           [2.4699, 48.90214], [2.2241, 48.90214]])
                [2.2241, 48.81554, 2.4699, 48.90214]) 
        
        See also
        --------
        :meth:`~GeoCoordinate.bbox2polygon`.
        """
        bbox = [min([p[0] for p in polygon]), min([p[1] for p in polygon]),
                max([p[0] for p in polygon]), max([p[1] for p in polygon])]
        if order=='lL':                   
            return bbox 
        elif order=='Ll': # default: order (lat,Lon)   
            return bbox[:2][::-1] + bbox[2:][::-1]
        else:
            raise happyError('unrecognized order argument')
            
    #/************************************************************************/
    @classmethod      
    def bboxintersects(cls, bbox1, bbox2): 
        """Determine if two AOI bounding boxes do intersect.
        
        ::
        
            >>> resp = GeoCoordinate.bboxintersects(bbox1, bbox2)
        
        Returns
        -------
        resp : bool
            :literal:`True` if :data:`bbox1` and :data:`bbox2` intersect, 
            :literal:`False` otherwise.

        Example
        ------- 
         
        See also
        --------
        :meth:`~GeoCoordinate.bbox2polygon`, :meth:`~GeoCoordinate.bboxintersection`,
        :meth:`~GeoCoordinate.bboxwithin`.
        """
        bbox = [max(bbox1[0],bbox2[0]), max(bbox1[1],bbox2[1]),
                min(bbox1[2],bbox2[2]), min(bbox1[3],bbox2[3])]        
        if bbox[0]>bbox[2] or bbox[1]>bbox[3]:      return False
        else:                                       return True   
            
    #/************************************************************************/
    @classmethod      
    def bboxwithin(cls, bbox1, bbox2):  
        """Determine if an AOI bounding box is contained in another one.
        
        ::
        
            >>> resp = GeoCoordinate.bboxwithin(bbox1, bbox2)
        
        Returns
        -------    
        resp : bool
            :literal:`True` if :data:`bbox1` is included within :data:`bbox2`, 
            :literal:`False` otherwise.
            
        Example
        ------- 
        
        ::

            >>> bbox = [2.2241, 48.81554, 2.4699, 48.90214]
            >>> lLr = (2.347, 48.85884, 14.50401801879798)
            >>> assert GeoCoordinate.bboxwithin(bbox, GeoCoordinate.latlon2bbox(*lLr))
         
        See also
        --------
        :meth:`~GeoCoordinate.bboxintersects`, :meth:`~GeoCoordinate.intersection`.
        """
        return bbox1[0]>=bbox2[0] and bbox1[1]>=bbox2[1] and bbox1[2]<=bbox2[2] \
        and bbox1[3]<=bbox2[3]
            
    #/************************************************************************/
    @classmethod      
    def bboxintersection(cls, bbox1, bbox2): 
        """Retrieve the intersection of two AOI bounding boxes.
        
        ::
        
            >>> bbox = GeoCoordinate.bboxintersection(bbox1, bbox2)
        
        Returns
        -------
        bbox : list
            a bounding box representing the intersection of both :data:`bbox1` and 
            :data:`bbox2` bounding boxes; when the intersection is empty, 
            :data:`bbox` is set to :data:`None`.

        Example
        ------- 
         
        See also
        --------
        :meth:`~GeoCoordinate.bboxintersects`, :meth:`~GeoCoordinate.bboxunion`,
        :meth:`~GeoCoordinate.bboxwithin`.
        """
        return [max(bbox1[0],bbox2[0]), max(bbox1[1],bbox2[1]),     \
                min(bbox1[2],bbox2[2]), min(bbox1[3],bbox2[3])]     \
                if cls.bboxintersects(bbox1, bbox2) else None
            
    #/************************************************************************/
    @classmethod      
    def bboxunion(bbox1, bbox2):  # takes the largest envelop
        """Retrieve the union (largest encompassing) of two AOI bounding boxes.
        
        ::
        
            >>> bbox = GeoCoordinate.bboxunion(bbox1, bbox2)

        Returns
        -------
        bbox : list
            a bounding box representing the union of both :data:`bbox1` and 
            :data:`bbox2` bounding boxes. 

        Example
        ------- 
         
        See also
        --------
        :meth:`~GeoCoordinate.bboxintersection`, :meth:`~GeoCoordinate.bboxwithin`.
        """
        return [min(bbox1[0],bbox2[0]), min(bbox1[1],bbox2[1]),
                max(bbox1[2],bbox2[2]), max(bbox1[3],bbox2[3])]


#%%
#==============================================================================
# CLASS GDALTool
#==============================================================================
    
class GDALTool(_Tool):
    """Class implementing simple |GDAL|-based operations on raster and/or vector
    data.
        
    ::

        >>> tool = tools.GDALTool(**kwargs)

    Arguments
    ---------
    driver_name : str
        name of the driver used for vector files; default is :data:`settings.DRIVER_NAME`,
        *e.g.* :literal:`'ESRI Shapefile'` to load common shapefiles.
    """
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        # initial settings
        self.__driver, self.__drivername = None, ''
        try:
            assert GDAL_TOOL is not False
        except:
            raise IOError('GDAL service not available')
        self.__drivername   = kwargs.pop('driver_name', settings.DRIVER_NAME)
        try:
            self.__driver = ogr.GetDriverByName(self.driver_name)
        except:
            try:
                self.__driver = ogr.GetDriver(0)
            except:
                raise IOError('driver not available')
            
    #/************************************************************************/    
    @property
    def driver(self):
        """Driver property (:data:`getter`) associated to the :class:`GDALTool` 
        instance, *e.g.* see :meth:`ogr.GetDriver` method. 
        """
        return self.__driver
            
    @property
    def driver_name(self):
        """Driver name property (:data:`getter`/:data:`setter`) associated to the 
        :class:`GDALTool` instance, *e.g.* see :meth:`ogr.GetDriverByName` method. 
        """
        return self.__driver_name
    @driver_name.setter#analysis:ignore
    def driver_name(self, driver_name):
        if not isinstance(driver_name, str):
            raise IOError('wrong type for DRIVER_NAME parameter')
        self.__driver_name = driver_name

    #/************************************************************************/
    @_Decorator.parse_file
    def file2layer(self, **kwargs):
        """
            >>> layer = tool.file2layer(filename)
        """
        filename = kwargs.pop(_Decorator.KW_FILE,'') 
        try:
            assert filename not in ('', None)
        except:
            raise happyError('input file not found')
        try:
            assert self.driver is not None
        except:
            raise happyError('offline driver not available')
        try:
            data = self.driver.Open(filename, 0) # 0 means read-only
            assert data is not None
        except:
            raise happyError('file %s not open' % filename)
        else:
            if settings.VERBOSE: print('file %s opened' % filename)
        try:
            layer = data.GetLayer()
            assert layer is not None
        except:
            raise IOError('could not get vector layer')
        return layer

    #/************************************************************************/
    @_Decorator.parse_coordinate
    def coord2vec(self, coord, **kwargs):
        """
            >>> vec = tool.coord2vec(coord, **kwargs)
        """
        vector = ogr.Geometry(ogr.wkbMultiPoint)
        for i in range(len(coord)):
            try:
                pt = ogr.Geometry(ogr.wkbPoint)
                pt.AddPoint(coord[i][::-1]) # first Lon, then lat
            except:
                happyVerbose('\ncould not add geolocation')
            else:
                vector.AddGeometry(pt)
        return vector
    
    #/************************************************************************/
    def vec2id(self, layer, vector):
        """
           >>> id = tool.vec2id(layer, vector)
        """
        answer = [] # will be same lenght as self.vector
        featureCount = layer.GetFeatureCount()
        happyVerbose('\nnumber of features in %s: %d' % (layer,featureCount))
        # iterate through points
        for i in range(0, vector.GetGeometryCount()): # because it is a MULTIPOINT
            pt = vector.GetGeometryRef(i)
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
                    answer.append(feature)
            if len(answer)<i+1:    
                answer.append(None)
        return answer

    #/************************************************************************/
    @_Decorator.parse_coordinate
    @_Decorator.parse_file
    def coord2id(self, coord, **kwargs):
        """
            >>> id = tool.coord2id(*args, **kwargs)
        """
        filename = kwargs.pop(_Decorator.KW_FILE,'') 
        try:
            assert filename not in ('', None)
        except:
            raise happyError('input file not found')
        try:
            layer = self.file2layer(filename)
            assert layer not in (None,[])
        except:
            raise happyError('could not load feature layer')
        try:
            vector = self.coord2vec(coord)
            assert vector not in (None,[])
        except:
            raise IOError('could not load geolocation vector')
        return self.vec2id(layer, vector)

#%%
#==============================================================================
# CLASS _Pools
#==============================================================================

class _Pools(object):
    """Class of generic pool workers for parallel mapping.
    """
    
    #/************************************************************************/
    @staticmethod
    def worker(f, ii, chunk, out_q, err_q, lock):  
        """A worker function that maps an input function over a slice of the input 
        iterable. 
        
            >>> res = worker(f, ii, chunk, out_q, err_q, lock)
        
        Arguments
        ---------
        f : callable
            callable function that accepts argument from iterable. 
        ii : 
            process ID. 
        chunk : 
            slice of input iterable. 
        out_q : 
            thread-safe output queue. 
        err_q : 
            thread-safe queue to populate on exception. 
        lock : 
            thread-safe lock to protect a resource (useful in extending :meth:`~Parallel.map_tasks`). 
        """  
        vals = []  
        # iterate over slice   
        for val in chunk:  
            try:  
                result = f(val)  
            except Exception as e:  
                err_q.put(e)  
                return  
        vals.append(result)  
        # output the result and task ID to output queue  
        out_q.put( (ii, vals) )  
      
      
    #/************************************************************************/
    @staticmethod
    def run_tasks(procs, err_q, out_q, num):  
        """A function that executes populated processes and processes the resultant 
        array. Checks error queue for any exceptions. 
        
            >>> res = run_tasks(procs, err_q, out_q, num) 

        Arguments
        ---------
        procs : 
             list of Process objects. 
        out_q : 
            thread-safe output queue. 
        err_q : 
            thread-safe queue to populate on exception. 
        num : 
            length of resultant array. 
        """  
        # function to terminate processes that are still running.  
        die = (lambda vals : [val.terminate() for val in vals  
                 if val.exitcode is None])  
        try:  
            for proc in procs:  proc.start()  
            for proc in procs:  proc.join()  
        except Exception as e:  
            # kill all slave processes on ctrl-C  
            die(procs)  
            raise e  
        if not err_q.empty():  
            # kill all on any exception from any one slave  
            die(procs)  
            raise err_q.get()  
        # Processes finish in arbitrary order. Process IDs double  
        # as index in the resultant array.  
        results=[None]*num;  
        while not out_q.empty():  
            idx, result = out_q.get()  
            results[idx] = result  
        # Remove extra dimension added by array_split  
        return list(np.concatenate(results))  
      
    #/************************************************************************/
    @staticmethod
    def map_tasks(function, sequence, numcores=None):  
        """A parallelized version of the native `Python` method :meth:`map` that 
        uses the `Python` :mod:`multiprocessing` module to divide and conquer sequence. 
        
            >>> res = map_tasks(function, sequence, numcores) 

        Arguments
        ---------
        function : callable
            callable function that accepts argument from iterable. 
        sequence : list,tuple
            iterable sequence.  
        numcores : int
            number of cores to use.

        Note
        ----
        :meth :`~_Pool.map_tasks` does not yet support multiple argument sequences. 
        """  
        if not callable(function):  
            raise TypeError("input function {} is not callable".format(repr(function)))  
        if not np.iterable(sequence):  
            raise TypeError("input {} is not iterable".format(repr(sequence)))
        size = len(sequence)  
        if not MULTIPROCESSING or size == 1:     return map(function, sequence)  
        if numcores is None:            numcores = NCPUS  
        # returns a started SyncManager object which can be used for sharing   
        # objects between processes. The returned manager object corresponds  
        # to a spawned child process and has methods which will create shared  
        # objects and return corresponding proxies.  
        manager = multiprocessing.Manager()  
        # Create FIFO queue and lock shared objects and return proxies to them.  
        # The managers handles a server process that manages shared objects that  
        # each slave process has access to. Bottom line -- thread-safe.  
        out_q = manager.Queue()  
        err_q = manager.Queue()  
        lock = manager.Lock()  
        # if sequence is less than numcores, only use len sequence number of   
        # processes  
        if size < numcores:             numcores = size   
        # group sequence into numcores-worth of chunks  
        sequence = np.array_split(sequence, numcores)  
        procs = [multiprocessing.Process(target=_Pools.worker,  
               args=(function, ii, chunk, out_q, err_q, lock))  
             for ii, chunk in enumerate(sequence)]  
        return _Pools.run_tasks(procs, err_q, out_q, numcores)  


