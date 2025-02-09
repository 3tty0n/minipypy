from minipypy.objects.baseobject import (
    W_IntObject, W_FloatObject, W_NoneObject, W_BoolObject
)

from rpython.rlib.objectmodel import not_rpython


class ObjSpace(object):

    def __init__(self):
        self.builtin_modules = {}
        self.reloading_modules = {}

        self.initialize()


    @not_rpython
    def initialize(self):
        pass

    @not_rpython
    def make_builtins(self):
        from pypy.module.__builtin__.moduledef import Module
        w_name = self.newtext('__builtin__')
        self.builtin = Module(self, w_name)
        w_builtin = self.wrap(self.builtin)
        w_builtin.install()
        self.setitem(self.builtin.w_dict, self.newtext('__builtins__'), w_builtin)

        bootstrap_modules = set(('__builtin__'))
        installed_builtin_modules = list(bootstrap_modules)

        # initialize with "bootstrap types" from objspace  (e.g. w_None)
        types_w = (self.get_builtin_types().items() +
                   exception_types_w.items())
        for name, w_type in types_w:
            self.setitem(self.builtin.w_dict, self.newtext(name), w_type)

        installed_builtin_modules.sort()
        w_builtin_module_names = self.newtuple(
            [self.wrap(fn) for fn in installed_builtin_modules])

        # force this value into the dict without unlazyfying everything
        self.setitem(self.sys.w_dict, self.newtext('builtin_module_names'),
                     w_builtin_module_names)


class StdObjectSpace(ObjSpace):

    @not_rpython
    def initialize(self):
        self.IntObjectCls = W_IntObject
        self.FloatObjectCls = W_FloatObject

        # singletons
        self.w_None = W_NoneObject.w_None
        self.w_False = W_BoolObject.w_False
        self.w_True = W_BoolObject.w_True
