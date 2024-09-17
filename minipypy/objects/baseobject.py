import operator

from rpython.rlib import jit
from rpython.rlib.rbigint import rbigint
from rpython.rlib.objectmodel import instantiate

prebuilt_from = 0
prebuilt_to = 100


def within_prebuilt_index(i):
    return prebuilt_from <= i < prebuilt_to


class WObjectOperationException(RuntimeError):
    pass


WObjectOperationNotImplemented = WObjectOperationException("Not implemented")


class W_RootObject(object):
    # TODO: workaround
    # _immutable_fields_ = ["co_code", "co_consts[*]", "co_names[*]",]

    def __repr__(self):
        return "W_RootObject()"

    def getrepr(self):
        return "W_RootObject()"

    def is_none(self):
        return False


class W_NoneObject(W_RootObject):
    _immutable_fields_ = ["value"]

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return "None"

    def is_true(self):
        return False

    def is_none(self):
        return True


W_NoneObject.W_None = W_NoneObject(None)


class W_BoolObject(W_RootObject):
    _immutable_fields_ = ["value"]

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
    _immutable_fields_ = ["value"]
    PREBUILT = []

    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return self.getrepr()

    def getrepr(self):
        return "%d" % (self.value)

    @jit.elidable
    def getvalue(self):
        return self.value

    def getstr(self):
        return str(self.value)

    def is_true(self):
        return self.value == 0

    @staticmethod
    def from_int(i):
        w_result = instantiate(W_IntObject)
        w_result.value = i
        return w_result

    def positive(self):
        return W_IntObject(+self.value)

    def negative(self):
        return W_IntObject(-self.value)

    def not_(self):
        if self.value == 0:
            return W_BoolObject.W_True
        return W_BoolObject.W_False

    def add(self, other):
        if isinstance(other, W_IntObject):
            x = self.value
            y = other.value
            return W_IntObject(x + y)
        elif isinstance(other, W_LongObject):
            x = self.value
            y = other.value
            return W_LongObject(rbigint.fromint(x).add(y))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def sub(self, other):
        if isinstance(other, W_IntObject):
            return W_IntObject(self.value - other.value)
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
            return W_IntObject(self.value / other.value)
        elif isinstance(other, W_LongObject):
            return W_LongObject(rbigint.fromint(self.value).div(other.getvalue()))
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def true_div(self, other):
        return self.div(other)

    def mod(self, other):
        x = self.value
        if isinstance(other, W_IntObject):
            y = other.value
            return W_IntObject(x % y)
        elif isinstance(other, W_LongObject):
            y = other.value.toint()
            return W_IntObject(x % y)
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def lshift(self, other):
        x = self.value
        if isinstance(other, W_IntObject):
            y = other.value
            return W_IntObject(x << y)
        elif isinstance(other, W_LongObject):
            y = other.value.toint()
            return W_IntObject(x << y)
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def rshift(self, other):
        x = self.value
        if isinstance(other, W_IntObject):
            y = other.value
            return W_IntObject(x >> y)
        elif isinstance(other, W_LongObject):
            y = other.value.toint()
            return W_IntObject(x >> y)
        else:
            raise WObjectOperationException("Unexpected object: %s" % (other))

    def eq(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.value == other.value)
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.value == other.value.toint())
        return W_BoolObject.W_True

    def lt(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.value < other.value)
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.value < other.value.toint())
        return W_BoolObject.W_True

    def le(self, other):
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.value <= other.value)
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.value <= other.value.toint())
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        return W_BoolObject.W_True

    def gt(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.value > other.value)
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.value > other.value.toint())
        return W_BoolObject.W_True

    def ge(self, other):
        if isinstance(other, W_NoneObject):
            return W_BoolObject.W_False
        if isinstance(other, W_IntObject):
            return W_BoolObject.from_bool(self.value >= other.value)
        if isinstance(other, W_LongObject):
            return W_BoolObject.from_bool(self.value >= other.value.toint())
        return W_BoolObject.W_True


class W_LongObject(W_RootObject):
    _immutable_fields_ = ["value"]
    PREBUILT = []

    def __init__(self, value):
        self.value = value  # instance of rbigint

    def __repr__(self):
        return self.getrepr()

    @staticmethod
    def from_int(intval):
        w_result = instantiate(W_LongObject)
        w_result.value = rbigint.fromint(intval)
        return w_result

    @staticmethod
    def from_rbigint(rbint):
        w_result = instantiate(W_LongObject)
        w_result.value = rbint
        return w_result

    @jit.elidable
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

    def not_(self):
        if self.value.toint() == 0:
            return W_BoolObject.W_False
        return W_BoolObject.W_True

    @jit.elidable
    def positive(self):
        return W_LongObject(self.value.abs())

    @jit.elidable
    def negative(self):
        return W_LongObject(self.value.neg())

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

    def mod(self, other):
        if isinstance(other, W_IntObject):
            return W_LongObject(self.value.mod(rbigint.fromint(other.value)))
        if isinstance(other, W_LongObject):
            return W_LongObject(self.value.mod(other.value))
        raise WObjectOperationException("Unexpected object: %s" % (other))

    def lshift(self, other):
        if isinstance(other, W_IntObject):
            y = other.value
            return W_LongObject(self.value.lshift(y))
        if isinstance(other, W_LongObject):
            y = other.value.toint()
            return W_LongObject(self.value.lshift(y))
        raise WObjectOperationException("Unexpected object: %s" % (other))

    def rshift(self, other):
        if isinstance(other, W_IntObject):
            y = other.value
            return W_LongObject(self.value.rshift(y))
        if isinstance(other, W_LongObject):
            y = other.value.toint()
            return W_LongObject(self.value.rshift(y))
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
    _immutable_fields_ = ["value"]

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

    def not_(self):
        if self.value is "":
            return W_BoolObject.W_True
        return W_BoolObject.W_False

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
    _immutable_fields_ = ["value"]

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

    def not_(self):
        return W_BoolObject.W_False

    @staticmethod
    def from_str(strval):
        assert isinstance(strval, str)
        return W_ByteObject(strval)

    def positive(self):
        raise WObjectOperationException("Unsupported operand type for +")

    def negative(self):
        raise WObjectOperationException("Unsupported operand type for -")

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


class W_IteratorObject(W_RootObject):
    _immutable_fields_ = ["value"]

    def __init__(self, value):
        self.value = value


class W_TupleObject(W_IteratorObject):

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

    def not_(self):
        if len(self.value) == 0:
            return W_BoolObject.W_True
        return W_BoolObject.W_False


class W_ListObject(W_IteratorObject):

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

    def not_(self):
        if len(self.value) == 0:
            return W_BoolObject.W_True
        return W_BoolObject.W_False

    def positive(self):
        raise WObjectOperationNotImplemented

    def negative(self):
        raise WObjectOperationNotImplemented

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
    _immutable_fields_ = ["body", "defaults[*]"]

    def __init__(self, body, defaults):
        self.body = body
        self.defaults = defaults

    def __repr__(self):
        return "Function(%s, %s)" % (self.body, self.defaults)

    def is_true(self):
        return True

    def positive(self):
        raise WObjectOperationNotImplemented

    def negative(self):
        raise WObjectOperationNotImplemented

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


def setup_prebuilt():
    for i in range(prebuilt_from, prebuilt_to):
        W_IntObject.PREBUILT.append(W_IntObject.from_int(i))
        W_IntObject.PREBUILT.append(W_LongObject.from_int(i))
