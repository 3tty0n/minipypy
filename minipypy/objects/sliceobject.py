from minipypy.objects.baseobject import W_RootObject

import sys

class W_SliceObject(W_RootObject):
    _immutable_fields_ = ['w_start', 'w_stop', 'w_step']

    def __init__(self, w_start, w_stop, w_step):
        assert w_start is not None
        assert w_stop is not None
        assert w_step is not None
        self.w_start = w_start
        self.w_stop = w_stop
        self.w_step = w_step

    def getrepr(self):
        pass

    @staticmethod
    def unwrap(w_slice):
        return slice(w_slice.value, w_slice.w_stop.value, w_slice.w_step.value)

    def unpack(w_slice, space):
        if space.is_w(w_slice.w_step, space.w_None):
            step = 1
        else:
            step = _eval_slice_index(space, w_slice.w_step)
            if step == 0:
                raise oefmt(space.w_ValueError, "slice step cannot be zero")
        if space.is_w(w_slice.w_start, space.w_None):
            if step < 0:
                start = sys.maxint
            else:
                start = 0
        else:
            start = _eval_slice_index(space, w_slice.w_start)
        if space.is_w(w_slice.w_stop, space.w_None):
            if step < 0:
                stop = -sys.maxint-1
            else:
                stop = sys.maxint
        else:
            stop = _eval_slice_index(space, w_slice.w_stop)
        return start, stop, step


# utility functions
def _eval_slice_index(space, w_int):
    # note that it is the *callers* responsibility to check for w_None
    # otherwise you can get funny error messages
    try:
        return space.getindex_w(w_int, None) # clamp if long integer too large
    except OperationError as err:
        if not err.match(space, space.w_TypeError):
            raise
        raise oefmt(space.w_TypeError,
                    "slice indices must be integers or None or have an "
                    "__index__ method")
