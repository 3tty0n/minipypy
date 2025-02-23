from minipypy.objects.baseobject import *
from minipypy.objects.listobject import W_List, W_ListObject

class ObjSpace(object):
    def __init__(self):
        self.builtin_modules = {}
        self.reloading_modules = {}

        self.builtin_functions_by_identifier = {'': None}

    def startup(self):
        raise NotImplementedError

    def finish(self):
        raise NotImplementedError



class StdObjSpace(ObjSpace):
    def __init__(self):
        pass

    def newlong(self, val): # val is an int
        return W_LongObject.from_int(val)

    def newint(self, val):
        return W_IntObject.from_int(val)

    def newbool(self, val):
        return W_BoolObject.from_bool(val)

    def newlist(self, list_w, sizehint=-1):
        assert not list_w or sizehint == -1
        return W_List().instantiate(list_w)
