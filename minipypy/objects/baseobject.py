import operator

from rpython.rlib import jit
from rpython.rlib.rbigint import rbigint


class WObjectOperationException(RuntimeError):
    pass


WObjectOperationNotImplemented = WObjectOperationException("Not implemented")


class W_RootObject(object):
    def __repr__(self):
        return "W_RootObject()"

    def getrepr(self):
        return "W_RootObject()"


class W_NoneObject(W_RootObject):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return "None"

    def is_true(self):
        return False


W_NoneObject.W_None = W_NoneObject(None)


class W_BoolObject(W_RootObject):
    def __init__(self, value):
        self.value = value

    def getrepr(self):
        if self.value:
            return "True"
        else:
            return "False"

    def __repr__(self):
        return self.getrepr()

    def is_true(self):
        if self.value:
            return True
        return False

    def not_(self):
        if self.value:
            return W_BoolObject(False)
        else:
            return W_BoolObject(True)

    @staticmethod
    def from_bool(boolprim):
        if boolprim:
            return W_BoolObject(True)
        else:
            return W_BoolObject(False)


W_BoolObject.W_True = W_BoolObject(True)
W_BoolObject.W_False = W_BoolObject(False)


class W_IntObject(W_RootObject):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return "%d" % (self.value)

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def is_true(self):
        return self.value == 0

    @staticmethod
    def from_int(i):
        return W_IntObject(i)

    def add(self, other):
        if isinstance(other, W_IntObject):
            return W_IntObject(self.value + other.getvalue())
        elif isinstance(other, W_LongObject):
            return W_LongObject(rbigint.fromint(self.value).add(other.getvalue()))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_IntObject):
            return W_IntObject(self.value - other.getvalue())
        elif isinstance(other, W_LongObject):
            return W_LongObject(rbigint.fromint(self.value).sub(other.getvalue()))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_IntObject):
            return W_IntObject(self.value * other.value)
        elif isinstance(other, W_LongObject):
            return W_LongObject(rbigint.fromint(self.value).mul(other.getvalue()))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def div(self, other):
        if isinstance(other, W_IntObject):
            return W_IntObject(self.value / other.getvalue())
        elif isinstance(other, W_LongObject):
            return W_LongObject(rbigint.fromint(self.value).div(other.getvalue()))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def true_div(self, other):
        return self.div(other)

    def eq(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.getvalue() == other.getvalue())
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue() == other.getvalue().toint())
        return W_BoolObject.W_True

    def lt(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.getvalue() < other.getvalue())
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue() < other.getvalue().toint())
        return W_BoolObject.W_True

    def le(self, other):
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.getvalue() <= other.getvalue())
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue() <= other.getvalue().toint())
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        return W_BoolObject.W_True

    def gt(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.getvalue() > other.getvalue())
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue() > other.getvalue().toint())
        return W_BoolObject.W_True

    def ge(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.getvalue() >= other.getvalue())
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue() >= other.getvalue().toint())
        return W_BoolObject.W_True


