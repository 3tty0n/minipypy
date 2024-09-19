from minipypy.objects.baseobject import W_ListObject, W_RootObject, W_StrObject
from minipypy.objects.dictobject import W_Dict

from rpython.rlib.objectmodel import compute_hash

def globals_w_key_eq(key, other):
    return compute_hash(key) == compute_hash(other)

class PyCode(W_RootObject):

    _immutable_fields_ = [
        "co_argcount",
        "co_nlocals",
        "co_stacksize",
        "co_flags",
        "co_code",
        "co_consts[*]",
        "co_names[*]",
        "co_varnames[*]",
        "co_freevars[*]",
        "co_cellvars[*]",
        "co_filename",
        "co_name",
        "co_firstlineno",
        "co_lnotab",
        "w_globals?"
    ]

    def __init__(
        self,
        argcount,
        nlocals,
        stacksize,
        flags,
        code,
        consts,
        names,
        varnames,
        freevars,
        cellvars,
        filename,
        name,
        firstlineno,
        lnotab,
    ):
        assert nlocals >= 0
        assert (
            isinstance(argcount, int) and
            isinstance(nlocals, int) and
            isinstance(stacksize, int) and
            isinstance(flags, int) and
            isinstance(code, str) and
            isinstance(consts, list) and
            isinstance(names, list) and
            isinstance(varnames, list) and
            isinstance(freevars, list) and
            isinstance(cellvars, list) and
            isinstance(name, W_StrObject) and
            isinstance(filename, W_StrObject)
        )
        self.co_argcount = argcount
        self.co_nlocals = nlocals
        self.co_stacksize = stacksize
        self.co_flags = flags
        self.co_code = code
        self.co_consts = consts
        self.co_names = names
        self.co_varnames = varnames
        self.co_freevars = freevars
        self.co_cellvars = cellvars
        self.co_filename = filename
        self.co_name = name
        self.co_firstlineno = firstlineno
        self.co_lnotab = lnotab

        self.w_globals = W_Dict()


    def __repr__(self):
        return self.get_repr()

    def get_repr(self):
        return "<code object %s, file '%s', line %d>" % (
            self.co_name.value,
            self.co_filename.value,
            self.co_firstlineno,
        )

    def frame_stores_global(self, w_globals):
        if self.w_globals is None:
            self.w_globals = w_globals
            return False
        if self.w_globals is w_globals:
            return False
        return True
