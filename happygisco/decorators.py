#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. _mod_decorators

Basic decorators used in the package `happygisco`.

**Description**

This module contains some basic definitions (classes and variables) that are used
for:

* simple geographical data handling and processing.

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Wed Apr 18 00:13:43 2018


import os
import inspect
import functools
import types

from happygisco import settings
from happygisco.settings import happyWarning, happyVerbose, happyError#analysis:ignore

       
POLYLINE            = False

USE_WRAPT = False
try:
    assert USE_WRAPT
    import wrapt 
except AssertionError:
    pass
except ImportError:
    happyWarning('module wrapt not imported; see https://github.com/GrahamDumpleton/wrapt')
  
try:
    from method_decorator import method_decorator as _MethodDecorator
except:
    happyWarning('module method_decorator not imported; see https://github.com/denis-ryzhkov/method_decorator')
    pass

try: 
    assert USE_WRAPT and wrapt
except:
    method_wrapper = functools.wraps
else:
    #/************************************************************************/
    def _enabled_decorators():
        return True
    #/************************************************************************/
    @wrapt.decorator(enabled=_enabled_decorators)
    def method_wrapper(wrapped, instance, _args, _kwargs):
        return wrapped(*_args, **_kwargs)

    
#/****************************************************************************/
# Method decorator 
#/****************************************************************************/
try:
    assert _MethodDecorator
except:
    #/****************************************************************************/
    class _MethodDecorator(object):    
        """Decorator that knows the class the decorated method is bound to.
        
        Original source code: :meth:`method_decorator`, available at:
        https://github.com/denis-ryzhkov/method_decorator
        
        .. code-block:: python
            
           import docdeco
           class new_decorator(docdeco.__MethodDecorator):
               # ...        
            
        The new implemented class :meth:`__MethodDecorator`:
        - knows the class the decorated method is bound to.
        - hides decorator traces by answering to system attributes more correctly than 
          another decorator class like :meth:`functools.wraps` does.
        - deals with bound an unbound instance-methods, class-methods, static-methods, 
          and plain functions (likewise the original :meth:`method_decorator` method)
          as well as properties.
                    
        Note
        ----   
       
       |   MIT License - Copyright (C) 2013, Denis Ryzhkov.
        
        See `README <https://github.com/denis-ryzhkov/method_decorator>`_ 
        full description.        
        See also `stackoverflow discussion <http://stackoverflow.com/questions/306130/python-decorator-makes-function-forget-that-it-belongs-to-a-class/3412743#3412743>`_\ .
        """
        
        def __init__(self, func, obj=None, cls=None, method_type='function'):
            self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type
        
        def __get__(self, obj=None, cls=None):
            if self.obj == obj and self.cls == cls:
                return self 
            if self.method_type=='property':
                return self.func.__get__(obj, cls)
            method_type = ( # note that we added 'property'
                'staticmethod' if isinstance(self.func, staticmethod) else
                'classmethod' if isinstance(self.func, classmethod) else
                'property' if isinstance(self.func, property) else 
                'instancemethod'
                )
            return object.__getattribute__(self, '__class__')( 
                self.func.__get__(obj, cls), obj, cls, method_type) 
                
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
    
        def __getattribute__(self, attr_name): 
            if attr_name in ('__init__', '__get__', '__call__', '__getattribute__', 'func', 'obj', 'cls', 'method_type'): 
                return object.__getattribute__(self, attr_name)
            try:
                return getattr(self.func, attr_name)
            except:
                pass
    
        def __repr__(self):
            return self.func.__repr__()

