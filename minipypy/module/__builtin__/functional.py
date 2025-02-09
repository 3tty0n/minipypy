from minipypy.objects.baseobject import W_IntObject, W_FloatObject
from minipypy.objects.error import oefmt, W_TypeError
from minipypy.objects.listobject import newlist
from rpython.rlib import jit, rarithmetic
from rpython.rlib.objectmodel import specialize
from rpython.rlib.rarithmetic import r_uint, intmask

def get_len_of_range(space, lo, hi, step):
    """
    Return number of items in range/xrange (lo, hi, step).
    Raise ValueError if step == 0 and OverflowError if the true value is too
    large to fit in a signed long.
    """

    # If lo >= hi, the range is empty.
    # Else if n values are in the range, the last one is
    # lo + (n-1)*step, which must be <= hi-1.  Rearranging,
    # n <= (hi - lo - 1)/step + 1, so taking the floor of the RHS gives
    # the proper value.  Since lo < hi in this case, hi-lo-1 >= 0, so
    # the RHS is non-negative and so truncation is the same as the
    # floor.  Letting M be the largest positive long, the worst case
    # for the RHS numerator is hi=M, lo=-M-1, and then
    # hi-lo-1 = M-(-M-1)-1 = 2*M.  Therefore unsigned long has enough
    # precision to compute the RHS exactly.
    if step == 0:
        raise oefmt(space.w_ValueError, "step argument must not be zero")
    elif step < 0:
        lo, hi, step = hi, lo, -step
    if lo < hi:
        uhi = r_uint(hi)
        ulo = r_uint(lo)
        diff = uhi - ulo - 1
        n = intmask(diff // r_uint(step) + 1)
        if n < 0:
            raise oefmt(space.w_OverflowError, "result has too many items")
    else:
        n = 0
    return n

def range_int(space, w_x, w_y=None, w_step=None):
    """Return a list of integers in arithmetic position from start (defaults
to zero) to stop - 1 by step (defaults to 1).  Use a negative step to
get a list in decending order."""

    if w_y is None:
        w_start = W_IntObject(0)
        w_stop = w_x
    else:
        w_start = w_x
        w_stop = w_y

    if isinstance(w_stop, W_FloatObject):
        raise oefmt(w_TypeError,
                    "range() integer end argument expected, got float.")
    if isinstance(w_start, W_FloatObject):
        raise oefmt(w_TypeError,
                    "range() integer start argument expected, got float.")
    if isinstance(w_step, W_FloatObject):
        raise oefmt(w_TypeError,
                    "range() integer step argument expected, got float.")

    w_start = w_start.toint()
    w_stop = sw_stop.toint()
    w_step = w_step.toint()

    # TODO: should check ovf err
    start = W_IntObject(w_start)
    stop = W_IntObject(w_stop)
    step = W_IntObject(w_step)

    howmany = get_len_of_range(space, start, stop, step)

    res_w = [None] * howmany
    v = start
    for idx in range(howmany):
        res_w[idx] = space.newint(v)
        v += step
    return newlist(res_w)