class W_LongObject(W_RootObject):
    def __init__(self, value):
        self.value = value  # instance of rbigint

    def __repr__(self):
        return self.getrepr()

    @staticmethod
    def fromint(intval):
        return W_LongObject(intval)

    @staticmethod
    def from_rbigint(rbint):
        return W_LongObject(rbint)

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def getrepr(self):
        return "%dL" % (self.value.toint())

    def is_true(self):
        if self.value.toint() == 0:
            return False
        return True

    def add(self, other):
        if isinstance(other, W_IntObject):
            return W_LongObject(self.value.add(rbigint.fromint(other.getvalue())))
        if isinstance(other, W_LongObject):
            return W_LongObject(self.value.add(other.getvalue()))
        raise WObjectOperationException("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_IntObject):
            return W_LongObject(self.value.sub(rbigint.fromint(other.getvalue())))
        if isinstance(other, W_LongObject):
            return W_LongObject(self.value.sub(other.getvalue()))
        raise WObjectOperationException("Unexpected object: %s" % (other))

    def mul(self, other):
        if isinstance(other, W_IntObject):
            return W_LongObject(self.value.mul(rbigint.fromint(other.getvalue())))
        elif isinstance(other, W_LongObject):
            return W_LongObject(self.value.mul(other.getvalue()))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def true_div(self, other):
        if isinstance(other, W_IntObject):
            return W_LongObject(self.value.div(rbigint.fromint(other.getvalue())))
        if isinstance(other, W_LongObject):
            return W_LongObject(self.value.div(other.getvalue()))
        raise WObjectOperationException("Unexpected object: %s" % (other))

    def eq(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(
                self.getvalue().eq(rbigint.fromint(other.getvalue()))
            )
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue().eq(other.getvalue()))
        return W_BoolObject.W_False

    def lt(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(
                self.getvalue().lt(rbigint.fromint(other.getvalue()))
            )
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue().lt(other.getvalue()))
        return W_BoolObject.W_True

    def le(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(
                self.getvalue().le(rbigint.fromint(other.getvalue()))
            )
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.getvalue().le(other.getvalue()))
        return W_BoolObject.W_True

    def gt(self, other):
        return other.lt(self)

    def ge(self, other):
        return other.le(self)


class W_StrObject(W_RootObject):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "'%s'" % self.value

    def getrepr(self):
        return "'%s'" % self.value

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def is_true(self):
        return self.value is not ""

    @staticmethod
    def from_str(strval):
        assert isinstance(strval, str)
        return W_StrObject(strval)

    def add(self, other):
        if (
            isinstance(other, W_StrObject)
            or isinstance(other, W_IntObject)
            or isinstance(other, W_LongObject)
        ):
            return W_StrObject(self.getstr() + other.getstr())
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def sub(self, other):
        raise WObjectOperationException("Unsupported operation -")

    def mul(self, other):
        if isinstance(other, W_IntObject):
            return W_StrObject(self.getvalue() * other.getvalue())
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def div(self, other):
        raise WObjectOperationException("Unsupported operaiton /")

    def true_div(self, other):
        raise WObjectOperationException("Unsupported operaiton /")

    def lt(self, other):
        if self.value == "":
            return W_BoolObject.W_False
        if isinstance(other, W_StrObject):
            return W_BoolObject.from_bool(self.getvalue() < other.getvalue())
        if isinstance(other, W_IntObject):
            raise WObjectOperationException("operation strign < int is not implemented")
        if isinstance(other, W_LongObject):
            raise WObjectOperationException(
                "operation strign < long is not implemented"
            )
        return W_BoolObject.W_False

    def le(self, other):
        if self.value == "":
            return W_BoolObject.W_False
        if isinstance(other, W_StrObject):
            return W_BoolObject.from_bool(self.getvalue() <= other.getvalue())
        if isinstance(other, W_IntObject):
            raise WObjectOperationException("operation strign < int is not implemented")
        if isinstance(other, W_LongObject):
            raise WObjectOperationException(
                "operation strign < long is not implemented"
            )
        return W_BoolObject.W_False

    def gt(self, other):
        if self.value == "":
            return W_BoolObject.W_False
        if isinstance(other, W_StrObject):
            return W_BoolObject.from_bool(self.getvalue() > other.getvalue())
        if isinstance(other, W_IntObject):
            raise WObjectOperationException("operation strign < int is not implemented")
        if isinstance(other, W_LongObject):
            raise WObjectOperationException(
                "operation strign < long is not implemented"
            )
        return W_BoolObject.W_False

    def ge(self, other):
        if self.value == "":
            return W_BoolObject.W_False
        if isinstance(other, W_StrObject):
            return W_BoolObject.from_bool(self.getvalue() >= other.getvalue())
        if isinstance(other, W_IntObject):
            raise WObjectOperationException("operation strign < int is not implemented")
        if isinstance(other, W_LongObject):
            raise WObjectOperationException(
                "operation strign < long is not implemented"
            )
        return W_BoolObject.W_False

    def eq(self, other):
        if self.value == "":
            return W_BoolObject.W_False
        if isinstance(other, W_StrObject):
            return W_BoolObject.from_bool(self.getvalue() == other.getvalue())
        if isinstance(other, W_IntObject):
            raise WObjectOperationException("operation strign < int is not implemented")
        if isinstance(other, W_LongObject):
            raise WObjectOperationException(
                "operation strign < long is not implemented"
            )
        return W_BoolObject.W_False


class W_ByteObject(W_RootObject):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return "%s(%r)" % (self.__class__.__name__, self._value)

    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def is_true(self):
        return False

    @staticmethod
    def from_str(strval):
        assert isinstance(strval, str)
        return W_ByteObject(strval)

    def add(self, other):
        raise WObjectOperationException("Unsupported operand type(s) for +")

    def sub(self, other):
        raise WObjectOperationException("Unsupported operand type(s) for -")

    def mul(self, other):
        raise WObjectOperationException("Unsupported operand type(s) for *")

    def div(self, other):
        raise WObjectOperationException("Unsupported operaiton /")

    def true_div(self, other):
        raise WObjectOperationException("Unsupported operaiton /")

    def lt(self, other):
        raise WObjectOperationNotImplemented

    def le(self, other):
        raise WObjectOperationNotImplemented

    def gt(self, other):
        raise WObjectOperationNotImplemented

    def ge(self, other):
        raise WObjectOperationNotImplemented

    def eq(self, other):
        raise WObjectOperationNotImplemented


class W_SequenceObject(W_RootObject):
    def __init__(self, value):
        self.value = value


class W_TupleObject(W_SequenceObject):
    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        s = "("
        for item in self.value:
            s += item.getrepr()
            s += ", "
        s += ")"
        return s

    def is_true(self):
        return len(self.value) != 0

    @staticmethod
    def from_list(lst):
        return W_TupleObject(lst)


class W_ListObject(W_SequenceObject):
    def getrepr(self):
        s = "["
        for item in self.value:
            s += item.getrepr()
            s += ", "
        s += "]"
        return s

    def __repr__(self):
        return self.getrepr()

    def is_true(self):
        return len(self.value) != 0

    def lt(self, other):
        raise WObjectOperationNotImplemented

    def le(self, other):
        raise WObjectOperationNotImplemented

    def gt(self, other):
        raise WObjectOperationNotImplemented

    def ge(self, other):
        raise WObjectOperationNotImplemented

    def eq(self, other):
        raise WObjectOperationNotImplemented


class W_FunctionObject(W_RootObject):
    def __init__(self, body, defaults):
        self.body = body
        self.defaults = defaults

    def __repr__(self):
        return "Function(%s, %s)" % (self.body, self.defaults)

    def is_true(self):
        return True

    def lt(self, other):
        raise WObjectOperationNotImplemented

    def le(self, other):
        raise WObjectOperationNotImplemented

    def gt(self, other):
        raise WObjectOperationNotImplemented

    def ge(self, other):
        raise WObjectOperationNotImplemented

    def eq(self, other):
        raise WObjectOperationNotImplemented
