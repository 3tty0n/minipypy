import os
import sys

from rpython.rlib import jit
from rpython.rlib.nonconst import NonConstant
from rpython.rlib.rsre import rsre_re as re
from rpython.memory.gc.base import GCBase
from rpython.memory.gc.hook import GcHooks

from minipypy.frontend import rpy_load_py2
from minipypy.interpret import PyFrame

def entry_point(argv):
    is_gc_stats = False

    i = 0
    while True:
        if not i < len(argv):
            break

        if argv[i] == "--jit":
            if len(argv) == i + 1:
                print("missing argument after --jit")
                return 2
            jitarg = argv[i + 1]
            jit.set_user_param(None, jitarg)
            del argv[i : i + 2]
            continue
        i += 1

    code = rpy_load_py2(argv[1])
    pyframe = PyFrame(code)
    w_x = pyframe.interpret()

    return 0

# _____ Define and setup target ___

def target(driver, _args):
    driver.exe_name = "targetminipypy"
    return entry_point, None


def jitpolicy(_driver):
    from rpython.jit.codewriter.policy import JitPolicy  # pylint: disable=import-error

    return JitPolicy()


if __name__ == "__main__":
    from rpython.translator.driver import TranslationDriver  # pylint: disable=E

    f, _ = target(TranslationDriver(), sys.argv)
    sys.exit(f(sys.argv))
