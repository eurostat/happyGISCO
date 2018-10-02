#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _start

Dumb start.

"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Mon Oct  1 23:59:22 2018

import os, sys

sys.path.insert(0, os.path.abspath(__file__))
# sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    import happygisco#analysis:ignore
except ImportError:
    raise IOError('environment not set to import happygisco')
    
#__import__('pkg_resources').declare_namespace(__name__)