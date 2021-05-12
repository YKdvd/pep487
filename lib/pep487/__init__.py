# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 by Gregor Giesen
#
# This is a backport of PEP487's simpler customisation of class
# creation by Martin Teichmann <https://www.python.org/dev/peps/pep-0487/>
# for Python versions before 3.6.
#
# PEP487 is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PEP487 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PEP487. If not, see <http://www.gnu.org/licenses/>.
#
"""pep487.py: Simpler customisation of class creation"""

import abc
import sys
import types

__all__ = ('PEP487Meta', 'PEP487Object', 'ABCMeta', 'ABC')

HAS_PY36 = sys.version_info >= (3, 6)
HAS_PEP487 = HAS_PY36
IS_PY27 = sys.version_info[:2] == (2, 7)

if HAS_PEP487:
    PEP487Meta = type         # pragma: no cover
    ABCMeta = abc.ABCMeta     # pragma: no cover
    ABC = abc.ABC             # pragma: no cover
    PEP487Base = object       # pragma: no cover
    PEP487Object = object     # pragma: no cover
else:
    class PEP487Meta(type):
        def __new__(mcls, name, bases, ns, **kwargs):
            init = ns.get('__init_subclass__')
            if isinstance(init, types.FunctionType):
                ns['__init_subclass__'] = classmethod(init)
            cls = super(PEP487Meta, mcls).__new__(mcls, name, bases, ns)
            for key, value in cls.__dict__.items():
                func = getattr(value, '__set_name__', None)
                if func is not None:
                    func(cls, key)
            super(cls, cls).__init_subclass__(**kwargs)
            return cls

        def __init__(cls, name, bases, ns, **kwargs):
            super(PEP487Meta, cls).__init__(name, bases, ns)

    class ABCMeta(abc.ABCMeta):
        def __new__(mcls, name, bases, ns, **kwargs):
            init = ns.get('__init_subclass__')
            if isinstance(init, types.FunctionType):
                ns['__init_subclass__'] = classmethod(init)
            cls = super(ABCMeta, mcls).__new__(mcls, name, bases, ns)
            for key, value in cls.__dict__.items():
                func = getattr(value, '__set_name__', None)
                if func is not None:
                    func(cls, key)
            super(cls, cls).__init_subclass__(**kwargs)
            return cls

        def __init__(cls, name, bases, ns, **kwargs):
            super(ABCMeta, cls).__init__(name, bases, ns)

    class PEP487Base(object):
        @classmethod
        def __init_subclass__(cls, **kwargs):
            pass

    if IS_PY27: # to support Python 2.7, we will need the code from six.with_metaclass
        # https://github.com/benjaminp/six/blob/3974f0c4f6700a5821b451abddff8b3ba6b2a04f/six.py#L856
        def with_metaclass(meta, *bases):   # taken from
            # Copyright (c) 2010-2020 Benjamin Peterson
            # Permission is hereby granted, free of charge, to any person obtaining a copy
            # of this software and associated documentation files (the "Software"), to deal
            # in the Software without restriction, including without limitation the rights
            # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            # copies of the Software, and to permit persons to whom the Software is
            # furnished to do so, subject to the following conditions:
            #
            # The above copyright notice and this permission notice shall be included in all
            # copies or substantial portions of the Software.
            """Create a base class with a metaclass."""

            # This requires a bit of explanation: the basic idea is to make a dummy
            # metaclass for one level of class instantiation that replaces itself with
            # the actual metaclass.
            import types
            class metaclass(type):

                def __new__(cls, name, this_bases, d):
                    if sys.version_info[:2] >= (3, 7):
                        # This version introduced PEP 560 that requires a bit
                        # of extra care (we mimic what is done by __build_class__).
                        resolved_bases = types.resolve_bases(bases)
                        if resolved_bases is not bases:
                            d['__orig_bases__'] = bases
                    else:
                        resolved_bases = bases
                    return meta(name, resolved_bases, d)

                @classmethod
                def __prepare__(cls, name, this_bases):
                    return meta.__prepare__(name, bases)

            return type.__new__(metaclass, 'temporary_class', (), {})


    class PEP487Object(with_metaclass(PEP487Meta, PEP487Base)):
        pass

    class ABC(with_metaclass(ABCMeta, PEP487Base)):
        pass