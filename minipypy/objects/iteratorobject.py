from minipypy.objects.baseobject import W_Root

from rpython.rlib.jit import elidable, unroll_safe

class W_IteratorObject(W_Root):
    _immutable_fields_ = ["wrappteditems"]

    def __init__(self, wrappeditems):
        self.wrappeditems = wrappeditems

    @elidable
    def unwrap(self):
        return self.wrappeditems

    def unpack(self, count):
        for i in range(count):
            yield self.unwrap()[-1-i]
