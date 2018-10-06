#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_happygisco

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _GISCO: http://ec.europa.eu/eurostat/web/gisco
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _OSM: https://www.openstreetmap.org
.. |OSM| replace:: `Open Street Map <OSM_>`_
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

The :mod:`happyGISCO` project will enable you to perform very basic geospatial 
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
        ['settings', 'base', 'tools', 'services', 'features']
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Thu Apr  5 16:40:31 2018

import os, sys, warnings#analysis:ignore
import imp, inspect
import collections, itertools, functools
import six

__all__ = ['settings', 'base', 'tools', 'services', 'features']#analysis:ignore


# sys.path.append(os.path.dirname(os.path.realpath(__file__)))

#==============================================================================
# PROGRAM METADATA
#==============================================================================

try:
    projdir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           '..'))
    metadata = imp.load_source('metadata', os.path.join(projdir, 'metadata.py'))
except:
    metadata = {'project'     : 'happyGISCO',
                'package'     : 'happygisco',
                'description' : '',
                'version'     : '',
                'author'      : '',
                'contact'     : '',
                'license'     : '',
                'copyright'   : '',
                'organization':'',
                'url'         : '',
                'date'        : '',
                'credits'     : ''
                }                                                       
else:
    metadata = metadata.metadata                            
    
VERBOSE             = False # True

REDUCE_ANSWER       = False # ! used for testing purpose: do not change !
EXCLUSIVE_ARGUMENTS = False # ! used for settings: do not change !

#%%
#==============================================================================
# CLASSES happyError/happyWarning/happyVerbose
#==============================================================================

class happyWarning(Warning):
    """Dummy class for warnings in this package.
    
        >>> happyWarning(warnmsg, expr=None)

    Arguments
    ---------
    warnmsg : str
        warning message to display.
        
    Keyword arguments
    -----------------
    expr : str 
        input expression in which the warning occurs; default: :data:`expr` is 
        :data:`None`.
        
    Example
    -------

        >>> happyWarning('This is a very interesting warning');
            happyWarning: ! This is a very interesting warning !
    """
    def __init__(self, warnmsg, expr=None):    
        self.warnmsg = warnmsg
        if expr is not None:    self.expr = expr
        else:                   self.expr = '' 
        # warnings.warn(self.msg)
        print(self)
    def __repr__(self):             return self.msg
    def __str__(self):              
        #return repr(self.msg)
        return ( 
                "! %s%s%s !" %
                (self.warnmsg, 
                 ' ' if self.warnmsg and self.expr else '',
                 self.expr
                 )
            )
    
class happyVerbose(object):
    """Dummy class for verbose printing mode in this package.
    
        >>> happyVerbose(msg, verb=True, expr=None)

    Arguments
    ---------
    msg : str
        verbose message to display.
        
    Keyword arguments
    -----------------
    verb : bool
        flag set to :data:`True` when the string :literal:`[verbose] -` is added
        in front of each verbose message displayed.
    expr : str 
        input expression in which the verbose mode is called; default: :data:`expr` is 
        :data:`None`.
        
    Example
    -------

        >>> happyVerbose('The more we talk, we less we do...', verb=True);
            [verbose] - The more we talk, we less we do...
    """
    def __init__(self, msg, expr=None, verb=VERBOSE):    
        self.msg = msg
        if verb is True:
            print('\n[verbose] - %s' % self.msg)
        if expr is not None:    self.expr = expr
    #def __repr__(self):             
    #    return self.msg
    def __str__(self):              
        return repr(self.msg)
    
