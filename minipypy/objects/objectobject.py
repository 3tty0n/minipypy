from minipypy.objects.baseobject import W_Root
from minipypy.objects.dictobject import Map

from rpython.rlib.jit import elidable, not_rpython, hint

class W_Class(W_Root):
    def __init__(self, name):
        self.name = name
        self.methods = {} # { key: str -> value: method }

    def instantiate(self):
        return W_Instance(self)

    def find_method(self, name):
        result = self.methods.get(name)
        if result is not None:
            return result
        raise AttributeError(name)

    def write_method(self, name, value):
        self.methods[name] = value


EMPTY_MAP = Map()


class W_Instance(W_Root):
    def __init__(self, cls):
        self.cls = cls
        self.map = EMPTY_MAP
        self.storage = []

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return self.cls.getrepr()

    def getfield(self, name):
        map = hint(self.map, promote=True)
        index = map.getindex(name)
        if index != -1:
            return self.storage[index]
        raise AttributeError(name)

    def write_attribute(self, name, value):
        map = hint(self.map, promote=True)
        index = map.getindex(name)
        if index != -1:
            self.storage[index] = value
            return
        self.map = map.new_map_with_additional_attribute(name)
        self.storage.append(value)

    def getattr(self, name):
        try:
            return self.getfield(name)
        except AttributeError:
            return self.cls.find_method(name)
