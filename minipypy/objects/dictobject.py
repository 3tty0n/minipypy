from rpython.rlib.jit import elidable, promote

from minipypy.objects.baseobject import W_RootObject

class Map(object):
    def __init__(self):
        self.indexes = {}
        self.other_maps = {}

    @elidable
    def getindex(self, name):
        return self.indexes.get(name, -1)

    @elidable
    def new_map_with_additional_name(self, name):
        if name not in self.other_maps:
            newmap = Map()
            newmap.indexes.update(self.indexes)
            newmap.indexes[name] = len(self.indexes)
            self.other_maps[name] = newmap
        return self.other_maps[name]


EMPTY_MAP = Map()


class W_Dict(W_RootObject):

    def __init__(self):
        self.map = EMPTY_MAP
        self.storage = []

    def __repr__(self):
        return self.get_repr()

    def get_repr(self):
        s = "{"
        for i in range(len(self.storage)):
            s += str(self.storage[i])
            s += ", "
        s += "}"
        return s

    def __getitem__(self, w_key):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            return self.storage[index]
        return None

    def __setitem__(self, w_key, w_val):
        map = promote(self.map)
        index = map.getindex(w_key)
        if index != -1:
            self.storage[index] = w_val
            return
        self.map = map.new_map_with_additional_name(w_key)
        self.storage.append(w_val)
