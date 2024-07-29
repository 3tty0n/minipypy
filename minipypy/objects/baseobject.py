class W_Root(object):
    def __init__(self, value):
        self.value = value


class W_Object(W_Root):
    typ = "object"

    pass


class W_None(W_Root):
    typ = "none"

    def __init__(self):
        pass

    def __repr__(self):
        return "None"


class W_Int(W_Root):
    typ = "int"

    def __repr__(self):
        return "%d" % (self.value)

    def add(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value + other.value)
        elif isinstance(other, W_Long):
            return W_Long(self.value + other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value - other.value)
        elif isinstance(other, W_Long):
            return W_Long(self.value - other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value * other.value)
        elif isinstance(other, W_Long):
            return W_Long(self.value * other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def div(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value / other.value)
        elif isinstance(other, W_Long):
            return W_Long(self.value / other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))


class W_Long(W_Root):
    typ = "long"

    def __repr__(self):
        return "%dL" % (self.value)

    def add(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Int(self.value + other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Int(self.value - other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Int(self.value * other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def div(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Int(self.value / other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))


class W_Str(W_Root):

    typ = "str"

    def __init__(self, value):
        self.value = str(value)

    def __repr__(self):
        return "'%s'" % self.value

    def add(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Str(self.value + str(other.value))
        elif isinstance(other, W_Str) or isinstance(other, W_Byte):
            return W_Str(self.value + str(other.value))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        raise Exception(
            "Unsupported operand type(s) for -: %s and %s" % (self.typ, other.typ)
        )

    def mul(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Str(self.value * other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))


class W_Byte(W_Root):

    typ = "byte"

    def __init__(self, value):
        self.value = bytes(value)

    def __repr__(self):
        return "b'%b'" % self.value

    def add(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Str(str(self.value) + other.value)
        elif isinstance(other, W_Str) or isinstance(other, W_Byte):
            return W_Str(str(self.value) + other.value)
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        raise Exception(
            "Unsupported operand type(s) for -: %s and %s" % (self.typ, other.typ)
        )

    def mul(self, other):
        if isinstance(other, W_Int) or isinstance(other, W_Long):
            return W_Str(self.value * other.value)
        else:
            raise Exception(
                "Unsupported operand type(s) for *: %s and %s" % (self.typ, other.typ)
            )


class W_Sequence(W_Root):
    typ = "sequence"

    def __init__(self, values):
        self.values = values


class W_Tuple(W_Sequence):
    typ = "tuple"

    def __repr__(self):
        s = "("
        for item in self.values:
            s += repr(s)
            s += ", "
        s += ")"
        return s


class W_List(W_Sequence):
    typ = "list"

    def __repr__(self):
        s = "["
        for item in self.values:
            s += repr(s)
            s += ", "
        s += "]"
        return s


class W_Code(W_Root):
    def __repr__(self):
        return repr(self.value)


class W_Function(W_Root):
    def __init__(self, body, defaults):
        self.body = body
        self.defaults = defaults

    def __repr__(self):
        return "Function(%s, %s)" % (self.body, self.defaults)
