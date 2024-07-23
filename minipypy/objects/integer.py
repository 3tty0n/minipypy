from minipypy.objects.abstract_object import W_Root

class W_Integer(W_Root):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Int(%d)" % (self.value)

    def add(self, other):
        if isinstance(other, W_Integer):
            return W_Integer(self.value + other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_Integer):
            return W_Integer(self.value - other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_Integer):
            return W_Integer(self.value * other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))
