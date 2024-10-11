from rpython.rlib import jit
from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rbigint import rbigint
from rpython.tool.descriptor import InstanceMethod

from minipypy.objects.baseobject import W_BoolObject, W_IntObject, W_StrObject, WObjectOperationException, WObjectOperationNotImplemented
from minipypy.objects.iteratorobject import W_IteratorObject
from minipypy.objects.objectobject import W_Instance, W_Class
from minipypy.objects.function import *

def get_list_strategy(w_list, sizehint):
    if not w_list:
        if sizehint != -1:
            return

class W_ListObject(W_IteratorObject):
    strategy = None

    def __init__(self, wrappeditems):
        assert isinstance(wrappeditems, list)
        self.wrappeditems = wrappeditems
        self.methods = {
            "append": W_InstanceMethod(_append, self, W_ListObject)
        }

    def getattr(self, name):
        assert isinstance(name, W_StrObject)
        return self.methods[name.value]

    def getrepr(self):
        if not self.wrappeditems:
            return "[]"
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

def _append(w_list, *args):
    w_item = args[0]
    w_list.wrappeditems.append(w_item)
    return w_list

def _getitem(w_list, *args, **kwargs):
    index = args[0]
    assert isinstance(index, W_IntObject)
    return w_list.wrappeditems[index.value]

def _getitem_copy(w_list, *args, **kwargs):
    index = args[0]
    res = [None] * len(w_list.wrappeditems)
    prevvalue = w_list.wrappeditems[0]
    w_item = prevvalue
    res[0] = w_item
    for index in range(1, len(w_list.wrappeditems)):
        item = w_list.wrappeditems[index]
        if jit.we_are_jitted():
            prevvalue = item
        res[index] = w_item
    return W_ListObject(res)

def _setitem(w_list, *args, **kwargs):
    index = args[0]
    w_item = args[1]
    w_list.wrappeditems[index] = w_item

def _inplace_mul(w_list, *args, **kwargs):
    times = args[0]
    num = times.toint()
    assert not isinstance(num, rbigint)
    w_result = [None] * len(w_list.wrappeditems) * num
    for i in range(num):
        for j in range(len(w_list.wrappeditems)):
            w_result[len(w_list.wrappeditems) * i + j] = w_list.wrappeditems[j]
    w_list.wrappeditems = w_result

@jit.unroll_safe
def _mul(w_list, *args, **kwargs):
    times = args[0]
    num = times.toint()
    assert not isinstance(num, rbigint)
    w_result = [None] * len(w_list.wrappeditems) * num
    for i in range(num):
        for j in range(len(w_list.wrappeditems)):
            w_result[len(w_list.wrappeditems) * i + j] = w_list.wrappeditems[j]
    return W_ListObject(w_result)

def _pop(w_list, *args, **kwargs):
    index = args[0]
    if index < 0:
        raise IndexError

    try:
        item = w_list.wrappeditems.pop(index)
    except IndexError:
        raise

    return item

def _reverse(w_list, *args, **kwargs):
    return w_list.wrappeditems.reverse()

def _sort(w_list, *args, **kwargs):
    return w_list.wrappeditems.sort()