#/****************************************************************************/
def _metaclass_maker(left_metas=(), right_metas=()):
    """Deal with metaclass conflict, i.e. when "the metaclass of a derived class 
    must be a (non-strict) subclass of the metaclasses of all its bases"
        
        >>> metaclass = _metaclass_maker(left_metas=(), right_metas=())
        
    Arguments:
    left_metas,right_metas : class
        classes (not strings) representing the metaclasses to 'merge'; note that
        :Data:`left_metas` has priority over :data:`right_metas`\ .
        
    Note
    ----
    The simplest case where a metatype conflict happens is the following. 
    Consider a class :class:`A` with metaclass :class:`M_A` and a class :class:`B` 
    with an independent metaclass :class:`M_B`; suppose we derive :class:`C` from 
    :class:`A` and :class:`B`. 
    The question is: what is the metaclass of :class:`C` ? Is it :class:`M_A` or
    :class:`M_B` ?    
    The correct answer is :class:`M_C`, where :class:`M_C` is a metaclass that 
    inherits from :class:`M_A` and :class:`M_B`, as in the following graph:

    .. digraph:: metaclass_conflict
    
       "M_A" -> "A"
       "M_B" -> "B"
       "A" -> "C"
       "B" -> "C"
       "M_A" -> "M_C"
       "M_B" -> "M_C"
       "M_C" -> "C"

    Note
    ----
    see http://code.activestate.com/recipes/204197-solving-the-metaclass-conflict/
    """
    def skip_redundant(iterable, skipset=None):
        # redundant items are repeated items or items in the original skipset
        if skipset is None: skipset = set()
        for item in iterable:
            if item not in skipset:
                skipset.add(item)
                yield item    
    def remove_redundant(metaclasses):
        skipset = set([types.ClassType])
        for meta in metaclasses: # determines the metaclasses to be skipped
            skipset.update(inspect.getmro(meta)[1:])
        return tuple(skip_redundant(metaclasses, skipset))    
        # now the core of the function: two mutually recursive functions ##
    memoized_metaclasses_map = {}    
    def get_noconflict_metaclass(bases, left_metas, right_metas):
         # make tuple of needed metaclasses in specified priority order
         metas = left_metas + tuple(map(type, bases)) + right_metas
         needed_metas = remove_redundant(metas)
         # return existing confict-solving meta, if any
         if needed_metas in memoized_metaclasses_map:
           return memoized_metaclasses_map[needed_metas]
         # nope: compute, memoize and return needed conflict-solving meta
         elif not needed_metas:         # wee, a trivial case, happy us
             meta = type
         elif len(needed_metas) == 1: # another trivial case
            meta = needed_metas[0]
         # check for recursion, can happen i.e. for Zope ExtensionClasses
         elif needed_metas == bases: 
             raise TypeError("Incompatible root metatypes", needed_metas)
         else: # gotta work ...
             metaname = '_' + ''.join([m.__name__ for m in needed_metas])
             meta = classmaker()(metaname, needed_metas, {})
         memoized_metaclasses_map[needed_metas] = meta
         return meta         
    def classmaker(left_metas=(), right_metas=()):
        class make_class(type):
            def __new__(meta, name, bases, attrs):
                metaclass = get_noconflict_metaclass(bases, left_metas, right_metas)
                return metaclass(name, bases, attrs)
            #def make_class(name, bases, adict):
            #    metaclass = get_noconflict_metaclass(bases, left_metas, right_metas)
            #    return metaclass(name, bases, adict)
        make_class.__name__ = '__metaclass__'
        return make_class    
    return classmaker(left_metas, right_metas)

#/****************************************************************************/
def _class_decorator(decorator, *attr_names, **kwargs):
    """Class decorator used to automatically decorate a family of methods of a class.

        >>> new_cls = _class_decorator(decorator, *attr_names, **kwargs)(cls)
        
    Arguments
    ---------
    decorator : callable
        universal or specific function/class decorator used to decorate methods
        and subclasses of the class :data:`cls`\ .
    attr_names : str, list of str, optional
        list of methods or classes to be decorated in the new class :data:`new_cls`; 
        if :literal:`None` or :literal:`()`, all instance/static/class methods as
        well as all classes of :data:`cls` are decorated in :data:`new_cls`, excepted 
        those whose names are in :data:`excludes` (if any, see below).
    
    Keyword Arguments
    -----------------
    excludes : list of str, optional
        list of methods or classes to exclude from the list of decorated ones in 
        the new class :data:`new_cls`\ .
    'base' : str, bool, optional
        variable conveying the name of a parent class of the input decorated class 
        :data:`cls` whose attributes will be further decorated; set to :literal:`True` 
        when a default name is selecte (:literal:'Base') and :literal:`False` when the 
        parent class should be ignored.
        
    Returns
    -------
    new_cls : class
        class inherited from :data:`new_cls` where methods and classes whose names 
        match :data:`attr_names` (all if :data:`()`) are decorated using the decorator
        :data:`method_decorator`\ .
    
    Examples
    --------    
    Let's create a method decorator that increments the output of a function on integer:

    >>> increment = lambda x: x+1
    >>> def decorator_increment(func):
    ...     def decorator(*args, **kwargs):
    ...         return increment(func(*args, **kwargs))
    ...     return decorator

    Let's consider a class with two methods:
    
    >>> class A(object):
    ...     def increment_twice(self,x):
    ...          return increment(increment(x))
    ...     def multiply_by_2(self, x):
    ...          return 2*x

    Let's implement different inherited classes using the class decorator:

    >>> @_class_decorator(decorator_increment)
    ... class B(A): # all methods of this class are decorated
    ...     pass
    >>> @_class_decorator(decorator_increment, 'multiply_by_2')
    ... class C(A): # only multiply_by_2 method is decorated
    ...     pass
    
    and test it :
    
    >>> a = A(); b = B(); c = C()
    >>> print a.increment_twice(1)
        3
    >>> print b.increment_twice(1) # decorated with one more call to increment
        4
    >>> print c.increment_twice(1) # not decorated
        3
    >>> print a.multiply_by_2(1)
        2
    >>> print b.multiply_by_2(1)
        3
    >>> print c.multiply_by_2(1) # also decorated
        3
    
    Note
    ----
    See <http://andrefsp.wordpress.com/2012/08/23/writing-a-class-decorator-in-python/>_\ .
    """
    if decorator is None:       return lambda x:x
    base_decorate = kwargs.pop('base', 'Base') 
    if base_decorate is True:   base_decorate = 'Base'
    attr_excludes = kwargs.pop('exclude',())
    attr_names = tuple(set(attr_names)-set(attr_excludes))
    special_members = ['__metaclass__','__module__','__weakref__','__dict__','__class__']#,'__doc__']#analysis:ignore
    # prepare/redefine the decorating method
    ## decorator = method_decorator(method_decorator, *func_names, **func_exclude)
    def _new_decorator(decorated, name):
        try:
            return decorator(decorated, name)
        except TypeError:
            return decorator(decorated)        
    def _optional_decorator(decorated, name):
        if (attr_names in ((),(None,)) or name in attr_names) and name not in attr_excludes:
            return _new_decorator(decorated, name) 
        return decorated
    # the class rebuilder
    def class_rebuilder(_cls): 
        #if _cls is None: _cls = object
        # let's find out if there is already a metaclass attribute to build 
        # on the top of...
        try: 
            meta_cls = _cls.__metaclass__
        except:
            meta_cls = type
        #class metaclass_decorator(MetaInheritor):
        #    @classmethod
        #    def pre_new(meta, name, bases, attrs):
        #        (name, bases, attrs) = MetaInheritor.__new__(meta, name, bases, attrs)
        #        ...
        #        return MetaInheritor.pre_new(name, bases, attrs) 
        class metaclass_decorator(meta_cls):
            def __new__(meta, name, bases, attrs):
                # the name new_cls will be bound (in global scope, in this case) 
                # to a class that in fact isn't the "real" _cls, but a subclass
                # (see below assignment new_cls.__name__ = _cls.__name__). So, 
                # any late-bound reference to that name, like in super() calls 
                # will get the subclass that's masquerading by that name -- that 
                # subclass's superclass is of course the "real" _cls, hence this 
                # may create infinite recursion.
                # to avoid this, we set the bases ('__bases__') classes of new_cls
                # to those of _cls
                bases = _cls.__bases__ 
                attrs.update(_cls.__dict__.copy())
                if base_decorate is not False:
                    [attrs.update({attr: obj}) for base in _cls.__bases__ for (attr,obj) in base.__dict__.items()
                        if not attr in attrs.keys() and base.__name__ == base_decorate]
                #print 'attrs.items', attrs.items
                for attr, obj in attrs.items(): # variant of vars(meta).items()
                    if attr in special_members:
                        continue
                    try: 
                        new_attr = _optional_decorator(obj, attr)
                    except: pass
                    else:
                        attrs[attr] = new_attr                        
                return meta_cls.__new__(meta, name, bases, attrs)
        if _cls.__name__ == '__metaclass__':
            class new_cls(_cls):
                # we deal with the super class of _cls
                def __getattribute__(self, attr): # __getattribute__ is run for every attribute
                    try:    
                        obj = super(new_cls, self).__getattribute__(attr)
                    except: pass # raise DecoratorError('wrong attribute name {}'.format(attr))
                    else:
                        return _new_decorator(obj, attr)
        else:
            class new_cls(_cls):
                # __doc__ = _cls.__doc__
                __metaclass__ = _metaclass_maker(right_metas=(metaclass_decorator,))
                #__metaclass__ = metaclass_maker(left_metas=(meta_cls,),right_metas=(metaclass_decorator,))
        # complete the inheritance
        try:    
            new_cls.__module__ = _cls.__module__ 
        except: pass
        try:    
            new_cls.__name__ = _cls.__name__
        except: pass
        else:
            return new_cls
    return class_rebuilder

      
