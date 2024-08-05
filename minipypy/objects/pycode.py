from minipypy.objects.baseobject import W_RootObject


class PyCode(W_RootObject):
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

    def __repr__(self):
        return '<code object %s at %s, file "%s", line %d>' % (
            self.co_name,
            id(self),
            self.co_filename,
            self.co_firstlineno,
        )
