from rpython.rlib.jit import elidable, promote

from minipypy.objects.baseobject import W_Root
from minipypy.objects.mapobject import Map

EMPTY_MAP = Map()

class W_Dict(W_Root):

    def __init__(self):
        self.map = EMPTY_MAP
        self.storage = []

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        s = "{"
        for i in range(len(self.storage)):
            s += str(self.storage[i])
            s += ", "
        s += "}"
        return s

    def get(self, w_key):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            return self.storage[index]
        return None

    __getitem__ = get

    def set(self, w_key, w_val):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            self.storage[index] = w_val
            return
        self.map = map.new_map_with_additional_name(w_key)
        self.storage.append(w_val)

    __setitem__ = set
