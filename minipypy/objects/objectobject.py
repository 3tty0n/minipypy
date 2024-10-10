from minipypy.objects.baseobject import W_NoneObject, W_RootObject, W_BoolObject, W_StrObject
from minipypy.objects.dictobject import Map

from rpython.rlib.jit import elidable, not_rpython, hint

class W_Class(W_RootObject):
    def __init__(self, name):
        self.name = name
        self.methods = {} # { key: str -> value: method }

    def instantiate(self):
        return W_Instance(self)

    def find_method(self, name):
        assert isinstance(name, W_StrObject)
        result = self.methods.get(name.value)
        if result is not None:
            return result
        raise AttributeError(name)

    def set_method(self, name, value):
        self.methods[name] = value


EMPTY_MAP = Map()


class W_Instance(W_RootObject):
    def __init__(self, obj):
        self.obj = obj
        self.map = EMPTY_MAP
        self.storage = []

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return self.obj.getrepr()

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
            return self.obj.find_method(name)