#/****************************************************************************/
# method/function decorators 
#/****************************************************************************/
def _method_decorator(func_decorator=None, *func_names, **kwargs):
    """Generic method decorator used to automatically decorate all the methods 
    of a given class.
    
        >>> new_func = method_decorator(func_decorator, *func_names, **kwargs)(func)
        
    Arguments
    ---------
    func_decorator : callable
        universal or specific function decorator used to decorate the method
        :data:`func`\ .
    func_names : str, list of str, optional
        list of methods that can be decorated; if :literal:`None` or :literal:`()`, 
        all methods, whatever their names are decorated, unless their names is
        passed to keyword argument :data:`exclude` (if any, see below).
    
    Keyword Argument
    ----------------
    exclude : list of str, optional
        list of methods to exclude from the list of potentially decorated ones.
     """
    func_excludes = kwargs.pop('exclude',())
    func_names = tuple(set(func_names)-set(func_excludes))
    try:
        assert USE_WRAPT and wrapt
    except:   
        if func_decorator is None:
            return _MethodDecorator
        # # solution 1 : original __MethodDecorator
        # method_rebuilder = __MethodDecorator(func_decorator)
        # # solution 2 : __MethodDecorator with options
        #def method_rebuilder(func):
        #    if (func_names in ((),(None,)) or func in func_names) and func not in func_exclude:
        #        @__MethodDecorator
        #        def new_func(*args, **kwargs):
        #            return func(*args, **kwargs)
        #        return new_func
        #    else:
        #        return func
        # the following method_rebuilder is invoked at run time (through __call__)
        class method_rebuilder(_MethodDecorator):
            def __init__(self, func, obj=None, cls=None, method_type='function'):
                _MethodDecorator.__init__(self, func, obj=obj, cls=cls, method_type=method_type)
                setattr(self,'__doc__',object.__getattribute__(func_decorator(self.func), '__doc__'))
            def __call__(self, *args, **kwargs):
                if (func_names in ((),(None,)) or self.func in func_names) and self.func not in func_excludes:
                    return func_decorator(self.func)(*args, **kwargs)                
                else:
                    return self.func(*args, **kwargs)                
            def __getattribute__(self, attr_name): 
                if attr_name in ('__init__','__get__', '__call__', '__getattribute__','__doc__','func', 'obj', 'cls', 'method_type'): 
                    return object.__getattribute__(self, attr_name) # ibid
                return getattr(self.func, attr_name)
    else:
        if func_decorator is None:
            return lambda f: f
        #@wrapt.decorator
        #def method_rebuilder(wrapped, instance, args, kwargs):
        #    return func_decorator(wrapped(*args, **kwargs))
        method_rebuilder = func_decorator(method_wrapper)
    return method_rebuilder

