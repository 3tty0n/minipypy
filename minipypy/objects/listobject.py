from minipypy.objects.dictobject import W_Dict
from minipypy.objects.mapobject import EMPTY_MAP, Map
from rpython.rlib import jit
from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rbigint import rbigint
from rpython.rlib.objectmodel import compute_hash, r_dict
from rpython.tool.descriptor import InstanceMethod

from minipypy.objects.baseobject import W_BoolObject, W_IntObject, W_NoneObject, W_StrObject
from minipypy.objects.iteratorobject import W_IteratorObject
from minipypy.objects.mapobject import Map
from minipypy.objects.function import *


def key_eq(key1, key2):
    assert isinstance(key1, W_StrObject)
    assert isinstance(key2, W_StrObject)
    return key1.value == key2.value


def key_hash(key):
    assert isinstance(key, W_StrObject)
    return compute_hash(key.value)


class W_List(W_Root):

    def __init__(self):
        self.methods = r_dict(key_eq, key_hash)
        self.write_method("append", _append)
        self.write_method("pop", _pop)

    def write_method(self, name, value):
        self.methods[W_StrObject(name)] = value

    def instantiate(self, wrappteditems):
        return W_ListObject(self, wrappteditems)


class W_ListObject(W_IteratorObject):
    strategy = None

    def __init__(self, cls, wrappeditems):
        self.cls = cls
        self.wrappeditems = wrappeditems

    def find_method(self, name):
        result = self.cls.methods.get(name, None)
        if result is not None:
            return W_InstanceMethod(result, self, self.cls)
        raise AttributeError(name)

    def getattr(self, name):
        assert isinstance(name, W_StrObject)
        return self.find_method(name)

    def getrepr(self):
        if not self.wrappeditems:
            return "[]"
        s = "["
        itemlen = len(self.wrappeditems)
        for i, item in enumerate(self.wrappeditems):
            s += item.getrepr()
            if i == itemlen - 1:
                break
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

    def getslice_0(self):
        return W_ListObject(self.cls, self.wrappeditems[:])

    def getslice_1(self, w_start):
        assert isinstance(w_start, W_IntObject)
        start = w_start.value
        assert start >= 0
        sublist = self.wrappeditems[start:]
        return W_ListObject(self.cls, sublist)

    def getslice_2(self, w_stop):
        assert isinstance(w_stop, W_IntObject)
        stop = w_stop.value
        assert stop >= 0
        sublist = self.wrappeditems[:stop]
        return W_ListObject(self.cls, sublist)

    def getslice_3(self, w_start, w_stop):
        assert isinstance(w_start, W_IntObject)
        assert isinstance(w_stop, W_IntObject)
        start = w_start.value
        stop = w_stop.value
        assert start >= 0
        assert stop >= 0
        sublist = self.wrappeditems[start:stop]
        return W_ListObject(self.cls, sublist)

    def getslice(self, start, stop, step, length):
        if step == 1 and 0 <= start <= stop:
            assert start >= 0
            assert stop >= 0
            sublist = self.wrappteditems[start:stop]
            return W_ListObject(self.cls, sublist)
        else:
            subitems_w = [W_NoneObject.W_None] * length
            self._fill_in_with_sliced_items(subitems_w, self.wrappeditems, start, step, length)
            return W_ListObject(self.cls, subitems_w)

    def _fill_in_with_sliced_items(self, subitems_w, l, start, step, length):
        for i in range(length):
            try:
                subitems_w[i] = l[start]
                start += step
            except IndexError:
                raise


def _append(w_list, *args):
    assert len(args) > 0, "append should take one argument"
    w_item = args[0]
    w_list.wrappeditems.append(w_item)
    return w_list


def _getitem(w_list, *args):
    index = args[0]
    assert isinstance(index, W_IntObject)
    return w_list.wrappeditems[index.value]


def _getitem_copy(w_list, *args):
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
    return W_List().instantiate(res)


def _setitem(w_list, *args):
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
    return W_List().instantiate(w_result)


def _pop(w_list, *args):
    if len(args) == 0:
        w_list.wrappeditems.pop()
        return W_NoneObject.W_None

    index = args[0]
    assert isinstance(index, W_IntObject), \
        "%s is not W_IntObject" % (index.getrepr())
    index = index.value
    if index < 0:
        raise IndexError

    try:
        item = w_list.wrappeditems.pop(index)
    except IndexError:
        raise

    return item


def _reverse(w_list, *args, **kwargs):
    wrappteditems = w_list.wrappeditems.reverse()
    w_list.wrappeditems = wrappteditems
    return w_list


def _sort(w_list, *args, **kwargs):
    wrappeditems = w_list.wrappeditems.sort()
    w_list.wrappeditems = wrappteditems
    return w_list
