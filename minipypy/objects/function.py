from minipypy.objects.abstract_object import W_Root


class W_Function(W_Root):
    def __init__(self, body, defaults):
        self.body = body
        self.defaults = defaults

    def __repr__(self):
        return "Function(%s, %s)" % (self.body, self.defaults)
