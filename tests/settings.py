#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. _mod_tests_settings_

Testing units for `nuts2place` settings.

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      0.1
--
*since*:        Sat Apr  7 01:41:10 2018


**Description**

**Usage**

    >>> from place2nuts import tests
    
"""

from settings import _geoDecorators


class test(object):

    def test_3_place_or_coordinates(self):
        class dummy(object):
            @_geoDecorators.parse_place_or_coordinates
            def meth(self, **kwargs):
                return kwargs.get('place') or [kwargs.get('lat'),kwargs.get('lon')]
        assertEqual(dummy.meth(place='Paris'), 'Paris')
        assertEqual(dummy.meth(lat=1, lon=2), [[1], [2]])
        
