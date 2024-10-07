from minipypy.objects.baseobject import W_RootObject

from rpython.rlib import jit

@jit.elidable_promote()
def _get_immutable_code(func):
    assert not func.can_change_code
    return func.code

class W_FunctionObject(W_RootObject):
    can_change_code = True
    _immutable_fields_ = ['code?',
                          'w_func_globals?',
                          #'closure?[*]',
                          'defs_w?[*]',
                          'name?']

    def __init__(self, code, w_globals=None, defs_w=[], closure=None,
                 forcename=None):
        # assert isinstance(code, PyCode)
        self.name = forcename or code.co_name.value
        self.code = code          # Code instance
        self.w_func_globals = w_globals  # the globals dictionary
        self.code.w_globals = w_globals
        self.closure = closure    # normally, list of Cell instances or None
        self.defs_w = defs_w
        self.w_func_dict = None   # filled out below if needed
        self.w_module = None

    def __repr__(self):
        # return "function %s.%s" % (self.space, self.name)
        # maybe we want this shorter:
        name = getattr(self, 'name', None)
        if not isinstance(name, str):
            name = '?'
        return "<%s %s>" % (self.__class__.__name__, name)

    def getcode(self):
        if jit.we_are_jitted():
            if not self.can_change_code:
                return _get_immutable_code(self)
            return jit.promote(self.code)
        return self.code

    def is_true(self):
        return True


class W_BuiltinFunction(W_RootObject):
    _immutable_fields_ = ["method"]

    def __init__(self, method):
        self.method = method
