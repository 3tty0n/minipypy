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

    def register_builtins(self):
        self.set_method("getitem", W_BuiltinFunction(self.getitem))
        self.set_method("getitem_copy", W_BuiltinFunction(self.getitem_copy))
        self.set_method("setitem", W_BuiltinFunction(self.setitem))
        self.set_method("append", W_BuiltinFunction(self.append))
        self.set_method("inplace_mul", W_BuiltinFunction(self.inplace_mul))
        self.set_method("mul", W_BuiltinFunction(self.mul))
        self.set_method("pop", W_BuiltinFunction(self.pop))
        self.set_method("reverse", W_BuiltinFunction(self.reverse))
        self.set_method("sort", W_BuiltinFunction(self.sort))

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

    def getitem(self, index):
        return self.wrappeditems[index]

    def getitem_copy(self):
        res = [None] * len(self.wrappeditems)
        prevvalue = self.wrappeditems[0]
        w_item = prevvalue
        res[0] = w_item
        for index in range(1, len(self.wrappeditems)):
            item = self.wrappeditems[index]
            if jit.we_are_jitted():
                prevvalue = item
            res[index] = w_item
        return res

    def setitem(self, index, w_item):
        self.wrappeditems[index] = w_item

    def append(self, w_item):
        self.wrappeditems.append(w_item)
        return self.wrappeditems

    def inplace_mul(self, times):
        self.wrappeditems *= times

    @jit.unroll_safe
    def mul(self, times):
        num = times.toint()
        assert not isinstance(num, rbigint)
        w_result = [None] * len(self.wrappeditems) * num
        for i in range(num):
            for j in range(len(self.wrappeditems)):
                w_result[len(self.wrappeditems) * i + j] = self.wrappeditems[j]
        return W_ListObject(w_result)

    def pop(self, index):
        if index < 0:
            raise IndexError

        try:
            item = self.wrappeditems.pop(index)
        except IndexError:
            raise

        return item

    def reverse(self):
        return self.wrappeditems.reverse()

    def sort(self):
        return self.wrappeditems.sort()
