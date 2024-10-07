from minipypy.objects.baseobject import W_RootObject
from minipypy.objects.objectobject import W_Instance, W_Class

class W_IteratorObject(W_Class):
    _immutable_fields_ = ["wrappteditems"]

    def __init__(self, wrappeditems):
        self.wrappeditems = wrappeditems
