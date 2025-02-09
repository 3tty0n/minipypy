from minipypy.objects.baseobject import W_Root
from minipypy.objects.dictobject import W_Dict

class Module(W_Root):
    _immutable_fields_ = ["w_dict"]

    def __init__(self):
        self.w_dict = W_Dict()