class happyError(Exception):
    """Dummy class for exception raising in this package.
    
        >>> raise happyError(errmsg, errtype=None, errcode=None, expr='')

    Arguments
    ---------
    errmsg : str
        message -- explanation of the error.
        
    Keyword arguments
    -----------------
    errtype : object
        error type; when :data:`errtype` is left to :data:`None`, the system tries
        to retrieve automatically the error type using :data:`sys.exc_info()`.
    errcode : (float,int)
        error code; default: :data:`errcode` is :data:`None`.
    expr : str 
        input expression in which the error occurred; default: :data:`expr` is 
        :data:`None`.
        
    Example
    -------
        
        >>> try:
                assert False
            except:
                raise happyError('It is False')
            Traceback ...
            ...
            happyError: !!! AssertionError: It is False !!!
    """
    
    def __init__(self, errmsg='', errtype=None, errcode=None, expr=''):   
        self.errmsg = errmsg
        if expr is not None:        self.expr = expr
        else:                       self.expr = '' 
        if errtype is None:
            try:
                errtype = sys.exc_info()[0]
            except:
                pass
        if inspect.isclass(errtype):            self.errtype = errtype.__name__
        elif isinstance(errtype, (int,float)):  self.errtype = str(errtype)
        else:                                   self.errtype = errtype
        if errcode is not None:     self.errcode = str(errcode)
        else:                       self.errcode = ''
        # super(happyError,self).__init__(self, msg)

    def __str__(self):              
        # return repr(self.msg)
        str_ = ("%s%s%s%s%s%s%s" %
                (self.errtype or '', 
                 ' ' if self.errtype and self.errcode else '',
                 self.errcode or '',
                 ': ' if (self.errtype or self.errcode) and (self.errmsg or self.expr) else '',
                 self.errmsg or '', 
                 ' ' if self.errmsg and self.expr else '',
                 self.expr or '' #[' ' + self.expr if self.expr else '']
                 )
                )
        return ( "%s%s%s" % 
                ('' if str_.startswith('!!!') else '!!! ',
                 str_,
                 '' if str_.endswith('!!!') else ' !!!'
                 )
                )


#%%
#==============================================================================
# FUNCTION happyDeprecated
#==============================================================================

def happyDeprecated(reason, run=True):
    """This is a decorator which can be used to mark functions as deprecated. 
        
        >>> new = settings.happyDeprecated(reason)  
        
    Arguments
    ---------
    reason : str
        optional string explaining the deprecation.
        
    Keywords arguments
    ------------------
    run : bool
        set to run the function/method/... despite being deprecated; default: 
        :data:`False` and the decorated method/function/... is not run.
        
    Examples
    --------
    The deprecated function can be used to decorate different objects:
        
        >>> @happyDeprecated("use another function")
        ... def old_function(x, y):
        ...     return x + y
        >>> old_function(1, 2)        
            __main__:1: DeprecationWarning: Call to deprecated function old_function (use another function).        
            3
        >>> class SomeClass(object):
        ... @happyDeprecated("use another method", run=False)
        ... def old_method(self, x, y):
        ...     return x + y
        >>> SomeClass().old_method(1, 2)
            __main__:1: DeprecationWarning: Call to deprecated function old_method (use another method).       
        >>> @happyDeprecated("use another class")
        ... class OldClass(object):
        ...     pass
        >>> OldClass()
            __main__:1: DeprecationWarning: Call to deprecated class OldClass (use another class).  
            <__main__.OldClass at 0x311e410f0>
            
    Note
    ----
    It will result in a warning being emitted when the function is used and when
    a :data:`reason` is passed.
    """
    # see https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
    if isinstance(reason, six.string_types): # happyType.isstring(reason):
        def decorator(func1):
            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."
            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
                warnings.simplefilter('default', DeprecationWarning)
                if run is True:
                    return func1(*args, **kwargs)
            return new_func1
        return decorator
    elif inspect.isclass(reason) or inspect.isfunction(reason):
        func2 = reason
        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."
        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            if run is True:
                return func2(*args, **kwargs)
        return new_func2
    else:
        raise happyError('wrong type for input reason - %s not supported' % repr(type(reason)))
        
#%%
#==============================================================================
# CLASS happyType
#==============================================================================
    
