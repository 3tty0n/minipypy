import sys

from rpython.rlib.rarithmetic import intmask, r_uint
from rpython.rlib import jit
from rpython.rlib.jit import JitDriver, hint

from minipypy.frontend import rpy_load_py2
from minipypy.objects.baseobject import *
from minipypy.objects.pycode import PyCode
from minipypy.opcode27 import Bytecodes, opmap, opname


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


class PyFrame(W_RootObject):

    def __init__(self, code):
        self.code = code
        self.stack = [None] * (code.co_stacksize + 1)
        self.valuestackdepth = 0
        self.locals_cells_stack_w = [None] * (code.co_stacksize + 1)
        self.pc = 0
        self.locals_w = {}

        self.lastblock = None

    def pop(self):
        self.valuestackdepth -= 1
        w_x = self.stack[self.valuestackdepth]
        assert -1 < self.valuestackdepth
        return w_x

    def push(self, w_x):
        self.stack[self.valuestackdepth] = w_x
        self.valuestackdepth += 1

    def top(self):
        return self.stack[self.valuestackdepth]

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
            pyframe.locals_cells_stack_w[i] = args[i]
        return pyframe

    def read_const(self, operand):
        return self.code.co_consts[operand]

    def read_operand(self):
        lo = ord(self.code.co_code[self.pc])
        hi = ord(self.code.co_code[self.pc + 1])
        self.pc += 2
        oparg = (hi * 256) | lo
        return oparg

    def POP_TOP(self):
        self.pop()

    def ROT_TWO(self):
        tos = self.stack[self.valuestackdepth]
        tos2 = self.stack[self.valuestackdepth - 1]
        self.stack[self.valuestackdepth] = tos2
        self.stack[self.valuestackdepth - 1] = tos

    def ROT_THREE(self):
        tos = self.stack[self.valuestackdepth]
        tos2 = self.stack[self.valuestackdepth - 1]
        tos3 = self.stack[self.valuestackdepth - 2]
        self.stack[self.valuestackdepth] = tos3
        self.stack[self.valuestackdepth - 1] = tos2
        self.stack[self.valuestackdepth - 2] = tos

    def STORE_NAME(self):
        operand1 = self.read_operand()

        var = self.code.co_names[operand1]
        self.locals_w[var] = self.pop()

    def STORE_FAST(self):
        operand1 = self.read_operand()
        w_x = self.pop()
        self.locals_cells_stack_w[operand1] = w_x

    def LOAD_NAME(self):
        operand1 = self.read_operand()

        var = self.code.co_names[operand1]
        self.push(self.locals_w[var])

    def LOAD_FAST(self):
        operand1 = self.read_operand()
        w_x = self.locals_cells_stack_w[operand1]
        self.push(w_x)

    def LOAD_CONST(self):
        operand1 = self.read_operand()

        const = self.read_const(operand1)
        if not const:
            self.push(W_NoneObject.W_None)
        elif isinstance(const, W_RootObject):
            self.push(const)
        else:
            raise Exception("Unimplemented pattern", const)

    def BINARY_POWER(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.power(w_y)
        self.push(w_z)

    def BINARY_MULTIPLY(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.mul(w_y)
        self.push(w_z)

    def BINARY_DIVIDE(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.div(w_y)
        self.push(w_z)

    def BINARY_MODULO(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.mod(w_y)
        self.push(w_z)

    def BINARY_ADD(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.add(w_y)
        self.push(w_z)

    def BINARY_SUBTRACT(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.sub(w_y)
        self.push(w_z)

    def BINARY_SUBSCR(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.subscr(w_y)
        self.push(w_z)

    def BINARY_FLOOR_DIVIDE(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.div(w_y)  # TODO: floor
        self.push(w_z)

    def BINARY_TRUE_DIVIDE(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.true_div(w_y)
        self.push(w_z)

    def COMPARE_OP(self):
        opnum = self.read_operand()
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

    def INPLACE_ADD(self):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.add(w_tos)
        self.push(w_result)

    def INPLACE_SUBTRACT(self):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.sub(w_tos)
        self.push(w_result)

    def INPLACE_MULTIPLY(self):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.mul(w_tos)
        self.push(w_result)

    def INPLACE_DIVIDE(self):
        w_tos = self.pop()
        w_tos1 = self.pop()
        w_result = w_tos1.div(w_tos)
        self.push(w_result)

    def RETURN_VALUE(self):
        return self.pop()

    def SETUP_LOOP(self):
        offsettoend = self.read_operand()
        block = LoopBlock(self, self.pc + offsettoend, self.lastblock)
        self.lastblock = block

    def POP_BLOCK(self):
        block = self.pop_block()
        block.cleanup(self)  # the block knows how to clean up the value stack

    def MAKE_FUNCTION(self):
        argc = self.read_operand()

        code = self.pop()
        arg_defaults = [None] * argc
        i = 0
        while i < argc:
            arg_defaults[i] = self.pop()
            i += 1
        w_function = W_FunctionObject(code, arg_defaults)
        self.push(w_function)

    def CALL_FUNCTION(self):
        argc = self.read_operand()

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

    def UNPACK_SEQUENCE(self):
        seqnum = self.read_operand()
        tos = self.pop()
        assert isinstance(tos, W_SequenceObject)
        seq = tos.value
        for i in range(seqnum):
            self.push(seq[len(seq) - (i + 1)])

    def BUILD_TUPLE(self):
        count = self.read_operand()
        values = [None] * count
        for i in range(count):
            values[count - i - 1] = self.pop()
        w_ret = W_TupleObject(values)
        self.push(w_ret)

    def PRINT_ITME(self):
        w_x = self.pop()
        print w_x.getrepr(),  # fmt: skip

    def PRINT_NEWLINE(self):
        print  # fmt: skip

    def interpret(self):
        next_instr = 0

        self = hint(self, access_directly=True)
        self.pc = r_uint(self.pc)

        while next_instr < len(self.code.co_code):
            jitdriver.jit_merge_point(
                code=self.code.co_code,
                pc=self.pc,
                stack=self.stack,
                valuestackdepth=self.valuestackdepth,
                self=self,
            )
            opcode = ord(self.code.co_code[self.pc])
            self.pc += 1

            self.valuestackdepth = hint(self.valuestackdepth, promote=True)

            # print(
            #     opcode,
            #     opname[opcode],
            #     self.pc,
            #     self.stack,
            #     self.valuestackdepth,
            #     self.locals_cells_stack_w,
            # )
            if opcode == Bytecodes.BINARY_ADD:
                self.BINARY_ADD()
            elif opcode == Bytecodes.BINARY_DIVIDE:
                self.BINARY_DIVIDE()
            elif opcode == Bytecodes.BINARY_SUBTRACT:
                self.BINARY_SUBTRACT()
            elif opcode == Bytecodes.BINARY_MULTIPLY:
                self.BINARY_MULTIPLY()
            elif opcode == Bytecodes.BINARY_TRUE_DIVIDE:
                self.BINARY_TRUE_DIVIDE()
            elif opcode == Bytecodes.BUILD_TUPLE:
                self.BUILD_TUPLE()
            elif opcode == Bytecodes.COMPARE_OP:
                self.COMPARE_OP()
            elif opcode == Bytecodes.INPLACE_ADD:
                self.INPLACE_ADD()
            elif opcode == Bytecodes.INPLACE_SUBTRACT:
                self.INPLACE_SUBTRACT()
            elif opcode == Bytecodes.INPLACE_DIVIDE:
                self.INPLACE_DIVIDE()
            elif opcode == Bytecodes.LOAD_NAME:
                self.LOAD_NAME()
            elif opcode == Bytecodes.LOAD_FAST:
                self.LOAD_FAST()
            elif opcode == Bytecodes.LOAD_CONST:
                self.LOAD_CONST()
            elif opcode == Bytecodes.PRINT_ITEM:
                self.PRINT_ITME()
            elif opcode == Bytecodes.PRINT_NEWLINE:
                self.PRINT_NEWLINE()
            elif opcode == Bytecodes.RETURN_VALUE:
                return self.RETURN_VALUE()
            elif opcode == Bytecodes.SETUP_LOOP:
                self.SETUP_LOOP()
            elif opcode == Bytecodes.STORE_NAME:
                self.STORE_NAME()
            elif opcode == Bytecodes.STORE_FAST:
                self.STORE_FAST()
            elif opcode == Bytecodes.POP_BLOCK:
                self.POP_BLOCK()
            elif opcode == Bytecodes.MAKE_FUNCTION:
                self.MAKE_FUNCTION()
            elif opcode == Bytecodes.CALL_FUNCTION:
                self.CALL_FUNCTION()
            elif opcode == Bytecodes.POP_TOP:
                self.POP_TOP()
            elif opcode == Bytecodes.ROT_TWO:
                self.ROT_TWO()
            elif opcode == Bytecodes.ROT_THREE:
                self.ROT_THREE()
            elif opcode == Bytecodes.UNPACK_SEQUENCE:
                self.UNPACK_SEQUENCE()
            elif opcode == Bytecodes.JUMP_IF_TRUE_OR_POP:
                tos = self.top()
                target = self.read_operand()
                if tos.is_true():
                    self.pc = target
                else:
                    self.pop()
            elif opcode == Bytecodes.JUMP_IF_FALSE_OR_POP:
                tos = self.top()
                target = self.read_operand()
                if not tos.is_true():
                    self.pc = target
                else:
                    self.pop()
            elif opcode == Bytecodes.POP_JUMP_IF_TRUE:
                tos = self.pop()
                target = self.read_operand()
                if tos.is_true():
                    self.pc = target
            elif opcode == Bytecodes.POP_JUMP_IF_FALSE:
                tos = self.pop()
                target = self.read_operand()
                if not tos.is_true():
                    self.pc = target
            elif opcode == Bytecodes.JUMP_ABSOLUTE:
                target = self.read_operand()
                self.pc = target
                jitdriver.can_enter_jit(
                    pc=self.pc,
                    code=self.code.co_code,
                    valuestackdepth=self.valuestackdepth,
                    stack=self.stack,
                    self=self,
                )
            elif opcode == Bytecodes.JUMP_FORWARD:
                target = self.read_operand()
                self.pc += target
            elif opcode == Bytecodes.STOP_CODE:
                pass


def get_printable_location(pc, code):
    opcode = ord(code[pc])
    return "%d @ %s" % (pc, opname[opcode])


jitdriver = JitDriver(
    greens=[
        "pc",
        "code",
    ],
    reds=["valuestackdepth", "stack", "self"],
    get_printable_location=get_printable_location,
)

if __name__ == "__main__":
    import sys
    import dis
    import minipypy.frontend as frontend

    code = rpy_load_py2(sys.argv[1])
    pyframe = PyFrame(code)
    w_x = pyframe.interpret()
