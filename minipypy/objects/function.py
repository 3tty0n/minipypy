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



class W_InstanceMethod(W_RootObject):
    "Like types.InstanceMethod, but with a reasonable (structural) equality."

    def __init__(self, im_func, im_self, im_class):
        self.im_func = im_func
        self.im_self = im_self
        self.im_class = im_class

    def run(self, *args):
        firstarg = self.im_self
        if firstarg is None:
            if not args or not isinstance(args[0], self.im_class):
                raise TypeError(
                    "must be called with %r instance as first argument" % (
                    self.im_class,))
            firstarg = args[0]
            args = args[1:]
        return self.im_func(firstarg, *args)

    def __eq__(self, other):
        return isinstance(other, W_InstanceMethod) and (
            self.im_func == other.im_func and
            self.im_self == other.im_self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.im_func, self.im_self))
