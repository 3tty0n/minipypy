from minipypy.objects.abstract_object import W_Root


class W_Object(W_Root):
    def __init__(self, value):
        self.value = value