#%%
#==============================================================================
# CLASS _geoDecorators
#==============================================================================
    
class _geoParsing(object):
    """Base class with dummy decorators used to parse and check place and coordinate 
    arguments, and not only, used in the various methods of the geolocation services 
    classes.
    """
    
    KW_PLACE        = 'place'
    KW_LAT          = 'lat'
    KW_LON          = 'lon'
    KW_COORD        = 'coord'
    KW_PROJECTION   = 'proj' 
    
    #/************************************************************************/
    class __parse(object):
        """Base parsing class for geographical entities. All decorators in 
        :class:`_geoDecorators` will inherit from this class.
        """
        def __init__(self, func, obj=None, cls=None, method_type='function'):
            self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type 
            setattr(self,'__doc__',object.__getattribute__(func, '__doc__'))
        def __get__(self, obj=None, cls=None):
            if self.obj == obj and self.cls == cls:
                return self 
            if self.method_type=='property':
                return self.func.__get__(obj, cls)
            method_type = ( # note that we added 'property'
                'staticmethod' if isinstance(self.func, staticmethod) else
                'classmethod' if isinstance(self.func, classmethod) else
                'property' if isinstance(self.func, property) else 
                'instancemethod'
                )
            return object.__getattribute__(self, '__class__')( 
                self.func.__get__(obj, cls), obj, cls, method_type) 
        #def __get__(self, obj, objtype):
        #    # support instance methods
        #    return functools.partial(self.__call__, obj)
        def __getattribute__(self, attr_name): 
            try:
                return object.__getattribute__(self, attr_name) 
            except AttributeError:
                return getattr(self.func, attr_name)
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_place(_MethodDecorator):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with place (topo,geo) names to functions and methods.
        """
        def __call__(self, *args, **kwargs):
            if args not in (None,()):      
                if all([isinstance(a,str) for a in args]):
                    place = list(args)
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    place = args[0]
                else:   
                    raise IOError('input arguments not recognised')
            else:                           
                place = kwargs.pop('place', None)
            if place in (None,[],''):
                raise IOError('no input arguments passed')
            if not isinstance(place,(list,tuple)):
                place = [place,]
            if not all([isinstance(p,str) for p in place]):
                raise IOError('wrong format for input place')
            return self.func(place, **kwargs)

    #/************************************************************************/
    class parse_coordinate(_MethodDecorator):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lng)` geographical coordinates to functions and methods.
        """
        KW_POLYLINE      = 'polyline'
        try:
            if POLYLINE:    import polyline
            else:           polyline = True
            assert polyline
        except:
            polyline = False
            happyWarning('POLYLINE (https://pypi.python.org/pypi/polyline/) not loaded')
        else:
            if POLYLINE:   happyWarning('POLYLINE help: https://github.com/hicsail/polyline')
            pass
        def __call__(self, *args, **kwargs):
            coord, lat, lon, poly = None, None, None, None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = list(args)
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2                                      \
                        and all([isinstance(args[0][i],(tuple,list)) or not hasattr(args[0][i],'__len__') for i in (0,1)]):
                        lat, lon = args[0]
                    elif all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
                elif len(args) == 1 and isinstance(args[0],(tuple,list)) and len(args[0])==2:
                    lat, lon = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],(tuple,list)) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    lat, lon = args
                else:   
                    raise IOError('input coordinate arguments not recognised')
            else:   
                coord = kwargs.pop('coord', None)         
                lat = kwargs.pop('lat', None) or kwargs.pop('x', None)
                lon = kwargs.pop('lon', None) or kwargs.pop('y', None)
                poly = self.polyline and kwargs.get(self.KW_POLYLINE)
            try:
                assert not(coord is None and lat is None and lon is None and poly in (False,None)) 
            except AssertionError:
                raise IOError('no input coordinate arguments passed')
            try:
                assert coord is None or (lat is None and lon is None)
            except AssertionError:
                raise IOError('too many input coordinate arguments')
            if poly not in (False,None):
                # coord = self.polyline.decode(poly)
                return self.func(None, None, **kwargs)
            if coord is not None:
                if not isinstance(coord,(list,tuple)):  
                    coord = [coord]
                try:
                    assert all(['lat' in c and 'lon' in c for c in coord])
                except AssertionError:
                    raise IOError('wrong dictionary keys for input coordinate argument')
                try:
                    lat, lon = [_ for _ in zip(*[(c['lat'], c['lon']) for c in coord])]
                except:
                    raise IOError('wrong input coordinate argument passed')
            if lat is None or lon is None:
                raise IOError('wrong geographical coordinates')
            if not isinstance(lat,(list,tuple)):  
                lat, lon = [lat,], [lon,]
            if not len(lat) == len(lon):
                raise IOError('incompatible geographical coordinates')
            return self.func(lat, lon, **kwargs)
       
    #/************************************************************************/
    class parse_place_or_coordinate(_MethodDecorator):
        """
        """
        def __call__(self, *args, **kwargs):
            try:
                place = _geoParsing.parse_place(lambda p, **kw: p)(*args, **kwargs)
            except:
                place = None
            else:
                kwargs.update({'place': place})
            try:
                lat, lon = _geoParsing.parse_coordinate(lambda l, L, **kw: [l, L])(*args, **kwargs)
            except:
                lat, lon = None, None
            else:
                kwargs.update({'lat': lat, 'lon': lon})
            try:
                assert not(place in ('',None) and lat in ([],None) and lon in ([],None))
            except:
                raise IOError('no geographical entity parsed to define the place')
            try:
                assert place in ('',None) or (lat in ([],None) and lon in ([],None))
            except:
                raise IOError('too many geographical entities parsed to define the place')
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_nuts(_MethodDecorator):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with NUTS information stored in GISCO-like formatted dictionary (from JSON 
        response) to functions and methods.
        """
        KW_RESULTS      = 'results'
        KW_ATTRIBUTES   = 'attributes'
        KW_FIELDNAME    = 'displayFieldName' 
        KW_LAYERID      = 'layerId'
        KW_LAYERNAME    = 'layerName'
        KW_VALUE        = 'value'
        KW_LEVEL        = 'LEVL_CODE'
        KW_NUTS_ID      = 'NUTS_ID' # nuts[self.KW_FIELDNAME]
        KW_CNTR_CODE    = 'CNTR_CODE'
        KW_NUTS_NAME    = 'NUTS_NAME'
        KW_OBJECTID     = 'OBJECTID'
        def __call__(self, *args, **kwargs):
            level = kwargs.pop('level',None)
            nuts, items = None, {}
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    nuts = list(args)
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        nuts = args[0]
            else:   
                nuts = kwargs.pop('nuts', {})   
                items = {self.KW_ATTRIBUTES: kwargs.pop(self.KW_ATTRIBUTES, None),
                         self.KW_FIELDNAME: kwargs.pop(self.KW_FIELDNAME, None),
                         self.KW_LAYERID: kwargs.pop(self.KW_LAYERID, None),
                         self.KW_LAYERNAME: kwargs.pop(self.KW_LAYERNAME, None),
                         self.KW_VALUE: kwargs.pop(self.KW_VALUE, None)}
            try:
                assert not(nuts in ({},None) and all([v in ([],None) for v in items.values()]))
            except AssertionError:
                # raise IOError('no input NUTS parsed')
                return self.func(None, *args, **kwargs)
            try:
                assert nuts in ({},None) or all([v in ([],None) for v in items.values()])
            except AssertionError:
                raise IOError('too many input file arguments')
            else:
                nuts = items if nuts in ({},None) else nuts
            if nuts in ((),[],None) or                                              \
                (isinstance(nuts,dict) and all([n in ([],None) for n in nuts.values()])):
                # raise IOError('no NUTS parsed')
                return self.func(*args, **kwargs)
            if not isinstance(nuts,(list,tuple)):
                nuts = [nuts,]
            if not all([isinstance(n,dict) and self.KW_ATTRIBUTES in n for n in nuts]): 
                raise IOError('NUTS attributes not recognised')
            if level is not None:
                nuts = [n for n in nuts if n[self.KW_ATTRIBUTES][self.KW_LEVEL] == str(level)]
            return self.func(nuts, **kwargs)

    #/************************************************************************/
    class parse_geometry(_MethodDecorator):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lng)` geographical coordinates stored in GISCO-like
        formatted dictionary (from JSON response) to functions and methods.
        """
        KW_FEATURES     = 'features'
        KW_GEOMETRY     = 'geometry'
        KW_PROPERTIES   = 'properties'
        KW_TYPE         = 'type'
        KW_OSM_KEY      = 'osm_key'
        KW_COORDINATES  = 'coordinates'
        def __call__(self, *args, **kwargs):
            coord = None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
            else:   
                coord = kwargs.pop('coord', None)        
            if coord is not None:
                if isinstance(coord,(list,tuple)) and all([isinstance(c,dict) for c in coord]):      
                    coord_ = [c for c in coord                                                               \
                       if self.KW_GEOMETRY in c and self.KW_PROPERTIES in c and self.KW_TYPE in c                 \
                       and c[self.KW_TYPE]=='Feature'                                                 \
                       and (not(settings.CHECK_TYPE) or c[self.KW_GEOMETRY][self.KW_TYPE]=='Point')         \
                       and (not(settings.CHECK_OSM_KEY) or c[self.KW_PROPERTIES][self.KW_OSM_KEY]=='place') \
                       ]
                    coord = coord[0] if coord_==[] else coord_[0]  
                    coord = dict(zip(['lon','lat'],coord[self.KW_GEOMETRY][self.KW_COORDINATES]))
                kwargs.update(coord) 
                return self.func(**kwargs)
            else:
                return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_projection(_MethodDecorator):
        """Generic class decorator used to parse keyword argument with projection 
        information to functions and methods.
        """
        PROJECTION      = {'WGS84': 4326, 4326: 4326,
                           4258: 4258,
                           'EPSG3857': 3857, 3857: 3857, 
                           'LAEA': 3035, 3035: 3035}
        def __call__(self, *args, **kwargs):
            proj = kwargs.pop('proj', 'WGS84')
            if proj in ('',None):
                return self.func(None,*args, **kwargs)
            if proj not in list(self.PROJECTION.keys() | self.PROJECTION.values()):
                raise IOError('projection %s not supported' % proj)
            kwargs.update({'proj': self.PROJECTION[proj]})                  
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_year(_MethodDecorator):
        """Generic class decorator used to parse keyword year argument used for  
        NUTS definition.
        """
        YEARS      = [2006, 2013, 2010, # 2016 ?
                      ]
        def __call__(self, *args, **kwargs):
            year = kwargs.pop('year', 2013)
            if year in ([],None):
                return self.func(None, *args, **kwargs)
            if year not in tuple(self.YEARS):
                raise IOError('year %s not supported' % year)
            kwargs.update({'year': year})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_file(__parse):
        """
        """
        def __call__(self, *args, **kwargs):
            dirname, basename, filename = None, None, None
            if args not in (None,()):      
                if len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2 and all([isinstance(args[0][i],str) for i in (0,1)]):
                        dirname, basename = args[0]
                    elif all([isinstance(args[0][i],str) for i in range(len(args[0]))]):
                        filename = args[0]
                elif len(args) == 1 and isinstance(args[0],str) and len(args[0])==2:
                    dirname, basename = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],str) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    dirname, basename = args
                else:   
                    raise IOError('input file arguments not recognised')
            else:   
                dirname = kwargs.pop('dir', '')         
                basename = kwargs.pop('base', '')
                filename = kwargs.pop('file', '')
            try:
                assert not(filename in ('',None) and basename in ('',None))
            except AssertionError:
                raise IOError('no input file arguments passed')
            try:
                assert filename in ('',None) or basename in ('',None)
            except AssertionError:
                raise IOError('too many input file arguments')
            if filename is None:
                try:
                    filename = os.path.join(os.path.realpath(dirname or ''), basename)
                except:
                    raise IOError('wrong input file argument passed')
            if not isinstance(filename,str):
                filename = [filename,]
            return self.func(filename, **kwargs)

    #/************************************************************************/
    class parse_route(_MethodDecorator):
        """
        """
        KW_CODE         = 'code'
        KW_ROUTES       = 'routes'
        KW_WAYPOITNS    = 'waypoints'
        def __call__(self, *args, **kwargs):
            pass
    

