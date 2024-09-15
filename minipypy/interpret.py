import sys

from rpython.rlib import jit
from rpython.rlib.jit import JitDriver, hint, promote, promote_string
from rpython.rlib.debug import ll_assert_not_none, make_sure_not_resized, check_nonneg
from rpython.rlib.objectmodel import always_inline, compute_hash
from rpython.rlib.rarithmetic import intmask, r_uint
from rpython.rlib.rerased import new_erasing_pair

from minipypy.frontend import rpy_load_py2
from minipypy.objects.baseobject import *
from minipypy.objects.pycode import PyCode
from minipypy.opcode27 import Bytecodes, opmap, opname, HAVE_ARGUMENT


class OpcodeNotImplementedError(RuntimeError):
    pass


class BytecodeCorruption(RuntimeError):
    pass


class SuspendedUnroller(W_RootObject):
    """Abstract base class for interpreter-level objects that
    instruct the interpreter to change the control flow and the
    block stack.

    The concrete subclasses correspond to the various values WHY_XXX
    values of the why_code enumeration in ceval.c:

                WHY_NOT,        OK, not this one :-)
                WHY_EXCEPTION,  SApplicationException
                WHY_RERAISE,    implemented differently, see Reraise
                WHY_RETURN,     SReturnValue
                WHY_BREAK,      SBreakLoop
                WHY_CONTINUE,   SContinueLoop
                WHY_YIELD       not needed
    """

    _immutable_ = True

    def nomoreblocks(self):
        raise BytecodeCorruption("misplaced bytecode - should not return")


class SReturnValue(SuspendedUnroller):
    """Signals a 'return' statement.
    Argument is the wrapped object to return."""

    _immutable_ = True
    kind = 0x01

    def __init__(self, w_returnvalue):
        self.w_returnvalue = w_returnvalue

    def nomoreblocks(self):
        return self.w_returnvalue


class SBreakLoop(SuspendedUnroller):
    """Signals a 'break' statement."""

    _immutable_ = True
    kind = 0x04

    def __init__(self):
        pass


SBreakLoop.singleton = SBreakLoop()


class SContinueLoop(SuspendedUnroller):
    """Signals a 'continue' statement.
    Argument is the bytecode position of the beginning of the loop."""

    _immutable_ = True
    kind = 0x08

    def __init__(self, jump_to):
        self.jump_to = jump_to


class FrameBlock(object):
    """Abstract base class for frame blocks from the blockstack,
    used by the SETUP_XXX and POP_BLOCK opcodes."""

    _immutable_ = True
    _opname = "UNKNOWN_OPCODE"

    def __init__(self, frame, handlerposition, previous):
        self.handlerposition = handlerposition
        self.valuestackdepth = frame.valuestackdepth
        self.previous = previous  # this makes a linked list of blocks

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.handlerposition == other.handlerposition
            and self.valuestackdepth == other.valuestackdepth
        )

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.handlerposition, self.valuestackdepth))

    def cleanupstack(self, frame):
        frame.dropvaluesuntil(self.valuestackdepth)

    def cleanup(self, frame):
        "Clean up a frame when we normally exit the block."
        self.cleanupstack(frame)

    # internal pickling interface, not using the standard protocol
    def _get_state_(self, space):
        return W_TupleObject.from_list(
            [
                W_ByteObject.from_str(self._opname),
                W_IntObject.from_int(self.handlerposition),
                W_IntObject.from_int(self.valuestackdepth),
            ]
        )

    def handle(self, frame, unroller):
        """Purely abstract method"""
        raise NotImplementedError


class LoopBlock(FrameBlock):
    """A loop block.  Stores the end-of-loop pointer in case of 'break'."""

    _immutable_ = True
    _opname = "SETUP_LOOP"
    handling_mask = SBreakLoop.kind | SContinueLoop.kind

    def handle(self, frame, unroller):
        if isinstance(unroller, SContinueLoop):
            # re-push the loop block without cleaning up the value stack,
            # and jump to the beginning of the loop, stored in the
            # exception's argument
            frame.append_block(self)
            jumpto = unroller.jump_to
            ec = frame.space.getexecutioncontext()
            return r_uint(frame.jump_absolute(jumpto, ec))
        else:
            # jump to the end of the loop
            self.cleanupstack(frame)
            return r_uint(self.handlerposition)


