from rpython.rlib import jit
from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rbigint import rbigint

from minipypy.objects.baseobject import W_BoolObject, W_IntObject, W_StrObject, WObjectOperationException, WObjectOperationNotImplemented
from minipypy.objects.iteratorobject import W_IteratorObject
from minipypy.objects.objectobject import W_Instance, W_Class
from minipypy.objects.function import W_BuiltinFunction

def get_list_strategy(w_list, sizehint):
    if not w_list:
        if sizehint != -1:
            return

class W_ListObject(W_IteratorObject):
    strategy = None

    def __init__(self, wrappeditems):
        W_Class.__init__(self,  "list")
        assert isinstance(wrappeditems, list)
        self.wrappeditems = wrappeditems
        self.register_builtins()

    def getrepr(self):
        s = "["
        for item in self.wrappeditems:
            s += item.getrepr()
            s += ", "
        s += "]"
        return s

    def __repr__(self):
        return self.getrepr()

    def is_true(self):
        return len(self.wrappeditems) != 0

    def not_(self):
        if len(self.wrappeditems) == 0:
            return W_BoolObject.W_True
        return W_BoolObject.W_False

    def register_builtins(self):
        self.set_method("getitem", W_BuiltinFunction(self, _getitem))
        self.set_method("getitem_copy", W_BuiltinFunction(self, _getitem_copy))
        self.set_method("setitem", W_BuiltinFunction(self, _setitem))
        self.set_method("append", W_BuiltinFunction(self, _append))
        self.set_method("inplace_mul", W_BuiltinFunction(self, _inplace_mul))
        self.set_method("mul", W_BuiltinFunction(self, _mul))
        self.set_method("pop", W_BuiltinFunction(self, _pop))
        self.set_method("reverse", W_BuiltinFunction(self, _reverse))
        self.set_method("sort", W_BuiltinFunction(self, _sort))

def _getitem(w_list, index):
    return w_list.wrappeditems[index]

def _getitem_copy(w_list):
    res = [None] * len(w_list.wrappeditems)
    prevvalue = w_list.wrappeditems[0]
    w_item = prevvalue
    res[0] = w_item
    for index in range(1, len(w_list.wrappeditems)):
        item = w_list.wrappeditems[index]
        if jit.we_are_jitted():
            prevvalue = item
        res[index] = w_item
    return res

def _setitem(w_list, index, w_item):
    w_list.wrappeditems[index] = w_item

def _append(w_list, w_item):
    w_list.wrappeditems.append(w_item)
    return w_list.wrappeditems

def _inplace_mul(w_list, times):
    num = times.toint()
    assert not isinstance(num, rbigint)
    w_result = [None] * len(w_list.wrappeditems) * num
    for i in range(num):
        for j in range(len(w_list.wrappeditems)):
            w_result[len(w_list.wrappeditems) * i + j] = w_list.wrappeditems[j]
    w_list.wrappeditems = w_result

@jit.unroll_safe
def _mul(w_list, times):
    num = times.toint()
    assert not isinstance(num, rbigint)
    w_result = [None] * len(w_list.wrappeditems) * num
    for i in range(num):
        for j in range(len(w_list.wrappeditems)):
            w_result[len(w_list.wrappeditems) * i + j] = w_list.wrappeditems[j]
    return W_ListObject(w_result)

def _pop(w_list, index):
    if index < 0:
        raise IndexError

    try:
        item = w_list.wrappeditems.pop(index)
    except IndexError:
        raise

    return item

def _reverse(w_list):
    return w_list.wrappeditems.reverse()

def _sort(w_list):
    return w_list.wrappeditems.sort()
