from rpython.rlib.rarithmetic import intmask

from minipypy.objects.pycode import PyCode
from minipypy.objects.baseobject import W_None, W_Str, W_Int, W_Long, W_Tuple, W_List

TYPE_NULL = "0"
TYPE_NONE = "N"
TYPE_FALSE = "F"
TYPE_TRUE = "T"
TYPE_STOPITER = "S"
TYPE_ELLIPSIS = "."
TYPE_INT = "i"
TYPE_INT64 = "I"
TYPE_FLOAT = "f"
TYPE_BINARY_FLOAT = "g"
TYPE_COMPLEX = "x"
TYPE_BINARY_COMPLEX = "y"
TYPE_LONG = "l"
TYPE_STRING = "s"
TYPE_INTERNED = "t"
TYPE_STRINGREF = "R"
TYPE_TUPLE = "("
TYPE_LIST = "["
TYPE_DICT = "{"
TYPE_CODE = "c"
TYPE_UNICODE = "u"
TYPE_UNKNOWN = "?"
TYPE_SET = "<"
TYPE_FROZENSET = ">"


stringtable_w = []


def start(f, typecode):
    tc = f.read(1)
    if tc != typecode:
        raise Exception("invalid marshal data")


def get_none(f):
    return None


def get_int(f):
    s = f.read(4)
    a = ord(s[0])
    b = ord(s[1])
    c = ord(s[2])
    d = ord(s[3])
    if d & 0x80:
        d -= 0x100
    x = a | (b << 8) | (c << 16) | (d << 24)
    return intmask(x)


def get_lng(f):
    s = f.read(4)
    a = ord(s[0])
    b = ord(s[1])
    c = ord(s[2])
    d = ord(s[3])
    x = a | (b << 8) | (c << 16) | (d << 24)
    if x >= 0:
        return x
    else:
        raise Exception("bad marshal data")


def atom_lng(f, typecode):
    start(f, typecode)
    return get_lng(f)


def get_str(f):
    lng = get_lng(f)
    return f.read(lng)


def atom_str(f):
    start(f, TYPE_STRING)
    return get_str(f)


# inlined version to save a recursion level
def get_tuple(f):
    lng = get_lng(f)
    res_w = [None] * lng
    idx = 0
    w_ret = None
    while idx < lng:
        tc = f.read(1)
        w_ret = dispatch(tc, f)
        if w_ret is None:
            break
        res_w[idx] = w_ret
        idx += 1
    if w_ret is None:
        raise Exception("NULL object in marshal data")
    return res_w


def get_list_w(self):
    return self.get_tuple_w()[:]


def dispatch(tc, f):
    if tc == TYPE_INT:
        return unmarshal_int(f)
    elif tc == TYPE_LONG:
        return unmarshal_lng(f)
    elif tc == TYPE_STRING:
        return W_Str(get_str(f))
    elif tc == TYPE_INTERNED:
        return unmarshal_interned_str(f)
    elif tc == TYPE_STRINGREF:
        return unmarshal_stringref(f)
    elif tc == TYPE_TUPLE:
        return unmarshal_tuple(f)
    elif tc == TYPE_NONE:
        return unmarshal_none(f)
    elif tc == TYPE_CODE:
        return unmarshal_pycode(f)
    else:
        import pdb; pdb.set_trace()
        raise Exception("Unsupported typecode %c" % tc)


def unmarshal_tuple(f):
    return W_Tuple(get_tuple(f))


def unmarshal_interned_str(f):
    w_ret = W_Str(get_str(f))
    stringtable_w.append(w_ret)
    return w_ret


def unmarshal_stringref(f):
    idx = get_int(f)
    try:
        return stringtable_w[idx]
    except IndexError:
        raise Exception("bad marshal data")


def unmarshal_str(f):
    tc = f.read(1)
    return dispatch(tc, f)


def unmarshal_none(f):
    return W_None()


def unmarshal_int(f):
    return W_Int(get_int(f))


def unmarshal_lng(f):
    return W_Long(get_lng(f))


def unmarshal_strlist(f, tc):
    lng = atom_lng(f, tc)
    return [unmarshal_str(f) for i in range(lng)]


# @unmarshaller(TYPE_CODE)
# def unmarshal_pycode(space, u, tc):
#     argcount    = u.get_int()
#     nlocals     = u.get_int()
#     stacksize   = u.get_int()
#     flags       = u.get_int()
#     code        = unmarshal_str(u)
#     u.start(TYPE_TUPLE)
#     consts_w    = u.get_tuple_w()
#     # copy in order not to merge it with anything else
#     names       = unmarshal_strlist(u, TYPE_TUPLE)
#     varnames    = unmarshal_strlist(u, TYPE_TUPLE)
#     freevars    = unmarshal_strlist(u, TYPE_TUPLE)
#     cellvars    = unmarshal_strlist(u, TYPE_TUPLE)
#     filename    = unmarshal_str(u)
#     name        = unmarshal_str(u)
#     firstlineno = u.get_int()
#     lnotab      = unmarshal_str(u)
#     return PyCode(space, argcount, nlocals, stacksize, flags,
#                   code, consts_w[:], names, varnames, filename,
#                   name, firstlineno, lnotab, freevars, cellvars)


def unmarshal_pycode(f):
    argcount    = get_int(f)
    nlocals     = get_int(f)
    stacksize   = get_int(f)
    flags       = get_int(f)
    code        = atom_str(f)
    start(f, TYPE_TUPLE)
    consts      = get_tuple(f)
    names       = unmarshal_strlist(f, TYPE_TUPLE)
    varnames    = unmarshal_strlist(f, TYPE_TUPLE)
    freevars    = unmarshal_strlist(f, TYPE_TUPLE)
    cellvars    = unmarshal_strlist(f, TYPE_TUPLE)
    filename    = unmarshal_str(f)
    name        = unmarshal_str(f)
    firstlineno = get_int(f)
    lnotab      = unmarshal_str(f)
    return PyCode(
        argcount, nlocals, stacksize, flags, code, consts, names, varnames, freevars, cellvars,
        filename, name, firstlineno, lnotab
    )
