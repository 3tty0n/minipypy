from minipypy.objects.baseobject import *
from minipypy.objects.iteratorobject import W_IteratorObject

from rpython.rlib import jit

class W_TupleObject(W_IteratorObject):

    def __repr__(self):
        return self.getrepr()

    @jit.elidable
    def unwrap(self):
        return self.wrappeditems

    def getrepr(self):
        s = "("
        for item in self.wrappeditems:
            s += item.getrepr()
            s += ", "
        s += ")"
        return s

    def is_true(self):
        return len(self.wrappeditems) != 0

    @staticmethod
    def from_list(lst):
        return W_TupleObject(lst)

    def not_(self):
        if len(self.wrappeditems) == 0:
            return W_BoolObject.W_True
        return W_BoolObject.W_False