class W_Dict(W_RootObject):
    # erase, unerase = new_erasing_pair("dict")
    # erase = staticmethod(erase)
    # unerase = staticmethod(unerase)

    def __init__(self):
        self.storage = [(None, None)] * 8
        self.storage_ptr = 0
        check_nonneg(self.storage_ptr)

    @jit.unroll_safe
    def getitem(self, w_key):
        assert w_key is not None
        for i in range(self.storage_ptr):
            (x, y) = self.storage[i]
            if x is w_key:
                return y
        return None

    @jit.unroll_safe
    def setitem(self, w_key, w_val):
        for i in range(self.storage_ptr):
            (x, y) = self.storage[i]
            if x is w_key:
                w_x = (x, w_val)
                assert w_x is not None
                self.storage[i] = w_x
                return

        w_x = (w_key, w_val)
        assert w_x is not None
        assert self.storage_ptr < len(self.storage)
        self.storage[self.storage_ptr] = w_x
        self.storage_ptr += 1


class PyFrame(W_RootObject):
    _virtualizable_ = [
        "last_intr", "code",
        "valuestackdepth",
        "locals_cells_stack_w[*]",
        "w_locals"
    ]

    _immutable_fields = ["code", "w_locals?"]

    pycode = None # code object executed by that frame
    locals_cells_stack_w = None # the list of all locals, cells and the valuestack
    valuestackdepth = 0 # number of items on valuestack
    lastblock = None
    lastblock = None
    w_locals = W_Dict()

    def __init__(self, code):
        self = hint(self, fresh_virtualizable=True, access_directly=True)
        assert isinstance(code, PyCode)
        self.code = code
        # the layout of this list is as follows:
        # | local vars | cells | stack |
        size = code.co_nlocals + len(code.co_cellvars) + len(code.co_freevars) + code.co_stacksize
        self.locals_cells_stack_w = [None] * size
        check_nonneg(self.valuestackdepth)

        self.last_instr = -1

    def getcode(self):
        return promote(self.code)

    def getco_code(self):
        return promote_string(self.getcode().co_code)

    def get_w_globals(self):
        return promote(self.code).w_globals

    def pop(self):
        valuestackdepth = self.valuestackdepth - 1
        assert valuestackdepth >= 0
        w_x = self.locals_cells_stack_w[valuestackdepth]
        self.locals_cells_stack_w[valuestackdepth] = None
        self.valuestackdepth = valuestackdepth
        return w_x

    def push(self, w_x):
        self.locals_cells_stack_w[self.valuestackdepth] = w_x
        self.valuestackdepth += 1

    def top(self):
        assert self.valuestackdepth >= 0
        return self.locals_cells_stack_w[self.valuestackdepth]

    @jit.unroll_safe
    def dropvaluesuntil(self, finaldepth):
        depth = self.valuestackdepth - 1
        finaldepth = hint(finaldepth, promote=True)
        assert finaldepth >= 0
        while depth >= finaldepth:
            self.locals_cells_stack_w[depth] = None
            depth -= 1
        self.valuestackdepth = finaldepth

    def append_block(self, block):
        assert block.previous is self.lastblock
        self.lastblock = block

    def pop_block(self):
        block = self.lastblock
        self.lastblock = block.previous
        return block

    def create_pyframe(self, code, args):
        pyframe = PyFrame(code)
        for i in range(len(args)):
            assert i >= 0
            pyframe.locals_cells_stack_w[i] = args[i]
            pyframe.valuestackdepth += 1
        pyframe.code.frame_stores_global(self.getcode().w_globals)
        return pyframe

    def read_const(self, operand):
        return self.getcode().co_consts[operand]

    def POP_TOP(self, oparg, next_instr):
        self.pop()

    def ROT_TWO(self, oparg, next_instr):
        tos = self.pop()
        tos2 = self.pop()
        self.push(tos2)
        self.push(tos)

    def ROT_THREE(self, oparg, next_instr):
        assert self.valuestackdepth - 2 >= 0
        tos = self.pop()
        tos2 = self.pop()
        tos3 = self.pop()
        self.push(tos)
        self.push(tos2)
        self.push(tos3)

    def STORE_NAME(self, oparg, next_instr):
        var = self.getcode().co_names[oparg]
        assert var is not None

        w_value = self.pop()
        self.w_locals.setitem(var, w_value)

    def STORE_FAST(self, oparg, next_instr):
        assert oparg >= 0
        self.locals_cells_stack_w[oparg] = self.pop()

    def STORE_GLOBAL(self, oparg, next_instr):
        co_names = promote(self.getcode().co_names)
        name = co_names[oparg]
        assert name is not None

        w_value = self.pop()
        self.getcode().w_globals[name] = w_value

    def LOAD_NAME(self, oparg, next_instr):
        co_names = promote(self.getcode().co_names)
        name = co_names[oparg]
        assert name is not None

        w_result = self.w_locals.getitem(name)
        if w_result is None:
            w_globals = self.getcode().w_globals
            w_result = w_globals.get(name)

        if w_result is None:
            raise BytecodeCorruption("LOAD_NAME is failed")
        self.push(w_result)

    @always_inline
    def LOAD_FAST(self, oparg, next_instr):
        w_value = self.locals_cells_stack_w[oparg]
        if w_value is None:
            raise BytecodeCorruption("LOAD_FAST is failed")
        self.push(w_value)

    def LOAD_CONST(self, oparg, next_instr):
        const = self.read_const(oparg)
        self.push(const)

    def LOAD_GLOBAL(self, oparg, next_instr):
        co_names = promote(self.getcode().co_names)
        name = co_names[oparg]
        assert name is not None

        w_result = self.w_locals.getitem(name)
        if w_result is None:
            w_globals = self.getcode().w_globals
            w_result = w_globals.get(name)

        if w_result is None:
            raise BytecodeCorruption("LOAD_NAME is failed")
        self.push(w_result)

    def BINARY_POWER(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.power(w_y)
        self.push(w_z)

    def BINARY_MULTIPLY(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.mul(w_y)
        self.push(w_z)

    def BINARY_DIVIDE(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.div(w_y)
        self.push(w_z)

    def BINARY_MODULO(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.mod(w_y)
        self.push(w_z)

    def BINARY_ADD(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.add(w_y)
        self.push(w_z)

    def BINARY_SUBTRACT(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.sub(w_y)
        self.push(w_z)

    def BINARY_SUBSCR(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.subscr(w_y)
        self.push(w_z)

    def BINARY_FLOOR_DIVIDE(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.div(w_y)  # TODO: floor
        self.push(w_z)

    def BINARY_TRUE_DIVIDE(self, oparg, next_instr):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.true_div(w_y)
        self.push(w_z)

    def COMPARE_OP(self, oparg, next_instr):
        opnum = oparg
        w_2 = self.pop()
        w_1 = self.pop()
        if opnum == 0:  # <
            w_result = w_1.lt(w_2)
        elif opnum == 1:  # <=
            w_result = w_1.le(w_2)
        elif opnum == 2:  # ==
            w_result = w_1.eq(w_2)
        elif opnum == 3:  # !=
            w_result = w_1.eq(w_2).not_()
        elif opnum == 4:  # >
            w_result = w_1.gt(w_2)
        elif opnum == 5:  # >=
            w_result = w_1.ge(w_2)
        elif opnum == 6:  # in
            raise BytecodeCorruption("in is not implemented")
        elif opnum == 7:
            raise BytecodeCorruption("not in not implemented")
        elif opnum == 8:  # is
            w_result = w_1.eq(w_2)
        elif opnum == 9:  # is not
            w_result = w_1.eq(w_2).not_()
        elif opnum == 10:
            raise BytecodeCorruption("exception match not implemented")
        else:
            raise BytecodeCorruption("Bad cmp op: %d" % (opnum))
        self.push(w_result)

    def INPLACE_ADD(self, oparg, next_instr):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.add(w_tos)
        self.push(w_result)

    def INPLACE_SUBTRACT(self, oparg, next_instr):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.sub(w_tos)
        self.push(w_result)

    def INPLACE_MULTIPLY(self, oparg, next_instr):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.mul(w_tos)
        self.push(w_result)

    def INPLACE_DIVIDE(self, oparg, next_instr):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.div(w_tos)
        self.push(w_result)

    def RETURN_VALUE(self, oparg, next_instr):
        return self.pop()

    def SETUP_LOOP(self, oparg, next_instr):
        block = LoopBlock(self, next_instr + oparg, self.lastblock)
        self.lastblock = block

    def POP_BLOCK(self, oparg, next_instr):
        block = self.pop_block()
        block.cleanup(self)  # the block knows how to clean up the value stack

    def MAKE_FUNCTION(self, oparg, next_instr):
        argc = oparg
        code = self.pop()
        arg_defaults = [None] * argc
        i = 0
        while i < argc:
            arg_defaults[i] = self.pop()
            i += 1
        w_function = W_FunctionObject(code, arg_defaults)
        self.push(w_function)

    @jit.unroll_safe
    def CALL_FUNCTION(self, oparg, next_instr):
        argc = oparg
        kwnum = argc >> 8
        argnum = argc & 0xFF
        args = [None] * argnum
        for i in range(argnum):
            args[i] = self.pop()
        w_function = self.pop()
        assert isinstance(w_function, W_FunctionObject)
        pyframe = self.create_pyframe(w_function.body, args)
        w_value = pyframe.interpret()
        if w_value:
            self.push(w_value)

    def UNPACK_SEQUENCE(self, oparg, next_instr):
        tos = self.pop()
        assert isinstance(tos, W_SequenceObject)
        seq = tos.value
        for i in range(oparg):
            self.push(seq[len(seq) - (i + 1)])

    def BUILD_TUPLE(self, oparg, next_instr):
        count = oparg
        values = [None] * count
        for i in range(count):
            values[count - i - 1] = self.pop()
        w_ret = W_TupleObject(values)
        self.push(w_ret)

    def PRINT_ITME(self, oparg, next_instr):
        w_x = self.pop()
        print w_x.getrepr(),  # fmt: skip

    def PRINT_NEWLINE(self, oparg, next_instr):
        print  # fmt: skip

    @jit.unroll_safe
    def interpret(self):
        next_instr = r_uint(self.last_instr + 1)
        oparg = r_uint(0)

        while next_instr < len(self.getco_code()):
            jitdriver.jit_merge_point(
                next_instr=next_instr,
                code=self.getcode(),
                valuestackdepth=self.valuestackdepth,
                self=self,
            )
            co_code = self.getco_code()
            opcode = ord(co_code[next_instr])
            next_instr += 1

            if HAVE_ARGUMENT <= opcode:
                lo = ord(co_code[next_instr])
                hi = ord(co_code[next_instr+1])
                next_instr += 2
                oparg = (hi * 256) | lo
            else:
                oparg = r_uint(0)

            self.valuestackdepth = hint(self.valuestackdepth, promote=True)

            if not jit.we_are_translated():
                print(
                    opcode,
                    next_instr,
                    opname[opcode],
                    self.locals_cells_stack_w,
                    self.valuestackdepth,
                    self.getcode().w_globals,
                )
            if opcode == Bytecodes.BINARY_ADD:
                self.BINARY_ADD(oparg, next_instr)
            elif opcode == Bytecodes.BINARY_DIVIDE:
                self.BINARY_DIVIDE(oparg, next_instr)
            elif opcode == Bytecodes.BINARY_SUBTRACT:
                self.BINARY_SUBTRACT(oparg, next_instr)
            elif opcode == Bytecodes.BINARY_MULTIPLY:
                self.BINARY_MULTIPLY(oparg, next_instr)
            elif opcode == Bytecodes.BINARY_TRUE_DIVIDE:
                self.BINARY_TRUE_DIVIDE(oparg, next_instr)
            elif opcode == Bytecodes.BUILD_TUPLE:
                self.BUILD_TUPLE(oparg, next_instr)
            elif opcode == Bytecodes.COMPARE_OP:
                self.COMPARE_OP(oparg, next_instr)
            elif opcode == Bytecodes.INPLACE_ADD:
                self.INPLACE_ADD(oparg, next_instr)
            elif opcode == Bytecodes.INPLACE_SUBTRACT:
                self.INPLACE_SUBTRACT(oparg, next_instr)
            elif opcode == Bytecodes.INPLACE_DIVIDE:
                self.INPLACE_DIVIDE(oparg, next_instr)
            elif opcode == Bytecodes.LOAD_NAME:
                self.LOAD_NAME(oparg, next_instr)
            elif opcode == Bytecodes.LOAD_FAST:
                self.LOAD_FAST(oparg, next_instr)
            elif opcode == Bytecodes.LOAD_CONST:
                self.LOAD_CONST(oparg, next_instr)
            elif opcode == Bytecodes.LOAD_GLOBAL:
                self.LOAD_GLOBAL(oparg, next_instr)
            elif opcode == Bytecodes.PRINT_ITEM:
                self.PRINT_ITME(oparg, next_instr)
            elif opcode == Bytecodes.PRINT_NEWLINE:
                self.PRINT_NEWLINE(oparg, next_instr)
            elif opcode == Bytecodes.RETURN_VALUE:
                return self.RETURN_VALUE(oparg, next_instr)
            elif opcode == Bytecodes.SETUP_LOOP:
                self.SETUP_LOOP(oparg, next_instr)
            elif opcode == Bytecodes.STORE_NAME:
                self.STORE_NAME(oparg, next_instr)
            elif opcode == Bytecodes.STORE_FAST:
                self.STORE_FAST(oparg, next_instr)
            elif opcode == Bytecodes.STORE_GLOBAL:
                self.STORE_GLOBAL(oparg, next_instr)
            elif opcode == Bytecodes.POP_BLOCK:
                self.POP_BLOCK(oparg, next_instr)
            elif opcode == Bytecodes.MAKE_FUNCTION:
                self.MAKE_FUNCTION(oparg, next_instr)
            elif opcode == Bytecodes.CALL_FUNCTION:
                self.CALL_FUNCTION(oparg, next_instr)
            elif opcode == Bytecodes.POP_TOP:
                self.POP_TOP(oparg, next_instr)
            elif opcode == Bytecodes.ROT_TWO:
                self.ROT_TWO(oparg, next_instr)
            elif opcode == Bytecodes.ROT_THREE:
                self.ROT_THREE(oparg, next_instr)
            elif opcode == Bytecodes.UNPACK_SEQUENCE:
                self.UNPACK_SEQUENCE(oparg, next_instr)
            elif opcode == Bytecodes.JUMP_IF_TRUE_OR_POP:
                tos = self.top()
                if tos.is_true():
                    next_instr = oparg
                else:
                    self.pop()
            elif opcode == Bytecodes.JUMP_IF_FALSE_OR_POP:
                tos = self.top()
                if not tos.is_true():
                    next_instr = oparg
                else:
                    self.pop()
            elif opcode == Bytecodes.POP_JUMP_IF_TRUE:
                tos = self.pop()
                if tos.is_true():
                    next_instr = oparg
            elif opcode == Bytecodes.POP_JUMP_IF_FALSE:
                tos = self.pop()
                if not tos.is_true():
                    next_instr = oparg
            elif opcode == Bytecodes.JUMP_ABSOLUTE:
                next_instr = oparg
                jitdriver.can_enter_jit(
                    next_instr=next_instr,
                    code=self.getcode(),
                    valuestackdepth=self.valuestackdepth,
                    self=self,
                )
            elif opcode == Bytecodes.JUMP_FORWARD:
                next_instr += oparg
            elif opcode == Bytecodes.STOP_CODE:
                pass


def get_printable_location(next_instr, code):
    opcode = ord(code.co_code[next_instr])
    name = opname[opcode]
    return '%s #%d %s' % (code.get_repr(), next_instr, name)


jitdriver = JitDriver(
    greens=["next_instr", "code",],
    reds=["valuestackdepth", "self"],
    virtualizables=["self"],
    get_printable_location=get_printable_location,
)

if __name__ == "__main__":
    import sys
    import dis
    import minipypy.frontend as frontend

    setup_prebuilt()

    code = rpy_load_py2(sys.argv[1])
    pyframe = PyFrame(code)
    w_x = pyframe.interpret()
