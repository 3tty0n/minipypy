from minipypy.objects.baseobject import W_Root, W_StrObject
from minipypy.objects.dictobject import Map, W_Dict

from rpython.rlib.jit import elidable, hint, unroll_safe

class W_ClassObject(W_Root):
    _immutable_fields_ = ["bases_w?[*]", "w_dict?"]

    def __init__(self, w_name, bases_w, w_dict):
        assert isinstance(w_name, W_StrObject)
        self.name = w_name.value
        assert isinstance(bases_w, list)
        self.bases_w = bases_w   # base classes tuple
        assert isinstance(w_dict, W_Dict)
        self.w_dict = w_dict     # methods dictionary

    def getrepr(self):
        return "class"

    def getdict(self):
        return self.w_dict

    def getdictvalue(self, attr):
        assert isinstance(attr, str)
        w_dict = self.getdict()
        if w_dict is not None:
            return w_dict.get(attr)
        return None

    def instantiate(self):
        return W_InstanceObject(self)

    def find_method(self, attr):
        return self.getdict().get(attr)

    @unroll_safe
    def is_subclass_of(self, other):
        assert isinstance(other, W_ClassObject)
        if self is other:
            return True
        for base in self.bases_w:
            assert isinstance(base, W_ClassObject)
            if base.is_subclass_of(other):
                return True
        return False

    @unroll_safe
    def lookup(self, attr):
        assert isinstance(attr, str)
        w_result = self.w_dict.get(attr)
        if w_result is not None:
            return w_result
        for base in self.bases_w:
            assert isinstance(base, W_ClassObject)
            w_result = base.lookup(attr)
            if w_result is not None:
                return w_result
        return None


EMPTY_MAP = Map()


class W_InstanceObject(W_Root):
    _immutable_fields_ = ['w_class']

    def __init__(self, w_class):
        assert isinstance(w_class, W_ClassObject)
        self.w_class = w_class
        self.map = EMPTY_MAP
        self.storage = [None] * 16
        self.storage_index = 0

    def storage_append(self, value):
        storage_index = hint(self.storage_index, promote=True)
        self.storage[storage_index] = value
        self.storage_index = storage_index + 1

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return "%s instance" % (self.w_class.name)

    def getfield(self, name):
        map = hint(self.map, promote=True)
        index = map.getindex(name)
        if index != -1:
            return self.storage[index]
        raise AttributeError(name)

    def write_attribute(self, name, value):
        map = hint(self.map, promote=True)
        name = name.value
        index = map.getindex(name)
        if index != -1:
            self.storage[index] = value
            return
        self.map = map.new_map_with_additional_attribute(name)
        self.storage_append(value)

    def getattr(self, name):
        try:
            return self.getfield(name)
        except AttributeError:
            return self.w_class.find_method(name)
