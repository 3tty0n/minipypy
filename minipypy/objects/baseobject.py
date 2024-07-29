from rpython.rlib.rbigint import rbigint


class W_Root(object):
    pass


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

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%d" % (self.value)

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def add(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value + other.getvalue())
        elif isinstance(other, W_Long):
            return W_Long(rbigint.fromint(self.value).add(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value - other.getvalue())
        elif isinstance(other, W_Long):
            return W_Long(rbigint.fromint(self.value).sub(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value * other.value)
        elif isinstance(other, W_Long):
            return W_Long(rbigint.fromint(self.value).mul(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def div(self, other):
        if isinstance(other, W_Int):
            return W_Int(self.value / other.getvalue())
        elif isinstance(other, W_Long):
            return W_Long(rbigint.fromint(self.value).div(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))


class W_Long(W_Root):
    typ = "long"

    def __init__(self, value):
        self.value = value  # instance of rbigint

    @staticmethod
    def fromint(intval):
        return W_Long(intval)

    @staticmethod
    def from_rbigint(rbint):
        return W_Long(rbint)

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def __repr__(self):
        return "%dL" % (self.value)

    def add(self, other):
        if isinstance(other, W_Int):
            return W_Long(self.value.add(rbigint.fromint(other.getvalue())))
        elif isinstance(other, W_Long):
            return W_Long(self.value.add(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_Int):
            return W_Long(self.value.sub(rbigint.fromint(other.getvalue())))
        elif isinstance(other, W_Long):
            return W_Long(self.value.sub(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_Int):
            return W_Long(self.value.mul(rbigint.fromint(other.getvalue())))
        elif isinstance(other, W_Long):
            return W_Long(self.value.mul(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))

    def div(self, other):
        if isinstance(other, W_Int):
            return W_Long(self.value.div(rbigint.fromint(other.getvalue())))
        elif isinstance(other, W_Long):
            return W_Long(self.value.div(other.getvalue()))
        else:
            raise Exception("Unexpected object: %s" % (other))


class W_Str(W_Root):

    typ = "str"

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "'%s'" % self.value

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    @staticmethod
    def from_str(strval):
        assert isinstance(strval, str)
        return W_Str(strval)

    def add(self, other):
        if (
            isinstance(other, W_Str)
            or isinstance(other, W_Int)
            or isinstance(other, W_Long)
        ):
            return W_Str(self.getstr() + other.getstr())
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

    def div(self, other):
        raise Exception("Unsupported operaiton /")


class W_Byte(W_Root):

    typ = "byte"

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "b'%b'" % self.value

    def getvalue(self):
        return self.value

    @staticmethod
    def from_str(strval):
        assert isinstance(strval, str)
        return W_Byte(strval)

    def add(self, other):
        raise Exception(
            "Unsupported operand type(s) for +: %s and %s" % (self.typ, other.typ)
        )

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

    def div(self, other):
        raise Exception("Unsupported operaiton /")


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
    "for debugging. contains code object obtained from marshal.load"

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class W_Function(W_Root):
    def __init__(self, body, defaults):
        self.body = body
        self.defaults = defaults

    def __repr__(self):
        return "Function(%s, %s)" % (self.body, self.defaults)