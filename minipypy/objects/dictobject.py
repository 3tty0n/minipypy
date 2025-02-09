import weakref, sys

from rpython.rlib.jit import elidable, promote, unroll_safe

from minipypy.objects.baseobject import W_Root
from minipypy.objects.mapobject import Map

EMPTY_MAP = Map()

class W_Dict(W_Root):

    def __init__(self):
        self.map = EMPTY_MAP
        self.storage = []

    def __repr__(self):
        return self.getrepr()

    @unroll_safe
    def getrepr(self):
        s = "{"
        for i in range(len(self.storage)):
            s += str(self.storage[i])
            s += ", "
        s += "}"
        return s

    def getitem(self, w_key):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            if index < len(self.storage):
                return self.storage[index]
        return None

    __getitem__ = getitem

    def setitem(self, w_key, w_val):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            self.storage[index] = w_val
            return
        self.map = map.new_map_with_additional_name(w_key)
        self.storage.append(w_val)

    __setitem__ = setitem

    def delitem(self, w_key):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            del self.storage[index]
            return
        raise Exception("%s is not defined" % (w_key))

def init_mapdict_cache(pycode):
    num_entries = len(pycode.co_names)
    pycode._mapdict_caches = [None] * num_entries


def LOAD_ATTR_caching(pycode, w_obj, nameindex):
    pass
