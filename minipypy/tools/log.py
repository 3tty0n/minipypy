import logging

# from rpython.rlib.jit import not_rpython

# @not_rpython
def debug_print(*args):
    logging.debug(args)