#/****************************************************************************/
#_docString 
#/****************************************************************************/
class _docString(object):
    """A bunch of docstrings classes, metaclasses and methods decorators.
    """
    #/************************************************************************/
    @classmethod
    def _format_obj(cls, **kwargs):
        """Create a decorator that applies on any kind of object and returns an 
        updated docstring through rewritting/reformating (possibly emptying) of 
        the :literal:`__doc__` special attribute of the considered object.
        
            >>> doc_rebuilder = Docstring._format_obj(**kwargs)
            
        Keyword Arguments
        -----------------
        kwargs : dict
            strings too look for and replace in the docstring documentation of the
            considered object; if :literal:`VOID` is passed as :literal:`True`, an
            empty string is returned.
            
        Returns
        -------
        doc_rebuilder : function
            a function that returns a string.
            
        Example
        -------
        >>> class DummyClass(object):
        ...     \"\"\"A {quality_doc} documentation for a {quality_class} class.\"\"\"
        ...     def dummy_method():
        ...         \"\"\"{x} documentation, like his father {y}.\"\"\"
        ...         return   
        >>> print Docstring._format_obj(quality_doc='dummy',quality_class='useless')(DummyClass)   
            A dummy documentation for a useless class.
        >>> print Docstring._format_obj(**{'x':'Dummy', 'y':DummyClass.__name__})(DummyClass.dummy_method)     
            Dummy documentation, like his father DummyClass.
        >>> Docstring._format_obj(VOID=True)(DummyClass)
            ''
        """
        def doc_rebuilder(obj):
            if kwargs.pop('VOID',False):
                return ''
            try:
                doc = getattr(obj,'__doc__')
                assert doc
            except:
                return ''
            else:
                return doc.format(**kwargs) # str(doc).format(**kwargs)
        return doc_rebuilder
            
    #/************************************************************************/
    @classmethod
    def format_method(cls, **kwargs):
        """Method decorator that enables to parameterize the docstring of a method
        by rewritting and reformating (possibly emptying) its :literal:`__doc__` 
        special attribute (and only this).       
            
            >>> new_func = Docstring.format_method(**kwargs)(func)
    
        Example
        ------- 
        Let's consider a dummy function whose documentation will be decorated:
        
        >>> def dummy_method():
        ...     \"\"\"A certainly {quality} documentation.\"\"\"
        ...     return            
        
        We can then adapt this 'base' function:
        
        >>> useless_method = Docstring.format_method(quality='useless')(dummy_method)
        >>> print useless_method.__doc__
            A certainly useless documentation.
        >>> useful_method = Docstring.format_method(quality='useful')(dummy_method)
        >>> print useful_method.__doc__
            A certainly useful documentation.
            
        We can even 'empty' the documentation using the :literal:`VOID` keyword:

        >>> empty_method = Docstring.format_method(VOID=True)(dummy_method)
        >>> empty_method.__doc__
            ''                
            
        Note that, as it is, the docstring of the base function looks rather irrelevant:
        
        >>> print dummy_method.__doc__
            A certainly {quality} documentation.
        
        In particular :literal:`staticmethod` and :literal:`classmethod` objects are 
        also supported (i.e. instance methods as well as normal functions) thanks
        to the :mod:`wrapt` module and the :class:`FunctionWrapper` class therein::
            
            class A(object):
            
                @Docstring.format_method(quality='static')
                @staticmethod
                def decorated_static_method():
                    \"\"\"A {quality} method documentation.\"\"\"
                    return            
            
                @Docstring.format_class(quality='class')
                @classmethod
                def decorated_class_method():
                    \"\"\"A {quality} method documentation.\"\"\"
                    return            
        
        where the decorator is inserted prior to the method closure definition
        (special decorators :literal:`@staticmethod` and :literal:`@classmethod`).
        Therefore, the methods are decorated as expected:
        
            >>> print A.decorated_static_method.__doc__
                A static method documentation.
            >>> A.decorated_class_method.__doc__
                A class method documentation.
        
        See also
        --------
        :meth:`format_class`
        """   
        _doc_formatter = cls._format_obj(**kwargs)                       
        ## using functools.wraps: this will work but the method type of any bounded
        ## function (static, instance or class method) is also altered
        #def _func_decorator(func):
        #    new_func = functools.wraps(func)(func)
        #    new_func.__doc__ = _doc_formatter(func)
        #    return new_func
        try:
            assert USE_WRAPT and wrapt
        except AssertionError:   
            class _func_decorator(_MethodDecorator):
                def __init__(self, func, obj=None, cls=None, method_type='function'):
                    #super(_func_decorator,self).__init__(func, obj=obj, cls=cls, method_type=method_type)
                    _MethodDecorator.__init__(self, func, obj=obj, cls=cls, method_type=method_type)
                    # we had one attribute wrt. a standard method_decorator instance
                    setattr(self,'__doc__',_doc_formatter(self.func))
                def __getattribute__(self, attr_name): 
                    # we ensure that the docstring which is the __doc__ attribute of the
                    # decorator, not that of the function itself
                    if attr_name in ('__doc__',):
                        return object.__getattribute__(self, attr_name) 
                    # otherwise behaves like the superclass class
                    #return super(_func_decorator,self).__getattribute__(attr_name)
                    return _MethodDecorator.__getattribute__(self, attr_name)
        else:
            def _func_decorator(func):
                #@my_wrapper
                #def new_func(*_args, **_kwargs):
                #   return func(*_args, **_kwargs)
                new_func = _method_decorator(func)
                #new_func = method_wrapper(func)
                # now we update the '__doc__' by recycling the doc already commited in 
                # the FunctionWrapper object new_func: this enables avoiding issues when
                # dealing with classmethod or staticmethod methods:
                #    "AttributeError: 'classmethod' object attribute '__doc__' is read-only"
                try:    # write on the wrapper...
                    new_func.__doc__ = _doc_formatter(new_func)
                except: 
                    # still, we allow this type of error, as it may occur in the case the
                    # order of closures was not well set, e.g. by implementing:
                    #    @classmethod
                    #    @Docstring.format_class(**kwargs)
                    # instead of:
                    #    @Docstring.format_class(**kwargs)
                    #    @classmethod
                    pass
                return new_func
        return _func_decorator

    #/************************************************************************/
    @classmethod
    def format_class(cls, **kwargs):
        """Ibid :meth:`format_method` for decorating classes by rewritting and 
        reformating (possibly emptying) their :literal:`__doc__` special attributes.       
            
            >>> new_cls = Docstring.format_class(**kwargs)(cls)
    
        Examples
        -------- 
        Let's consider a dummy function whose documentation will be decorated:
        
        >>> class dummy_class(object):
        ...     \"\"\"A certainly {quality} documentation.\"\"\"
        ...     pass            
                
        >>> useless_class = Docstring.format_class(quality='useless')(dummy_class)
        >>> print useless_class.__name__
            dummy_class
        >>> print useless_class.__doc__
            A certainly useless documentation.                
            
        However, in the case an :literal:`empty` keyword is passed, the docstring will
        be emptied (even in the case other keyword arguments are present)
        
        >>> empty_class = Docstring.format_class(VOID=True)(dummy_class)
        >>> empty_class.__doc__
            ''
        >>> empty_class = Docstring.format_class(quality='useless', VOID=True)(dummy_class)
        >>> empty_class.__doc__
            ''
            
        See also
        --------
        :meth:`format_method`
        """     
        _doc_formatter = cls._format_obj(**kwargs)                       
        try:
            assert wrapt
            happyWarning('wrapt based class decorator not implemented')
        except:
            pass
        finally:
            def _class_decorator(_cls):
                try: 
                    meta_cls = _cls.__metaclass__
                except:
                    meta_cls = type
                class metaclass_decorator(meta_cls):
                    def __new__(meta, name, bases, attrs):
                        name = _cls.__name__
                        attrs = _cls.__dict__
                        bases = _cls.__bases__
                        return meta_cls.__new__(meta, name, bases, attrs)
                metaclass_decorator.__name__ = '__metaclass__'
                class new_cls(_cls):
                    __metadata__ = metaclass_decorator
                    # We set the __doc__ directly when defining the new class, as to avoid the
                    # 'non-writable' issue with __doc__
                    # indeed attribute '__doc__' of 'type' objects is not writable:
                    #    "AttributeError: attribute '__doc__' of 'type' objects is not writable"
                    # hence new-style classes (child of 'object' type) have non writable docstring
                    __doc__ = _doc_formatter(_cls)
                    # override new_cls.__init__ to prevent recursion, because new_cls.__init__ 
                    # is _cls.__init__ and it keeps calling itself.
                # name set after the class declaration
                try:
                    new_cls.__name__ = _cls.__name__
                except: pass
                try:
                    new_cls.__module__ = _cls.__module__
                except: pass
                return new_cls
        return _class_decorator

    #/************************************************************************/
    @classmethod
    def format(cls, **kwargs):
        """Universal decorator that enables to parameterize the docstring of any method 
        or class by rewritting and reformating (possibly emptying) its :literal:`__doc__` 
        special attribute (and only this).  
            
            >>> new_obj = Docstring.format(**kwargs)(obj)
    
        Examples
        -------- 
        The format conversion method can be applied indifferently over classes or methods:
        
        >>> class dummy_class(object):
        ...     \"\"\"A certainly {quality} documentation.\"\"\"
        ...     pass            
        >>> useful_class = Docstring.format(quality='useful')(dummy_class)
        >>> print useful_class.__doc__
            A certainly useful documentation.
        >>> def dummy_method():
        ...     \"\"\"A certainly {quality} documentation.\"\"\"
        ...     return            
        >>> useless_method = Docstring.format(quality='useless')(dummy_method)
        >>> print useless_method.__doc__
            A certainly useless documentation.
      
        Note
        ----
        Mostly a copy/paste of :meth:`format_method` and :meth:`format_class` methods.
      
        See also
        --------
        :meth:`format_method`, :meth:`format_class`        
        """
        def _decorator(obj):
            if inspect.isclass(obj):
                _class_decorator = cls.format_class(**kwargs)                       
                return _class_decorator(obj)
            else:
                _func_decorator = cls.format_method(**kwargs)                       
                return _func_decorator(obj)
        return _decorator
        
    #/************************************************************************/
    @classmethod
    def decorate(cls, attr_names=None, **kwargs):
        """Universal decorator that enables to parameterize the docstring of any
        class by rewritting and reformating (possibly emptying) the :literal:`__doc__` 
        special attributes (and only this) of all its members.  
            
            >>> new_cls = Docstring.decorate(attr_names=None, **kwargs)(cls)
    
        Examples
        --------
         
        Note
        ----
        Inside this project, we also use the :meth:`decorate` method to decorate, 
        through the special attribute :literal:`__metaclass__`, all methods inherited 
        from :data:`base` classes, namely::
        
            class Base(object):
                def dummy_method_from_Base():
                    \"\"\"A certainly {quality} documentation that is decorated.\"\"\"
                    return
                    
            class Derived(Base):
                @Docstring.decorate(Base.__dict__.keys(),quality='useful')
                class __metaclass__(type): pass
                def dummy_method_from_Derived():
                    \"\"\"A certainly {quality} documentation that is left as it is.\"\"\"
                    return            
                
        as indeed, this way, the methods inherited from :class:`Base`, and those only,
        are decorated:
        
        >>> print Derived.dummy_method_from_Derived.__doc__ # not decorated
            A certainly {quality} documentation that is left as it is.
        >>> print Derived.dummy_method_from_Base.__doc__
            A certainly useful documentation that is decorated.
        """
        if attr_names is None:
            attr_names = ()
        elif not isinstance(attr_names,(list,tuple)):
            raise happyError('type {} not accepted for list/tuple of decorated members'.format(type(attr_names)))
        # various local objects
        obj_decorator = cls._format_obj(**kwargs)#analysis:ignore
        format_decorator = cls.format(**kwargs)#analysis:ignore
        str_format = lambda s: s.format(**kwargs) if s is not None else ''                   
        special_members = ['__metaclass__','__module__','__weakref__','__dict__','__class__']#analysis:ignore
        def decorator(obj, obj_name=None):
             # deal with special '__doc__' member
            if obj_name=='__doc__':
                try:    
                    return str_format(obj)
                except:  return obj or ''
            # don't consider other special members and other special members unless 
            # it is explicitely to decorate them (e.g. __init__)
            elif obj_name in special_members:                               \
                # or (obj_name.startswith('__') and obj_name.endswith('__') and obj_name not in attr_names):
                return obj
            # deal with properties
            elif isinstance(obj, property):                 
                try:   
                    return property(obj.__get__, obj.__set__, obj.__delattr__, str_format(obj.__doc__))
                except:  return obj # e.g. property not decorated
            # deal with class members
            elif inspect.isclass(obj):
                try: 
                    return cls.format_class(**kwargs)(obj) 
                except: return obj
            # deal with method members
            elif inspect.isroutine(obj): # inspect.ismethod(obj):
                try: 
                    return  cls.format_method(**kwargs)(obj) 
                except: return obj
            ## deal with attribute members
            else: 
                try: # whenever __doc__ is writeable
                    obj.__doc__ = obj_decorator(obj)
                    return obj
                except: 
                    return obj
        return _class_decorator(decorator, *attr_names)