class happyType(object):
    """Class implementing various dummy types' checking.
    """
    
    #/************************************************************************/
    @classmethod
    def typename(cls, inst): 
        """Return the class name of a given instance: nothing else than 
        :data:`instance.__class__.__name__`.
    
            >>> name = happyType.typename(inst)  
            
        Arguments
        ---------
        inst : object
            an instance of a class.
            
        Returns
        -------
        name : str
            name of the class of the instance :data:`inst`.
        """
        try:
            return inst.__class__.__name__
        except:
            raise happyError('input not recognised as an instance')
    
    #/************************************************************************/
    @classmethod
    def istype(cls, inst, str_cls):
        """Determine if a given instance is of a certain type defined by a string 
        (instead of a :class:`type` like in :meth:`isintance`).
        
            >>> ans = happyType.istype(inst, str_cls)
            
        Arguments
        ---------
        inst : object
            an instance of a class.
        str_cls : str
            the name of a class to test (not the class itself).
            
        Returns
        -------
        ans : bool
            :data:`True` when :data:`inst` class name is :data:`str_cls`, :data:`False`
            otherwise.
        """
        try:
            return cls.typename(inst) == str_cls
        except:
            raise happyError('class not recognised')
    
    
    #/************************************************************************/
    @classmethod
    def isnumeric(cls, arg):
        """Check whether an argument is a number.
        
            >>> ans = happyType.isnumeric(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is a number, :data:`False` 
            otherwise.
        """
        try:
            float(arg)
            return True
        except (ValueError,TypeError):
            return False    
    
    #/************************************************************************/
    @classmethod
    def isstring(cls, arg):
        """Check whether an argument is a string.
        
            >>> ans = happyType.isstring(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is a string, :data:`False` 
            otherwise.
        """
        return isinstance(arg, six.string_types)
    
    #/************************************************************************/
    @classmethod
    def issequence(cls, arg):
        """Check whether an argument is a "pure" sequence (*e.g.*, a :data:`list` 
        or a :data:`tuple`), *i.e.* an instance of the :class:`collections.Sequence`,
        except strings excepted.
        
            >>> ans = happyType.issequence(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is an instance of the 
            :class:`collections.Sequence` class, but not a string (*i.e.,* not an 
            instance of the :class:`six.string_types` class), :data:`False` 
            otherwise.
        """
        return (isinstance(arg, collections.Sequence) and not cls.isstring(arg))
    
    #/************************************************************************/
    @classmethod
    def ismapping(cls, arg):
        """Check whether an argument is a dictionary.
        
            >>> ans = happyType.ismapping(arg)
      
        Arguments
        ---------
        arg : 
            any input to test.
      
        Returns
        -------
        ans : bool
            :data:`True` if the input argument :data:`arg` is an instance of the 
            :class:`collections.Mapping` class.
        """
        return (isinstance(arg, collections.Mapping))  
    
    #/************************************************************************/
    @classmethod
    def seqflatten(cls, arg, rec=False):
        """Flatten a list of lists (one-level only).
        
            >>> flat = happyType.seqflatten(arg, rec = False)
            
        Arguments
        ---------
        arg : list[list]
            a list of nested lists.
            
        Keyword arguments
        -----------------
        rec : bool
            :data:`True` when the flattening shall be applied recursively over 
            nested lists; default: :data:`False`.
      
        Returns
        -------
        flat : list
            a list from which all nested elements have been flatten from 1 "level"
            up (case :data:`rec=False`) or through all levels (otherwise).
            
        Examples
        --------
        A very basic way to flatten a list of lists:
            
            >>> happyType.seqflatten([[1],[[2,3],[4,5]],[6,7]])
                [1, [2, 3], [4, 5], 6, 7]
            >>> happyType.seqflatten([[1,1],[[2,2],[3,3],[[4,4],[5,5]]]])
                [1, 1, [2, 2], [3, 3], [[4, 4], [5, 5]]]
                
        As for the difference between recursive and non-recursive calls:
            
            >>> seq = [[1],[[2,[3.5,3.75]],[[4,4.01],[4.25,4.5],5]],[6,7]]
            >>> settings.happyType.seqflatten(seq, rec=True)
                [1, [2, [3.5, 3.75]], [[4, 4.01], [4.25, 4.5], 5], 6, 7]
            >>> settings.happyType.seqflatten(seq, rec=True)
                [1, 2, 3.5, 3.75, 4, 4.01, 4.25, 4.5, 5, 6, 7]
        """
        if not cls.issequence(arg):
            arg = [arg,]
        def recurse(alist):
            if not any([cls.issequence(a) for a in alist]):
                return alist
            if all([cls.issequence(a) for a in alist]):
               nlist  = list(itertools.chain.from_iterable(alist))
            else:
                nlist = alist
            if any([cls.issequence(nlist) for a in nlist]):
                res = []
                for item in nlist:
                    if cls.issequence(item):
                        res += recurse(item)
                    else:
                        res.append(item)
            else:
                res = nlist
            return res
        if rec is True:
            return recurse(arg)
        else:
            return list(itertools.chain.from_iterable(arg))

    #/************************************************************************/
    @classmethod
    def jsonstringify(cls, arg, rec=True):
        """Format a dictionary into a JSON-compliant string where property names
        are enclosed in double quotes :data:`"`.
        
            >>> ans = happyType.jsonstringify(arg, rec=True)
      
        Arguments
        ---------
        arg : dict
            an input argument to parse as a JSON dictionary.
            
        Keyword arguments
        -----------------
        rec : bool
            :data:`True` when the formatting shall be applied recursively over 
            nested dictionary; default: :data:`False`.
      
        Returns
        -------
        ans : str
            string representing the input dictionary :data:`arg` where all property 
            names are enclosed in double quotes :data:`"`.
            
        Examples
        --------
        All keys in the dictionary are transformed in double quoted strings:
            
            >>> a = {1:'a', 2:{"b":3, 4:5}, "6":'d'}
            >>> print(happyType.jsonstringify(a, rec=False))
                {1: "a", 2: {"b": 3, 4: 5}, "6": "d"}
            >>> print(happyType.jsonstringify(a))
                {"1": "a", "2": {"b": 3, "4": 5}, "6": "d"}

        The method can be used to parse the input dictionary as a properly formatted
        string that can be loaded into a dictionary through :mod:`json`:

            >>> import json
            >>> b = {'a':1, 'b':{'c':2, 'd':3}, 'e':4} 
            >>> json.loads("%s" % b)
                Traceback (most recent call last):                
                ...                
                JSONDecodeError: Expecting property name enclosed in double quotes            
            >>> s = happyType.jsonstringify(b)
            >>> print(s)
                '{"a": 1, "b": {"c": 2, "d": 3}, "e": 4}'
            >>> json.loads(s)
                {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
        """
        if not cls.issequence(arg):
            arg = [arg,]
        def recurse(dic):
            ndic = dic.copy()
            for k, v in dic.items():
                if not cls.isstring(k):
                    ndic.update({"%s" % k:v})  
                    ndic.pop(k)
                    k = "%s" % k
                if cls.ismapping(v):
                    # ndic.update({k: cls._keystr(v)})
                    ndic[k] = recurse(v)
            return ndic
        if rec is True:
            arg = ["""%s""" % recurse(a) for a in arg]
        else:
            arg = ["""%s""" % a if not cls.isstring(a) else a for a in arg]
        arg = [a.replace("'","\"") for a in arg]        
        #try:
        #    arg = [json.loads(a) for a in arg]
        #except:
        #    raise happyError('impossible conversion of vector entry') 
        return arg if arg is None or len(arg)>1 else arg[0]


