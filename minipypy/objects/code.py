from minipypy.objects.abstract_object import W_Root


class W_Code(W_Root):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)
