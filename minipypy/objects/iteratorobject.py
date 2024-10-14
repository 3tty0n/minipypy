from minipypy.objects.baseobject import W_Root

class W_IteratorObject(W_Root):
    _immutable_fields_ = ["wrappteditems"]

    def __init__(self, wrappeditems):
        self.wrappeditems = wrappeditems
